"""Cross-source island community trail, 1785–1829: cite, compare, do not merge.

The 1889 civic narrative, 1820 census transcription and scanned federal
register OCR are DIFFERENT source families, but not original genealogical
birth/parentage proof. This module cannot change any canonical relationship.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link, safe_external_url

FILE = Path(__file__).resolve().parent / "data" / "phase44_fox_islands_government_census_crosswalk.json"
ALLOWED_STATUS = {
    "printed_name_only_unassigned",
    "indexed_head_not_original_confirmed",
    "OCR_office_name_unassigned_publication_year_inconsistent",
}
REQUIRED_SOURCE_FAMILIES = {
    "1889-vinalhaven-historical-sketch",
    "2019-transcribed-1820-head-index",
    "federal-register-scanned-text-single-edition",
}


def load_government_trail(path: Path = FILE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 1:
        raise ValueError("Expected a single versioned Fox Islands source collection")
    trail = data[0]
    sources = {s["id"]: s for s in trail["sources"]}
    if (len(sources) != 3 or len(trail["sources"]) != 3 or
            {s["source_family"] for s in sources.values()} != REQUIRED_SOURCE_FAMILIES):
        raise ValueError("Three independent source families are required")
    if len(trail["records"]) != 8:
        raise ValueError("Eight documented early island source observations required")
    for source in sources.values():
        if (source["original_manuscript_read"] or not source["limits"] or
                not safe_external_url(source["url"])):
            raise ValueError("Published source is not original manuscript proof")
        if source.get("alternate_url") and not safe_external_url(source["alternate_url"]):
            raise ValueError("Unsafe alternate scan locator")
    ids = set()
    for record in trail["records"]:
        if record["id"] in ids:
            raise ValueError("Repeated source record")
        ids.add(record["id"])
        if (record["source_id"] not in sources or
                record["identity_status"] not in ALLOWED_STATUS or
                not record["next_original"] or not record["page"]):
            raise ValueError("Invalid source identity or missing original-proof limits")
        if not 1785 <= record["sort_year"] <= 1829:
            raise ValueError("Historical chronology not in recorded range")
        if (record["id"] == "register-1827-1829-john" and
                ("1827 OR 1829" not in record["date_label"] or
                 "unresolved" not in record["date_label"])):
            raise ValueError("Disputed official-register publication date must remain open")
    return trail


def trail_for_candidate(person_id: str, data: dict | None = None) -> list[dict]:
    """These are RESEARCH comparisons, not confirmed dated profile events."""
    rows = (data or load_government_trail())["records"]
    return [r for r in rows if person_id in r["candidate_person_ids"]]


def trail_route(record_id: str = "") -> str:
    route = "?page=collection&view=source-expedition&community=1"
    return route + ("&community_record=" + quote(record_id, safe="")
                    if record_id else "")


def trail_counts(data: dict | None = None) -> dict:
    trail = data or load_government_trail()
    rows = trail["records"]
    return {
        "source_families": len(trail["sources"]),
        "research_observations": len(rows),
        "retrospective_meeting_mentions": sum(r["source_id"] == "vinalhaven-1889-narrative" for r in rows),
        "1820_census_head_names": sum(r["source_id"] == "vinalhaven-1820-index" for r in rows),
        "federal_ocr_mentions": sum(r["source_id"] == "federal-official-register" for r in rows),
        "original_manuscripts_inspected": 0,
        "confirmed_profile_identity_links": 0,
    }


def trail_csv(trail: dict | None = None) -> str:
    case = trail or load_government_trail()
    out = io.StringIO()
    keys = ("id", "date_label", "printed_name", "event_type", "details",
            "source_id", "page", "identity_status", "next_original")
    writer = csv.DictWriter(out, fieldnames=keys)
    writer.writeheader()
    for row in case["records"]:
        writer.writerow({k: row[k] for k in keys})
    return out.getvalue()


def render_fox_islands_government_trail(people: dict, *, selected: str = "") -> None:
    trail = load_government_trail()
    rows = trail["records"]
    source_map = {source["id"]: source for source in trail["sources"]}
    ids = {r["id"]: r for r in rows}
    numbers = trail_counts(trail)
    st.subheader("Fox Islands · from plantation clerk to federal customs")
    st.write("Travel through early island records from the 1785 plantation "
             "meeting, through the 1820 census household-head index, to a "
             "federal Customs inspector's printed name. The items come from "
             "**three different publication/source families**, each with its "
             "own limitations; no implied family relationship is inserted.")
    a,b,c = st.columns(3)
    a.metric("Historical observations",numbers["research_observations"])
    b.metric("Publication families",numbers["source_families"])
    c.metric("Confirmed profile identities",0)
    st.warning("Original 1785–1789 meeting minutes, 1820 census age boxes and "
               "original federal register title/entry have NOT been inspected. "
               "The federal edition is ambiguously indexed as 1827 or 1829; "
               "the officeholder has not been assigned to John White Beverage.")
    requested = selected if selected in ids else ""
    if st.session_state.get("_community_last_url") != requested:
        st.session_state["community_selected_id"] = requested
        st.session_state["_community_last_url"] = requested
    selected_id = st.selectbox(
        "Follow an original historical clue",
        ["",*(r["id"] for r in rows)],
        format_func=lambda x: "All records in chronological order" if not x else (
            ids[x]["date_label"] + " · " + ids[x]["printed_name"]),
        key="community_selected_id",
    )
    shown = [ids[selected_id]] if selected_id else sorted(
        rows,key=lambda r:(r["sort_year"],r["date_label"],r["printed_name"]))
    for row in shown:
        source=source_map[row["source_id"]]
        with st.container(border=True):
            st.markdown("**"+row["date_label"]+" — "+row["printed_name"]+"**")
            st.write(row["event_type"])
            st.write(row["details"])
            st.caption("Source locator: "+row["page"])
            st.caption("Source family: "+source["title"])
            route_link("Read the published/archival source",source["url"])
            if source.get("alternate_url"):
                route_link("See the alternate scan of this SAME publication",
                           source["alternate_url"],type="tertiary")
            st.warning("What this DOES NOT prove: "+source["limits"])
            with st.expander("What original record would actually resolve it?"):
                st.write(row["next_original"])
                st.caption("Candidate profile comparisons are only research leads; "
                           "none of these names proves parents or a person identity.")
                for pid in row["candidate_person_ids"]:
                    if pid in people:
                        route_link("Compare existing profile: " +
                                   str(people[pid].get("full_name") or pid),
                                   "?page=people&profile="+quote(pid,safe=""),
                                   type="tertiary")
            if not selected_id:
                route_link("Open just this historical observation",
                           trail_route(row["id"]),type="tertiary")
    st.subheader("Sources are not votes")
    st.write("The 1785, 1788 and 1789 meeting narratives come from the SAME "
             "1889 Vinalhaven book as the previously indexed officer roster. "
             "The 2019 census transcription is not the original handwritten "
             "household schedule. Two scans of one federal government register "
             "are not two independent historical witnesses. Multiple names "
             "can be compared without being assigned to a parent or child.")
    st.download_button("Download full eight-record source comparison (CSV)",
                       trail_csv(trail),file_name="fox-islands-early-sources-1785-1829.csv",
                       mime="text/csv")
