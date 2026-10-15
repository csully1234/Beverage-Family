"""Searchable research, linked in context throughout the existing archive."""

from __future__ import annotations

import csv
import io
import math

import streamlit as st
from routing_ui import route_markdown, route_link

from archive import archive_url, safe_url
from research_collection import (
    CONFIDENCE, REPORT_DIR, STRONG, CollectionIndex, matches, source_ids,
)
from conflict_review_ui import resolution_for, render_resolution, render_review_page


def md(value) -> str:
    return str(value or "").replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


@st.cache_data(show_spinner=False)
def load_collection() -> CollectionIndex:
    return CollectionIndex.load()


def finding_link(record: dict) -> str:
    return f"[{md(record['Navigation']['title'])}]({archive_url('collection', finding=record['Research ID'])})"


def register_link(source: dict) -> str:
    return f"[{source['Source ID']} · {md(source['Title'])}]({archive_url('archive', source=source['Source ID'])})"


def render_finding(record: dict, collection: CollectionIndex, people: dict,
                   *, detail: bool = False) -> None:
    resolution = resolution_for(record["Research ID"])
    if resolution:
        route_markdown(f"### {finding_link(record)}")
        st.caption(record["Research ID"] + " · Original research finding retained below")
        render_resolution(resolution, collection, people, detail=detail)
        if detail:
            with st.expander("Original 14 October research snapshot"):
                _render_original_finding(record, collection, people, detail=True)
        return
    _render_original_finding(record, collection, people, detail=detail)


def _render_original_finding(record: dict, collection: CollectionIndex, people: dict,
                            *, detail: bool = False) -> None:
    rid = record["Research ID"]
    route_markdown(f"### {finding_link(record)}")
    st.caption(f"{rid} · {record['Confidence']} · {record['Change type']} · Family review: {record['Human-review status']}")
    st.caption(f"{record['Date or date range']} · {record['Location']} · {record['Event category']}")
    if record["Confidence"] == "Conflict":
        st.warning("Research conflict requiring family review. The existing record is preserved.")
    elif record["Confidence"] in {"Probable", "Possible lead", "Rejected"}:
        st.info(f"{record['Confidence']} — read the evidence limits before treating this as an established fact.")
    st.write(record["Proposed fact or narrative"])
    # Always visible, including compact profile and search cards. A confirmed
    # catalog entry does not establish every identity or event described by it.
    route_markdown("**Evidence limits:** " + md(record["Notes about uncertainty"]))
    st.caption("Examined: " + str(record["Evidence basis"]))
    route_markdown("**Sources:** " + " · ".join(register_link(collection.sources[sid]) for sid in source_ids(record)))
    if not detail:
        return
    st.subheader("Exact citation and locator")
    st.write(record["Exact citation"])
    st.write(record["Locator"])
    nav = record["Navigation"]
    if nav["people_ids"]:
        route_markdown("**Related profiles:** " + " · ".join(
            f"[{md(people[pid]['full_name'])}]({archive_url('people', profile=pid)})"
            for pid in nav["people_ids"] if pid in people))
        st.caption("These are research cross-references. They do not create a family relationship or resolve a disputed identity.")
    if nav["place_ids"]:
        route_markdown("**Historical places:** " + " · ".join(
            f"[{md(pid.replace('_', ' ').title())}]({archive_url('places', place=pid)})" for pid in nav["place_ids"]))
    for eid in nav["event_ids"]:
        route_link("Open related timeline record", archive_url("timeline", event=eid))
    for name in ("Properties and Deeds", "Images and Maps", "Candidate People"):
        rows = collection.inventory_rows(name, rid)
        if rows:
            with st.expander(name, expanded=name == "Properties and Deeds"):
                for row in rows:
                    for key, value in row.items():
                        if value is not None:
                            route_markdown(f"**{md(key)}:** {md(value)}")
                    st.divider()
    targets = collection.targets_for(record)
    if targets:
        st.subheader("Related retrieval targets")
        for target in targets:
            route_markdown(f"- [{target['Target ID']} · {md(target['Title'])}]({archive_url('collection', target=target['Target ID'])})")


