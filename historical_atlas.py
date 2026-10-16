"""1859 Fox Islands scans: provenance-first public atlas, independent of parcel claims."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from routing_ui import route_markdown

ASSET = Path(__file__).parent / "static" / "historical_atlas.html"
SOURCE = "https://holmgren.org/NorthHavenHistoricalMaps/"
ZIP_URL = SOURCE + "NorthHaven-Vinalhaven1859.zip"

# The originals are served by their holding map archive, not copied into this repo.
# These are illustrations of named residences, NOT surveyed ownership boundaries.
MAPS = (
    {
        "id": "fox-islands",
        "name": "North Haven & Vinalhaven",
        "file": "NorthHaven-Vinalhaven1859.jpg",
        "description": "Both Fox Islands, with roads, harbors and labeled residences. Start here to explore the family's historic North Haven neighborhood.",
        "note": "Some Beverage labels appear on North Haven. A surname beside a building marks a historic name/location, not an acreage boundary.",
        "alt": "1859 map showing North Haven and Vinalhaven with hundreds of historical residence labels",
    },
    {
        "id": "north-haven-village",
        "name": "North Haven village",
        "file": "NorthHavenTown1859.jpg",
        "description": "Enlarged village plan with a directory that includes Henry Beverage (captain) and Josiah Beverage 2nd (fisherman).",
        "note": "A directory entry alone does not identify the family's plot, deed, or precise house location.",
        "alt": "1859 North Haven village inset with roads, houses and a local directory",
    },
    {
        "id": "carvers-harbor",
        "name": "Carver's Harbor, Vinalhaven",
        "file": "CarversHarbor1859.jpg",
        "description": "Detailed plan and business directory of Carver's Harbor on nearby Vinalhaven.",
        "note": "Useful for neighboring families and island context; this is not a map of North Haven property holdings.",
        "alt": "1859 Carver's Harbor Vinalhaven inset showing residences and its commercial directory",
    },
)


def atlas_payload() -> dict:
    return {
        "maps": [{**item, "url": SOURCE + item["file"]} for item in MAPS],
        "source": SOURCE,
        "download": ZIP_URL,
    }


def build_historical_atlas_html() -> str:
    """Embed a safe JSON catalogue in the self-contained (offline-script) viewer."""
    payload = json.dumps(atlas_payload(), ensure_ascii=True).replace("<", "\\u003c").replace("&", "\\u0026")
    template = ASSET.read_text(encoding="utf-8")
    return template.replace("ATLAS_JSON", payload)


def render_historical_atlas() -> None:
    st.write(
        "Browse three detailed views from the **1859 Map of Waldo County, Maine**, "
        "published by J. Chace Jr. & Co. Scroll or use the controls to zoom; drag to explore "
        "individual household labels. The originals open at full resolution."
    )
    st.iframe(build_historical_atlas_html(), height=840)
    st.caption(
        "Source: J. Chace Jr. & Co., Map of Waldo County (1859), surveys by D. Kelsey and "
        "D. H. Davison. Digital excerpts provided by the Historical Maps of North Haven "
        "Island and Environs collection (holmgren.org). Images load from that external "
        "archive; an internet connection is required."
    )
    st.warning(
        "Map labels are clues to residences, not legal property boundaries or proof of "
        "acreage. In particular, identifying the person behind a partially legible "
        "“B. C. Beverage” label requires independent census/deed corroboration."
    )
    route_markdown(
        f"[View map collection and historical notes]({SOURCE}) · "
        f"[Download all three original image files (ZIP)]({ZIP_URL})"
    )
