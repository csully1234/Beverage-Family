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


def render_family_discoveries(people_by_id: dict) -> None:
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
    requested = str(st.query_params.get("finding", "") or "")
    if not requested:
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
