"""A visitor-first exhibit of one recorded relative's life and source materials.

This page is a presentation layer over EXISTING source, genealogy, event,
photograph, and research indexes. It never resolves an uncertain identity,
creates an ancestor, downloads external scans, or publishes unapproved images.
"""
from __future__ import annotations

from urllib.parse import quote
from typing import Mapping

import streamlit as st

from evidence_explorer import evidence_catalog, for_event, for_person, render_source_card, source_items
from family_data import life_span, format_date, date_sort_key, friendly_identifier, relationship_index
from family_research_index import build_index
from profile_life_stories import (life_record_overview, linked_book_illustrations,
                                  profile_milestones)
from family_books import load_books, book_pdf_path
from family_navigation import branch_context, unresolved_relative_ids
from primary_source_expedition import cases_for_person, expedition_route
from identity_claim_review import cases_for_person as conflicting_cases_for_person, claim_review_route
from original_record_intake import acquisition_for_person, acquisition_route
from vinalhaven_civic_history import civic_for_candidate, civic_route
from fox_islands_government_trail import trail_for_candidate,trail_route
from early_fox_island_atlas import source_atlas_for_candidate, early_islands_route
from colony_photos import source_photo_preview
from family_photo_navigation import photo_gallery_route
from routing_ui import route_link

SECTIONS = (
    "Life & timeline", "Original records", "Photographs & book", "Family connections"
)
RELATIONSHIP_LABELS = (
    ("parents", "Parents"), ("spouses", "Spouses"),
    ("children", "Children"), ("siblings", "Siblings")
)
CITATION_PAGE_SIZE = 6


def visible_citations(citations: list[dict], *, linked_only: bool = False) -> list[dict]:
    """Retain original cited order and identity; hide no references permanently."""
    return [source for source in citations if not linked_only or bool(source.get("url"))]


def citation_page(citations: list[dict], page: int, size: int = CITATION_PAGE_SIZE) -> list[dict]:
    """Paginate the *display* only, preserving every historical citation."""
    if size <= 0 or page < 1:
        return []
    return citations[(page - 1) * size:page * size]


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


def event_evidence_for_person(person_id: str, events: list[dict],
                              catalog: list[dict] | None = None) -> list[dict]:
    """Expose event-level sources only for events explicitly linked by exact ID.

    A bibliography is not necessarily an original scan. Do not use a name/OCR
    match to attribute an event to a person, and never filter out unlinked refs.
    """
    curated = catalog if catalog is not None else evidence_catalog()
    found = []
    for event in events:
        if person_id not in (event.get("people_involved") or []):
            continue
        event_id = str(event.get("id") or "")
        if not event_id:
            continue
        sources = source_items(for_event(event_id, curated), event.get("sources") or [])
        if sources:
            found.append({
                "event_id": event_id,
                "title": str(event.get("title") or event_id),
                "date": format_date(event.get("date"), event.get("date_precision")),
                "date_key": date_sort_key(event),
                "sources": sources,
                "linked": sum(bool(item.get("url")) for item in sources),
            })
    return sorted(found, key=lambda item: (item["date_key"],
                                           item["title"].casefold(), item["event_id"]))


