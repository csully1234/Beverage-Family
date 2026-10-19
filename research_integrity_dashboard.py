"""Family-facing, evidence-first health dashboard for the *current* family archive.

All panels read effective profile, event, relationship and reviewed source
data. No score describes genealogical certainty; missing evidence is a
research priority, not a reason to delete people or rewrite their ancestry.
"""
from __future__ import annotations

from collections import Counter
from urllib.parse import quote

import streamlit as st

from family_data import life_span
from genealogy_integrity import audit_family_archive, audit_csv
from relationship_evidence import KIND_NAMES, STATUS_NAMES
from routing_ui import route_link


def _person_link(pid: str, people: dict, *, prefix: str = "Explore") -> None:
    person = people.get(pid)
    if person:
        route_link(prefix + " " + str(person.get("full_name") or pid),
                   "?page=people&profile=" + quote(pid, safe=""))
    else:
        st.caption(pid + " · referenced in records; no verified profile entered")


def _source_list(sources: list[dict]) -> None:
    for source in sources:
        name = str(source.get("title") or source.get("citation") or "Historical source")
        destination = source.get("route") or source.get("url")
        if destination:
            route_link("Inspect: " + name, destination)
        else:
            st.caption("Bibliography only: " + name)
        if source.get("type"):
            st.caption(str(source["type"]))
        if source.get("route") and not source.get("url"):
            st.caption("Read the indexed source notebook; the original archival image is not published.")


def _summary(data: dict, people: dict) -> None:
    s = data["summary"]
    st.subheader("Current family-history evidence inventory")
    st.write("This audit checks *every effective profile* and *every relationship in the "
             "current tree*. Counts describe **documentation and connectivity**, "
             "never the percentage of ancestors proven correct.")
    cols = st.columns(4)
    cols[0].metric("People", s["people"])
    cols[1].metric("Family links", s["distinct_relationships"])
    cols[2].metric("Links individually reviewed", s["individual_relationship_reviews"])
    cols[3].metric("Separate family groups", s["connected_groups"])
    st.caption(str(s["parent_child_links"]) + " parent-child links · " +
               str(s["spouse_links"]) + " spouse links · " +
               str(s["sibling_links_including_inferred"]) +
               " sibling links, including automatic shared-parent sibling inference.")
    cols = st.columns(4)
    cols[0].metric("Links needing review", s["relationships_awaiting_review"])
    cols[1].metric("Unresolved profile IDs", s["unresolved_profile_references"])
    cols[2].metric("Profiles without direct citation URLs", s["profiles_without_direct_citation_url"])
    cols[3].metric("Events lacking citations", s["events_without_citation"])
    st.caption("An old bibliography label or an unpublished court paper may be useful "
               "evidence even when no direct URL exists. An inferred sibling link is "
               "not a separately attested sibling relationship.")
    st.divider()
    st.subheader("Highest-impact next documents")
    for heading, text, route in (
        ("Bridge the disconnected historic branches",
         "The Matthew of Hope, Nathaniel of Rockland and Mercy Henry groups "
         "must be connected only through a specific parentage, probate or deed document.",
         "?page=collection&view=matthew"),
        ("Retrieve the 1786 Fox Islands survey and Matthew's earliest deed",
         "Compare the original petition and Putnam survey to the 1837 probate "
         "without equating similarly named people.",
         "?page=collection&view=family-origins"),
        ("Audit individual family relationships",
         "A profile bibliography does not prove every family edge. Start with "
         "record-specific relationships and disputed early-era identities.",
         "?page=collection&view=integrity&section=relationships"),
        ("Complete event-level original-source links",
         "Attach verifiable record URLs or note where manuscript originals are not digitized.",
         "?page=collection&view=integrity&section=records"),
    ):
        with st.container(border=True):
            st.markdown("**" + heading + "**")
            st.write(text)
            route_link("Open the relevant evidence", route)


