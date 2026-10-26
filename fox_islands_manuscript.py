"""Primary-manuscript register for the newly supplied 1785/1786 Fox Islands leaves.

A selected-reading edition, NOT a complete diplomatic transcription or a claim
that the original TIFF pixels are served by GitHub. The 1785 minor is NOT
automatically linked to any canonical genealogy profile.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import streamlit as st

from routing_ui import route_link

DATA_FILE = Path(__file__).resolve().parent / "data" / "phase47_fox_islands_original_manuscripts.json"
EXPECTED_LEAVES = ("petition-1", "petition-2", "petition-3", "petition-4",
                   "resolve-1", "resolve-2", "resolve-3")
EXPECTED_PEOPLE = ("James Beveridge", "Thomas Beveridge", "Matthew Beveridge")


def load_fox_manuscripts(path: Path = DATA_FILE) -> dict:
    """Validate that a direct manuscript name is not accidentally promoted to kinship."""
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValueError("Expected a single versioned manuscript collection")
    record = entries[0]
    if tuple(row["id"] for row in record["leaves"]) != EXPECTED_LEAVES:
        raise ValueError("Seven original leaves required, in canonical manuscript order")
    if record["manuscripts_locally_available"] != len(EXPECTED_LEAVES):
        raise ValueError("Manifest and manuscript leaf count differ")
    if record["manuscript_images_status"] != "original_scans_received_and_examined_not_hosted_in_repository":
        raise ValueError("The site must describe image-hosting status accurately")
    if record["settler_count_in_resolve"] != 72 or record["survey_acres"] != 16527:
        raise ValueError("Historical figure transcription changed without review")
    if record["eligibility_date"] != "1784-01-01":
        raise ValueError("Original grant cutoff changed without review")
    if tuple(row["name"] for row in record["key_findings"]) != EXPECTED_PEOPLE:
        raise ValueError("Original manuscript name index changed without review")
    ids = [row["id"] for row in record["key_findings"]]
    if len(ids) != len(set(ids)) or any(row["leaf"] != 3 or row["document"] != "petition"
                                      for row in record["key_findings"]):
        raise ValueError("Name mentions must remain separately identified on petition leaf 3")
    if any(row["full_transcription_verified"] for row in record["leaves"]):
        raise ValueError("Unverified selected passages must not be labelled complete transcriptions")
    return record


def name_mentions(data: dict | None = None) -> list[dict]:
    """These are document observations, never canonical person relationships."""
    return list((data or load_fox_manuscripts())["key_findings"])


def manuscript_csv(data: dict | None = None) -> str:
    data = data or load_fox_manuscripts()
    out = io.StringIO()
    fields = ("id", "group", "leaf", "label", "description",
              "excerpt", "confidence", "source_file")
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for leaf in data["leaves"]:
        writer.writerow({name: leaf.get(name, "") for name in fields})
    return out.getvalue()


def render_original_manuscripts() -> None:
    data = load_fox_manuscripts()
    st.subheader("NEW · Original 1785 petition and 1786 legislative resolve")
    st.write(
        "Seven Massachusetts Archives manuscript leaves were supplied as "
        "high-resolution scans and directly examined: four petition leaves "
        "and three resolution leaves. The accompanying annotations below "
        "are **selected manuscript readings**, not a complete verified "
        "word-for-word diplomatic transcription."
    )
    st.info(
        "The scans are held in the project research package but have **not yet "
        "been uploaded to the site's static image collection**. This online "
        "record publishes the verified names, document locations and selected "
        "readings; it does not pretend to display unavailable images."
    )
    a, b, c = st.columns(3)
    a.metric("Original manuscript leaves examined", 7)
    b.metric("Named Beveridge mentions", 3)
    c.metric("Identified family relationships", 0)
    st.caption("Original dossier: " + data["archival_identifier"])
    st.markdown("**Directly legible Beveridge entries, petition leaf 3**")
    for mention in name_mentions(data):
        with st.container(border=True):
            st.markdown("**" + mention["name"] + "**")
            st.caption("Petition leaf " + str(mention["leaf"]) + " · " + mention["column"] + " column")
            st.write(mention["evidence"])
            st.caption("Identity limit: " + mention["identity_status"])
    st.warning(
        "These are names on a contemporary petition list, not proof of "
        "three individually signed declarations, a family group, specific "
        "land parcels, or Matthew's identity with the 1837 Hope decedent."
    )

    st.markdown("**What the 1786 resolution actually says**")
    st.write(
        "The legislative record refers to a surveyed total of **16,527 acres** "
        "and **72 settlers before January 1, 1784**. The settlement-date "
        "cutoff relates to eligibility for the conditional grant, not proof "
        "that each of the three named Beveridges personally met the condition."
    )
    st.caption(
        "Later histories' count of 75 petitioning inhabitants is a different "
        "measurement from the resolve's count of 72 early settlers."
    )
    by_id = {row["id"]: row for row in data["leaves"]}
    selected = st.selectbox(
        "Read the manuscript page notes",
        list(EXPECTED_LEAVES),
        format_func=lambda key: by_id[key]["label"],
        key="fox-1785-manuscript-leaf-selector",
    )
    row = by_id[selected]
    with st.container(border=True):
        st.markdown("**" + row["label"] + "**")
        st.write(row["description"])
        st.code(row["excerpt"], language=None)
        st.caption("Reading quality: " + row["confidence"])
        st.caption("Original supplied image: " + row["source_file"])
        st.caption("Complete verified diplomatic transcription: No")
    st.download_button(
        "Download seven-page documentary inventory (CSV)",
        manuscript_csv(data), file_name="fox-islands-manuscripts-1785-1786.csv",
        mime="text/csv", key="fox-1785-manuscript-export"
    )
    with st.expander("Primary and supporting archival source citations"):
        for source in data["sources"]:
            st.markdown("**" + source["title"] + "**")
            st.caption(source["type"])
            if source.get("url"):
                route_link("Open archival or scholarly source", source["url"], type="tertiary")
    with st.expander("Unresolved document work and family relationships"):
        for item in data["outstanding"]:
            st.write("• " + item)
        route_link(
            "Compare the Hope 1837 probate and identity evidence",
            "?page=collection&view=waldo-probate",
            type="tertiary",
        )