def render_context(kind: str, identifier: str, people: dict, *, topic: str = "",
                   strong_only: bool = False, limit: int = 3) -> None:
    collection = load_collection()
    records = collection.for_subject(kind, identifier)
    if topic:
        records = [r for r in records if topic in r["Navigation"]["topics"]]
    if strong_only:
        records = [r for r in records if r["Confidence"] in STRONG]
    if not records:
        return
    st.subheader(f"Additional research ({len(records)})")
    st.caption("Research collection · 14 October 2026 · Evidence and identity limits accompany each finding.")
    for record in records[:limit]:
        with st.container(border=True):
            render_finding(record, collection, people)
    params = {kind: identifier} if kind in {"person", "place"} else {}
    if topic:
        params["topic"] = topic
    route_link("Browse the related research collection", archive_url("collection", **params))


def paginate(records: list, key: str, size: int = 12) -> list:
    pages = max(1, math.ceil(len(records) / size))
    if st.session_state.get(key, 1) > pages:
        st.session_state[key] = 1
    if pages == 1:
        return records
    page = st.selectbox("Results page", range(1, pages + 1), key=key,
                        format_func=lambda value: f"{value} of {pages}")
    return records[(page - 1) * size:page * size]


def render_register_source(source: dict, collection: CollectionIndex) -> None:
    st.subheader(source["Title"])
    st.caption(f"{source['Source ID']} · {source['Repository']} · {source['Source type']}")
    st.info(str(source["Viewed status"]))
    st.write(source["What it supports"])
    route_markdown("**Exact locator:** " + md(source["Locator"]))
    st.caption(f"Access date: {source['Access date']} · {source['Baseline or new']}")
    st.write("Access result recorded during research: " + str(source["URL status"]))
    if source.get("Link check 2026 10 14"):
        st.caption("Link check: " + str(source["Link check 2026 10 14"]))
    if safe_url(source.get("URL")):
        route_link("Open source / catalog record", source["URL"])
    else:
        st.caption("No verified direct URL was supplied for this citation.")
    if source.get("Alternate locations"):
        st.write("Alternate locations: " + str(source["Alternate locations"]))
    route_markdown("**Rights and reuse:** " + md(source["Rights"]))
    linked = collection.for_source(source["Source ID"])
    st.subheader(f"Findings citing this source ({len(linked)})")
    for record in linked:
        route_markdown(f"- {finding_link(record)} · {record['Confidence']}")
        st.write(record["Exact citation"])
    if not linked:
        st.caption("This entry is retained in the baseline or retrieval register; it is not cited by a new finding.")
    route_link("Browse the research source register", archive_url("collection", view="Sources"))


def render_register(collection: CollectionIndex, *, prefix: str = "register") -> None:
    st.write("All registered citations, including inherited sources and inaccessible leads. Read each entry’s viewed status.")
    cols = st.columns([2, 1])
    query = cols[0].text_input("Search the research source register", key=prefix + "_search")
    repository = cols[1].selectbox("Holding repository", ["All", *sorted({s["Repository"] for s in collection.sources.values()})], key=prefix + "_repository")
    records = [s for s in collection.sources.values() if matches(query, s)
               and (repository == "All" or repository == s["Repository"])]
    st.caption(f"{len(records)} of {len(collection.sources)} research source records")
    for source in paginate(records, prefix + "_page"):
        with st.container(border=True):
            route_markdown(f"### {register_link(source)}")
            st.caption(f"{source['Repository']} · {source['Source type']}")
            st.write(source["What it supports"])
            st.caption(str(source["Viewed status"]))
    if not records:
        st.info("No source records match these filters.")


def render_target(target: dict, collection: CollectionIndex) -> None:
    st.subheader(f"{target['Target ID']} · {target['Title']}")
    st.caption(f"Priority {target['Priority']} · {target['Status']}")
    for field in ("Exact research question", "Record or collection target", "Barrier",
                  "Contact or retrieval route", "Suggested request language", "Published fees"):
        route_markdown(f"**{field}**")
        st.write(target[field])
    st.caption("Fees and contacts are recorded as of 14 October 2026; confirm with the repository before ordering.")
    for url in (target.get("Repository links") or "").splitlines():
        if safe_url(url):
            route_markdown(f"[{md(url)}]({url})")
    route_markdown("**Source register:** " + " · ".join(register_link(collection.sources[sid]) for sid in source_ids(target, "Source IDs")))


