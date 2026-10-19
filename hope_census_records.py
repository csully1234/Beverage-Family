"""Source-faithful pre-1837 Hope census investigation.

A named head in a transcript is distinct from an original schedule reading.
An absent head in a transcription is not evidence of physical absence.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit
import streamlit as st

from routing_ui import route_link
from hope_primary_access import render_hope_primary_access

DATA = Path(__file__).resolve().parent / "data" / "phase32_hope_census_originals.json"
VALID_STATUS = {
    "surname_absent_from_published_head_transcription",
    "original_reel_located_not_person_verified",
    "name_in_published_head_index_original_not_checked",
}


def load_hope_census_trail(source: Path = DATA) -> dict:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("Expected one source-specific Hope census case")
    case = payload[0]
    rows = case["cases"]
    if [row["year"] for row in rows] != [1790, 1800, 1810, 1820]:
        raise ValueError("Census records must be complete and ordered")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate census source identity")
    for row in rows:
        if row["status"] not in VALID_STATUS or not row["limitations"]:
            raise ValueError("Missing or invalid census evidentiary status")
        if not all(urlsplit(str(row.get(key) or "")).scheme == "https"
                   for key in ("source_url", "finding_aid_url") if row.get(key)):
            raise ValueError("Insecure census archival link")
    return case


def census_evidence_counts(data: dict | None = None) -> dict:
    case = data if data is not None else load_hope_census_trail()
    rows = case["cases"]
    return {
        "census_years": len(rows),
        "transcribed_absent_named_heads": sum(
            row["status"] == "surname_absent_from_published_head_transcription"
            for row in rows),
        "named_head_transcriptions": sum(row["named_matthew_head"] is True for row in rows),
        "original_person_lines_inspected": sum(row["original_image_checked"] for row in rows),
    }


def _census_record(row: dict) -> None:
    with st.container(border=True):
        st.markdown("**" + str(row["year"]) + " · " + row["place"] + "**")
        st.caption("Original archive locator: " + row["archive_locator"])
        if row["named_matthew_head"] is True:
            st.markdown("**Named Matthew household-head entry in a published transcription**")
        elif row["named_matthew_head"] is False:
            st.markdown("**Surname not found among transcribed household heads**")
        else:
            st.markdown("**Original schedules located — person-level reading outstanding**")
        st.write(row["head_claim"])
        st.caption("Evidence limit: " + row["limitations"])
        route_link("Open the published census transcription or original reel",
                   row["source_url"])
        if row.get("finding_aid_url"):
            route_link("See the independent microfilm and town-page locator",
                       row["finding_aid_url"])
        with st.expander("What to inspect in the original schedule"):
            st.write(row["original_request"])
            st.caption("Original household image inspected here: **No**. "
                       "Do not invent handwriting, household ages or unnamed relatives.")


def render_hope_census_trail() -> None:
    case = load_hope_census_trail()
    counts = census_evidence_counts(case)
    st.title("Barrettstown to Hope: 1790–1820 census trail")
    st.write("This investigation tests a possible transition from the Fox "
             "Islands-era Matthew to the Hope town clerk and 1837 decedent, "
             "without presuming that records with similar names belong to "
             "the same man.")
    st.warning("**Negative household-head lists do not prove a person's absence.** "
               "The census schedules name household heads, not everyone "
               "living with them. No original 1810 Matthew census entry, "
               "1820 household age tally or parentage is yet verified.")
    a,b,c = st.columns(3)
    a.metric("Census years checked", counts["census_years"])
    b.metric("Years with no surname in transcribed head list",
             counts["transcribed_absent_named_heads"])
    c.metric("Verified original Matthew census lines", counts["original_person_lines_inspected"])
    st.caption("In 1820, a separate 2019 name index explicitly reports a "
               "Mathew Beveridge household head. That is not an inspected "
               "original census line.")
    for row in case["cases"]:
        _census_record(row)
    render_hope_primary_access()
    st.subheader("Compare against the separate town-clerk evidence")
    st.write("Hope's municipal record transcription names **Matthew "
             "Beveridge by June 23, 1806**. This is positive civic evidence "
             "between the unconfirmed 1800 and 1810 census identities, "
             "but does not resolve his parents, land title, or Fox Islands origin.")
    route_link("Read the dated Hope clerk entries from 1806 onward",
               "?page=collection&view=hope-matthew")
    route_link("Open the 1785–1786 Fox Islands original-document trail",
               "?page=collection&view=fox-originals")
    route_link("Compare Matthew's 1837 probate and family evidence",
               "?page=collection&view=waldo-probate")
    st.caption("All four census findings retain their source status and can "
               "be retrieved in the searchable family research workbench. "
               "No birth, marriage, parent, child, property or family branch "
               "was changed by this research.")
