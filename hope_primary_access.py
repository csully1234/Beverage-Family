"""Read-only source trail for Hope's 1820 original roll and 1813/1821 clerk votes.

These are document access leads. An indexed name or modern ledger transcription
cannot independently establish a historical person's identity or relationships.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from routing_ui import route_link, safe_external_url

FILE = Path(__file__).resolve().parent / "data" / "phase34_hope_original_reel_and_civic_votes.json"
EXPECTED = (
    ("hope-1820-original-roll-36", 1820, "digitized_original_roll_not_person_line"),
    ("hope-1813-collector-bond-vote", 1813, "municipal_ledger_transcription"),
    ("hope-1821-town-clerk-vote", 1821, "municipal_ledger_transcription"),
)


def load_hope_primary_access(path: Path = FILE) -> dict:
    """Load only attributed source excerpts; refuse invented manuscript readings."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise ValueError("Expected exactly one Hope primary-access research case")
    case = payload[0]
    records = case.get("cases")
    if not isinstance(records, list) or [
        (item.get("id"), item.get("year"), item.get("kind"))
        for item in records
    ] != list(EXPECTED):
        raise ValueError("Expected ordered original-reel and civic-vote source records")
    for record in records:
        if not all(record.get(key) for key in
                   ("source_title", "locator", "finding", "limits", "needs", "status", "date_label")):
            raise ValueError("Source attribution or evidence limits missing")
        if not safe_external_url(record.get("source_url")):
            raise ValueError("Missing safe source URL")
        if record.get("companion_url") and not safe_external_url(record["companion_url"]):
            raise ValueError("Unsafe companion URL")
        for flag in ("original_line_inspected", "manuscript_verified", "original_image_reproduced"):
            if record.get(flag) is not False:
                raise ValueError("An unpublished or unread original cannot be treated as verified")
        if "person_id" in record or "parents" in record or "children" in record:
            raise ValueError("Document access cards must not assert canonical genealogy")
    return case


def render_hope_primary_access() -> None:
    """Display complete cited external sources inside the existing family gate."""
    case = load_hope_primary_access()
    st.subheader("New original-reel access and local records, 1813–1821")
    st.write(case["summary"])
    st.caption(case["source_family_count_note"])
    st.warning("No original 1820 Mathew household row or age counts have been read. "
               "A modern town-record transcription is not a scanned manuscript. "
               "No 1785 Fox Islands or 1837 probate identity bridge is proved.")
    for item in case["cases"]:
        with st.container(border=True):
            st.markdown("**" + item["title"] + "**")
            st.caption(item["date_label"] + " · " + item["status"])
            st.write(item["finding"])
            st.caption("Source locator: " + item["locator"])
            st.caption("What this does not prove: " + item["limits"])
            route_link("Open source: " + item["source_title"], item["source_url"])
            if item.get("companion_url"):
                route_link("Compare published named-head transcription", item["companion_url"])
            with st.expander("Original-document verification still needed"):
                st.write(item["needs"])
                st.caption("Original manuscript line independently inspected: No. "
                           "Original census household demographic tallies: not transcribed. "
                           "No new source image has been republished.")
    st.caption("All items remain separate from person's recorded ancestry. "
               "Consult the full family source index to compare with the dated clerk, "
               "Fox Islands petition and 1837 probate evidence.")
