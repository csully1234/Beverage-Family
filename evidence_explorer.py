"""Source-first evidence explorer for relatives, events, and original document leads.

Public claims stay separate from identity hypotheses. This module never assumes
that an external URL is a scan, a historical label means corroboration, or that
a source linked to a candidate person establishes the candidate's identity.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from event_source_access import source_target
from routing_ui import route_link

ROOT = Path(__file__).resolve().parent
EVIDENCE_FILE = ROOT / "data" / "evidence_exhibits.json"


def evidence_catalog(path: Path = EVIDENCE_FILE) -> list[dict]:
    """Load curated, rights-aware source links without mutating base research."""
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def safe_document_url(value: str | None) -> str | None:
    """Reject local, injected, credential-bearing, and non-http source URLs."""
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"https", "http"} or not parsed.hostname:
            return None
        if parsed.username or parsed.password or parsed.port not in (None, 80, 443):
            return None
        if "\\" in value or "<" in value or ">" in value:
            return None
        return value
    except ValueError:
        return None


def for_person(person_id: str, catalog: list[dict]) -> list[dict]:
    return [item for item in catalog if person_id in item.get("people_ids", [])]


def for_event(event_id: str, catalog: list[dict]) -> list[dict]:
    return [item for item in catalog if event_id in item.get("event_ids", [])]


def source_record(source, position: int = 0) -> dict:
    """Normalize a preexisting citation without inventing its access level."""
    title, url = source_target(source)
    if isinstance(source, dict):
        title = str(source.get("title") or source.get("short_title") or title)
        evidence = str(source.get("evidence_level") or source.get("record_type")
                       or source.get("source_type") or "Bibliographic reference")
        description = str(source.get("supports") or source.get("summary") or
                          source.get("citation") or "")
        return {
            "id": str(source.get("id") or source.get("source_id") or
                      f"legacy-{position}"),
            "title": title,
            "date": str(source.get("record_date") or source.get("date") or ""),
            "type": evidence,
            "access": "Cited source page" if url else "Bibliographic reference only",
            "url": safe_document_url(url),
            "claim": description,
            "limits": ("The linked page may be a published text, catalog or index "
                       "rather than an original image. Confirm the record before "
                       "relying on its identity attribution."),
            "rights": "",
            "association": "historical_citation",
            "preview_pdf": False,
            "collection": "Other citations",
        }
    return {
        "id": f"legacy-{position}", "title": title, "date": "",
        "type": "Bibliographic reference", "access": "Link not verified" if not url
        else "Cited source page", "url": safe_document_url(url),
        "claim": "", "limits": "This citation alone does not establish a family relationship.",
        "rights": "", "association": "historical_citation",
        "preview_pdf": False, "collection": "Other citations",
    }


def source_items(catalog_items: list[dict], other_sources: list | None = None,
                 archive_sources: list[dict] | None = None) -> list[dict]:
    """Deduplicate exact destinations, preferring curated claim-level metadata."""
    ordered = []
    seen = set()
    for item in [
        *catalog_items,
        *(source_record(src, i) for i, src in enumerate(other_sources or [])),
        *(source_record(src, i) for i, src in enumerate(archive_sources or [])),
    ]:
        url = safe_document_url(item.get("url"))
        key = ("url", url.rstrip("/")) if url else (
            "label", str(item.get("title", "")).casefold()
        )
        if key in seen:
            continue
        seen.add(key)
        ordered.append({**item, "url": url})
    return ordered


def is_external_pdf(item: dict) -> bool:
    url = safe_document_url(item.get("url"))
    if not url or not item.get("preview_pdf"):
        return False
    return urlsplit(url).path.lower().endswith(".pdf")


def render_source_card(item: dict, *, context: str, number: int) -> None:
    with st.container(border=True):
        st.markdown("**" + str(item.get("title") or "Untitled historical source") + "**")
        props = [str(item.get("date") or ""), str(item.get("type") or ""),
                 str(item.get("access") or "")]
        st.caption(" · ".join(value for value in props if value))
        if item.get("claim"):
            st.write(str(item["claim"]))
        if item.get("association") == "candidate":
            st.caption("Possible identity connection — not a confirmed family-tree relationship")
        if item.get("limits"):
            st.caption("Evidence limits: " + str(item["limits"]))
        if item.get("rights"):
            st.caption("Image and reuse rights: " + str(item["rights"]))
        if item.get("url"):
            route_link("Open cited record at its source", item["url"])
            if is_external_pdf(item):
                key = "evidence_pdf_" + hashlib.sha256(
                    (context + "|" + str(number) + "|" + item["url"]).encode()
                ).hexdigest()[:20]
                if st.checkbox("Read external PDF on this page", value=False, key=key):
                    st.caption(
                        "Preview loads the publisher's PDF; if embedding is blocked, "
                        "use the direct source link. We do not host a copy."
                    )
                    st.components.v1.iframe(item["url"], height=600, scrolling=True)
        else:
            st.caption("No direct digitized item is currently identified for this citation.")


def render_profile_highlights(person_id: str) -> None:
    """Make verified and explicitly hypothetical source links reachable above tabs."""
    curated = for_person(person_id, evidence_catalog())
    if not curated:
        return
    with st.expander(f"Explore original records and research leads ({len(curated)})"):
        st.caption("These sources are linked to this profile for investigation. "
                   "A candidate match is not a proven parent, spouse or identity.")
        for i, item in enumerate(curated[:4]):
            render_source_card(item, context="highlight-" + person_id, number=i)
        if len(curated) > 4:
            st.caption(f"See all {len(curated)} curated records in the Historical records tab.")


def render_profile_browser(person: dict, archive_sources: list[dict]) -> None:
    items = source_items(for_person(str(person["id"]), evidence_catalog()),
                         person.get("sources") or [], archive_sources)
    st.subheader("Examine the evidence")
    if not items:
        st.caption("No source records are attached to this profile.")
        return
    linked = sum(bool(item.get("url")) for item in items)
    st.caption(f"{len(items)} distinct references · {linked} linked record pages or scans. "
               "Open sources to inspect them, including where permitted an external PDF preview. "
               "Citation counts do not equal independently inspected original documents.")
    choices = ["All references", "Linked records", "Research leads", "Unlinked citations"]
    selected = st.selectbox("Show evidence", choices, key="person_evidence_filter_" + str(person["id"]))
    selected_items = [
        item for item in items
        if selected == "All references"
        or selected == "Linked records" and item.get("url")
        or selected == "Research leads" and item.get("association") == "candidate"
        or selected == "Unlinked citations" and not item.get("url")
    ]
    for i, item in enumerate(selected_items):
        render_source_card(item, context="profile-" + str(person["id"]), number=i)


def render_event_browser(event: dict, *, compact: bool = False) -> None:
    event_id = str(event.get("id") or "")
    items = source_items(for_event(event_id, evidence_catalog()), event.get("sources") or [])
    if not items:
        st.caption("No historical source citations have been entered.")
        return
    with st.expander(f"Explore supporting evidence ({len(items)} references)"):
        st.caption("Open the cited document, inspect its claim and limitations, or "
                   "preview a PDF when available. External sources retain their own rights.")
        for i, item in enumerate(items):
            render_source_card(item, context="event-" + event_id + ("-compact" if compact else "-full"), number=i)


def render_exhibit_library() -> None:
    st.subheader("Browse original evidence and research leads")
    st.write("Open documents, diary transcripts, historical films, maps and archive "
             "exhibits directly from their custodians. We distinguish original evidence "
             "from later transcriptions and proposed family connections.")
    items = evidence_catalog()
    options = ["All collections", *sorted({str(it.get("collection") or "Other") for it in items})]
    choice = st.selectbox("Evidence collection", options, key="exhibits_collection")
    keyword = st.text_input("Search evidence by name, claim or place", key="exhibits_search").strip().casefold()
    shown = [item for item in items
             if (choice == "All collections" or item.get("collection") == choice)
             and (not keyword or keyword in json.dumps(item, ensure_ascii=False).casefold())]
    st.caption(f"{len(shown)} of {len(items)} curated records and research leads")
    for i, item in enumerate(shown):
        render_source_card(item, context="library", number=i)
