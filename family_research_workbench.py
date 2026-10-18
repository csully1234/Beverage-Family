"""Interactive source-first family research workbench.

The current data remain read-only; user actions browse citations and download
plain-text research packets. No record is changed or published automatically.
"""
from __future__ import annotations

from collections import Counter
from urllib.parse import quote

import streamlit as st

from family_books import load_book_ocr_navigation
from family_research_index import (CATEGORIES, build_index, case_packet,
                                   overview, search_index)
from routing_ui import route_link

CASES = ("Open identity questions", "Historical investigations", "Relationship evidence")


def pages_for_terms(index: dict, terms: list[str], *, require_all: bool = True) -> list[int]:
    """Book OCR term intersection/union with no inferred name-to-person links."""
    postings = [set(int(page) for page in index.get("hits", {}).get(term, []))
                for term in terms if term]
    if not postings:
        return []
    pages = set.intersection(*postings) if require_all else set.union(*postings)
    max_page = int(index.get("scanned_pages", 0))
    return sorted(page for page in pages if 1 <= page <= max_page)


def _card(row: dict, *, expanded_sources: bool = False) -> None:
    with st.container(border=True):
        st.markdown("**" + row["title"] + "**")
        st.caption(row["category"] + " · " + row["status"])
        if row["source_date"]:
            st.caption("Recorded date / period: " + row["source_date"])
        if row["summary"]:
            st.write(row["summary"])
        st.caption("Evidence limitation: " + row["limits"])
        if row["route"]:
            route_link("Open original context and related records →", row["route"])
        if row["sources"]:
            with st.expander("Source documents · " + str(len(row["sources"])),
                             expanded=expanded_sources):
                for source in row["sources"]:
                    route_link(source["title"], source["url"])
                    if source["note"]:
                        st.caption(source["note"])
        if row["pages"]:
            st.caption("Scanned source pages: " + ", ".join(map(str, row["pages"][:12])) +
                       (" …" if len(row["pages"]) > 12 else ""))
        st.download_button(
            "Download source-attributed research note",
            case_packet(row), file_name="family-research-" +
            row["id"].replace(":", "-")[:85] + ".md", mime="text/markdown",
            key="workbench_packet_" + row["id"],
        )


def _query_sync() -> None:
    query = str(st.session_state.get("workbench_query", "")).strip()
    if query:
        st.query_params["q"] = query
    elif "q" in st.query_params:
        del st.query_params["q"]