def exhibit_overview(person: dict, events: list[dict], indexed: list[dict],
                     catalog: list[dict] | None = None,
                     pictures: list[dict] | None = None) -> dict:
    """Full counts include unlinked references but do not call them scanned originals."""
    pid = str(person["id"])
    evidence = catalog if catalog is not None else evidence_catalog()
    curated = for_person(pid, evidence)
    citations = source_items(curated, person.get("sources") or [])
    rows = exhibit_research_rows(pid, indexed)
    photos = pictures if pictures is not None else linked_book_illustrations(pid)
    milestones = profile_milestones(person, events)
    return {
        "id": pid,
        "milestones": milestones,
        "research": rows,
        "citations": citations,
        "event_evidence": event_evidence_for_person(pid, events, evidence),
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
        linked_only = st.checkbox(
            "Show only citations with a record link",
            value=False, key="museum_linked_citations_" + overview["id"],
            help="Unchecked shows every reference, including bibliographic-only citations.",
        )
        candidates = visible_citations(cited, linked_only=linked_only)
        st.caption(f"{len(candidates)} of {len(cited)} citation(s) shown. "
                   "Unlinked bibliographies remain available when the filter is off.")
        if not candidates:
            st.info("No linked original record is currently available. "
                    "Turn off the filter to inspect all cited sources.")
        else:
            count = max(1, (len(candidates) + CITATION_PAGE_SIZE - 1) // CITATION_PAGE_SIZE)
            citation_key = "museum_citation_page_" + overview["id"]
            if st.session_state.get(citation_key) not in range(1, count + 1):
                st.session_state[citation_key] = 1
            if count > 1:
                chosen = st.selectbox(
                    "Citation page", range(1, count + 1),
                    format_func=lambda n: f"{n} of {count}",
                    key=citation_key,
                )
            else:
                chosen = 1
            for offset, source in enumerate(citation_page(candidates, chosen)):
                render_source_card(
                    source, context="museum-" + overview["id"],
                    number=(chosen - 1) * CITATION_PAGE_SIZE + offset,
                )
    st.markdown("**Sources attached to this relative's dated events**")
    event_items = overview["event_evidence"]
    if not event_items:
        st.caption("No dated event with a citation is attributed to this exact person ID.")
    else:
        st.caption(f"{len(event_items)} dated event(s) with citations, including references "
                   "without scans. An event citation may describe an index, book, or "
                   "secondary account rather than original proof.")
        page_size = 5
        pages = max(1, (len(event_items) + page_size - 1) // page_size)
        key = "museum_event_evidence_page_" + overview["id"]
        if st.session_state.get(key) not in range(1, pages + 1):
            st.session_state[key] = 1
        chosen = st.selectbox("Dated evidence page", range(1, pages + 1),
                              format_func=lambda n: f"{n} of {pages}", key=key) if pages > 1 else 1
        for event in event_items[(chosen - 1) * page_size:chosen * page_size]:
            heading = (event["date"] + " · " + event["title"] + " · " +
                       str(len(event["sources"])) + " citation(s)")
            with st.expander(heading):
                st.caption(str(event["linked"]) + " accessible source link(s); "
                           "all source labels are retained even where no digital original is available.")
                route_link("Read this event in the full timeline",
                           "?page=timeline&event=" + quote(event["event_id"], safe=""))
                for number, source in enumerate(event["sources"]):
                    render_source_card(source, context="event-in-exhibit-" +
                                       overview["id"] + "-" + event["event_id"], number=number)
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
    route_link("View this relative's photographs in the full family gallery",
               photo_gallery_route(person_id=overview["id"]))
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
    branch = branch_context(pid, people, relationships)
    if branch:
        st.caption("Recorded family group " + str(branch["number"]) + " of " +
                   str(branch["total"]) + " · " + str(branch["size"]) +
                   " indexed people with a path through recorded family links.")
        if branch["total"] > 1:
            st.info("Other separately recorded groups have not been connected by a "
                    "supported relationship in this archive. A shared surname or "
                    "nearby residence is not enough to join family branches.")
            route_link("Explore every recorded family group",
                       "?page=collection&view=integrity&section=branches")
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
                    st.caption(friendly_identifier(related) +
                               " · unresolved reference; no verified profile is available")
    missing = unresolved_relative_ids(pid, people, relationships)
    if missing:
        st.caption(str(len(missing)) + " family-reference ID(s) above remain unresolved. "
                   "These are not extra confirmed ancestors or selectable profiles.")
    route_link("Center this relative in the focused family tree",
               "?page=tree&profile=" + quote(pid, safe=""))
    route_link("Find this person in the complete family map",
               "?page=full-tree&profile=" + quote(pid, safe=""))
    route_link("Inspect the evidence status of every listed family relationship",
               "?page=collection&view=integrity&section=relationships&person="
               + quote(pid, safe=""))


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

    # Offer relevant original-document investigations where a precise indexed
    # person's identity is being studied. A case link is not family-link proof.
    open_cases = cases_for_person(person_id)
    if open_cases:
        st.caption("Open family-origin research questions connected to this record")
        for item in open_cases:
            route_link("Investigate: " + item["title"], expedition_route(item["id"]))
    conflicting = conflicting_cases_for_person(person_id)
    if conflicting:
        st.caption("Historical identity and parentage questions requiring original records")
        for dispute in conflicting:
            route_link("Compare sources: " + dispute["title"],
                       claim_review_route(dispute["id"]))
    original_targets = acquisition_for_person(person_id)
    if original_targets:
        st.caption("Original records still needed to verify this relative's ancestry")
        for target in original_targets:
            route_link("Find original: " + target["title"],
                       acquisition_route(target["id"]))
    possible_civic = civic_for_candidate(person_id)
    if possible_civic:
        st.caption("Same-name officeholders in the 1889 Vinalhaven civic history — "
                   "identity NOT verified by this printed name")
        printed = sorted({row["printed_name"] for row in possible_civic})
        for printed_name in printed:
            route_link("Compare historical civic name: " + printed_name,
                       civic_route(printed_name))
    early_community = trail_for_candidate(person_id)
    if early_community:
        st.caption("Earlier Fox Islands government and household source-name "
                   "comparisons (NOT verified identities)")
        for item in early_community:
            route_link("Compare source name: " + item["date_label"] + " · " +
                       item["printed_name"], trail_route(item["id"]))
    earlier_census=source_atlas_for_candidate(person_id)
    if earlier_census:
        st.caption("Historic surname-matched 1790 household research, "
                   "not evidence of a confirmed profile identity")
        for row in earlier_census:
            route_link("Read original census context: " + row["title"],
                       early_islands_route(row["id"]))
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
