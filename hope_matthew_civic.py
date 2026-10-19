"""Evidence-first Hope town-clerk timeline for a named historical Matthew.

The town-ledger source is an EDITORIAL TRANSCRIPTION of original-era municipal
entries. Seven clerk excerpts are one documentary source family; they are not
seven independent witnesses or direct evidence of parents and marriages.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from routing_ui import route_link

SOURCE = Path(__file__).resolve().parent / "data" / "phase20_hope_matthew_civic_records.json"
EARLIER = Path(__file__).resolve().parent / "data" / "phase31_hope_earliest_clerk_research.json"

def load_hope_civic_records() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("Hope civic research file must be a one-document JSON array")
    data = payload[0]
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("Hope record evidence must be an indexed research document")
    earlier = json.loads(EARLIER.read_text(encoding="utf-8"))[0]
    data["records"] = sorted([*data["records"], *earlier["records"]],
                             key=lambda row: (row["date"], row["id"]))
    data["source_family_warning"] = (
        "All town-clerk passages, including the newly indexed 1806–1807 "
        "entries, derive from ONE historic Hope municipal ledger as rendered "
        "in a modern transcription, not independent original witnesses. "
        "The separate 1820 census is a distinct but uninspected original.")
    return data

def evidence_counts(data: dict) -> dict:
    records=data["records"]
    return {
        "observations":len(records),
        "ledger_entries":sum(row["category"]=="town_clerk_transcription" for row in records),
        "census_leads":sum(row["category"]=="census_index_secondary" for row in records),
        "distinct_source_families":len({row["category"] for row in records}),
    }

def record_for_id(record_id: str, data: dict | None = None) -> dict | None:
    for row in (data if data is not None else load_hope_civic_records())["records"]:
        if row["id"] == record_id:
            return row
    return None

def _card(row: dict) -> None:
    with st.container(border=True):
        st.markdown("**"+row["date"]+" · "+row["label"]+"**")
        st.caption(row["town"]+" · "+row["source_page"])
        st.write(row["claim"])
        st.caption("Evidence limitation: "+row["limit"])
        st.caption("Verification: "+row["verification"])
        route_link("Read the source transcription or index",row["source_url"])
        st.caption(row["source_title"])

def render_hope_civic_timeline(*, compact:bool=False) -> None:
    data=load_hope_civic_records()
    st.subheader("Matthew Beveridge in Hope's town records, 1806–1827")
    st.write("The 1804–1848 Hope municipal ledger names **Matthew Beveridge as "
             "town clerk at least by June 23, 1806**, with dated transcribed "
             "entries in 1807, 1811, 1813, 1821 and 1827. A separate 1820 "
             "household-head transcription lists Mathew Beveridge in Hope. "
             "This places a man of that name in contemporaneous civic records; "
             "the family's exact identity and his parents remain unproved.")
    counts=evidence_counts(data)
    cols=st.columns(3)
    cols[0].metric("Dated record occurrences",counts["observations"])
    cols[1].metric("Ledger entries",counts["ledger_entries"])
    cols[2].metric("Separate census lead",counts["census_leads"])
    st.caption(data["source_family_warning"])
    st.caption("The original handwritten municipal pages and 1820 federal census "
               "sheet have not been directly inspected. The visible links lead "
               "to a modern literal transcript or household-index summary.")

    options=["Every date","1806–1807","1811–1813","1820–1821","1827"]
    choice=st.selectbox("Browse the town records by period",options,
                         key="hope_matthew_period")
    records=sorted(data["records"],key=lambda row:row["date"])
    if choice=="1806–1807":
        records=[r for r in records if r["date"][:4] in {"1806","1807"}]
    elif choice=="1811–1813":
        records=[r for r in records if r["date"][:4] in {"1811","1813"}]
    elif choice=="1820–1821":
        records=[r for r in records if r["date"][:4] in {"1820","1821"}]
    elif choice=="1827":
        records=[r for r in records if r["date"].startswith("1827")]
    for row in records:
        _card(row)
    jurisdiction=data.get("jurisdiction_context")
    if jurisdiction:
        with st.expander("Why Hope's records switch counties in 1827 and 1860"):
            st.write(jurisdiction["finding"])
            st.caption(jurisdiction["limit"])
            route_link("Read Maine's legislative county history (PDF, p. 57)",
                       jurisdiction["url"])
    st.info("Update: a probate-office-supplied packet for Matthew of Hope "
             "has since been received (October 2026). Earlier retrieval statuses "
             "below are preserved as the original Phase 20 research snapshot; "
             "the court evidence now has its own review.")
    route_link("Review Matthew's Waldo County probate and eight named heirs",
               "?page=collection&view=waldo-probate")
    with st.expander("How to check the town manuscript and census (historical research snapshot)",expanded=not compact):
        for target in data["original_retrieval"]:
            st.markdown("**"+target["target"]+"**")
            st.caption("Status: "+target["status"].replace("_"," "))
            st.write(target["instructions"])
            route_link("Open the documented archive or finding aid",target["url"])

    route_link("Compare Capt. Matthew's two published marriages and ten children",
               "?page=collection&view=matthew")
    st.caption("No Matthew person profile, legal spouse relationship, "
               "property boundary or parent-child link is added by this research.")
