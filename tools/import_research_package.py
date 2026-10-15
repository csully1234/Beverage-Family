"""Import the approved research workbooks without changing genealogy records.

Usage: python tools/import_research_package.py PATH_TO_FIVE_REPORTS
Requires only Python's standard library. The checked-in navigation file is
editorial: it links subjects for browsing, never creates family relationships.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "research" / "collection_2026-10-14"
N = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
FILES = {
    "Beverage_Family_Master_Research.xlsx": "Master research workbook",
    "Beverage_Family_Site_Candidates.xlsx": "Website candidates and review status",
    "Beverage_Family_Research_Dossier.docx": "Research dossier",
    "Beverage_Family_Source_Register.docx": "Complete source register",
    "Beverage_Family_Research_Gaps.docx": "Research gaps and retrieval requests",
}


def read_workbook(path: Path) -> list[dict]:
    """Read cell values, preserving empty cells and the workbook's column order."""
    with ZipFile(path) as book:
        strings = []
        if "xl/sharedStrings.xml" in book.namelist():
            strings = ["".join(node.itertext()) for node in
                       ET.fromstring(book.read("xl/sharedStrings.xml"))]
        rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in
                ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))}
        result = []
        for sheet in ET.fromstring(book.read("xl/workbook.xml")).find("s:sheets", N):
            target = rels[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            rows = []
            for row in ET.fromstring(book.read(target)).findall("s:sheetData/s:row", N):
                # The supplied workbooks use rows 1–3 for title/spacing and
                # row 4 for the actual table headers on every sheet.
                if int(row.attrib["r"]) < 4:
                    continue
                values = []
                for cell in row:
                    letters = re.match(r"[A-Z]+", cell.attrib["r"])[0]
                    col = 0
                    for letter in letters:
                        col = col * 26 + ord(letter) - 64
                    while len(values) < col:
                        values.append(None)
                    value = cell.findtext("s:v", namespaces=N)
                    kind = cell.attrib.get("t")
                    if kind == "s" and value is not None:
                        value = strings[int(value)]
                    elif kind == "inlineStr":
                        value = "".join(cell.find("s:is", N).itertext())
                    elif value is not None and kind not in {"str", "e"}:
                        number = float(value)
                        value = int(number) if number.is_integer() else number
                    values[col - 1] = value
                rows.append(values)
            if rows:
                headers = rows[0]
                result.append({"name": sheet.attrib["name"], "headers": headers,
                               "rows": [(r + [None] * len(headers))[:len(headers)] for r in rows[1:]]})
        return result


def records(table: dict) -> list[dict]:
    return [dict(zip(table["headers"], row)) for row in table["rows"]]


def read_dossier(path: Path) -> list[dict]:
    """Keep paragraphs, hyperlinks and tables for an on-site section reader."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(path) as book:
        rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in
                ET.fromstring(book.read("word/_rels/document.xml.rels"))}
        body = ET.fromstring(book.read("word/document.xml")).find("w:body", ns)
        sections = [{"title": "About this dossier", "blocks": []}]

        def paragraph(node):
            parts = []
            for child in node:
                text = "".join(t.text or "" for t in child.findall(".//w:t", ns))
                if child.tag.endswith("}hyperlink"):
                    rid = child.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                    url = rels.get(rid, "")
                    if url.startswith(("https://", "http://")):
                        text = f"[{text}]({url})"
                parts.append(text)
            return "".join(parts)

        for node in body:
            if node.tag.endswith("}p"):
                text = paragraph(node)
                style = node.find("w:pPr/w:pStyle", ns)
                style_name = style.get("{" + ns["w"] + "}val", "") if style is not None else ""
                if style_name == "Heading1":
                    sections.append({"title": text, "blocks": []})
                elif text:
                    sections[-1]["blocks"].append({"type": "heading" if style_name.startswith("Heading") else "paragraph", "text": text})
            elif node.tag.endswith("}tbl"):
                rows = [["\n".join(paragraph(p) for p in cell.findall("w:p", ns))
                         for cell in row.findall("w:tc", ns)] for row in node.findall("w:tr", ns)]
                sections[-1]["blocks"].append({"type": "table", "rows": rows})
        return sections


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    args = parser.parse_args()
    REPORTS.mkdir(parents=True, exist_ok=True)
    manifest = []
    for filename, title in FILES.items():
        source = args.input_dir / filename
        if not source.exists():
            source = args.input_dir / filename.replace(".", "(1).", 1)
        destination = REPORTS / filename
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        manifest.append({"filename": filename, "title": title,
                         "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
    master = read_workbook(REPORTS / "Beverage_Family_Master_Research.xlsx")
    candidates = read_workbook(REPORTS / "Beverage_Family_Site_Candidates.xlsx")
    tables = {table["name"]: table for table in master}
    candidate_tables = {table["name"]: table for table in candidates}
    navigation = json.loads((REPORTS / "navigation.json").read_text())
    findings = records(candidate_tables["Site Candidates"])
    for finding in findings:
        finding["Navigation"] = navigation[finding["Research ID"]]
    collection = {
        "date": "2026-10-14",
        "baseline_commit": "4e3d4860d3c8d9ae9cbcb19567dafa17e1a93db1",
        "findings": findings,
        "sources": records(candidate_tables["Source Lookup"]),
        "targets": records(tables["Offline and Paywalled Records"]),
        "inventories": master + [candidate_tables["Review Guide"]],
        "reports": manifest,
        "dossier": read_dossier(REPORTS / "Beverage_Family_Research_Dossier.docx"),
    }
    collection_path = ROOT / "data" / "collections" / "2026-10-14.json"
    collection_path.parent.mkdir(parents=True, exist_ok=True)
    collection_path.write_text(
        json.dumps(collection, indent=2, ensure_ascii=False) + "\n")
    print(f"Imported {len(findings)} findings, {len(collection['sources'])} sources, "
          f"{len(collection['targets'])} retrieval targets, and {len(manifest)} reports.")


if __name__ == "__main__":
    main()