def render_inventory(collection: CollectionIndex) -> None:
    names = list(collection.inventories)
    name = st.selectbox("Research inventory", names, key="collection_inventory", on_change=sync_collection_route)
    st.caption("Snapshot of the supplied workbook. Baseline assertions, candidate people, and proposed relationships retain their original labels; they are not new verified genealogy.")
    query = st.text_input("Search this inventory", key="collection_inventory_search")
    rows = [row for row in collection.inventory_rows(name) if matches(query, row)]
    st.caption(f"{len(rows)} of {len(collection.inventories[name]['rows'])} rows")
    # String projection avoids mixed-type Arrow coercion and preserves the
    # workbook's date strings, uncertain readings and identifiers verbatim.
    display = [{key: "" if value is None else str(value) for key, value in row.items()} for row in rows]
    st.dataframe(display, hide_index=True, width="stretch", height=480)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=collection.inventories[name]["headers"])
    writer.writeheader()
    writer.writerows(display)
    st.download_button("Download this filtered inventory (CSV)", output.getvalue(),
                       file_name=name.replace(" ", "_") + ".csv", mime="text/csv")
    ids = list(dict.fromkeys(row.get("Research ID") for row in rows if row.get("Research ID") in collection.findings))
    if ids:
        route_markdown("**Open a related finding**")
        for rid in ids:
            route_markdown(f"- {finding_link(collection.findings[rid])}")


def render_reports(collection: CollectionIndex) -> None:
    st.write("The five original reports preserve the complete narratives, source register, inventories, search log, and proposed additions.")
    st.caption("These are the original research-stage snapshots. Statements that no repository changes were made describe that stage. Website review statuses remain as supplied.")
    for report in collection.raw["reports"]:
        with st.container(border=True):
            st.subheader(report["title"])
            filename = report["filename"]
            mime = "application/vnd.openxmlformats-officedocument." + (
                "spreadsheetml.sheet" if filename.endswith(".xlsx") else "wordprocessingml.document")
            st.download_button("Download " + filename, (REPORT_DIR / filename).read_bytes(),
                               file_name=filename, mime=mime, key="report_" + filename)
    route_link("Read the full source register on the site", archive_url("collection", view="Sources"))
    route_link("Browse all workbook inventories", archive_url("collection", view="Inventories"))
    st.subheader("Read the dossier")
    sections = collection.raw["dossier"]
    section_id = st.selectbox("Dossier section", range(len(sections)),
                              format_func=lambda i: sections[i]["title"], key="dossier_section")
    section = sections[section_id]
    st.subheader(section["title"])
    for block in section["blocks"]:
        if block["type"] == "heading":
            route_markdown("#### " + md(block["text"]))
        elif block["type"] == "table":
            rows = block["rows"]
            if rows:
                st.dataframe([dict(zip(rows[0], row)) for row in rows[1:]], hide_index=True, width="stretch")
        else:
            route_markdown(block["text"])
    st.caption("Numbered citations resolve in the Endnotes and bibliography section. Source IDs also open in the Source Archive.")


def render_images(collection: CollectionIndex) -> None:
    st.subheader("Photographs, maps and objects")
    st.write("Open the holding institution’s page to view the authentic item. Captions retain the research limits; permission may be needed to reproduce an image.")
    query = st.text_input("Find an image, place or person", key="image_query")
    records = [r for r in collection.inventory_rows("Images and Maps") if matches(query, r)]
    records.sort(key=lambda r: collection.findings.get(r["Research ID"], {}).get("Navigation", {}).get("sort_year") or 9999)
    st.caption(f"{len(records)} item descriptions · Ordered by the earliest associated year, which may differ from the image date.")
    for r in paginate(records, "image_results_page", size=8):
        with st.container(border=True):
            route_markdown("### " + md(r["Subject"]))
            st.caption(str(r["Date"]) + " · " + str(r["Holding institution"]))
            st.write(r["Item or caption"])
            st.caption(str(r["Collection or item identifier"]))
            if safe_url(r["Direct item page"]):
                route_link("View item at the holding institution", r["Direct item page"])
            st.caption("Examined: " + str(r["Viewed status"]) + " · " + str(r["Confidence"]))
            with st.expander("Rights, resolution and evidence"):
                st.write(r["Rights"])
                st.write("High resolution: " + str(r["High resolution"]))
                if r["Research ID"] in collection.findings:
                    route_markdown(finding_link(collection.findings[r["Research ID"]]))
    if not records:
        st.info("No image descriptions match. Try a surname or a broader place.")