def _branches(data: dict, people: dict) -> None:
    st.subheader("Disconnected family groups")
    st.write("All groups below are complete connected components of the recorded "
             "family links. Separate groups may be historically related, but that "
             "connection is **not yet established by the current graph**.")
    groups = data["components"]
    st.caption(str(len(groups)) + " group(s). Every profile remains available. "
               "Do not add a parent or sibling solely to connect the diagram.")
    for i, group in enumerate(groups, 1):
        example = str(people.get(group[0], {}).get("full_name") or group[0])
        with st.expander(f"Group {i}: {len(group)} profiles · {example}",
                         expanded=i>1):
            names = sorted(group, key=lambda pid: (
                str(people.get(pid, {}).get("full_name") or pid).casefold(), pid
            ))
            st.caption(str(len(names)) + " individual indexed profiles; "
                       "group membership proves only that a path exists in the current record.")
            choices = [(pid, people[pid]) for pid in names if pid in people]
            selected = st.selectbox(
                "Jump to a member", options=[pid for pid, _ in choices],
                format_func=lambda pid: str(people[pid].get("full_name") or pid) +
                                        " · " + life_span(people[pid]),
                key="integrity_component_person_" + str(i),
            )
            _person_link(selected, people)
            st.caption("Use the profile's Family tab or focused tree to inspect "
                       "the actual steps and each relationship's evidence.")
    st.divider()
    st.subheader("Similar names that warrant comparison")
    st.caption("These are exact normalized display-name collisions, NOT deduplications. "
               "Names frequently repeat across different generations.")
    if not data["same_names"]:
        st.info("No identical normalized full-name groups were found.")
    for row in data["same_names"]:
        with st.expander(row["name"].title() + " · " + str(len(row["ids"])) + " separate IDs"):
            for pid in row["ids"]:
                _person_link(pid, people)
            st.caption("Check source dates, spouses and original registrations before "
                       "considering any identity merge; no profiles were changed.")
    st.divider()
    st.subheader("Incomplete referenced relatives")
    st.caption("The following are relationship IDs mentioned in a source profile "
               "but not fully represented as profiles. Some may remain unresolved.")
    for entry in data["unresolved"]:
        with st.container(border=True):
            st.markdown("**" + entry["id"].replace("_", " ") + "**")
            st.caption("Referenced by " + str(len(entry["referenced_by"])) + " indexed relative(s)")
            for pid in entry["referenced_by"]:
                _person_link(pid, people, prefix="Referenced from")


def _relationship_row(row: dict, people: dict) -> None:
    a, b = row["from_id"], row["to_id"]
    with st.container(border=True):
        st.markdown("**" + str(people.get(a, {}).get("full_name") or a) +
                    " → " + str(people.get(b, {}).get("full_name") or b) + "**")
        st.caption(KIND_NAMES[row["kind"]] + " · " + STATUS_NAMES[row["status"]])
        st.caption("Graph origin: " + row["origin"])
        if row.get("finding"):
            st.write(row["finding"])
        st.caption("What this does not prove: " + row["limitations"])
        _source_list(row["sources"])
        for pid in (a, b):
            _person_link(pid, people, prefix="Open")


