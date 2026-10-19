"""Visitor-focused historical discovery browser.

All original research source files, inventories, search logs and review notes
remain in GitHub for provenance, but are NOT browsing destinations for visitors.
"""
from __future__ import annotations

import json
import streamlit as st

from research_collection_ui import load_collection, render_finding
from routing_ui import route_link
from family_data import relationship_index
from relationship_evidence import render_relationship_coverage
from ancestry_bridge_casework import render_ancestry_dossiers
from family_research_workbench import render_research_workbench
from matthew_reconciliation import render_matthew_reconciliation
from hope_matthew_civic import render_hope_civic_timeline
from waldo_probate import render_waldo_probate
from family_origins_casework import render_family_origins
from family_exhibits import render_person_exhibit


def render_family_discoveries(people_by_id: dict, events: list | None = None,
                              relationships: dict | None = None) -> None:
    if str(st.query_params.get("view", "") or "") == "person-exhibit":
        person_id = str(st.query_params.get("person", "") or "")
        render_person_exhibit(person_id, people_by_id, events or [], relationships)
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    if str(st.query_params.get("view", "") or "") == "family-origins":
        render_family_origins()
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    if str(st.query_params.get("view", "") or "") == "waldo-probate":
        st.title("Waldo County probate — Matthew Beverage estate papers")
        render_waldo_probate()
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    if str(st.query_params.get("view", "") or "") == "hope-matthew":
        st.title("Matthew Beveridge — original-era Hope civic records")
        render_hope_civic_timeline()
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    if str(st.query_params.get("view", "") or "") == "matthew":
        st.title("Matthew Beverage — historical family-group evidence")
        render_matthew_reconciliation()
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    if str(st.query_params.get("view", "") or "") == "workbench":
        render_research_workbench(people_by_id)
        route_link("← Return to Historical Discoveries", "?page=collection")
        return
    collection = load_collection()
    st.title("Historical Discoveries")
    st.write(
        "Explore historical discoveries connected to the family: "
        "testimony, island life, old photographs, marriages, property and family relationships."
    )
    st.caption(
        "All historical findings are shown, including possible and disputed connections. "
        "Original sources and evidence explanations remain available with each discovery."
    )
    route_link("Open the complete Family Research Workbench — search every source, "
               "original book page and relationship",
               "?page=collection&view=workbench")
    requested = str(st.query_params.get("finding", "") or "")
    if not requested:
        route_link("EXPLORE A LIFE: Matthew's family, court records and historical timeline",
                   "?page=collection&view=person-exhibit&person=matthew_beveridge_hope_1837")
        route_link("NEW RESEARCH: Clarissa Cobb's 1786 Carver birth family and Matthew's unresolved origins",
                   "?page=collection&view=family-origins")
        route_link("NEW: Matthew's 1837 Waldo probate — Clarissa, eight heirs and court papers",
                   "?page=collection&view=waldo-probate")
        route_link("New original-era town record trail: Matthew Beveridge, Hope Town Clerk (1811–1827)",
                   "?page=collection&view=hope-matthew")
        route_link("Research breakthrough: Matthew's FIRST wife Abigail Dyer and SECOND wife Clarissa Cobb in the 1865 source",
                   "?page=collection&view=matthew")
        render_ancestry_dossiers(people_by_id)
        with st.expander("How are family relationships documented? · Complete connection audit"):
            render_relationship_coverage(people_by_id,
                                         relationship_index(people_by_id.values()))
    if requested:
        record = collection.findings.get(requested)
        if record is None:
            st.warning("That historical discovery was not found.")
        else:
            render_finding(record, collection, people_by_id, detail=True)
        route_link("← See all historical discoveries", "?page=collection")
        return

    search = st.text_input("Search family discoveries", key="family_discoveries_search",
                           placeholder="Thomas, North Haven, boats, land, marriage…").strip().casefold()
    topics = sorted({topic for finding in collection.findings.values()
                     for topic in finding["Navigation"].get("topics", [])})
    topic = st.selectbox("Subject", ["", *topics],
                         format_func=lambda value: value or "All historical subjects",
                         key="family_discoveries_topic")
    person = str(st.query_params.get("person", "") or "")
    place = str(st.query_params.get("place", "") or "")
    legacy_topic = str(st.query_params.get("topic", "") or "")
    findings = []
    for record in collection.findings.values():
        nav = record["Navigation"]
        if topic and topic not in nav.get("topics", []):
            continue
        if legacy_topic and legacy_topic not in nav.get("topics", []):
            continue
        if person and person not in nav.get("people_ids", []):
            continue
        if place and place not in nav.get("place_ids", []):
            continue
        if search and search not in json.dumps(
            {"title": nav.get("title"), "summary": record.get("Proposed fact or narrative"),
             "location": record.get("Location"), "date": record.get("Date or date range")},
            ensure_ascii=False, default=str,
        ).casefold():
            continue
        findings.append(record)
    # Preserve date hints without implying unsupported chronological precision.
    findings.sort(key=lambda r: (
        str(r.get("Date or date range") or "Undated"),
        str(r["Navigation"].get("title") or "")
    ))
    st.caption(f"{len(findings)} historical discoveries matching your selection")
    if not findings:
        st.info("No discoveries matched. Try another subject or search term.")
    for record in findings:
        with st.container(border=True):
            heading = str(record["Navigation"].get("title") or "Historical record")
            st.markdown("**" + heading + "**")
            st.caption(f"{record.get('Date or date range', 'Undated')} · {record.get('Location', '')}")
            st.write(record.get("Proposed fact or narrative", ""))
            certainty = record.get("Confidence", "")
            if certainty in {"Possible lead", "Probable", "Conflict", "Rejected"}:
                st.caption("Historical interpretation: " + certainty.lower() +
                           " — see original evidence for details.")
            route_link("Read more and see original sources",
                       "?page=collection&finding=" + record["Research ID"])