def reset_collection_filters() -> None:
    for key in ("query", "confidence", "topic", "person", "place", "location"):
        st.session_state["collection_" + key] = ""
    st.session_state["collection_results_page"] = 1
    view = st.session_state.get("collection_view", "Findings")
    st.query_params.clear()
    st.query_params["page"] = "collection"
    if view == "Chronology":
        st.query_params["view"] = view
    st.session_state.pop("_collection_route", None)


def sync_collection_route() -> None:
    """Keep shareable filters and the selected view after refresh/navigation."""
    st.query_params["page"] = "collection"
    for query_key, widget_key in (("view", "view"), ("q", "query"), ("status", "confidence"),
                                  ("topic", "topic"), ("person", "person"), ("place", "place"),
                                  ("location", "location"), ("inventory", "inventory")):
        value = st.session_state.get("collection_" + widget_key, "")
        if value:
            st.query_params[query_key] = value
        elif query_key in st.query_params:
            del st.query_params[query_key]
    st.session_state["collection_results_page"] = 1


def render_collection_page(people: dict, places: dict) -> None:
    collection = load_collection()
    st.title("Research Collection")
    st.write("Explore the additional family research by person, place, subject, and evidence. Every finding keeps its citation, confidence, and unresolved questions.")
    metrics = st.columns(4)
    metrics[0].metric("Findings", len(collection.findings))
    metrics[1].metric("Registered sources", len(collection.sources))
    metrics[2].metric("Original conflict records", sum(r["Confidence"] == "Conflict" for r in collection.findings.values()))
    metrics[3].metric("Retrieval targets", len(collection.targets))
    st.caption("14 October 2026 research package · Coverage remains partial. Confirmed can describe a source’s contents or catalog attribution; identity and interpretation limits are stated separately.")
    finding_id = st.query_params.get("finding", "")
    target_id = st.query_params.get("target", "")
    if finding_id or target_id:
        if finding_id in collection.findings:
            render_finding(collection.findings[finding_id], collection, people, detail=True)
        elif target_id in collection.targets:
            render_target(collection.targets[target_id], collection)
        else:
            st.warning("That research record was not found.")
        route_link("Browse all findings", archive_url("collection"))
        route_link("Browse the retrieval plan", archive_url("collection", view="Retrieval plan"))
        return

    views = ["Findings", "Conflict review", "Images", "Chronology", "Sources", "Retrieval plan", "Inventories", "Reports"]
    route = tuple((key, st.query_params.get(key, "")) for key in
                  ("view", "person", "place", "topic", "status", "q", "inventory", "location"))
    if st.session_state.get("_collection_route") != route or "collection_person" not in st.session_state:
        requested = st.query_params.get("view", "Findings")
        st.session_state["collection_view"] = requested if requested in views else "Findings"
        st.session_state["collection_query"] = st.query_params.get("q", "")
        st.session_state["collection_confidence"] = st.query_params.get("status", "") if st.query_params.get("status", "") in CONFIDENCE else ""
        topics = {topic for r in collection.findings.values() for topic in r["Navigation"]["topics"]}
        st.session_state["collection_topic"] = st.query_params.get("topic", "") if st.query_params.get("topic", "") in topics else ""
        for kind, options in (("person", people), ("place", places)):
            value = st.query_params.get(kind, "")
            st.session_state["collection_" + kind] = value if value in options else ""
        locations = {r["Location"] for r in collection.findings.values()}
        st.session_state["collection_location"] = st.query_params.get("location", "") if st.query_params.get("location", "") in locations else ""
        inventory = st.query_params.get("inventory", "Overview")
        st.session_state["collection_inventory"] = inventory if inventory in collection.inventories else "Overview"
        st.session_state["collection_results_page"] = 1
        st.session_state["_collection_route"] = route
    view = st.selectbox("Collection view", views, key="collection_view", on_change=sync_collection_route)
    if view == "Conflict review":
        render_review_page(collection, people)
        return
    if view == "Images":
        render_images(collection)
        return
    if view == "Sources":
        render_register(collection)
        return
    if view == "Reports":
        render_reports(collection)
        return
    if view == "Inventories":
        render_inventory(collection)
        return
    if view == "Retrieval plan":
        query = st.text_input("Search retrieval questions and archives", key="target_query")
        targets = sorted((r for r in collection.targets.values() if matches(query, r)), key=lambda r: (r["Priority"], r["Target ID"]))
        st.caption(f"{len(targets)} retrieval targets · Includes offline, blocked, and online records not yet examined.")
        for target in paginate(targets, "target_page"):
            with st.expander(f"Priority {target['Priority']} · {target['Target ID']} · {target['Title']}"):
                render_target(target, collection)
                route_link("Link to this retrieval target", archive_url("collection", target=target["Target ID"]))
        return

    query = st.text_input("Search findings and their sources", key="collection_query", placeholder="Name, property, vessel, institution, date, research ID…", on_change=sync_collection_route)
    st.button("Clear research filters", on_click=reset_collection_filters)
    cols = st.columns(2)
    confidence = cols[0].selectbox("Confidence", ["", *CONFIDENCE], format_func=lambda v: v or "All confidence levels", key="collection_confidence", on_change=sync_collection_route)
    topics = sorted({topic for r in collection.findings.values() for topic in r["Navigation"]["topics"]})
    topic = cols[1].selectbox("Subject", ["", *topics], format_func=lambda v: v or "All subjects", key="collection_topic", on_change=sync_collection_route)
    with st.expander("Filter by person or location", expanded=bool(st.session_state["collection_person"] or st.session_state["collection_place"])):
        cols = st.columns(2)
        person = cols[0].selectbox("Related profile", ["", *sorted(people, key=lambda p: people[p]["full_name"])], format_func=lambda v: people[v]["full_name"] if v else "All profiles", key="collection_person", on_change=sync_collection_route)
        place = cols[1].selectbox("Related historical place", ["", *sorted(places, key=lambda p: places[p]["name"])], format_func=lambda v: places[v]["name"] if v else "All historical places", key="collection_place", on_change=sync_collection_route)
        location = st.selectbox("Location as recorded in the research", ["", *sorted({r["Location"] for r in collection.findings.values()})], format_func=lambda v: v or "All research locations", key="collection_location", on_change=sync_collection_route)
    selected = collection.select(query, confidence, topic, person, place, location)
    if view == "Chronology":
        selected.sort(key=lambda r: (r["Navigation"]["sort_year"] or 9999, r["Research ID"]))
        st.caption("Ordered by the first year mentioned in each finding. Publication, registration, recollection, and event dates remain distinguished in the text; approximate dates are not converted to exact dates.")
    st.caption(f"{len(selected)} of {len(collection.findings)} findings")
    if not selected:
        st.info("No findings match. Broaden the search or clear a filter.")
    for record in paginate(selected, "collection_results_page"):
        with st.container(border=True):
            render_finding(record, collection, people)


def render_timeline_research(people: dict, person_id: str | None, query: str,
                             years: tuple[int, int], newest: bool = False) -> None:
    collection = load_collection()
    records = collection.select(query=query, person_id=person_id or "")
    records = [r for r in records if r["Navigation"]["sort_year"] is None or
               (r["Navigation"]["sort_year"] <= years[1] and r["Navigation"]["last_year"] >= years[0])]
    records.sort(key=lambda r: r["Navigation"]["sort_year"] or 9999, reverse=newest)
    with st.expander(f"Additional dated research ({len(records)})"):
        st.caption("Uses the timeline’s search, person and year range. Research confidence and categories are separate from the established event filters. Dates retain their source meaning, including catalog and registration dates.")
        for record in records[:5]:
            with st.container(border=True):
                render_finding(record, collection, people)
        route_link("Browse the complete research chronology", archive_url("collection", view="Chronology", person=person_id or "", q=query))
