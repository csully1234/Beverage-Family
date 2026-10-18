"""Historical bridge casework: evidence to investigate, never fabricated tree edges.

This research layer is intentionally separate from people.json and relationship_index.
External archives are linked, not republished without permission.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import streamlit as st

from routing_ui import route_link

DATA = Path(__file__).resolve().parent / "data" / "phase16_ancestry_bridge_dossiers.json"

STATUS = {
    "published_family_claim_not_original_register": "Historical family report · original registers pending",
    "published_kinship_needs_original_bridge": "Historical kinship report · parentage not proven",
    "original_maps_cataloged_family_plot_unverified": "Original maps cataloged · family land not identified",
    "uncorroborated_compiled_tree_hypothesis": "Compiled-tree hypothesis · original evidence missing",
}


def load_ancestry_bridge_dossiers() -> list[dict]:
    records = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Ancestry investigation index must be an array")
    return records


def linked_dossiers(person_id: str, records: list[dict] | None = None) -> list[dict]:
    return [d for d in (records if records is not None else load_ancestry_bridge_dossiers())
            if person_id in d.get("person_ids", [])]


def render_ancestry_case(dossier: dict, people: Mapping[str, dict]) -> None:
    with st.container(border=True):
        st.markdown("**" + str(dossier["title"]) + "**")
        st.caption(str(dossier["period"]) + " · " +
                   STATUS.get(str(dossier["status"]), "Evidence status requires checking"))
        st.write(str(dossier["finding"]))
        st.caption("Evidence limit: " + str(dossier["limitations"]))
        for source in dossier.get("sources", []):
            route_link("Open evidence · " + str(source["title"]), str(source["url"]))
            st.caption("What this record establishes: " + str(source["claim"]))
            st.caption("Exact location: " + str(source["locator"]))
        st.markdown("**What would settle the question?**")
        for i, task in enumerate(dossier.get("next_originals", []), 1):
            st.write(str(i) + ". " + str(task))
        linked = [pid for pid in dossier.get("person_ids", []) if pid in people]
        if linked:
            st.caption("Existing linked profiles (not newly created ancestors):")
            for pid in linked:
                route_link(str(people[pid].get("full_name", pid)), "?page=people&profile=" + pid,
                           type="tertiary")


def render_ancestry_dossiers(people: Mapping[str, dict]) -> None:
    with st.expander("Open ancestry investigations · Matthew, Nathaniel and early Topsham"):
        st.write("These are historical clues whose original marriage, birth, deed or probate "
                 "records still need checking. They are kept visible without adding "
                 "unverified parents or properties to the family tree.")
        term = st.text_input("Search these investigations", key="ancestry_bridge_search",
                             placeholder="Matthew, Clarissa Cobb, Nathaniel, Topsham lot…").strip().casefold()
        records = load_ancestry_bridge_dossiers()
        matches = [case for case in records if not term or term in json.dumps(
            {key: case.get(key) for key in ("title", "finding", "limitations", "named_people",
                                           "period", "place", "type")},
            ensure_ascii=False).casefold()]
        st.caption(str(len(matches)) + " documented investigation" + ("" if len(matches)==1 else "s"))
        for case in matches:
            render_ancestry_case(case, people)
        if not matches:
            st.info("No cases matched; try a surname or different spelling.")


def render_person_bridge_casework(person_id: str, people: Mapping[str, dict]) -> None:
    records = linked_dossiers(person_id)
    if not records:
        return
    with st.expander(f"Historical ancestry questions connected to this relative · {len(records)}"):
        st.caption("A reference to a relative in a printed historical account is not a "
                   "newly verified parent or uncle in the genealogy chart.")
        for case in records:
            render_ancestry_case(case, people)