def _browse(records: list[dict], people: dict) -> None:
    st.subheader("Search across every family collection")
    st.caption("Records are linked to their actual sources. Search matches help find "
               "evidence; they do not validate a claimed relationship or turn OCR "
               "mentions into identified ancestors.")
    cols = st.columns([2, 1, 1])
    with cols[0]:
        q = st.text_input("Search names, years, records and topics",
                          value=str(st.query_params.get("q", "") or ""),
                          key="workbench_query", on_change=_query_sync,
                          placeholder="Nathaniel, 1786, Lowell, Topsham lots…")
    with cols[1]:
        category = st.selectbox("Collection", ["All collections", *CATEGORIES],
                                key="workbench_category")
    with cols[2]:
        ids = sorted(people, key=lambda pid: (
            str(people[pid].get("full_name", pid)).casefold(), pid))
        preferred = str(st.query_params.get("person", "") or "")
        if preferred in people and st.session_state.get("_wb_last_person_route") != preferred:
            st.session_state["workbench_person"] = preferred
        st.session_state["_wb_last_person_route"] = preferred
        person = st.selectbox("Relative", ["", *ids],
                              format_func=lambda p: people[p].get("full_name", p)
                              if p else "All relatives",
                              key="workbench_person")
    ocr = st.checkbox("Include tentative OCR page matches", value=True,
                      key="workbench_include_ocr")
    try:
        source_page = int(st.query_params.get("book_page", "") or 0)
    except (ValueError, TypeError):
        source_page = 0
    if not 1 <= source_page <= 305:
        source_page = 0
    found = search_index(records, query=q,
                         category=category if category != "All collections" else "",
                         person_id=person, show_ocr=ocr, book_page=source_page)
    if source_page:
        st.caption("Original scanned source page " + str(source_page) +
                   " · these are documentary associations, not verified identities")
        route_link("Return to the full archive search", "?page=collection&view=workbench")
    st.caption(f"{len(found)} matching indexed items · all results reachable")
    if person:
        route_link("Open " + people[person].get("full_name", person) + "'s profile",
                   "?page=people&profile=" + quote(person))
    page_size = 9
    pages = max(1, (len(found) + page_size - 1) // page_size)
    current = st.session_state.get("workbench_page", 1)
    if not isinstance(current, int) or current < 1 or current > pages:
        st.session_state["workbench_page"] = 1
    selected_page = st.selectbox("Result page", list(range(1, pages + 1)),
                                 format_func=lambda i: f"{i} of {pages}",
                                 key="workbench_page")
    first = (selected_page - 1) * page_size
    for row in found[first:first + page_size]:
        _card(row)
    if not found:
        st.info("No indexed item matched. Try fewer words or choose all collections. "
                "The OCR vocabulary is limited; a zero result does not prove that "
                "a name is absent from the original book.")


def _cases(records: list[dict], initial_id: str = "") -> None:
    cases = [r for r in records if r["category"] in CASES]
    if not cases:
        st.info("No open case files are indexed.")
        return
    lookup = {r["id"]: r for r in cases}
    if initial_id and initial_id not in lookup:
        st.warning("The requested case is not indexed; showing the investigation library.")
    choices = sorted(lookup, key=lambda ident: (lookup[ident]["category"],
                                                lookup[ident]["title"].casefold()))
    default = choices.index(initial_id) if initial_id in lookup else 0
    if initial_id in lookup and st.session_state.get("_wb_last_case_route") != initial_id:
        st.session_state["workbench_case"] = initial_id
    st.session_state["_wb_last_case_route"] = initial_id
    chosen = st.selectbox("Open a source-by-source investigation",
                          choices, index=default,
                          format_func=lambda ident: lookup[ident]["title"] + " · " +
                          lookup[ident]["category"],
                          key="workbench_case")
    route_link("Share a link to this case",
               "?page=collection&view=workbench&case=" + quote(chosen, safe=""))
    _card(lookup[chosen], expanded_sources=True)
    st.caption("Source packets do not create or change genealogy records, and "
               "copyrighted external historical materials are linked, not rehosted.")


def _book_cross_search() -> None:
    nav = load_book_ocr_navigation()
    st.subheader("Cross-search the 305-page scanned book")
    st.write("Compare two indexed words to narrow the original scanned pages worth "
             "inspecting. Matching pages are **not** proof that the words refer to "
             "the same person, photograph or family relationship.")
    terms = sorted(nav.get("hits", {}), key=str.casefold)
    if not terms:
        st.info("The book's OCR navigation index is not available.")
        return
    a, b, c = st.columns([2, 2, 1])
    with a:
        first = st.selectbox("First indexed word", terms, key="wb_book_word_a")
    with b:
        second = st.selectbox("Optional second word", ["", *terms],
                              key="wb_book_word_b",
                              format_func=lambda v: v or "Any second word")
    with c:
        method = st.selectbox("Find pages", ["Both words", "Either word"],
                              key="wb_book_mode")
    chosen = [first] + ([second] if second else [])
    pages = pages_for_terms(nav, chosen, require_all=method=="Both words")
    st.caption(f"{len(pages)} possible matching original pages · OCR is a navigation aid only")
    if not pages:
        st.info("No page in this limited OCR index contains the selected combination. "
                "This does not prove those terms are absent from the book.")
        return
    batch = st.selectbox("Pages", list(range(1, (len(pages)+14)//15+1)),
                         key="wb_book_result_page",
                         format_func=lambda n: f"{n} of {(len(pages)+14)//15}")
    for page in pages[(batch-1)*15:batch*15]:
        route_link("Open *The Colony*, PDF page " + str(page) +
                   " and its original scanned evidence",
                   "?page=family-books&book_page=" + str(page))
    route_link("Read the complete 305-page edition", "?page=family-books")


def _priorities(records: list[dict]) -> None:
    st.subheader("What should we investigate next?")
    st.write("These are unresolved cases that can benefit from originals—birth, marriage, "
             "probate, deed and contemporary testimony. The order below is for "
             "browsing, **not a numerical probability that an ancestor is correct**.")
    groups = [("Unresolved book people", lambda row: row["id"].startswith("unresolved:")),
              ("Early ancestry investigations", lambda row: row["id"].startswith("ancestry:")),
              ("Other identity cases", lambda row: row["id"].startswith("identity:"))]
    for title, predicate in groups:
        subset = [row for row in records if predicate(row)]
        with st.expander(f"{title} · {len(subset)}", expanded=title=="Early ancestry investigations"):
            for row in subset:
                with st.container(border=True):
                    st.markdown("**" + row["title"] + "**")
                    st.caption(row["status"])
                    st.write(row["limits"])
                    route_link("Open case evidence",
                               "?page=collection&view=workbench&case=" + quote(row["id"], safe=""))
    st.caption("A citation from one original cemetery marker printed in multiple "
               "books still counts as one underlying historical source, not multiple "
               "independent confirmations.")


def render_research_workbench(people: dict) -> None:
    records = build_index(people)
    info = overview(records)
    st.title("Family Research Workbench")
    st.write("Explore every branch of the historical archive in one place: "
             "original book pages, family photographs, disputed identities, "
             "cited historical findings and individual relationship claims.")
    st.caption("This is a research discovery tool, not a new verified family tree. "
               "The cited originals and existing records remain authoritative.")
    a, b, c = st.columns(3)
    a.metric("Searchable archive entries", info["total"])
    b.metric("Book pages with OCR clues", info["unique_book_pages"])
    c.metric("Unresolved book identities", info["unresolved_book_names"])
    requested = str(st.query_params.get("case", "") or "")
    if requested:
        selected_case = next((r for r in records
                              if r["id"] == requested and r["category"] in CASES), None)
        if selected_case:
            st.subheader("Requested historical case file")
            _card(selected_case, expanded_sources=True)
        else:
            st.warning("The case link is not in the currently indexed case register.")
    tabs = st.tabs(["Explore the archive", "Case files", "Cross-search book pages",
                    "Unresolved research priorities"])
    with tabs[0]:
        if requested:
            st.info("A specific case was requested. Open the Case files tab to inspect "
                    "its evidence, source links, and downloadable research packet.")
        _browse(records, people)
    with tabs[1]:
        _cases(records, requested)
    with tabs[2]:
        _book_cross_search()
    with tabs[3]:
        _priorities(records)
