"""Visitor-friendly archival associations kept outside genealogical edges."""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
from routing_ui import route_link

PATH = Path(__file__).resolve().parent / "data" / "documented_associations.json"


def load_documented_associations() -> list[dict]:
    if not PATH.is_file():
        return []
    rows = json.loads(PATH.read_text(encoding="utf-8"))
    return rows if isinstance(rows, list) else []


def associations_for_person(person_id: str) -> list[dict]:
    return [row for row in load_documented_associations()
            if row.get("person_id") == person_id]


def render_documented_associations(person_id: str) -> None:
    items = associations_for_person(person_id)
    if not items:
        return
    st.subheader("Documented companions and historical associations")
    st.caption("These relationships preserve what sources report, without "
               "implying legal marriage, shared ancestry, or other unproved links.")
    for row in items:
        with st.container(border=True):
            st.markdown("**" + row["associated_name"] + "**")
            st.write(row.get("association_type", "Historical association"))
            st.write(row.get("description", ""))
            st.caption(row.get("status", "Original evidence pending"))
            for source in row.get("sources", []):
                route_link(source.get("title", "Inspect published evidence"),
                           source.get("url", ""))
