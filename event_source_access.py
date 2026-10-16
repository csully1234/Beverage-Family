"""Links between family-event citations and the accessible historical evidence.

Some legacy entries contain bibliography *labels*, not URLs or scans. Do not
misrepresent those names as verified source images. When a stable record ID or
explicit URL is present, link to the record's actual source page.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

import streamlit as st

from routing_ui import route_link

_FINDAGRAVE = re.compile(r"^Find A Grave memorial\s+(\d+)\s*$", flags=re.I)


# A verified obituary for Grace Elizabeth Beverage (née Reed), not a marriage certificate.
_VERIFIED_RECORD_PAGES = {
    "grace beverage obituary": "https://www.legacy.com/us/obituaries/mainetoday-centralmaine/name/grace-beverage-obituary?id=25022664",
}


def source_target(source) -> tuple[str, str | None]:
    if isinstance(source, dict):
        label = str(source.get("title") or source.get("citation") or "Historical source")
        candidate = str(source.get("url") or "")
        parsed = urlparse(candidate)
        return (label, candidate) if parsed.scheme in {"https", "http"} and parsed.netloc else (label, None)
    label = str(source)
    known_record = _VERIFIED_RECORD_PAGES.get(label.strip().casefold())
    if known_record:
        return label, known_record
    match = _FINDAGRAVE.fullmatch(label.strip())
    if match:
        return label, "https://www.findagrave.com/memorial/" + match.group(1)
    return label, None


def render_event_source_access(sources: list, *, compact: bool = False) -> None:
    """Always expose individual source references, even in compact cards."""
    if not sources:
        st.caption("No historical citation is entered for this event.")
        return
    with st.expander(f"See {len(sources)} source reference{'s' if len(sources)!=1 else ''} and available records"):
        accessible = 0
        for number, source in enumerate(sources, 1):
            name, url = source_target(source)
            if url:
                accessible += 1
                route_link(f"{number}. Open source: {name}", url)
                st.caption("Opens the cited record or publication; this source may not prove every detail of the event.")
            else:
                st.markdown(f"**{number}. {name}**")
                st.caption("Bibliographic reference only. No verified original scan or direct record URL is attached to this citation yet.")
        if accessible != len(sources):
            st.caption(
                f"{len(sources)} cited reference(s); {accessible} linked record(s). "
                "A citation count is not the number of digitized clippings stored on this site."
            )