def _relationships(data: dict, people: dict) -> None:
    st.subheader("Audit every recorded relationship")
    st.write("Each parent-child, spouse and sibling edge is tracked separately. "
             "A missing individualized review is **not evidence that the link is false**.")
    summary = data["edge_summary"]
    a, b, c = st.columns(3)
    a.metric("All relationship links", summary["total"])
    b.metric("Reviewed individually", summary["reviewed"])
    c.metric("Awaiting review", summary["awaiting_review"])
    options = ["All status values", *[STATUS_NAMES[key] for key in STATUS_NAMES]]
    status_to_display = {value: key for key, value in STATUS_NAMES.items()}
    selected_status = st.selectbox("Evidence review status", options, key="integrity_status")
    requested_person = str(st.query_params.get("person") or "")
    if requested_person in people:
        st.caption("Showing relationships involving " + str(people[requested_person].get("full_name") or requested_person))
        route_link("Show all relationships", "?page=collection&view=integrity&section=relationships")
    query = st.text_input("Find family links by name", key="integrity_relationship_query",
                          placeholder="Matthew, Clarissa, Lowell…").strip().casefold()
    kind = st.selectbox("Relationship type", ["All", *KIND_NAMES.values()],
                        key="integrity_relation_kind")
    allowed_kinds = {label: k for k, label in KIND_NAMES.items()}
    rows = [row for row in data["edges"]
            if (selected_status == "All status values"
                or row["status"] == status_to_display[selected_status])
            and (kind == "All" or row["kind"] == allowed_kinds[kind])
            and (not requested_person or requested_person not in people or
                 requested_person in (row["from_id"], row["to_id"]))
            and (not query or query in (" ".join(
                str(people.get(pid, {}).get("full_name") or pid)
                for pid in (row["from_id"], row["to_id"]))).casefold())]
    st.caption(str(len(rows)) + " relationship(s) match. The default includes "
               "unreviewed and inherited relationships, without hiding them.")
    size = 8
    pages = max(1, (len(rows)+size-1)//size)
    key = "integrity_relation_page"
    if st.session_state.get(key) not in range(1, pages+1):
        st.session_state[key] = 1
    page = st.selectbox("Relationship page", range(1, pages+1),
                        key=key, format_func=lambda n: f"{n} of {pages}")
    for row in rows[(page-1)*size:page*size]:
        _relationship_row(row, people)


def _records(data: dict, people: dict) -> None:
    st.subheader("Profile and original-record coverage")
    st.caption("Missing links are a task queue, not a measure of genealogical accuracy. "
               "Original images may be withheld for rights reasons.")
    s = data["summary"]
    cols = st.columns(3)
    cols[0].metric("Profiles without birth date", s["birth_dates_unrecorded"])
    cols[1].metric("Profiles without death date", s["death_dates_unrecorded"])
    cols[2].metric("Events without direct source URL", s["events_without_direct_citation_url"])
    selected = st.selectbox("Find profiles needing documentation", [
        "No direct citation URL", "No profile citation",
        "Birth date not recorded", "Death date not recorded",
        "Relationships awaiting review", "All people",
    ], key="integrity_profile_filter")
    options = data["profiles"]
    if selected == "No direct citation URL":
        options = [r for r in options if not r["direct_source_urls"]]
    elif selected == "No profile citation":
        options = [r for r in options if not r["citation_entries"]]
    elif selected == "Birth date not recorded":
        options = [r for r in options if not r["birth_recorded"]]
    elif selected == "Death date not recorded":
        options = [r for r in options if not r["death_recorded"]]
    elif selected == "Relationships awaiting review":
        options = [r for r in options
                   if r["relationship_links"] > r["individually_reviewed_links"]]
    st.caption(str(len(options)) + " profile(s) match. Use these to prioritize "
               "archive retrievals, not to erase missing dates or links.")
    size = 10
    pages = max(1, (len(options)+size-1)//size)
    key = "integrity_profile_page"
    if st.session_state.get(key) not in range(1, pages+1):
        st.session_state[key] = 1
    page = st.selectbox("Profile audit page", range(1, pages+1),
                        key=key, format_func=lambda n: f"{n} of {pages}")
    for row in options[(page-1)*size:page*size]:
        with st.container(border=True):
            _person_link(row["id"], people)
            st.caption(str(row["citation_entries"]) + " bibliography entries; " +
                       str(row["direct_source_urls"]) + " direct cited URLs; " +
                       str(row["events"]) + " linked events")
            st.caption(str(row["individually_reviewed_links"]) + " of " +
                       str(row["relationship_links"]) +
                       " relationship links have individual evidence review notes")
    with st.expander("Events without any citation · " + str(len(data["events_no_citations"]))):
        for event in data["events_no_citations"]:
            st.caption(str(event.get("title") or event["id"]))
            route_link("Read event context", "?page=timeline&event=" +
                       quote(str(event["id"]), safe=""))
    no_link = [event for event in data["events_no_direct_link"] if event.get("sources")]
    with st.expander("Cited events without an accessible direct source URL · " + str(len(no_link))):
        st.caption("These events have bibliographic references but no HTTP(S) link in "
                   "their own citations. A direct link may lead to a catalog, not "
                   "necessarily an original record. Curated exhibits elsewhere can "
                   "provide additional context; this queue audits event fields only.")
        size = 10
        pages = max(1, (len(no_link) + size - 1) // size)
        key = "integrity_event_no_link_page"
        if st.session_state.get(key) not in range(1, pages + 1):
            st.session_state[key] = 1
        page = st.selectbox("Unlinked event page", range(1, pages + 1), key=key,
                            format_func=lambda n: f"{n} of {pages}") if pages > 1 else 1
        for event in no_link[(page - 1) * size:page * size]:
            st.caption(str(event.get("date") or "Undated") + " · " +
                       str(event.get("title") or event["id"]))
            route_link("Inspect event and bibliography", "?page=timeline&event=" +
                       quote(str(event["id"]), safe=""))
    with st.expander("Mechanical chronology screening · " + str(len(data["chronology"]))):
        st.caption("A screening is only a clue to re-check records and date precision.")
        for row in data["chronology"]:
            with st.container(border=True):
                st.write(row["note"])
                for pid in row["person_ids"]:
                    _person_link(pid, people)


def _exports(data: dict) -> None:
    st.subheader("Download the current review queues")
    st.caption("These files contain the source archive's recorded names and IDs; "
               "keep family research exports within the intended family audience. "
               "They do not contain unpublished original-image binaries.")
    st.download_button(
        "Download complete profile evidence checklist (CSV)",
        data=audit_csv(data["profiles"], ("id","name","birth_recorded","death_recorded",
                                         "citation_entries","direct_source_urls","events",
                                         "relationship_links","individually_reviewed_links",
                                         "needs_research")),
        file_name="family-profile-evidence-audit.csv", mime="text/csv",
    )
    st.download_button(
        "Download every relationship and review status (CSV)",
        data=audit_csv(data["edges"], ("kind","from_id","to_id","status","origin",
                                      "finding","limitations")),
        file_name="family-relationship-evidence-audit.csv", mime="text/csv",
    )
    st.download_button(
        "Download events missing direct citation links (CSV)",
        data=audit_csv(data["events_no_direct_link"], ("id", "date", "title")),
        file_name="family-event-source-link-audit.csv", mime="text/csv",
    )
    st.caption("Source collection links, original interpretation and legal reuse "
               "terms remain in the archive; a CSV does not establish a relationship.")


def render_integrity_dashboard(people: dict, events: list[dict],
                               relationships: dict) -> None:
    data = audit_family_archive(people, events, relationships)
    st.title("Family history — evidence and integrity dashboard")
    st.write("An accountable inventory of the *whole* current family tree: "
             "every person, each recorded family link, and the available source notes.")
    st.caption("Built from today's effective genealogy overlays; no people, tree edges, "
               "historical claims or images are edited by this dashboard.")
    section = str(st.query_params.get("section") or "overview")
    options = ("overview", "branches", "relationships", "records", "exports")
    if section not in options:
        section = "overview"
    control_key = "family_integrity_section"
    if st.session_state.get("_integrity_route") != section:
        st.session_state[control_key] = section
        st.session_state["_integrity_route"] = section
    chosen = st.radio("Explore the audit", options,
                      format_func=lambda value: {
                          "overview":"Overview","branches":"Disconnected branches",
                          "relationships":"Relationship evidence","records":"Missing records",
                          "exports":"Download checklists",
                      }[value], horizontal=True, key=control_key)
    st.session_state["_integrity_route"] = chosen
    if chosen != section:
        st.query_params["section"] = chosen
    if chosen == "overview":
        _summary(data, people)
    elif chosen == "branches":
        _branches(data, people)
    elif chosen == "relationships":
        _relationships(data, people)
    elif chosen == "records":
        _records(data, people)
    else:
        _exports(data)
