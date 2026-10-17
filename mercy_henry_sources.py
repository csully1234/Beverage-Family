"""Curated Mercy Beveridge / James Henry evidence trails, without invented kinship."""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
from routing_ui import route_link

FILE = Path(__file__).resolve().parent / "data" / "phase12_mercy_henry_sources.json"


def load_mercy_henry_sources() -> list[dict]:
    if not FILE.is_file():
        return []
    entries = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Mercy/James historic source file must be an array")
    return sorted(entries, key=lambda e: (int(e.get("year", 9999)), e["id"]))


def render_mercy_henry_evidence() -> None:
    st.subheader("Mercy Beveridge Henry: a newly documented name")
    st.write("Two historical records narrow this mystery: an 1831 grave record "
             "names Mercy Beveridge as James Henry's wife, while an 1878 family "
             "history *suggests* a 1776 wedding. Her Beveridge birth family has "
             "not yet been established.")
    st.caption("The 1930 gravestone transcription and later cemetery index likely "
               "describe the same stone. They should not be counted as two "
               "independent certificates. These research leads do not modify "
               "the family tree.")
    for case in load_mercy_henry_sources():
        with st.container(border=True):
            st.markdown("**" + str(case["title"]) + "**")
            st.caption(str(case["status"]))
            st.write(str(case["summary"]))
            route_link("Read the published source", str(case["source_url"]))
            with st.expander("Compare sources and missing original records"):
                for source in case.get("supporting_sources", []):
                    route_link(str(source["title"]), str(source["url"]))
                    st.caption(str(source["role"]))
                st.info("Evidence limit: " + str(case["limits"]))
                st.write("Next original: " + str(case["next_record"]))
