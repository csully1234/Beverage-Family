"""Archive screens that share the same relationship index as the map."""

from __future__ import annotations

import streamlit as st

from archive import ArchiveIndex, archive_url, safe_url
from family_data import format_date
from historical_map import build_historical_map_html


def md(value) -> str:
    return str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def source_link(source) -> str:
    return f"[{md(source['short_title'])}]({archive_url('archive', source=source['id'])})"


def place_link(place) -> str:
    return f"[{md(place['name'])}]({archive_url('places', place=place['id'])})"


def render_assertion(link, archive: ArchiveIndex) -> None:
    kind = link["subject_type"]
    record = (archive.people if kind == "person" else archive.events)[link["subject_id"]]
    url = archive_url("people", profile=record["id"]) if kind == "person" else archive_url("timeline", event=record["id"])
    label = record.get("full_name", record.get("title"))
    st.markdown(f"**[{md(label)}]({url})** · {md(link['relation'].replace('_', ' '))}")
    first = format_date(link["date_from"], link["date_precision"])
    last = format_date(link["date_to"], link["date_precision"])
    period = first if link["date_from"] == link["date_to"] else f"{first} – {last}"
    st.caption(f"{period} · {link['evidence_level'].replace('_', ' ').title()}")
    st.write(link["summary"])
    st.markdown("Evidence: " + " · ".join(source_link(archive.sources[sid]) for sid in link["source_ids"]))
    for note in link["notes"]:
        st.caption(note)


def render_source_record(source, archive: ArchiveIndex) -> None:
    st.subheader(source["title"])
    st.caption(f"{source['source_type'].replace('_', ' ').title()} · {source['repository']}")
    st.write(source["summary"])
    st.markdown(f"**Document date:** {format_date(source['date'], source['date_precision'])}")
    st.caption(f"Evidence: {source['evidence_level'].replace('_', ' ')} · Last accessed: {source['accessed']}")
    if source["collection"]:
        st.write("Collection: " + source["collection"])
    st.markdown("**Citation**")
    st.write(source["citation"])
    if safe_url(source["url"]):
        st.link_button("Open original / repository record", source["url"])
    if source["excerpt"]:
        st.markdown("**Excerpt / transcription**")
        st.text(source["excerpt"])
    for note in source["notes"]:
        st.caption(note)
    for conflict in source["conflicts"]:
        st.warning(conflict)
    if source["people_ids"]:
        st.markdown("**Connected people**")
        st.markdown(" · ".join(f"[{md(archive.people[pid]['full_name'])}]({archive_url('people', profile=pid)})" for pid in source["people_ids"]))
    if source["place_ids"]:
        st.markdown("**Places**")
        st.markdown(" · ".join(place_link(archive.places[pid]) for pid in source["place_ids"]))
    if source["event_ids"]:
        st.markdown("**Timeline records**")
        for eid in source["event_ids"]:
            st.markdown(f"- [{md(archive.events[eid]['title'])}]({archive_url('timeline', event=eid)})")
    assertions = [link for link in archive.links if source["id"] in link["source_ids"]]
    if assertions:
        with st.expander(f"What this source supports ({len(assertions)} place assertions)"):
            for link in assertions:
                st.markdown(place_link(archive.places[link["place_id"]]))
                render_assertion(link, archive)


def render_archive_page(archive: ArchiveIndex) -> None:
    st.title("Source Archive")
    st.write("Browse the records behind the family’s historical places and events.")
    requested = st.query_params.get("source", "")
    if requested:
        if requested in archive.sources:
            render_source_record(archive.sources[requested], archive)
        else:
            st.warning("That source record was not found.")
        st.link_button("Browse all sources", archive_url("archive"))
        return
    search, kind = st.columns([2, 1])
    with search:
        query = st.text_input("Search source titles, citations, and summaries", key="archive_search").strip().casefold()
    with kind:
        source_type = st.selectbox("Source type", ["All", *sorted({s['source_type'] for s in archive.sources.values()})],
                                   format_func=lambda value: value.replace("_", " ").title(), key="archive_type")
    matches = [s for s in archive.sources.values() if (source_type == "All" or s["source_type"] == source_type)
               and (not query or query in " ".join(str(s.get(k, "")) for k in ("title", "short_title", "citation", "summary", "repository", "collection")).casefold())]
    st.caption(f"{len(matches)} of {len(archive.sources)} source records")
    if not matches:
        st.info("No sources match. Try a broader search or another source type.")
    for source in sorted(matches, key=lambda s: (s["date"] or "9999", s["title"])):
        with st.container(border=True):
            st.markdown(f"### {source_link(source)}")
            st.caption(f"{source['repository']} · {format_date(source['date'], source['date_precision'])} · {source['evidence_level'].replace('_', ' ')}")
            st.write(source["summary"])
            st.caption(f"{len(source['people_ids'])} people · {len(source['event_ids'])} events · {len(source['place_ids'])} places")


