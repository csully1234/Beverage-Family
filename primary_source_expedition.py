"""Family Origins Expedition: source-led, read-only genealogy research casework.

Manuscript locations are *retrieval targets* unless an entry explicitly records
original inspection. Candidate parent-child edges are not canonical genealogy.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Mapping
from urllib.parse import quote

import streamlit as st

from genealogy_integrity import connected_components
from family_bridge_lab import PROPOSALS, bridge_preview, proposal_worklist
from identity_claim_review import render_conflict_review
from original_record_intake import render_acquisition_center
from vinalhaven_civic_history import render_vinalhaven_civic, civic_route
from fox_islands_government_trail import render_fox_islands_government_trail, trail_route
from routing_ui import route_link, safe_external_url

DATA = Path(__file__).resolve().parent / "data" / "phase39_primary_record_expedition.json"


def load_expedition(path: Path = DATA) -> dict:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError("The family-origins expedition must have one versioned case register")
    data = records[0]
    sources = data.get("sources", [])
    cases = data.get("cases", [])
    if len(cases) != 4 or len(sources) < 10:
        raise ValueError("Family origins source expedition is incomplete")
    ids = [s["id"] for s in sources]
    case_ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)) or len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate family origins source or investigation ID")
    valid = set(ids)
    for s in sources:
        if s.get("url") and not safe_external_url(s["url"]):
            raise ValueError("Unsafe source address in family origins register")
        if s.get("original_access") and not safe_external_url(s["original_access"]):
            raise ValueError("Unsafe original-source archive link")
        if s["class"] == "exact_original_image_locator_uninspected" and s["original_inspected"]:
            raise ValueError("An uninspected original locator cannot be marked inspected")
    for case in cases:
        if not case.get("next_checks") or not case.get("source_ids"):
            raise ValueError("Every origins case needs original evidence and follow-up")
        if not set(case["source_ids"]) <= valid:
            raise ValueError("Origins case refers to nonexistent source record")
    return data


def expedition_route(case_id: str | None = None) -> str:
    base = "?page=collection&view=source-expedition"
    return base + ("&case=" + quote(str(case_id), safe="") if case_id else "")


def branch_status(case: dict, people: Mapping[str, dict], relationships: Mapping) -> dict:
    """Which *existing* tree components does a hypothesis reference?

    Multiple groups listed are NOT a new relationship between those groups.
    """
    components = connected_components(people, relationships)
    component_by_id = {pid: i + 1 for i, group in enumerate(components)
                       for pid in group}
    people_ids = [pid for pid in case["people_ids"] if pid in people]
    groups = sorted({component_by_id[pid] for pid in people_ids})
    return {
        "people_ids": people_ids,
        "component_numbers": groups,
        "cross_component_lead": len(groups) > 1,
        "component_count": len(components),
        "unknown_profile_ids": sorted(set(case["people_ids"]) - set(people)),
    }


def source_progress(data: dict) -> dict:
    """Counts represent editorial inspection status, NOT proof of kinship."""
    sources = data["sources"]
    return {
        "sources": len(sources),
        "originals_read_or_reviewed": sum(bool(s["original_inspected"]) for s in sources),
        "retrieval_targets": sum(not bool(s["original_inspected"]) for s in sources),
        "cases": len(data["cases"]),
    }


def expedition_csv(data: dict) -> str:
    """Export source retrieval checklist for independent archival review."""
    buf = io.StringIO()
    cols = ("case_priority", "case_id", "case_title", "source_id", "source_title",
            "source_class", "source_year", "repository", "original_locator",
            "original_inspected", "source_url", "original_collection_url",
            "evidence_limit", "next_checks")
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    source_by_id = {s["id"]: s for s in data["sources"]}
    for case in sorted(data["cases"], key=lambda c: c["priority"]):
        for source_id in case["source_ids"]:
            s = source_by_id[source_id]
            writer.writerow({
                "case_priority": case["priority"],
                "case_id": case["id"],
                "case_title": case["title"],
                "source_id": s["id"],
                "source_title": s["title"],
                "source_class": s["class"],
                "source_year": s["year"],
                "repository": s["repository"],
                "original_locator": s["locator"],
                "original_inspected": "yes" if s["original_inspected"] else "no",
                "source_url": s["url"],
                "original_collection_url": s.get("original_access", ""),
                "evidence_limit": s["limits"],
                "next_checks": " | ".join(case["next_checks"]),
            })
    return buf.getvalue()


def cases_for_person(person_id: str, data: dict | None = None) -> list[dict]:
    """Show exactly attributed research *questions* on existing profiles."""
    current = data if data is not None else load_expedition()
    return sorted((case for case in current["cases"]
                   if person_id in case["people_ids"]),
                  key=lambda case: (case["priority"], case["title"]))


def _selected_case_changed() -> None:
    """Keep the selected case shareable, even when switched via the dropdown."""
    case_id = str(st.session_state.get("origins_expedition_selected_case") or "")
    if case_id:
        st.query_params["case"] = case_id
    elif "case" in st.query_params:
        del st.query_params["case"]
    st.session_state["_origins_last_case_query"] = case_id


def _source_card(source: dict) -> None:
    with st.container(border=True):
        st.markdown("**" + source["title"] + "**")
        st.caption(str(source["year"]) + " · " + source["repository"])
        st.caption("Archival location: " + source["locator"])
        st.write(source["establishes"])
        st.caption("Original inspected: " + ("yes — see study notes"
                    if source["original_inspected"] else
                    "NO — record locator or edited transcript only"))
        st.caption("What it does NOT prove: " + source["limits"])
        if source.get("url"):
            route_link("Open cited repository/editorial source", source["url"])
        if source.get("original_access") and source["original_access"] != source.get("url"):
            route_link("Open original record collection", source["original_access"])
        st.caption(source["rights"])


def render_source_expedition(people: dict, relationships: dict) -> None:
    data = load_expedition()
    progress = source_progress(data)
    source_by_id = {s["id"]: s for s in data["sources"]}
    cases = sorted(data["cases"], key=lambda row: row["priority"])
    case_by_id = {case["id"]: case for case in cases}
    requested = str(st.query_params.get("case") or "")
    st.title("Family Origins Expedition")
    st.write("A guided investigation into the earliest Beverage and Beveridge lines, "
             "the four currently separate recorded family groups, and original "
             "documents that could genuinely prove new family links.")
    st.caption("A precise archive image number is an invitation to inspect a record, "
               "not a claim it was read. A shared surname and a family-tree website "
               "do not make an ancestral relationship true.")
    columns = st.columns(3)
    columns[0].metric("Major family-history investigations", progress["cases"])
    columns[1].metric("Cited source records", progress["sources"])
    columns[2].metric("Originals to read or verify", progress["retrieval_targets"])

    # An exact-person exhibit deep-link should show its contested record FIRST,
    # not make a visitor scroll through four other case reports on a phone.
    requested_conflict = str(st.query_params.get("conflict_case") or "")
    if requested_conflict:
        render_conflict_review(people, selected=requested_conflict)
        st.divider()

    # Original-document recovery is the priority for research visitors.
    # Keep direct book-marked source targets close to the top of the view.
    requested_source = str(st.query_params.get("source_target") or "")
    if requested_source or st.query_params.get("acquire") == "1":
        render_acquisition_center(people, selected=requested_source)
        st.divider()

    # Historical civic office names are real printed entries, but profile
    # identity must not be inferred. Deep links show the selected year first.
    requested_civic = str(st.query_params.get("civic") or "")
    if requested_civic == "1":
        render_vinalhaven_civic(
            people,
            source_name=str(st.query_params.get("officer") or ""),
            focus_year=str(st.query_params.get("office_year") or ""),
        )
        st.divider()
    else:
        route_link("Explore the 1889 Vinalhaven civic history: 55 original printed office entries",
                   civic_route())
    # Three distinct historical publication families compared side-by-side,
    # with recorded name strings never promoted to person-event/parent facts.
    community_target = str(st.query_params.get("community_record") or "")
    if st.query_params.get("community") == "1" or community_target:
        render_fox_islands_government_trail(people,selected=community_target)
        st.divider()
    else:
        route_link("Trace Fox Islands residents through plantation, census and customs records",
                   trail_route())
    valid_ids = ["", *(case["id"] for case in cases)]
    requested_option = requested if requested in case_by_id else ""
    if st.session_state.get("_origins_last_case_query") != requested_option:
        st.session_state["origins_expedition_selected_case"] = requested_option
        st.session_state["_origins_last_case_query"] = requested_option
    selected_case = st.selectbox(
        "Choose a family mystery to investigate",
        valid_ids,
        format_func=lambda cid: ("All investigations" if not cid else
                                 str(case_by_id[cid]["priority"]) + " · " +
                                 case_by_id[cid]["title"]),
        key="origins_expedition_selected_case",
        on_change=_selected_case_changed,
    )
    if requested and requested not in case_by_id:
        st.info("The bookmarked research case was not found; all current cases remain accessible.")
    displayed = [case_by_id[selected_case]] if selected_case else cases
    for case in displayed:
        st.divider()
        with st.container(border=True):
            st.subheader(case["title"])
            st.caption("Research priority " + str(case["priority"]) + " · " +
                       case["period"] + " · " + case["place"])
            st.caption(case["status"])
            st.markdown("**The question**")
            st.write(case["question"])
            st.markdown("**What the records suggest**")
            st.write(case["working_theory"])
            st.markdown("**What we can say with evidence**")
            st.write(case["strong_evidence"])
            st.markdown("**What is not yet established**")
            st.warning(case["not_proved"])
            status = branch_status(case, people, relationships)
            if status["cross_component_lead"]:
                st.caption("This investigation discusses people currently in SEPARATE "
                           "recorded family groups (" +
                           ", ".join(str(x) for x in status["component_numbers"]) +
                           "). Their grouping has NOT been changed.")
            for pid in status["people_ids"]:
                record = people[pid]
                route_link("Explore existing relative: " +
                           str(record.get("full_name") or pid),
                           "?page=people&profile=" + quote(pid, safe=""))
            route_link("Explore the related archive section", case["existing_route"])
            st.caption("Why this case matters: " + case["research_value"])
            with st.expander("View every original-document locator and its limitations",
                             expanded=bool(selected_case)):
                for source_id in case["source_ids"]:
                    _source_card(source_by_id[source_id])
            with st.expander("Original records needed to resolve this case",
                             expanded=bool(selected_case)):
                for index, task in enumerate(case["next_checks"], 1):
                    st.write(str(index) + ". " + task)
            route_link("Open or bookmark this exact research investigation",
                       expedition_route(case["id"]), type="tertiary")
    st.divider()
    if not requested_conflict:
        render_conflict_review(people)
        st.divider()
    st.subheader("Family connection laboratory — explore without changing the tree")
    st.write("What would happen if a proposed parent-child relationship were eventually "
             "proved by an original register? Compare the recorded family groups "
             "with a hypothetical view. **No relationship is added or saved.**")
    st.caption("Both possible parents below come from ONE contributed genealogy, "
               "not two independent witnesses. The printed 1865 kinship clue "
               "does not identify the parents.")
    selected_bridges = st.multiselect(
        "Research a potential parentage connection",
        [p["id"] for p in PROPOSALS],
        format_func=lambda pid: next(p["title"] for p in PROPOSALS
                                     if p["id"] == pid),
        key="origins_unproved_bridge_preview",
    )
    preview = bridge_preview(PROPOSALS, people, relationships, selected_bridges)
    col_before, col_after = st.columns(2)
    col_before.metric("Recorded separate family groups", preview["before"])
    col_after.metric("IF selected theories were proven",
                     preview["hypothetical_after"])
    st.caption("The hypothetical count is an in-memory illustration only. The "
               "published graph and every person's parents remain unchanged.")
    for item in proposal_worklist(PROPOSALS, people):
        with st.expander(item["title"] + " — ORIGINAL PROOF REQUIRED"):
            st.write(item["basis"])
            st.warning("Before changing the family tree: " + item["needed"])
            st.caption("Current evidence status: " + item["status"])
            route_link("Read all original-record targets for this bridge",
                       expedition_route(item["case"]))
            route_link("Compare the currently separate family groups",
                       "?page=collection&view=integrity&section=branches")
    if not (requested_source or st.query_params.get("acquire") == "1"):
        st.divider()
        render_acquisition_center(people)
    st.divider()
    st.subheader("Take the evidence checklist to the archives")
    st.write("Every case includes its exact reel, register, page or image "
             "location when known, plus a source status and specific questions "
             "to resolve. You can download all these leads for your own "
             "research without exposing unpublished probate scans.")
    st.download_button(
        "Download all original-source retrieval tasks (CSV)",
        expedition_csv(data),
        file_name="beverage-family-origins-original-source-expedition.csv",
        mime="text/csv",
    )
    route_link("Compare disconnected family groups and missing relatives",
               "?page=collection&view=integrity&section=branches")
    route_link("Search the complete research source index",
               "?page=collection&view=workbench")
