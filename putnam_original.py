"""Visitor-facing record of the newly supplied Putnam settlement list.

This is a source-reading exhibit, not a modification of canonical ancestors.
The uploaded eight-page PDF is preserved by the user and is NOT served here.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import streamlit as st
from routing_ui import route_link

FILE = Path(__file__).resolve().parent / "data" / "phase50_putnam_original_settlement_statement.json"


def load_putnam_original(path: Path = FILE) -> dict:
    collection = json.loads(path.read_text(encoding="utf-8"))
    if len(collection) != 1:
        raise ValueError("Expected one versioned Putnam source case")
    row = collection[0]
    if row["pdf_page_count"] != 8 or row["original_uploaded_file"] != "4-29462-F012.pdf":
        raise ValueError("Unexpected original Putnam manuscript edition")
    if len(row["page_inventory"]) != 8 or [x["pdf_page"] for x in row["page_inventory"]] != list(range(1, 9)):
        raise ValueError("Eight ordered pages must be cataloged")
    obs = row["observation"]
    if (obs["name_as_written"] != "Thomas Beverage"
            or obs["duration_as_written"] != "15"
            or obs["pdf_page"] != 7):
        raise ValueError("The Thomas source reading changed without original review")
    if row["digital_facsimile_hosted_publicly"] or not row["no_new_relationships"]:
        raise ValueError("This edition cannot claim image hosting or added genealogy edges")
    if row["full_diplomatic_transcription_verified"]:
        raise ValueError("No complete paleographic transcript is verified")
    if len(row["uploaded_pdf_sha256"]) != 64:
        raise ValueError("Original file checksum must be preserved")
    return row


def putnam_csv(case: dict | None = None) -> str:
    case = case or load_putnam_original()
    event = case["observation"]
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=[
        "name_as_written", "duration_as_written", "unit", "interpreted_settlement_year",
        "precision", "pdf_page", "candidate_link_status", "source_file_sha256"
    ])
    writer.writeheader()
    writer.writerow({**{key: event.get(key, "") for key in writer.fieldnames},
                     "source_file_sha256": case["uploaded_pdf_sha256"]})
    return out.getvalue()


def render_putnam_original() -> None:
    case = load_putnam_original()
    obs = case["observation"]
    st.subheader("New original · Thomas Beverage's reported settlement")
    st.write(
        "An eight-page scan headed **Description of the Quality of the Land Surveyed "
        "for the Commonwealth of Massachusetts in the County of Lincoln 1785** "
        "names Rufus Putnam, Jonathan Stone, Samuel Titcomb and John Mathews. "
        "It contains a December 16, 1785 signature and a later supplementary "
        "settlers' list signed in Boston on March 18, 1786."
    )
    st.caption("Supplied document: 4-29462-F012.pdf · Page 7 of 8 · "
               "Original manuscript page scanned, not a later printed genealogy")
    left, middle, right = st.columns(3)
    left.metric("Named settler", "Thomas Beverage")
    middle.metric("Time when settled", "15 years")
    right.metric("Approximate year", "c. 1771")
    st.write(
        "Under the source's **Names / Time when Settled** columns, the Fox Islands "
        "entry reads **Thomas Beverage — 15**. Counting backward from the "
        "March 1786 supplementary signing suggests settlement around **1771**. "
        "This is a reported duration, not a dated arrival certificate."
    )
    st.warning(
        "Identity caution: this Thomas could be the Thomas named in the 1785 "
        "petition and the Thomas Beverege household enumerated in 1790, but "
        "a matching name in the same area does not prove those are the same "
        "individual. Neither age, birthplace, parents, land title, nor any "
        "new parent-child relationship is established by this document."
    )
    st.caption("Other similarly spelled manuscript names have not been assigned "
               "to the Beveridge family without independent verification.")
    with st.expander("Read the source's eight-page inventory"):
        for leaf in case["page_inventory"]:
            st.write("**PDF page " + str(leaf["pdf_page"]) + ":** " + leaf["description"])
    with st.expander("Document provenance and source limitations"):
        st.write("Original PDF SHA-256: " + case["uploaded_pdf_sha256"])
        st.write("Report title: " + case["original_document_heading"])
        st.write("The PDF appears related to the separately cited March 18, 1786 "
                 "Putnam report held in the Maine State Archives, Box 001; "
                 "the physical archive identifier for the supplied scan has "
                 "not independently been confirmed.")
        st.write("The eight-page original PDF was supplied for this research. "
                 "It is not currently hosted in the public GitHub repository; "
                 "this site presents attributed findings only.")
        for lead in case["next_verification"]:
            st.write("• " + lead)
    st.download_button("Download the Thomas settlement entry (CSV)", putnam_csv(case),
                       file_name="thomas-beverage-1786-putnam-settlement.csv",
                       mime="text/csv", key="putnam-1786-entry-csv")
    route_link("Compare the 1790 Thomas household and early islands atlas",
               "?page=collection&view=source-expedition&early-islands=1",
               type="tertiary")
