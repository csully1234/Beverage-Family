"""A visitor-first exhibit of one recorded relative's life and source materials.

This page is a presentation layer over EXISTING source, genealogy, event,
photograph, and research indexes. It never resolves an uncertain identity,
creates an ancestor, downloads external scans, or publishes unapproved images.
"""
from __future__ import annotations

from urllib.parse import quote
from typing import Mapping

import streamlit as st

from evidence_explorer import evidence_catalog, for_person, render_source_card, source_items
from family_data import life_span, format_date, relationship_index
from family_research_index import build_index
from profile_life_stories import (life_record_overview, linked_book_illustrations,
                                  profile_milestones)
from family_books import load_books, book_pdf_path
from colony_photos import source_photo_preview
from routing_ui import route_link

SECTIONS = (
    "Life & timeline", "Original records", "Photographs & book", "Family connections"
)
RELATIONSHIP_LABELS = (
    ("parents", "Parents"), ("spouses", "Spouses"),
    ("children", "Children"), ("siblings", "Siblings")
)
GROUP_ORDER = (
    "Relationship evidence", "Historical investigations",
    "Historical research findings", "Historical source exhibits",
    "Historical record trails", "Original source register",
    "Scanned book photographs"
)


def exhibit_route(person_id: str, section: str | None = None) -> str:
    """Stable private-site link. Never include names or biographical notes in URLs."""
    url = "?page=collection&view=person-exhibit&person=" + quote(person_id, safe="")
    if section and section in SECTIONS:
        url += "&section=" + quote(section, safe="")
    return url


def exhibit_research_rows(person_id: str, indexed: list[dict]) -> list[dict]:
    """Exact person-ID attribution only; never link name-matched OCR or candidates."""
    return sorted((
        row for row in indexed
        if person_id in row.get("person_ids", [])
        and row.get("category") not in {
            "Existing family profiles", "Scanned book OCR leads"
        }
    ), key=lambda row: (
        GROUP_ORDER.index(row["category"]) if row["category"] in GROUP_ORDER else 99,
        str(row.get("source_date") or ""),
        str(row["title"]).casefold(), str(row["id"])
    ))


def exhibit_overview(person: dict, events: list[dict], indexed: list[dict],
                     catalog: list[dict] | None = None,
                     pictures: list[dict] | None = None) -> dict:
    """Full counts include unlinked references but do not call them scanned originals."""
    pid = str(person["id"])
    curated = for_person(pid, catalog if catalog is not None else evidence_catalog())
    citations = source_items(curated, person.get("sources") or [])
    rows = exhibit_research_rows(pid, indexed)
    photos = pictures if pictures is not None else linked_book_illustrations(pid)
    milestones = profile_milestones(person, events)
    return {
        "id": pid,
        "milestones": milestones,
        "research": rows,
        "citations": citations,
        "photos": photos,
        "linked_citations": sum(bool(source.get("url")) for source in citations),
        "linked_research": sum(bool(row.get("sources")) for row in rows),
    }


def sync_exhibit_section(person_id: str) -> None:
    selected = st.session_state.get("exhibit_section_" + person_id)
    if selected in SECTIONS:
        st.query_params["section"] = selected


def _life_section(person: dict, overview: dict) -> None:
    st.subheader("A life told through recorded events")
    sentences = life_record_overview(person)
    if sentences:
        st.write(" ".join(sentences))
        st.caption("These statements summarize indexed fields, not a newly verified biography.")
    elif person.get("biography"):
        st.write(person["biography"])
    else:
        st.info("The archive has not yet established enough dated details to write a life narrative.")
    if person.get("biography") and sentences:
        with st.expander("Read the existing biography"):
            st.write(person["biography"])

    items = overview["milestones"]
    if not items:
        st.caption("No dated milestone is linked to this person.")
    else:
        st.caption(str(len(items)) + " dated entries, including any approximate or provisional records. "
                   "A profile date is not necessarily independently verified.")
    for item in items:
        with st.container(border=True):
            st.caption(item["date_label"] or "Date not established")
            st.markdown("**" + item["title"] + "**")
            st.caption(item["status"])
            route_link("Open recorded event and its sources" if item["kind"] == "event"
                       else "Open original profile context",
                       item["url"], type="tertiary")
    if person.get("notes"):
        with st.expander("Historical notes and unresolved details"):
            st.write(person["notes"])
    route_link("See the full timeline for this relative",
               "?page=timeline&person=" + quote(str(person["id"]), safe=""))


