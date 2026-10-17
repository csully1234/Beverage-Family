"""Visitor-friendly evidence trails separate from unsupported genealogy edges.

Curated cases represent published *claims* and the original records needed to
evaluate them.  Merely loading these records NEVER alters the family tree.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from routing_ui import route_link

FILE = Path(__file__).resolve().parent / "data" / "phase8_identity_evidence.json"


def load_identity_cases() -> list[dict]:
    """Keep readable, stable cases; never use case names as implicit person IDs."""
    if not FILE.is_file():
        return []
    records = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Identity evidence catalog must be an array")
    return sorted(records, key=lambda row: (int(row.get("priority", 99)), str(row.get("name", "")).casefold()))


def cases_for_profile(person_id: str) -> list[dict]:
    """Only exact, reviewed IDs: no fuzzy name to profile mapping."""
    return [row for row in load_identity_cases()
            if row.get("tree_profile_id") == person_id]


def cases_for_page(page: int) -> list[dict]:
    """Book-page association is contextual, NOT a verified person identity."""
    return [row for row in load_identity_cases() if page in row.get("book_pages", [])]


def _source_label(kind: str) -> str:
    return {
        "contemporary_obituary": "Contemporary obituary",
        "contemporary_diary_transcription": "Transcribed firsthand diary",
        "institutional_index": "Institutional catalog/index",
        "historical_genealogy_1851": "Historic published genealogy",
        "published_genealogy": "Published genealogy",
        "derivative_compilation": "Compiled genealogy — confirm originals",
        "archive_finding_aid": "Original-record search collection",
        "official_record_guide": "Official archive guide",
    }.get(kind, "Historical source")


def render_case_evidence(record: dict, *, show_book_links: bool = True) -> None:
    st.write(str(record.get("known", "")))
    st.caption("Evidence status: " + str(record.get("status", "Not fully verified")))
    if record.get("limits"):
        st.info("What this does **not** establish: " + str(record["limits"]))
    sources = record.get("sources", [])
    if sources:
        st.markdown("**Explore supporting records**")
        for item in sources:
            label = str(item.get("title", "Inspect source"))
            st.caption(_source_label(str(item.get("kind", ""))))
            route_link(label, str(item.get("url", "")))
            if item.get("proves"):
                st.caption(str(item["proves"]))
    if show_book_links:
        pages = sorted(set(int(x) for x in record.get("book_pages", [])))
        if pages:
            st.markdown("**Examine the original book pages**")
            for page in pages:
                route_link(f"The Colony — scanned PDF page {page}",
                           "?page=family-books&book_page=" + str(page))
    original = record.get("next_originals", [])
    if original:
        st.markdown("**Which original records would settle this?**")
        for need in original:
            st.markdown("**" + str(need.get("record", "Original record")) + "**")
            st.write(str(need.get("where", "")))


def render_identity_explorer() -> None:
    """Public visitor case view; not a raw internal spreadsheet."""
    catalog = load_identity_cases()
    st.subheader("Family mysteries — explore what the records really show")
    st.write("Compare family memories, independent historical documents, and "
             "the source records still needed to connect our relatives responsibly.")
    st.caption("A person mentioned in a document is not automatically a verified "
               "member of the tree. All links open their existing family profile, "
               "the original book, or the external record holder.")
    term = st.text_input("Find an identity or family question",
                         placeholder="Lyford, Priscilla, Vernon, Matthew…",
                         key="phase8_case_search").strip().casefold()
    group = st.selectbox("Show", ["All evidence questions", "Most promising connections",
                                  "Other research questions"], key="phase8_case_group")
    filtered = [row for row in catalog
                if (not term or term in (" ".join([
                    str(row.get("name", "")), str(row.get("known", "")),
                    str(row.get("status", ""))])).casefold())
                and (group == "All evidence questions" or
                     (row.get("priority") == 1) == (group == "Most promising connections"))]
    st.caption(f"{len(filtered)} family questions with clickable evidence")
    for row in filtered:
        with st.expander(str(row.get("name", "Historical identity"))):
            render_case_evidence(row)
            if row.get("tree_profile_id"):
                route_link("View the existing relative's profile",
                           "?page=people&profile=" + str(row["tree_profile_id"]))


def render_profile_identity_evidence(person_id: str) -> None:
    cases = cases_for_profile(person_id)
    if not cases:
        return
    with st.expander(f"Original evidence and family questions ({len(cases)})"):
        for record in cases:
            st.markdown("**" + str(record.get("name", "Family history")) + "**")
            render_case_evidence(record)
