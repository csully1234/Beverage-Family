"""Curated eighteenth-century Maine record trails. These do not create people or tree edges."""
from __future__ import annotations

import json
from pathlib import Path
import streamlit as st
from routing_ui import route_link

RECORDS = Path(__file__).resolve().parent / "data" / "phase10_early_maine_records.json"


def load_early_maine_record_leads() -> list[dict]:
    """Read editorial records with stable IDs and exact cited-source limitations."""
    if not RECORDS.is_file():
        return []
    data = json.loads(RECORDS.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Early Maine record index must contain an array")
    return sorted(data, key=lambda item: (int(item.get("year", 9999)), item.get("id", "")))


def render_early_maine_source_trail() -> None:
    """Keep the history engaging while showing what each surviving record can prove."""
    records = load_early_maine_record_leads()
    st.subheader("Follow the earliest mainland clues")
    st.write("A marriage intention, an early town map, settler names and a Revolutionary "
             "War roster provide possible connections between Topsham and North Haven. "
             "Explore the printed sources before drawing family relationships.")
    st.caption("No original deed or muster image has yet been authenticated for these "
               "named people; locations are historical context, not home addresses or "
               "surveyed modern property lines.")
    query = st.text_input("Find a name or topic in these early records",
                          placeholder="James, Samuel, Robert, map, 1776…",
                          key="early_maine_sources_search").strip().casefold()
    filtered = [item for item in records
                if not query or query in " ".join((
                    str(item.get("title", "")), str(item.get("summary", "")),
                    str(item.get("year", "")), str(item.get("kind", ""))
                )).casefold()]
    st.caption(f"{len(filtered)} cited historical leads")
    for entry in filtered:
        with st.container(border=True):
            stamp = str(entry.get("date") or entry["year"])
            st.markdown("**" + stamp + " · " + str(entry["title"]) + "**")
            st.write(str(entry["summary"]))
            st.caption("Evidence: " + str(entry["status"]))
            route_link("Read the source — " + str(entry["source_title"]),
                       str(entry["source_url"]))
            linked = entry.get("related_existing_event_id")
            if linked:
                route_link("See the following Topsham civic event on the timeline",
                           "?page=timeline&event=" + str(linked))
            with st.expander("What would prove this family connection?"):
                st.write(str(entry["next_record"]))
                st.caption(str(entry["person_status"]))


JAMES_CHAIN = RECORDS.with_name("phase11_james_record_chain.json")


def load_james_record_chain() -> list[dict]:
    """Chronological published attestations, NOT pre-joined person identities."""
    if not JAMES_CHAIN.is_file():
        return []
    rows = json.loads(JAMES_CHAIN.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Early James identity comparison must be an array")
    return rows


def render_james_identity_comparison() -> None:
    """Show six distinct sources without assuming all James mentions mean one man."""
    records = load_james_record_chain()
    if not records:
        return
    st.subheader("Which James Beveridge was which?")
    st.write("Six published records contain the name James between 1723 and 1764. "
             "Their chronology is useful, but matching a name is not proof "
             "that all six describe one individual or even the same household.")
    st.caption("Each entry below is a SOURCE SIGHTING. It does not create or "
               "change a family tree person, marriage, parent or land record.")
    for item in records:
        with st.container(border=True):
            st.markdown("**" + item["date"] + " · " + item["record"] + "**")
            st.caption(item["place"])
            st.write(item["proof"])
            route_link("Inspect the published record", item["source_url"])
            st.caption("Connection still unresolved: " + item["link_status"])
