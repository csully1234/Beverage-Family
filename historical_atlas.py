"""Historic Fox Islands map atlas and cited early-family research."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from routing_ui import route_markdown

ROOT = Path(__file__).parent
ASSET = ROOT / "static" / "historical_atlas.html"
EVIDENCE = ROOT / "research" / "early_fox_islands_evidence.json"
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
    {
        "id": "1776-bay",
        "name": "1776 · Penobscot Bay / Pulpit Cove",
        "file": "DesBarres1776-Org.jpg",
        "description": "Des Barres' British coastal chart, reflecting the earliest detailed survey-era depiction of settlements near Pulpit Cove and Kent Cove.",
        "note": "The tiny settlement marks are not identifiable Beverage households. Use to contextualize the family during the American Revolution.",
        "alt": "1776 British naval chart of Penobscot Bay and the Fox Islands",
    },
    {
        "id": "1867-survey",
        "name": "1867 · Detailed North Haven survey",
        "file": "NorthHaven1867.jpg",
        "description": "Frederick W. Dorr's U.S. Coast Survey at 1:10,000, with buildings, roads, stone walls, fields, streams and harbors.",
        "note": "Best detailed landscape comparison for 1859 household labels, gristmill and bridge research; wall lines are not an independently verified Beverage boundary.",
        "alt": "Frederick W Dorr's detailed 1867 Coast Survey map of North Haven",
    },
    {
        "id": "1868-thoroughfare",
        "name": "1868 survey · Fox Islands Thoroughfare",
        "file": "FoxIslandsThoroughfare_1868.jpg",
        "description": "Fox Islands Thoroughfare Coast Survey, with 1867–1868 topography and marine soundings; this surviving edition includes 1886 navigational updates.",
        "note": "Compare coastal transit and buildings against the 1867 land survey; do not treat the 1886 chart corrections as changes in all 1868 land features.",
        "alt": "Detailed historical navigational chart of the Fox Islands Thoroughfare",
    },
    {
        "id": "northern-islands-1873",
        "name": "1873–74 · Northern offshore islands",
        "file": "NorthernIslands1873-74.jpg",
        "description": "U.S. Coast Survey detail of Oak, Compass, Spruce Head, Butter and nearby islands north of North Haven.",
        "note": "Useful for fishing routes, outlying family places and matching island names in deeds, not evidence that a named family owned an island.",
        "alt": "U.S. Coast Survey of northern islands beyond North Haven, 1873 to 1874",
    },
    {
        "id": "1890-islands",
        "name": "1890 · North Haven / Hurricane Isle",
        "file": "NorthHaven-VinalHaven-HurricaneIsle1890.jpg",
        "description": "J. B. Stuart's 1890 atlas reduction; useful for roads, bridges, village geography and the period after the 1883 Beach Bridge project.",
        "note": "A road crossing here may be compared with records of Alvin G. Beverage's bridge, but attribution needs the Historical Society's bridge evidence.",
        "alt": "1890 atlas of North Haven, Vinalhaven and Hurricane Isle",
    },
    {
        "id": "1901-islands",
        "name": "1901 revision · Fox Islands topography",
        "file": "FoxIslands1901.jpg",
        "description": "U.S. Geological Survey Vinalhaven quadrangle revised in 1901; this sheet was published in 1904.",
        "note": "Shows the island before twentieth-century purchases and demolitions of Pulpit Harbor farms and buildings.",
        "alt": "Fox Islands topographic survey revised 1901 and published 1904",
    },
    {
        "id": "1941-islands",
        "name": "1941 survey · Fox Islands",
        "file": "FoxIslands1941.jpg",
        "description": "U.S. Geological Survey 1941 Vinalhaven quadrangle, edition of 1944; compare with the 1867 and 1901 island landscapes.",
        "note": "Later shoreline roads and structures help illustrate community change but do not identify ownership of former Beverage farms.",
        "alt": "1941 topographic survey of North Haven and Vinalhaven, 1944 edition",
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


def load_early_evidence() -> dict:
    """Read a provenance-focused research register, without modifying genealogy."""
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def render_historical_atlas() -> None:
    st.write(
        "Explore ten original historical map views, from the Revolutionary era "
        "through the 1940s. The most useful for tracing family homes are the "
        "**1859 named residences** and **1867 detailed topography**. "
        "Select a year, zoom in and drag to explore."
    )
    st.iframe(build_historical_atlas_html(), height=840)
    st.caption(
        "Map files and contextual descriptions: Historical Maps of North Haven "
        "Island and Environs (holmgren.org), reproducing Des Barres' chart, "
        "J. Chace's Waldo County map, U.S. Coast Survey sheets, Stuart's "
        "1890 atlas, and USGS maps. Full images load from the source archive."
    )
    st.warning(
        "Mapped names are historic house-location clues, not surveyed "
        "ownership boundaries. The identification of 'B. C. Beverage' "
        "and family acreage both require independent deed and census evidence."
    )

    evidence = load_early_evidence()
    st.subheader("Original land records & founding-era family discoveries")
    st.write(
        "Follow the first Fox Islands surveys and later historical accounts "
        "without confusing an old claimant list with verified parentage or a deed."
    )
    for finding in evidence["findings"]:
        with st.expander(f"{finding['date']} · {finding['title']}"):
            st.caption(finding["confidence"])
            st.write(finding["summary"])
            st.caption(finding["status"])
            supporting = [
                src for src in evidence["sources"]
                if src["id"] in finding["source_ids"]
            ]
            route_markdown(
                "Sources: " + " · ".join(
                    f"[{src['title']}]({src['url']})" for src in supporting
                )
            )
    st.markdown("#### Examine the earliest surviving plans")
    for sid in ("putnam_1785", "island_list_1785", "fox_outline_1786", "fox_copy_1838"):
        source = next(s for s in evidence["sources"] if s["id"] == sid)
        route_markdown(f"**[{source['title']}]({source['url']})** — {source['detail']}")
    st.caption(evidence["caveat"])
    route_markdown(
        f"[Original map archive]({SOURCE}) · "
        f"[Download the 1859 three-map set (ZIP)]({ZIP_URL})"
    )
