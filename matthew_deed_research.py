"""Probate court-child designations and historically grounded Hope deed trail.

The extracts are partial review transcriptions/abstracts, NEVER an assertion
that all scanned court pages have been diplomatically transcribed. No map
coordinates are generated from an unverified former grantor's name.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from routing_ui import route_link

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "phase23_probate_deed_trail.json"


def load_probate_deed_trail() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("Expected one source-attributed probate deed-trail report")
    data = payload[0]
    if len(data.get("principal_people", [])) != 10 or len(data.get("land_clues", [])) != 5:
        raise ValueError("Court family or land leads incomplete")
    return data


def recorded_children(data: dict | None = None) -> list[dict]:
    data = data if data is not None else load_probate_deed_trail()
    return [person for person in data["principal_people"] if person["role"].startswith("named child")]


def priority_deed_targets(data: dict | None = None) -> list[dict]:
    data = data if data is not None else load_probate_deed_trail()
    return data["land_clues"]


def render_court_children() -> None:
    data = load_probate_deed_trail()
    st.subheader("Eight people the court explicitly calls Matthew's children")
    st.write("The October 1837 partition warrant (received scan 09) says the real estate "
             "is to be divided **among his children** and names eight people. "
             "The earlier review only recorded them as heirs. The court's wording "
             "supports placing these children under Matthew in the family tree.")
    st.caption("It does NOT identify their mothers, prove exact birth dates or "
               "connect Matthew to Capt. Thomas Beverage or the 1785 Fox Islands minor.")
    route_link("Read the original source's metadata and court-child wording (scan 09)",
               "?page=collection&view=waldo-probate&scan=9")
    route_link("Open Matthew's new sourced profile in the focused tree",
               "?page=tree&profile=matthew_beveridge_hope_1837")
    route_link("View Matthew's position on the full family map",
               "?page=full-tree&profile=matthew_beveridge_hope_1837")
    for person in recorded_children(data):
        with st.container(border=True):
            st.markdown("**" + person["label"] + "**")
            st.caption("Court-described child · review scans " +
                       ", ".join(str(n).zfill(2) for n in person["evidence_scans"]))
            if person.get("limitation"):
                st.caption("Identity qualification: " + person["limitation"])
            route_link("Open the probate-sourced person profile",
                       "?page=people&profile=" + quote(person["person_id"], safe=""))


def render_deed_targets() -> None:
    data = load_probate_deed_trail()
    st.subheader("Trace Matthew's 1837 Hope property back to the original deeds")
    st.write("The appraisers describe a homestead plus several additional lots. "
             "Their report seems to remember earlier sellers, providing names "
             "worth testing against historic grantee and grantor indexes. "
             "**No specific deed has yet been located or authenticated**, and "
             "no parcel has been matched to a modern address.")
    st.caption("Source: estate appraisers' report, received scan 02. "
               "The spellings and lot figures below are working readings, "
               "not final deed transcriptions.")
    route_link("Read the scan 02 provenance and document classification",
               "?page=collection&view=waldo-probate&scan=2")
    for clue in priority_deed_targets(data):
        with st.container(border=True):
            st.markdown("**" + clue["label"] + "**")
            st.write(clue["reading"])
            st.caption("Review confidence: " + clue["certainty"])
            st.caption("Next verification: " + clue["search_strategy"])
    st.subheader("Verified archive search paths")
    for lead in data["source_leads"]:
        with st.expander(lead["repository"] + " · " + lead["date_scope"]):
            st.write(lead["detail"])
            st.caption(lead["proof_status"])
            route_link("Open this historic deed or map research resource", lead["url"])
    st.warning("A registry's published index collection proves where deeds might "
               "be found. It does not prove that Matthew acquired any particular "
               "parcel from a named person until the specific deed is inspected.")


def render_probate_excerpts() -> None:
    data = load_probate_deed_trail()
    st.subheader("Working transcription and reading notebook")
    st.write("High-confidence short extracts from directly reviewed 1837 court scans "
             "are separated from interpretive abstracts. Ellipses or bracketed "
             "readings must not be silently treated as original manuscript text.")
    st.caption("This is not a full diplomatic transcription of all 30 unique images. "
               "It highlights the passages most likely to resolve parentage and deeds.")
    for excerpt in data["transcriptions"]:
        with st.container(border=True):
            st.markdown("**Review scan " + str(excerpt["scan"]).zfill(2) +
                        " · " + excerpt["type"].replace("_", " ") + "**")
            st.caption(str(excerpt["date"]) + " · " + excerpt["status"])
            st.write(excerpt["text"])
            st.caption("Reading note: " + excerpt["note"])
            route_link("Open source-scan provenance", "?page=collection&view=waldo-probate&scan=" +
                       str(excerpt["scan"]))
    with st.expander("Outstanding document review and original-deed requests"):
        for question in data["open_questions"]:
            st.write("• " + question)
    st.download_button(
        "Download the research readings and deed search plan",
        json.dumps(data, indent=2, ensure_ascii=False),
        file_name="matthew-hope-probate-deed-research.json",
        mime="application/json",
        key="phase23_deed_research_download",
    )
