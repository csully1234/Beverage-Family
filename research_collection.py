"""Read-only research collection; no overlays or inferred family relationships."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from archive import historical_person, safe_url

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "research" / "collection_2026-10-14"
CONFIDENCE = ("Confirmed", "Strongly supported", "Probable", "Possible lead", "Conflict", "Rejected")
STRONG = frozenset(CONFIDENCE[:2])


def source_ids(record: dict, field: str = "Supporting sources") -> list[str]:
    return list(dict.fromkeys(re.findall(r"\bSRC\d{3}\b", record.get(field) or "")))


def search_text(record: Any) -> str:
    return json.dumps(record, ensure_ascii=False).casefold()


def matches(query: str, record: Any) -> bool:
    text = search_text(record)
    return all(term in text for term in query.casefold().split())


class CollectionIndex:
    def __init__(self, raw: dict):
        self.raw = raw
        self.findings = {r["Research ID"]: r for r in raw["findings"]}
        self.sources = {r["Source ID"]: r for r in raw["sources"]}
        self.targets = {r["Target ID"]: r for r in raw["targets"]}
        self.inventories = {r["name"]: r for r in raw["inventories"]}

    @classmethod
    def load(cls, path: Path | None = None) -> "CollectionIndex":
        return cls(json.loads((path or ROOT / "data" / "collections" / "2026-10-14.json").read_text()))

    def for_subject(self, kind: str, identifier: str) -> list[dict]:
        field = {"person": "people_ids", "place": "place_ids", "event": "event_ids"}[kind]
        return [r for r in self.findings.values() if identifier in r["Navigation"][field]]

    def for_source(self, identifier: str) -> list[dict]:
        return [r for r in self.findings.values() if identifier in source_ids(r)]

    def targets_for(self, record: dict) -> list[dict]:
        ids = set(source_ids(record))
        return [r for r in self.targets.values() if ids.intersection(source_ids(r, "Source IDs"))]

    def select(self, query: str = "", confidence: str = "", topic: str = "",
               person_id: str = "", place_id: str = "", location: str = "") -> list[dict]:
        result = []
        for record in self.findings.values():
            nav = record["Navigation"]
            if confidence and record["Confidence"] != confidence:
                continue
            if topic and topic not in nav["topics"]:
                continue
            if person_id and person_id not in nav["people_ids"]:
                continue
            if place_id and place_id not in nav["place_ids"]:
                continue
            if location and location != record["Location"]:
                continue
            evidence = [self.sources[sid] for sid in source_ids(record) if sid in self.sources]
            if matches(query, [record, evidence]):
                result.append(record)
        return result

    def inventory_rows(self, name: str, research_id: str | None = None) -> list[dict]:
        table = self.inventories[name]
        rows = [dict(zip(table["headers"], row)) for row in table["rows"]]
        return rows if research_id is None else [r for r in rows if r.get("Research ID") == research_id]


def validate_collection(collection: CollectionIndex, site: dict, root: Path = ROOT) -> list[str]:
    """Validate references, ratings, report integrity and the preserved snapshot."""
    errors = []
    raw = collection.raw
    for records, key in ((raw["findings"], "Research ID"), (raw["sources"], "Source ID"),
                         (raw["targets"], "Target ID")):
        ids = [r[key] for r in records]
        if len(ids) != len(set(ids)):
            errors.append(f"Duplicate {key}")
    indexes = {"people_ids": {r["id"]: r for r in site["people"]},
               "place_ids": {r["id"]: r for r in site["places"]},
               "event_ids": {r["id"]: r for r in site["events"]}}
    for rid, record in collection.findings.items():
        if record.get("Confidence") not in CONFIDENCE:
            errors.append(f"{rid}: invalid confidence")
        for field in ("Proposed fact or narrative", "Exact citation", "Notes about uncertainty",
                      "Evidence basis", "Human-review status"):
            if not record.get(field):
                errors.append(f"{rid}: missing {field}")
        refs = source_ids(record)
        if not refs or not set(refs) <= collection.sources.keys():
            errors.append(f"{rid}: missing source reference")
        nav = record["Navigation"]
        for field, index in indexes.items():
            if not set(nav[field]) <= index.keys():
                errors.append(f"{rid}: unknown {field}")
        for pid in nav["people_ids"]:
            if pid in indexes["people_ids"] and not historical_person(indexes["people_ids"][pid]):
                errors.append(f"{rid}: newly linked possibly living profile {pid}")
    for sid, record in collection.sources.items():
        if record.get("URL") and not safe_url(record["URL"]):
            errors.append(f"{sid}: invalid source URL")
    for gid, record in collection.targets.items():
        if not set(source_ids(record, "Source IDs")) <= collection.sources.keys():
            errors.append(f"{gid}: unknown source")
    for report in raw["reports"]:
        path = root / "research" / "collection_2026-10-14" / report["filename"]
        if path.name != report["filename"] or not path.is_file():
            errors.append(f"Missing report: {report['filename']}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != report["sha256"]:
            errors.append(f"Report checksum differs: {report['filename']}")
    # This package is additive. The existing Tea Party, address, property,
    # relationship and date records all remain byte-identical to the baseline.
    baseline = root / "research" / "collection_2026-10-14" / "baseline_hashes.json"
    for record in json.loads(baseline.read_text()):
        if hashlib.sha256((root / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"Research import changed baseline: {record['file']}")
    return errors
