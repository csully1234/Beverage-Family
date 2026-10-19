"""Critical source comparison for Clarissa's maternal Cobb family and Matthew's origins.

Published Carver town vital records and an independently titled family history
have different evidentiary roles. Their combination links the older mother and
father group to the documented Hope widow, without settling Matthew's origins.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link

RESEARCH = Path(__file__).resolve().parent / "data" / "phase24_cobb_vital_identity_research.json"


def load_family_origins_research() -> dict:
    payload = json.loads(RESEARCH.read_text(encoding="utf-8"))
    if len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("Expected one reviewed Phase 24 family-origins case file")
    item = payload[0]
    if len(item.get("sources", [])) != 7 or len(item.get("findings", [])) != 7:
        raise ValueError("Origins research source and finding register is incomplete")
    return item


def findings_by_status(data: dict | None = None) -> dict[str, list[dict]]:
    data = data or load_family_origins_research()
    grouped: dict[str, list[dict]] = {}
    for finding in data["findings"]:
        grouped.setdefault(finding["status"], []).append(finding)
    return grouped


def _source_card(source: dict) -> None:
    with st.container(border=True):
        st.markdown("**" + source["title"] + "**")
        st.caption(str(source["year"]) + " · " + source["page"] +
                   " · " + source["class"].replace("_", " "))
        st.write(source["claim"])
        st.caption("Actually reviewed: " + source["directly_inspected"])
        st.caption("Limitation: " + source["limitations"])
        route_link("Read the published source or source index", source["url"])
        if source.get("original_scan_locator"):
            route_link("Open original publication's digitized scan catalog",
                       source["original_scan_locator"])


def _finding_card(finding: dict, source_by_id: dict) -> None:
    with st.container(border=True):
        st.markdown("**" + finding["title"] + "**")
        st.caption(finding["date"] + " · " + finding["status"].replace("_", " "))
        st.write(finding["claim"])
        st.caption("Evidence boundary: " + finding["limits"])
        for pid in finding.get("person_ids", []):
            route_link("View person: " + pid.replace("_", " "),
                       "?page=people&profile=" + quote(pid, safe=""))
        for sid in finding["source_ids"]:
            source = source_by_id[sid]
            route_link("Read " + source["title"], source["url"])


def render_family_origins() -> None:
    data = load_family_origins_research()
    sources = {s["id"]: s for s in data["sources"]}
    st.title("Matthew's origins and Clarissa Cobb's documented family")
    st.write("A substantial new discovery concerns **Clarissa**, the wife/widow "
             "named in Matthew's 1837 probate. **Carver's town-record-based birth "
             "transcription identifies her parents as Barnabas and Jerusha Cobb**, "
             "and a separate Cobb genealogy calls that daughter Capt. Matthew's "
             "wife in Hope. The marriage identity is supported by later genealogy "
             "and still needs an original marriage return.")
    st.caption("Matthew's own parents, his proposed relationship with Capt. Thomas "
               "and the 1785 Fox Islands petition minor are NOT proved by these records.")

    a, b, c = st.columns(3)
    a.metric("Birth-family parents", 2)
    b.metric("Sourced case findings", len(data["findings"]))
    c.metric("Original Matthew deeds verified", 0)
    route_link("Start at Clarissa's sourced family profile",
               "?page=people&profile=clarissa_beveridge_widow_1837")
    route_link("Explore the focused Cobb–Beveridge family tree",
               "?page=tree&profile=clarissa_beveridge_widow_1837")
    first, second, third, fourth = st.tabs([
        "Clarissa's birth family", "Matthew's identity question",
        "Historical sources", "Next original documents"])

    with first:
        st.subheader("The maternal link into eighteenth-century Carver")
        st.write("A **1911 town-record compilation**, citing Carver vital records "
                 "on printed page 21, records Clarissa Cobb born 27 March 1786 "
                 "to Barnabas and Jerusha. **Philip L. Cobb's 1907 genealogy** "
                 "identifies that Clarissa with Capt. Matthew Beverage of Hope.")
        st.caption("These books are independent publications but the genealogical "
                   "account can depend on earlier writers such as Eaton. Two "
                   "published copies are not automatically two independent primary "
                   "record witnesses.")
        for id in ("clarissa-carver-born", "clarissa-hope-identity",
                   "maternal-grandparent-leads", "barnabas-carver-clerk"):
            _finding_card(next(f for f in data["findings"] if f["id"] == id), sources)
        st.warning("The named parents Barnabas and Jerusha are in the main family "
                   "tree via a sourced overlay. Ebenezer Cobb and Jerusha Cushman "
                   "are **future research candidates**, not linked as verified "
                   "grandparents. Clarissa is NOT automatically the biological "
                   "mother of Matthew's eight probate-identified children.")

    with second:
        st.subheader("Do the 1785 minor, the 1811 clerk, and the 1837 decedent match?")
        st.write("Name similarity and geography are insufficient to bridge these "
                 "record identities. This comparison documents the evidence for "
                 "each while preserving unresolved joins.")
        for candidate in data["identity_matrix"]:
            with st.container(border=True):
                st.markdown("**" + candidate["date"] + " · " + candidate["name"] + "**")
                st.caption(candidate["location"])
                st.write(candidate["evidence"])
                st.caption("Connection to 1837 estate: " + candidate["link_to_probate_matthew"])
                st.caption("Evidence limitation: " + candidate["limitation"])
        for id in ("matthew-fox-minor", "matthew-deeds", "fox-putnam-original-target"):
            _finding_card(next(f for f in data["findings"] if f["id"] == id), sources)
        route_link("Read the original-era Hope town-clerk research",
                   "?page=collection&view=hope-matthew")
        route_link("Read Matthew's 1837 court evidence and children",
                   "?page=collection&view=waldo-probate")

    with third:
        for source in data["sources"]:
            _source_card(source)

    with fourth:
        for target in sorted(data["original_retrieval"], key=lambda x: x["priority"]):
            with st.container(border=True):
                st.markdown("**" + str(target["priority"]) + ". " + target["target"] + "**")
                st.caption(target["repository"] + " · " + target["status"].replace("_", " "))
                st.write(target["expected"])
                route_link("Open source collection / finding aid", target["url"])
        st.info("No purchases, archival record requests, or external messages "
                "have been sent. A collection's availability is not proof of "
                "a specific Matthew deed or a parent-child relationship.")
