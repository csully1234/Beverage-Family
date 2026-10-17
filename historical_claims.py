"""Modern source annotations to contested legacy events (without rewriting them)."""
from __future__ import annotations

import json
from pathlib import Path
import streamlit as st
from routing_ui import route_link

FILE = Path(__file__).resolve().parent / "data" / "phase8_event_evidence.json"


def event_source_annotations(event_id: str) -> list[dict]:
    if not FILE.is_file():
        return []
    records = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Event evidence must be an array")
    return [item for item in records if item.get("event_id") == event_id]


def render_event_source_review(event_id: str) -> None:
    rows = event_source_annotations(event_id)
    for entry in rows:
        with st.expander("What the original evidence actually says", expanded=(
            event_id == "event_marriage_james_jr_jean_white_1749"
        )):
            st.markdown("**" + str(entry.get("headline", "Evidence clarification")) + "**")
            st.write(entry.get("assessment", ""))
            for source in entry.get("sources", []):
                route_link(str(source.get("title", "Examine historical source")),
                           str(source.get("url", "")))
                st.caption(str(source.get("supports", "")))
            st.caption("Still needed: " + str(entry.get("original_record_needed", "An original record")))


def reviewed_event_presentation(event: dict) -> dict:
    """Return safer *display copy*, never rewriting the archived event record.

    The original event and source list remain immutable. A claim can be
    downgraded from a recorded marriage to its actual surviving evidence
    without silently changing historical source data or person relations.
    """
    rendered = dict(event)
    for note in event_source_annotations(str(event.get("id", ""))):
        if note.get("display_title"):
            rendered["title"] = note["display_title"]
        if note.get("display_summary"):
            rendered["description"] = note["display_summary"]
        if note.get("display_evidence_status"):
            rendered["evidence_status"] = note["display_evidence_status"]
    return rendered