def _records_section(overview: dict) -> None:
    records = overview["research"]
    cited = overview["citations"]
    st.subheader("Find the actual evidence behind this relative")
    st.caption("Original documents, published transcriptions, family-history claims, "
               "and tentative research leads are distinct kinds of evidence. "
               "A citation is not a scanned record, and several references can "
               "describe one underlying historical source.")
    st.markdown("**Citations attached to this profile**")
    if not cited:
        st.info("No bibliography or curated source is attached directly to this profile yet.")
    else:
        st.caption(f"{len(cited)} distinct cited destinations or labels; "
                   f"{overview['linked_citations']} lead to a web page or document.")
        for number, source in enumerate(cited):
            render_source_card(source, context="museum-" + overview["id"], number=number)
    st.markdown("**Research findings linked to this exact relative**")
    if not records:
        st.caption("No additional finding has been linked by a reviewed person ID. "
                   "A name search alone is not proof of identity.")
        return
    categories = ["All topics", *sorted({r["category"] for r in records})]
    choice = st.selectbox("Evidence collection", categories,
                          key="museum_sources_filter_" + overview["id"])
    filtered = [row for row in records if choice == "All topics" or row["category"] == choice]
    st.caption(str(len(filtered)) + " source-attributed finding(s) shown; "
               + str(len(records)) + " associated findings in the full catalog.")
    # All records are reachable. Page size limits rendering work, not archive coverage.
    size = 8
    pages = max(1, (len(filtered) + size - 1) // size)
    page_key = "museum_sources_page_" + overview["id"]
    if st.session_state.get(page_key) not in range(1, pages + 1):
        st.session_state[page_key] = 1
    page = st.selectbox("Evidence page", list(range(1, pages + 1)),
                        format_func=lambda n: str(n) + " of " + str(pages),
                        key=page_key)
    for row in filtered[(page - 1) * size:page * size]:
        with st.container(border=True):
            st.markdown("**" + row["title"] + "**")
            st.caption(row["category"] + " · " + row["status"])
            if row.get("source_date"):
                st.caption("Recorded year / period: " + str(row["source_date"]))
            if row.get("summary"):
                st.write(row["summary"])
            if row.get("limits"):
                st.caption("What this does not prove: " + row["limits"])
            if row.get("route"):
                route_link("Inspect this finding in its original context", row["route"])
            for source in row.get("sources", []):
                route_link("Read source: " + source["title"], source["url"])
            for book_page in row.get("pages", []):
                route_link("Open the original book, PDF page " + str(book_page),
                           "?page=family-books&book_page=" + str(book_page))
    route_link("Search all archival records for this relative",
               "?page=collection&view=workbench&person=" + quote(overview["id"], safe=""))


def _photographs_section(overview: dict) -> None:
    st.subheader("Photographs and illustrations from the family book")
    photos = overview["photos"]
    st.caption("Book-page links come from a reviewed exact-person cross-reference, "
               "not an OCR name match. Captions describe the book author's "
               "identification; they are not independent identity proof.")
    if not photos:
        st.info("No photo-bearing pages in the available book are linked to this exact profile.")
        route_link("Browse the complete illustrated family book", "?page=family-books")
        return
    books = load_books()
    pdf = book_pdf_path(books[0]) if books else None
    st.caption(str(len(photos)) + " attributed image-bearing page(s) · oldest-to-newest "
               "by source PDF page, not by assumed photograph date.")
    # Lazy page access avoids rendering dozens of high-resolution book scans
    # on phones, while retaining every approved illustration in the catalog.
    page_size = 6
    max_pages = max(1, (len(photos) + page_size - 1) // page_size)
    photo_page = st.selectbox("Illustration page", range(1, max_pages + 1),
                              key="museum_photos_page_" + overview["id"],
                              format_func=lambda n: str(n) + " of " + str(max_pages))
    for photo in photos[(photo_page - 1) * page_size:photo_page * page_size]:
        with st.container(border=True):
            if pdf and pdf.is_file():
                st.image(source_photo_preview(str(pdf), photo["page"], photo["crop"]),
                         width="stretch")
            st.markdown("**" + photo["title"] + "**")
            st.caption("The Colony · original PDF page " + str(photo["page"]))
            st.write(photo["caption"])
            st.caption(photo["attribution"])
            if not pdf or not pdf.is_file():
                st.caption("Original book image not yet available on this deployment.")
            route_link("Open the original book page with its full printed caption",
                       photo["url"])


def _family_section(overview: dict, people: Mapping[str, dict],
                    relationships: dict) -> None:
    pid = overview["id"]
    st.subheader("Move through documented family connections")
    st.caption("These are the archive's recorded relationships. Some are "
               "disputed or still being checked; open each profile to see its evidence.")
    for key, title in RELATIONSHIP_LABELS:
        ids = sorted(relationships.get(key, {}).get(pid, set()),
                     key=lambda ident: (str(people.get(ident, {}).get("full_name") or ident).casefold(), ident))
        with st.container(border=True):
            st.markdown("**" + title + " · " + str(len(ids)) + "**")
            if not ids:
                st.caption("No relationship recorded; absence is not negative evidence.")
            for related in ids:
                known = people.get(related)
                if known:
                    route_link(str(known.get("full_name") or related) + " · " + life_span(known),
                               exhibit_route(related))
                else:
                    st.caption(related + " · unresolved reference; no profile is available")
    route_link("Center this relative in the focused family tree",
               "?page=tree&profile=" + quote(pid, safe=""))
    route_link("Find this person in the complete family map",
               "?page=full-tree&profile=" + quote(pid, safe=""))


def render_person_exhibit(person_id: str, people: Mapping[str, dict],
                          events: list[dict], relationships: dict | None = None,
                          index: list[dict] | None = None) -> None:
    person = people.get(person_id)
    if not person:
        st.warning("That person isn't in the reviewed family index. "
                   "Choose a profile rather than assuming this historical name is the same person.")
        route_link("Browse the complete people directory", "?page=people")
        return
    overview = exhibit_overview(person, events, index if index is not None
                                else build_index(dict(people)))
    st.caption("FAMILY ARCHIVE · LIFE AND ORIGINAL EVIDENCE")
    st.title(str(person.get("full_name") or person_id))
    st.caption(life_span(person))
    st.write("Explore the recorded life, follow family connections, "
             "and examine the records behind the story.")
    info = st.columns(3)
    info[0].metric("Dated entries", len(overview["milestones"]))
    info[1].metric("Attributed research items", len(overview["research"]))
    info[2].metric("Book-photo pages", len(overview["photos"]))
    st.caption("These are catalog counts, not counts of independently verified events or original manuscripts.")
    nav = st.columns(3)
    with nav[0]:
        route_link("Open person's profile", "?page=people&profile=" + quote(person_id, safe=""),
                   width="stretch")
    with nav[1]:
        route_link("Focused tree", "?page=tree&profile=" + quote(person_id, safe=""),
                   width="stretch")
    with nav[2]:
        route_link("Full family map", "?page=full-tree&profile=" + quote(person_id, safe=""),
                   width="stretch")

    requested = str(st.query_params.get("section", "") or "")
    state_key = "exhibit_section_" + person_id
    if st.session_state.get("_last_exhibit_route") != (person_id, requested):
        st.session_state[state_key] = requested if requested in SECTIONS else SECTIONS[0]
        st.session_state["_last_exhibit_route"] = (person_id, requested)
    selected = st.radio("Explore this relative", SECTIONS,
                        key=state_key, horizontal=True,
                        on_change=sync_exhibit_section, args=(person_id,))
    # Remember the selection after Streamlit updates the URL in a widget callback.
    st.session_state["_last_exhibit_route"] = (person_id, str(st.query_params.get("section", "") or ""))

    if selected == SECTIONS[0]:
        _life_section(person, overview)
    elif selected == SECTIONS[1]:
        _records_section(overview)
    elif selected == SECTIONS[2]:
        _photographs_section(overview)
    else:
        _family_section(overview, people, relationships or relationship_index(people.values()))
