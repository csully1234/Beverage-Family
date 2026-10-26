"""Fox Islands archive reader: directly examined 1785/1786 originals plus legacy access register.

October 26 manuscript scans supersede Phase 30's older 'not obtained' status for
the Massachusetts petition/resolve; the separate Putnam report is outstanding.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from routing_ui import route_link
from fox_islands_manuscript import render_original_manuscripts

SOURCE_FILE = Path(__file__).resolve().parent / "data" / "phase30_fox_islands_original_source_access.json"
DIGITIZED = ("digitized_historical_cartographic_copy",)
PUBLISHED = ("digitized_published_secondary_transcription",)
MANUSCRIPT = ("located_original_document_not_inspected",)


def load_fox_islands_sources(path: Path = SOURCE_FILE) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("Expected one Phase 30 original-source provenance case")
    data = payload[0]
    ids = [source["id"] for source in data["sources"]]
    if len(ids) != len(set(ids)) or len(ids) < 6:
        raise ValueError("Fox Islands source IDs must be unique and complete")
    for source in data["sources"]:
        if not all(source.get(field) for field in (
            "title", "repository", "identifier", "category", "url",
            "inspected", "establishes", "does_not_establish", "request"
        )):
            raise ValueError("Incomplete archive source: " + source["id"])
    return data


def original_access_register(data: dict | None = None) -> dict[str, list[dict]]:
    data = data if data is not None else load_fox_islands_sources()
    result = {"digitized_maps": [], "original_requests": [], "published_context": []}
    for row in data["sources"]:
        if row["category"] in DIGITIZED:
            result["digitized_maps"].append(row)
        elif row["category"] in MANUSCRIPT:
            result["original_requests"].append(row)
        else:
            result["published_context"].append(row)
    for items in result.values():
        items.sort(key=lambda row: (row["priority"], row["id"]))
    return result


def request_note(source: dict) -> str:
    """Copyable research specifications; not a message sent to an archivist."""
    return "\n".join([
        "Historical record inquiry (draft only — not sent)",
        "Holding institution: " + str(source["repository"]),
        "Locator: " + str(source["identifier"]),
        "Purpose: Determine original source contents and whether any "
        "Matthew Beveridge identity claim is actually supported.",
        "Requested material: " + str(source["request"]),
        "Please advise original folios, any photocopy fees or permissions, "
        "and whether a public catalog scan exists.",
        "Do not assume the 1785 minor is the Hope 1837 decedent.",
    ])


def _source_card(source: dict) -> None:
    with st.container(border=True):
        st.markdown("**" + source["title"] + "**")
        st.caption(source["date"] + " · " + source["repository"])
        st.caption("Exact locator: " + source["identifier"])
        st.write(source["establishes"])
        st.caption("What was examined: " + source["inspected"])
        st.caption("Does NOT prove: " + source["does_not_establish"])
        route_link("Open the holding institution's catalog or source", source["url"])
        with st.expander("Original document retrieval or examination checklist"):
            st.write(source["request"])
            if source["category"] in MANUSCRIPT:
                st.code(request_note(source), language=None)
                st.caption("This is a draft retrieval specification. "
                           "No archivist was contacted, no purchase was made, and "
                           "no unpublished scan was added to the website.")


def render_fox_originals() -> None:
    data = load_fox_islands_sources()
    grouped = original_access_register(data)
    st.title("Fox Islands, 1785–1786: the original-document trail")
    render_original_manuscripts()
    st.divider()
    st.subheader("Historical source-access register · 19 October 2026")
    st.caption("This register documents the earlier retrieval state. Its assertion "
               "that the manuscript was unavailable was superseded when seven "
               "original manuscript scans were supplied on October 26.")
    st.write("In the archived October 19 source-access study, island papers were traced to "
             "plan books and two manuscript collections. Those records are not "
             "interchangeable: **a surveyed coastline, an original petition, a "
             "claimant's settlement statement, and a later printed history are "
             "different types of evidence.**")
    st.warning("No source in this collection proves that the Matthew Beveridge "
               "called a minor in the original 1785 petition became Matthew of "
               "Hope who died in 1837. His parents and link to Capt. Thomas "
               "remain unverified.")
    a,b,c = st.columns(3)
    a.metric("Digitized archival map/list records", len(grouped["digitized_maps"]))
    b.metric("Specific original paper targets", len(grouped["original_requests"]))
    c.metric("Verified Matthew parentage documents", 0)
    st.caption("These figures count **different catalog entries**, not "
               "independent witnesses to one person's ancestry. Two map "
               "entries may reproduce the same historic plan.")
    tabs = st.tabs(("Digitized plans", "Original manuscripts to obtain",
                    "Published records & access", "Three Matthews identity test"))
    with tabs[0]:
        st.subheader("Start with the state archives' original-era plan records")
        st.caption("Maine State Archives provides historic scans or previews at "
                   "these specific hosted catalog entries; full manuscript "
                   "names and map features have not been independently read.")
        for row in grouped["digitized_maps"]:
            _source_card(row)
    with tabs[1]:
        st.subheader("Exact archival shelf references, not merely a web search")
        st.write("The original October 19 register located the Massachusetts "
                 "petition and the Maine Putnam report. The Massachusetts "
                 "petition and resolution scans were supplied and examined on "
                 "October 26. The separate Putnam report is still outstanding.")
        for row in grouped["original_requests"]:
            _source_card(row)
    with tabs[2]:
        st.subheader("Keep nineteenth-century transcriptions separate")
        for row in grouped["published_context"]:
            _source_card(row)
        st.caption("The 1889 book's transcription names a Matthew Beveridge "
                   "as a minor alongside separately listed James and Thomas "
                   "Beveridge. Their appearance on one settler list does not "
                   "establish siblings or any later identity.")
    with tabs[3]:
        st.subheader("What would actually join these historical identities?")
        for row in data["identity_status"]:
            with st.container(border=True):
                st.markdown("**" + row["name"] + "**")
                st.caption(row["current_link"])
        st.write("An original land claim with an identifiable lot and later "
                 "conveyance, a signed petition naming guardians/parents, or "
                 "a matching Hope deed or contemporary marriage record "
                 "could establish a defensible bridge.")
        st.caption("Without such evidence, the existing four branches remain "
                   "separate in the family tree and no new parent-child edge "
                   "is introduced.")
        route_link("See the full-family relationship evidence audit",
                   "?page=collection&view=integrity")
        route_link("Read Matthew's original 1837 probate research",
                   "?page=collection&view=waldo-probate")
        route_link("Examine the Hope town-clerk record trail",
                   "?page=collection&view=hope-matthew")
