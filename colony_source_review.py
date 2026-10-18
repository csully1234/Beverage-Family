"""Book-page research, visual-review limits and expanded OCR navigation.

Every page hit is machine-generated or an attributed statement from the
2016 family book. The PDF scan remains the authoritative displayed source.
This module never adds relatives, edits historical claims, or constructs kinship.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import streamlit as st
from routing_ui import route_link
from family_books import load_book_ocr_navigation

ROOT = Path(__file__).resolve().parent
REVIEW_FILE = ROOT / "data" / "phase18_colony_page_source_review.json"
EXPANDED_FILE = ROOT / "data" / "colony_expanded_ocr_index.json"

def load_book_page_reviews() -> list[dict]:
    data = json.loads(REVIEW_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Page annotations must be an array")
    return data

def reviews_for_book_page(page: int) -> list[dict]:
    return [item for item in load_book_page_reviews() if item["pdf_page"] == page]

def load_expanded_ocr_navigation() -> dict:
    if EXPANDED_FILE.is_file():
        data = json.loads(EXPANDED_FILE.read_text(encoding="utf-8"))
        result = data[0] if isinstance(data, list) and data else {}
        if isinstance(result, dict) and result.get("scanned_pages") == 305:
            return result
    # If the optional generated file has not arrived, never claim the complete
    # transcript is searchable. Preserve the previous 35-term aid.
    original = load_book_ocr_navigation()
    return {
        "scanned_pages": original.get("scanned_pages", 305),
        "terms": original.get("hits", {}),
        "method": "Legacy limited OCR term index, not full text",
        "review_status": "Machine-detected index is incomplete and unverified",
        "vocabulary_size": len(original.get("hits", {})),
        "contains_full_original_text": False,
        "no_identifying_person_ids": True,
    }

def pages_for_book_terms(index: Mapping, terms: list[str], *, both: bool) -> list[int]:
    hits = index.get("terms", {})
    selected = [set(int(p) for p in hits.get(t, [])) for t in terms if t]
    if not selected:
        return []
    result = set.intersection(*selected) if both else set.union(*selected)
    return sorted(p for p in result if 1 <= p <= 305)

def _show_case(item: dict, people_by_id: Mapping | None = None) -> None:
    with st.container(border=True):
        st.markdown("**" + item["title"] + "**")
        st.caption("The Colony (2016), original PDF page " + str(item["pdf_page"]) +
                   " · " + item["category"])
        st.write(item["observation"])
        st.caption("Evidence interpretation: " + item["status"])
        st.caption("Page review: " + item["verification"])
        st.markdown("**Why this record matters**")
        st.write(item["why_it_matters"])
        route_link("Open and visually inspect the exact original book page",
                   "?page=family-books&book_page=" + str(item["pdf_page"]))
        if people_by_id:
            for pid in item.get("people_ids", []):
                person = people_by_id.get(pid)
                if person:
                    route_link("See related profile: " +
                               str(person.get("full_name", pid)),
                               "?page=people&profile=" + pid, type="tertiary")
        with st.expander("Original records still needed"):
            for step in item["next_originals"]:
                st.write("• " + step)

def render_page_review_notes(page: int) -> None:
    records = reviews_for_book_page(int(page))
    if not records:
        return
    st.subheader("What is known about statements on this page?")
    st.caption("These notes distinguish the author's reported history, later published "
               "genealogy and corroboration still needed. They do not update the family tree.")
    for record in records:
        _show_case(record)
    if page == 17:
        from matthew_reconciliation import render_matthew_case_from_book
        render_matthew_case_from_book(page)

def render_source_review_notebook(people_by_id: Mapping | None = None) -> None:
    st.subheader("Source review notebook")
    st.write("Explore specific historical claims in the original 305-page family book. "
             "A visually checked line can establish what the **book reports**, not that "
             "the reported birth, marriage or kinship is independently proven.")
    rows = load_book_page_reviews()
    q = st.text_input("Search source-review notes",
                      placeholder="Matthew, Clarissa, land petition, Scotland, Olive…",
                      key="colony_page_review_query").strip().casefold()
    categories = sorted({item["category"] for item in rows})
    topic = st.selectbox("Study topic", ["All topics", *categories],
                         key="colony_page_review_topic")
    selected = [r for r in rows
                if (topic == "All topics" or r["category"] == topic)
                and (not q or q in json.dumps(r,ensure_ascii=False).casefold())]
    st.caption(f"{len(selected)} of {len(rows)} source-question notes · "
               "only selected pages manually investigated so far")
    for row in selected:
        _show_case(row, people_by_id)

def render_expanded_ocr_finder() -> None:
    nav = load_expanded_ocr_navigation()
    terms = sorted(nav.get("terms", {}), key=str.casefold)
    st.subheader("Search machine-indexed words throughout the scanned book")
    st.caption("The entire PDF remains image-only. Indexed occurrences are "
               "OCR-detected page leads, **not verified quotations or family relationships**. "
               "A word may be misread, omitted or refer to a namesake.")
    st.caption(str(nav.get("method", "")) + " · " + str(len(terms)) +
               " terms with possible page matches")
    if not terms:
        st.info("The OCR page index is unavailable; the full PDF remains readable above.")
        return
    a,b,c = st.columns([2,2,1])
    with a:
        term_a = st.selectbox("First topic, name or year",terms,key="expanded_book_term_a")
    with b:
        term_b = st.selectbox("Second word (optional)",["",*terms],
                              format_func=lambda v:v or "Any second word",
                              key="expanded_book_term_b")
    with c:
        mode = st.selectbox("Match",["Both", "Either"],key="expanded_book_term_mode")
    results=pages_for_book_terms(nav,[term_a,term_b],both=mode=="Both")
    st.caption(f"{len(results)} potential original PDF pages")
    size = 20
    pages = max(1,(len(results)+size-1)//size)
    if st.session_state.get("expanded_book_results_page",1) not in range(1,pages+1):
        st.session_state["expanded_book_results_page"]=1
    page = st.selectbox("Result page",range(1,pages+1),
                        format_func=lambda x:f"{x} of {pages}",
                        key="expanded_book_results_page")
    for found in results[(page-1)*size:page*size]:
        route_link("Inspect original source image · PDF p. " + str(found),
                   "?page=family-books&book_page=" + str(found))
    if not results:
        st.info("No result in the current vocabulary. This does NOT establish that the "
                "name or topic is absent from the printed pages.")
    st.caption("OCR text is not copied into the site or reused as an authenticated "
               "source; read the original page and its printed caption.")
