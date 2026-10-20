"""Human-readable, read-only archive-wide research and source access desk."""
from __future__ import annotations

from urllib.parse import quote

import streamlit as st

from archive_triage import (person_source_matrix, matrix_counts,
                            unresolved_reference_cases)
from genealogy_integrity import audit_csv
from routing_ui import route_link


def render_missing_reference_cases(people: dict, relationships: dict) -> None:
    st.subheader("Six unresolved relationship references: full case desk")
    st.caption("An unresolved identifier is not automatically a newly discovered "
               "person. Name-comparison leads are NOT confirmed matches. "
               "Do not join branches or change relatives from similarity alone.")
    cases = unresolved_reference_cases(people, relationships)
    for item in cases:
        with st.expander(item["id"].replace("_", " ") + " · " +
                         str(len(item["references"])) + " explicit reference(s)"):
            for ref in item["references"]:
                st.caption("Recorded as " + ref["kind"] + " of " + ref["owner_name"])
                route_link("Open the person who recorded this relationship",
                           "?page=people&profile=" + quote(ref["owner_id"], safe=""))
            if not item["references"]:
                st.caption("This unresolved ID has no direct profile reference; "
                           "it may appear in a derived relationship and needs review.")
            if item["potential_name_matches"]:
                st.markdown("**Existing profiles to compare — not identity matches**")
                for candidate in item["potential_name_matches"]:
                    route_link("Compare: " + candidate["name"],
                               "?page=people&profile=" + quote(candidate["id"], safe=""))
            else:
                st.caption("No indexed person has a matching first and last name.")
            st.caption("What resolves the case: an original vital, marriage, court, "
                       "or other record identifying both parties; no unsourced link.")
    export = [{
        "id": item["id"],
        "references": "; ".join(ref["owner_name"] + " (" + ref["kind"] + ")"
                                for ref in item["references"]),
        "comparison_ids": "; ".join(x["id"] for x in
                                    item["potential_name_matches"]),
    } for item in cases]
    st.download_button("Download every missing-profile research case (CSV)",
                       data=audit_csv(export, ("id", "references", "comparison_ids")),
                       file_name="family-unresolved-relationship-cases.csv",
                       mime="text/csv")


def render_archive_access(people: dict, events: list[dict],
                          relationships: dict, edges: list[dict]) -> None:
    """Explore all exact-person citations without judging truth from link counts."""
    rows = person_source_matrix(people, events, relationships, edges=edges)
    summary = matrix_counts(rows)
    st.subheader("Source access across the entire family")
    st.write("This combines links from **profile bibliographies**, curated exhibits, "
             "**dated events**, exact-ID research findings, and "
             "**individually reviewed family connections**.")
    st.caption("Counts reflect source navigation only. An external link can lead "
               "to a published index or catalog rather than an original manuscript. "
               "No external website has been checked for current availability; "
               "source rights and identity cautions still apply.")
    cols = st.columns(3)
    cols[0].metric("Indexed relatives", summary["people"])
    cols[1].metric("With a linked source somewhere", summary["any_external_link"])
    cols[2].metric("Without a source URL in these catalogs",
                   summary["no_external_link_in_indexed_contexts"])
    filters = (
        "Everyone",
        "No direct source URL anywhere indexed",
        "Unlinked profile citation but links elsewhere",
        "Has individual relationship evidence review",
        "Has original-book photo page attribution",
    )
    chosen = st.selectbox("Evidence access filter", filters,
                          key="integrity_access_filter")
    query = st.text_input("Search relative's name",
                          key="integrity_access_name").strip().casefold()
    filtered = [
        row for row in rows if (not query or query in row["name"].casefold())
        and (chosen != filters[1] or row["direct_source_links"] == 0)
        and (chosen != filters[2] or (row["direct_profile_links"] == 0 and
                                      row["direct_source_links"] > 0))
        and (chosen != filters[3] or row["reviewed_relationships"] > 0)
        and (chosen != filters[4] or bool(row["book_photo_pages"]))
    ]
    st.caption(str(len(filtered)) + " profile(s) match. A missing external URL "
               "is an archival retrieval task, not proof no evidence exists.")
    if filtered:
        ids = [row["id"] for row in filtered]
        requested = str(st.query_params.get("person") or "")
        selected_id = st.selectbox(
            "Read one relative's complete source-access paths",
            ids, index=ids.index(requested) if requested in ids else 0,
            format_func=lambda pid: str(people[pid].get("full_name") or pid),
        )
        row = next(r for r in filtered if r["id"] == selected_id)
        metric = st.columns(3)
        metric[0].metric("Distinct external source URLs", row["direct_source_links"])
        metric[1].metric("Cited dated events", row["events_with_citations"])
        metric[2].metric("Individually reviewed family links",
                         row["reviewed_relationships"])
        st.caption(str(row["profile_references"]) + " profile/exhibit reference(s) · " +
                   str(row["attributed_research_items"]) + " specifically attributed "
                   "research item(s) · " + str(row["total_relationships"]) +
                   " recorded direct relationship(s)")
        route_link("Open full profile",
                   "?page=people&profile=" + quote(selected_id, safe=""))
        route_link("Open this person's original-record and dated-event reader",
                   "?page=collection&view=person-exhibit&person=" +
                   quote(selected_id, safe="") + "&section=Original%20records")
        route_link("Review the specific evidence for their family links",
                   "?page=collection&view=integrity&section=relationships&person=" +
                   quote(selected_id, safe=""))
        if row["book_photo_pages"]:
            st.markdown("**Source-book photographs (author-attributed, not independent proof)**")
            for page in row["book_photo_pages"]:
                route_link("Open original book PDF page " + str(page),
                           "?page=family-books&book_page=" + str(page))
        st.markdown("**All distinct accessible external sources for this relative**")
        if not row["source_links"]:
            st.info("No direct source URL was identified in the indexed contexts. "
                    "Bibliographic-only references, unpublished archive material, "
                    "and unresolved records remain visible elsewhere.")
        else:
            with st.expander(str(len(row["source_links"])) +
                             " distinct linked source destinations", expanded=True):
                for item in row["source_links"]:
                    st.caption(item["kind"])
                    route_link(item["title"], item["url"])
        if row["research_routes"]:
            with st.expander("Open all " + str(len(row["research_routes"])) +
                             " research contexts"):
                for i, destination in enumerate(row["research_routes"], 1):
                    route_link("Open attributed research item/context " + str(i),
                               destination)
    else:
        st.info("No indexed relatives match that search or evidence-access filter.")
    st.download_button(
        "Download full family source-access matrix (CSV)",
        data=audit_csv(rows, (
            "id", "name", "profile_references", "direct_profile_links",
            "dated_events", "events_with_citations", "direct_event_links",
            "attributed_research_items", "direct_research_links",
            "reviewed_relationships", "total_relationships",
            "direct_relationship_links", "direct_source_links",
        )), file_name="family-complete-source-access.csv", mime="text/csv",
    )
