"""Early Fox Islands primary-source bridge: actual 1785–1786 pages to 1819 testimony.

Source-first visitor UI. This module does not add or modify people, parentage,
land coordinates, or genealogical relationships. The 1819 institutional images
remain at Maine Historical Society, per host usage restrictions.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import streamlit as st
from routing_ui import route_link

PATH = Path(__file__).resolve().parent / "data" / "phase49_fox_islands_source_bridge.json"
SOURCE_IDS = {"mass-original", "benjamin-1819", "1790-thomas", "1800-origins", "putnam-1786"}
YEARS = (1765, 1785, 1786, 1790, 1800, 1819)


def load_fox_source_bridge(path: Path = PATH) -> dict:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError("Expected one Fox Islands source-bridge case")
    data = records[0]
    sources = data["sources"]
    if len(sources) != 5 or {s["id"] for s in sources} != SOURCE_IDS:
        raise ValueError("Five independently described source groups required")
    observations = data["observations"]
    if tuple(o["year"] for o in observations) != YEARS:
        raise ValueError("Early Fox Islands historical order changed")
    for obs in observations:
        if not obs["source_ids"] or any(i not in SOURCE_IDS for i in obs["source_ids"]):
            raise ValueError("Unsourced historical observation")
        if not obs["limits"] or not obs["evidence"]:
            raise ValueError("Each record requires explicit evidence limitations")
    letter = data["letter_analysis"]
    if (letter["manuscript_pages"] != 2 or letter["manuscript_date"] != "1819-12-20"
            or letter["existing_site_source_id"] != "src_vinalhaven_manuscript_1819"):
        raise ValueError("Incorrect original letter provenance or duplicate source identity")
    if any(not item["qualification"] for item in letter["selected_facts"]):
        raise ValueError("Contextual 1819 figures must retain explicit caveats")
    if not data["no_tree_edges_modified"] or not data["no_outbound_messages_sent"]:
        raise ValueError("Bridge project may not assert unverified family connections")
    return data


def bridge_csv(data: dict | None = None) -> str:
    data = data or load_fox_source_bridge()
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=(
        "id", "year", "title", "statement", "evidence", "limits", "source_ids"
    ))
    writer.writeheader()
    for entry in data["observations"]:
        writer.writerow({name: (", ".join(entry[name]) if name == "source_ids"
                              else entry.get(name, "")) for name in writer.fieldnames})
    return handle.getvalue()


def render_fox_source_bridge() -> None:
    data = load_fox_source_bridge()
    sources = {source["id"]: source for source in data["sources"]}
    st.subheader("From the 1785 settlers' petition to Benjamin Beverage's 1819 account")
    st.write(
        "These sources can be read together without pretending they are the "
        "same person's records: the 1785–1786 manuscript petitions and "
        "legislation, a printed summary of the 1790 census, the unusual 1800 "
        "migration-origin research lead, and a surviving 1819 island letter."
    )
    chronology, letter_tab, research = st.tabs((
        "Early island chronology", "Benjamin's original letter · 1819",
        "Evidence & next archive targets"
    ))
    with chronology:
        for obs in data["observations"]:
            with st.container(border=True):
                st.markdown("**" + str(obs["year"]) + " · " + obs["title"] + "**")
                st.write(obs["statement"])
                st.caption("Evidence class: " + obs["evidence"].replace("_", " "))
                st.caption("Do not infer: " + obs["limits"])
                for source_id in obs["source_ids"]:
                    source = sources[source_id]
                    route_link("Source: " + source["label"], source["url"], type="tertiary")
        st.download_button(
            "Download complete six-event documentary comparison (CSV)",
            bridge_csv(data),
            file_name="fox-islands-settlement-primary-source-concordance.csv",
            mime="text/csv", key="fox-early-island-bridge-download",
        )
    with letter_tab:
        letter = data["letter_analysis"]
        st.markdown("**December 20, 1819 · written and signed Benjamin Beverage**")
        st.caption("Maine Historical Society · William D. Williamson Papers, Coll. 62 · item 20801")
        st.write(
            "This rare two-page handwritten letter was already in the site's "
            "source catalog. The original page images and their transcription "
            "were subsequently examined together. It now has a dedicated "
            "historical commentary that distinguishes Benjamin's contemporary "
            "observations from facts independently verified by other records."
        )
        st.info(
            "The manuscript is held by the Maine Historical Society. "
            "Read its photographs and full original transcription at the host; "
            "their scanned images are not mirrored on this site."
        )
        route_link("View the original handwritten letter · Maine Memory Network",
                   sources["benjamin-1819"]["url"])
        route_link("Read the host's complete two-page transcription alongside the images",
                   sources["benjamin-1819"]["transcript_url"])
        st.write(
            "Benjamin mentions settlement in 1765 and describes the 1785 "
            "survey, the Massachusetts grant, the town's land values, vessels, "
            "schools and religious life. He closes by asking that his own "
            "name not be cited as authority—a useful reminder to preserve "
            "his account as testimony, not automatic proof."
        )
        for fact in letter["selected_facts"]:
            with st.expander(fact["topic"]):
                st.write(fact["detail"])
                st.caption("Evidence limit: " + fact["qualification"])
        st.warning(
            "Benjamin's account rounds the islands' size to about 17,000 acres; "
            "the March 1786 resolution instead uses the more specific "
            "16,527-acre survey figure. Do not silently substitute one source's "
            "measurement for the other's or treat a rounded figure as error."
        )
        st.caption(
            "Already indexed in the site's canonical archive source register as "
            + letter["existing_site_source_id"] + ". No duplicate source "
            "identity or new family-tree relationship was introduced."
        )
    with research:
        st.write(
            "The critical gaps are individual settlers' declared arrival "
            "years, named land conveyances, and the original 1800 census "
            "migration-origin responses. All are still unresolved."
        )
        for task in data["research_queue"]:
            with st.container(border=True):
                st.markdown("**Priority " + str(task["priority"]) + ": " + task["title"] + "**")
                st.caption("Archive target: " + task["target"])
                st.write(task["goal"])
        for source in data["sources"]:
            with st.expander(source["label"]):
                st.caption("Access: " + source["access"])
                st.caption("Limit: " + source["limits"])
                route_link("Open holding archive or publication", source["url"], type="tertiary")
        route_link("Review existing Matthew of Hope original probate trail",
                   "?page=collection&view=waldo-probate", type="tertiary")
        st.caption("Archival requests are drafts only. No outgoing correspondence has been sent.")
