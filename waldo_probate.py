"""Source-first, copyright-aware browser for the supplied 1837 Waldo probate packet.

The user received scanned court papers from a probate office.  The public
repository contains a navigational manifest and limited research summaries,
NOT the supplied image binaries; approval to redistribute those copies must
be independently confirmed.  Review-page IDs are not the court's folio order.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import streamlit as st

from routing_ui import route_link
from matthew_deed_research import (render_court_children, render_deed_targets,
                                   render_probate_excerpts)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "phase22_matthew_waldo_probate.json"
MEDIA_ROOT = (ROOT / "static" / "approved_media" / "waldo_probate_1837").resolve()
SCAN = re.compile(r"^images/[0-9]{2}_[a-z0-9_]+\.png$")


def load_waldo_probate() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(source, list) or len(source) != 1:
        raise ValueError("Expected one provenance-preserved Waldo probate source family")
    data = source[0]
    if len(data.get("scans", [])) != 31 or len(data.get("heirs", [])) != 8:
        raise ValueError("Probate source inventory must include the full supplied packet")
    return data


def scan_by_number(number: int, data: dict | None = None) -> dict | None:
    data = data or load_waldo_probate()
    return next((s for s in data["scans"] if s["review_page"] == number), None)


def available_scan_path(scan: dict, *, publication_authorized: bool = False,
                        root: Path = MEDIA_ROOT) -> Path | None:
    """Fail closed: having a local file does not grant redistribution rights."""
    if not publication_authorized or scan.get("reproduction_status") != "approved_for_publication":
        return None
    asset = str(scan.get("normalized_filename") or "")
    if not SCAN.fullmatch(asset):
        return None
    path = (root / Path(asset).name).resolve()
    folder = root.resolve()
    return path if path.parent == folder and path.is_file() else None


def source_summary(data: dict) -> dict:
    scans = data["scans"]
    return {
        "received_scans": len(scans),
        "unique_scans": len({s["sha256"] for s in scans}),
        "heirs_named": len(data["heirs"]),
        "documentary_claims": len(data["claims"]),
        "source_families": 1,
    }


def _render_reference(data: dict, pages: list[int]) -> None:
    st.caption("Packet review scan(s): " + ", ".join(f"{n:02d}" for n in pages)
               + " · researcher-assigned numbering; not court pagination")
    for n in pages:
        route_link("Inspect scan " + str(n) + " record and provenance",
                   "?page=collection&view=waldo-probate&scan=" + str(n))


def _scan_detail(data: dict, scan: dict) -> None:
    page = scan["review_page"]
    st.markdown("**Review scan " + str(page).zfill(2) + " — " + scan["label"] + "**")
    st.caption("Waldo County, Maine · Matthew Beverage estate · 1837 packet")
    st.write("Classification: " + scan["provisional_type"].replace("_", " "))
    if scan.get("duplicate_of"):
        st.warning("This image is an exact duplicate of review scan " +
                   str(scan["duplicate_of"]) + "; it is not additional documentary evidence.")
    st.caption("Supplied original filename: " + scan["original_zip_filename"])
    st.caption("Source image SHA-256: " + scan["sha256"])
    image_path = available_scan_path(
        scan, publication_authorized=bool(data.get("image_publication_authorized", False)))
    if image_path:
        st.image(str(image_path), caption="Original supplied court-paper scan · "
                 "editorial title and ordering are not original", width="stretch")
    else:
        st.info("Original scan retained in the researcher's offline source packet. "
                "It is not published from this public GitHub repository because "
                "redistribution permission for the supplied files is not yet documented.")
    for claim in data["claims"]:
        if page in claim["review_pages"]:
            st.markdown("**Related finding:** " + claim["label"])
            st.write(claim["finding"])
            st.caption("Evidence limit: " + claim["limits"])


def render_waldo_probate(*, compact: bool = False) -> None:
    data = load_waldo_probate()
    st.subheader("Matthew Beverage's Waldo County probate, 1837")
    st.write("A group of court papers supplied by a probate office identifies "
             "**Clarissa Beveridge** as Matthew's widow and names eight contemporary "
             "estate heirs. This is substantially stronger direct evidence than a "
             "later genealogical compilation, but it does **not** establish Matthew's "
             "parents, the 1785 minor's identity, or every heir's biological mother.")
    stats = source_summary(data)
    first, second, third = st.columns(3)
    first.metric("Received scans", stats["received_scans"])
    second.metric("Unique scans", stats["unique_scans"])
    third.metric("Named heirs", stats["heirs_named"])
    st.caption(data["record_group"] + " · " + data["source_received"])
    st.info("**New evidence review:** The October 1837 court order (scan 09) "
            "explicitly calls eight heirs Matthew's 'children'. They now have "
            "source-attributed profiles, with their mothers deliberately unassigned.")
    st.warning("Scans are not publicly redistributed until image rights are confirmed. "
               "The source descriptions, dates and provisional findings below are "
               "available now. These are not certified transcriptions.")
    raw_scan = str(st.query_params.get("scan", "") or "")
    try:
        selection = int(raw_scan) if raw_scan else 0
    except ValueError:
        selection = 0
    requested = scan_by_number(selection, data) if selection else None
    if raw_scan:
        if requested:
            with st.container(border=True):
                st.markdown("### Linked source record")
                _scan_detail(data, requested)
        else:
            st.warning("The requested scan number is not in the supplied packet.")

    (claims_tab, children_tab, deeds_tab, excerpts_tab,
     scans_tab, limits_tab) = st.tabs(
        ["Court findings", "Eight court-named children", "Trace the Hope land",
         "Transcription notebook", "All 31 scans", "Provenance and next steps"])
    with claims_tab:
        for claim in data["claims"]:
            with st.container(border=True):
                st.markdown("**" + claim["label"] + "**")
                st.caption(claim["date"] + " · " + claim["status"])
                st.write(claim["finding"])
                st.caption("Evidence limit: " + claim["limits"])
                _render_reference(data, claim["review_pages"])
    with children_tab:
        render_court_children()
        st.caption("The warrant goes beyond heirship and expressly calls "
                   "these eight people the deceased's children. It does not "
                   "establish individual maternity or every published middle name.")
        for heir in data["heirs"]:
            with st.container(border=True):
                st.markdown("**" + heir["name"] + "**")
                st.write(heir["evidence"])
                st.caption("Comparison with Eaton's 1865 published family: " +
                           heir["published_alignment"])
                _render_reference(data, heir["review_pages"])
    with deeds_tab:
        render_deed_targets()
    with excerpts_tab:
        render_probate_excerpts()
    with scans_tab:
        number = st.selectbox("Choose a source image by review number",
                              list(range(1, stats["received_scans"] + 1)),
                              format_func=lambda n: str(n).zfill(2) + " · " +
                              scan_by_number(n, data)["label"],
                              key="waldo_probate_scan_number")
        if number:
            with st.container(border=True):
                _scan_detail(data, scan_by_number(number, data))
        with st.expander("Browse the entire filename and scan index"):
            for scan in data["scans"]:
                route_link("Scan " + str(scan["review_page"]).zfill(2) + " · " +
                           scan["label"], "?page=collection&view=waldo-probate&scan=" +
                           str(scan["review_page"]))
    with limits_tab:
        st.write("Source state: " + data["record_authentication"])
        st.caption(data["crosswalk_note"])
        st.caption(data["licensing"])
        st.write("An inventory of received copies is not proof of their original "
                 "sequence or that every page represents a separate filed instrument.")
        for target in data["unresolved"]:
            st.write("• " + target)
        st.download_button(
            "Download this documentary source index (not scanned images)",
            json.dumps(data, ensure_ascii=False, indent=2),
            file_name="matthew-waldo-1837-source-index.json",
            mime="application/json",
            key="waldo_probate_index_download",
        )
    if not compact:
        route_link("Compare Eaton's published first and second marriages",
                   "?page=collection&view=matthew")
        route_link("Read Matthew's Hope town clerk trail",
                   "?page=collection&view=hope-matthew")
