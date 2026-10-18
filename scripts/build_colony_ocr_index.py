"""Generate a restricted-vocabulary, page-level OCR navigation index.

Run offline in a trusted environment with Python, PyMuPDF, and Tesseract 5:
    python scripts/build_colony_ocr_index.py

The 305-page source is image-only and remains the authoritative book.
NO OCR transcript is published to the repository and NO people IDs are inferred.
Every page hit is a machine-generated, possibly inaccurate navigation clue.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf"
OUT = ROOT / "data/colony_expanded_ocr_index.json"
NAV = ROOT / "data/colony_ocr_navigation_index.json"

# A conservative vocabulary, never an automatically verified family identity.
# Older terms are preserved. New historical subjects and persons are navigation
# labels ONLY; matching a full name does not prove a genealogical relationship.
HISTORICAL_TERMS = """
James Beveridge|James Beverage|James Beviridge|Sarah Bennett|Sarah Holman|
Jean White|Jean McKinney|George White|John White|Nicholas White|
Thomas Beverage|Mercy Kent|Mercy Beveridge|Ezekiel Kent|Susannah Kent|
John Richard Kent|Nathaniel Winslow|Penelope Kent|Benjamin Kent|
Matthew Beverage|Abigail Dyer|Captain Eleazer Crabtree|Eleazer Crabtree|
Jemima Crabtree|Benjamin Crabtree Beverage|Amelia Beverage|Hanson Beverage|
Norwood Beverage|Hannah Grant|Solomon Grant|Andrew Grant|Peter Grant|
Orris Lyford Beverage|Rose Emma Pierson|Florence Merrill Budlong|
Ida Louisa Gattrell|Charles Gattrell|Albion Pierson|Priscilla Delano|
Ruth Bingham Reynolds|Vernon Linwood Beverage|Nellie Marion Ames|
Sarah Loveland|Ella May Thompson|Annie Ursula Leadbetter|Daniel Green|
Lyford Pierson Beveridge|Lowell Pierson Beveridge|Helen Beveridge|
Olive Amelia Beveridge|Eliot Pierson Beveridge|Norwood Pierson Beveridge|
Captain Barnabas Cobb|Clarissa Cobb|John Minot|Francis McLean|
Solomon Lovell|Stephen Gatchell|Ezekiel Kent Jr|
Marblehead|Fort Richmond|Kennebec|Brunswick|Topsham|Georgetown|
Marshfield|Mere Point|Minot's stockade|Fort Richmond|
Fox Islands|North Haven|Vinalhaven|Southern Harbor|Pulpit Harbor|
Kent Cove|Marsh Cove|Mair Point|Pejepscot|Penobscot|Castine|
Majabigwaduce|Cushing|Camden|Rockland|Hope Maine|Thomaston|
Warren Maine|Dorchester|Kenduskeag|Orono|Tenants Harbor|
Brattleboro|Newburyport|Newton|Harvard|Radcliffe|Boston Latin|
Red Cottage|Point Cottage|The Colony|Benjamin's Farm|Crabtree Point|
Boston Tea Party|Battle of Dunbar|Penobscot Expedition|War of Independence|
Revolutionary War|French and Indian War|Continental Army|British Royal Navy|
British Navy|Castine expedition|Fort Richmond soldier|privateer|
shipbuilder|land petition|land grant|town meeting|1763 petition|
1785 petition|1786 testimony|schooner Ann|Lucy & Nancy|
sheep farming|sheep barn|schoolhouse|farmhouse|Cobb family|
marriage|birth|probate|deed|testimony|petition|cemetery|
woodpile|lumber|blacksmith|captain|shipwreck|harbor|
1750|1752|1758|1763|1764|1774|1776|1781|1785|1786|1801|1831|1918|1936
"""

def terms() -> list[str]:
    old = json.loads(NAV.read_text(encoding="utf-8"))[0]["hits"]
    raw = [*old.keys(), *HISTORICAL_TERMS.replace("\n", "").split("|")]
    return sorted({t.strip() for t in raw if len(t.strip()) >= 3}, key=str.casefold)

def ocr_page(page: int) -> tuple[int, str, int]:
    # Each task opens its own document. PyMuPDF documents are not shared across processes.
    with fitz.open(PDF) as doc:
        pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(2, 2),
                                      colorspace=fitz.csGRAY, alpha=False)
        image = pix.tobytes(output="png")
    result = subprocess.run(
        ["tesseract", "stdin", "stdout", "-l", "eng", "--psm", "3"],
        input=image, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=40, check=True,
        env={**os.environ, "OMP_THREAD_LIMIT": "1"},
    )
    text = result.stdout.decode("utf-8", "replace")
    return page, text, len(re.findall(r"\b\w+\b", text))

def build(*, jobs: int = 4) -> dict:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    with fitz.open(PDF) as doc:
        pages = len(doc)
    if pages != 305:
        raise ValueError(f"Expected 305 source pages, found {pages}")
    vocabulary = terms()
    compiled = {
        t: re.compile(r"(?<!\w)" + r"\s+".join(map(re.escape, t.split())) + r"(?!\w)",
                      re.IGNORECASE)
        for t in vocabulary
    }
    matches = {t: [] for t in vocabulary}
    page_words = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        for page, text, count in pool.map(ocr_page, range(1, pages+1)):
            page_words[page] = count
            for term, pattern in compiled.items():
                if pattern.search(text):
                    matches[term].append(page)
    return {
        "source": "The Colony (2016), author-supplied clean 305-page PDF",
        "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "scanned_pages": pages,
        "method": "Tesseract 5 English psm 3, 144dpi grayscale; controlled navigation vocabulary",
        "review_status": "Entire index is MACHINE-GENERATED AND UNVERIFIED. Not a genealogical transcript.",
        "meaning": "A listed page may mention a term; the scan must be inspected for correct context.",
        "limitations": "Missing or false hits possible, namesakes not resolved, and no new parentage asserted.",
        "vocabulary_size": len(vocabulary),
        "terms": {term: values for term, values in matches.items() if values},
        "page_word_counts": [page_words[page] for page in range(1, pages+1)],
        "no_identifying_person_ids": True,
        "contains_full_original_text": False,
    }

if __name__ == "__main__":
    result = build()
    OUT.write_text(json.dumps([result], ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("Indexed", result["scanned_pages"], "pages;",
          result["vocabulary_size"], "controlled terms;",
          len(result["terms"]), "terms found; index", OUT.stat().st_size, "bytes")