def render_places_page(archive: ArchiveIndex) -> None:
    st.title("Historical Places")
    if not archive.places:
        st.info("No reviewed historical places have been added yet.")
        return
    ids = sorted(archive.places, key=lambda pid: archive.places[pid]["name"])
    requested = st.query_params.get("place", "")
    if requested and requested not in archive.places:
        st.warning("That place was not found. Choose a place below.")
    if st.session_state.get("_archive_place_query") != requested:
        st.session_state["archive_place_selector"] = requested if requested in archive.places else ids[0]
        st.session_state["_archive_place_query"] = requested
    def select_place():
        st.query_params["place"] = st.session_state["archive_place_selector"]
    pid = st.selectbox("Choose a historical place", ids, format_func=lambda value: archive.places[value]["name"],
                       key="archive_place_selector", on_change=select_place)
    place = archive.places[pid]
    st.subheader(place["name"])
    st.write(place["historical_notes"])
    st.caption(f"{place['type'].replace('_', ' ').title()} · {place['coordinate_precision'].replace('_', ' ')} point · {place['confidence']} location confidence")
    if place["alternate_names"]:
        st.caption("Also recorded as: " + "; ".join(place["alternate_names"]))
    if place["parent_place_id"]:
        st.markdown("Within " + place_link(archive.places[place["parent_place_id"]]))
    st.caption(place["coordinate_notes"])
    st.markdown("Coordinate reference: " + source_link(archive.sources[place["coordinate_source_id"]]))
    st.link_button("View on historical map", archive_url("map", place=pid))
    linked = archive.related(pid)
    metrics = st.columns(3)
    for col, key in zip(metrics, ("people", "events", "sources")):
        col.metric(key.title(), len(linked[key]))
    people_tab, events_tab, sources_tab = st.tabs(["People", "Events", "Sources"])
    for tab, kind in ((people_tab, "person"), (events_tab, "event")):
        with tab:
            assertions = [link for link in linked["links"] if link["subject_type"] == kind]
            if not assertions:
                st.info("No reviewed links of this type yet.")
            for link in assertions:
                with st.container(border=True):
                    render_assertion(link, archive)
    with sources_tab:
        for source in linked["sources"]:
            st.markdown(f"- {source_link(source)} — {md(source['evidence_level'].replace('_', ' '))}")


def render_map_page(archive: ArchiveIndex) -> None:
    st.title("Historical Map")
    st.write("Explore the family’s places, from Penobscot Bay to the wider world. Select a pin to read the connections and their evidence.")
    if not archive.places:
        st.info("No reviewed historical places have been added yet.")
        return
    html = build_historical_map_html(archive, person_id=st.query_params.get("person", ""),
                                     event_id=st.query_params.get("event", ""),
                                     place_id=st.query_params.get("place", ""))
    st.iframe(html, height=1050)
    st.caption("Source and profile links open in a new tab. Modern map: © OpenStreetMap contributors. Cemetery indexes are corroboration; broad markers do not identify a building, private home, or historic boundary.")
    st.markdown(f"[Browse place records]({archive_url('places')}) · [Browse supporting sources]({archive_url('archive')})")


def render_person_archive(person_id: str, archive: ArchiveIndex) -> None:
    links = archive.by_subject["person", person_id]
    if links:
        st.subheader("Documented historical places")
        st.link_button("Explore this person’s places on the map", archive_url("map", person=person_id))
        for link in links:
            with st.container(border=True):
                st.markdown(place_link(archive.places[link["place_id"]]))
                st.write(link["summary"])
                st.caption(link["evidence_level"].replace("_", " ").title())
                st.markdown("Evidence: " + " · ".join(source_link(archive.sources[sid]) for sid in link["source_ids"]))


def render_event_archive(event_id: str, archive: ArchiveIndex) -> None:
    places = archive.places_for("event", event_id)
    if places:
        st.markdown("**Historical places:** " + " · ".join(place_link(p) for p in places))
        st.markdown(f"[Explore this event on the map]({archive_url('map', event=event_id)})")
        st.markdown("**Archive records:** " + " · ".join(source_link(s) for s in archive.sources_for("event", event_id)))
