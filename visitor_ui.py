"""Visitor-facing stories, people directory, media catalog and historical documents.

Only researched claims and repository-backed assets appear here. An image description
is not treated as a hosted photograph, and unresolved genealogical identities remain
explicitly uncertain.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st

from routing_ui import route_link, route_markdown
from research_collection_ui import load_collection, render_finding
from family_data import life_span, year_from_date

ROOT = Path(__file__).resolve().parent
MEDIA_ROOT = (ROOT / "static" / "approved_media").resolve()
MEDIA_MANIFEST = ROOT / "data" / "media_manifest.json"

STORIES = (
    {
        "id": "thomas-revolution",
        "title": "Thomas Beverage and the American Revolution",
        "period": "1781–1786",
        "summary": "A sworn statement about a British fishing pass, a schooner named Ann and disputed wartime ownership.",
        "body": "In 1786, Thomas Beverage provided a sworn declaration at Fox Island at Paul Reed's request. Thomas said he personally witnessed Robert Duglass obtain a fishing pass from British Captain Henry Mowat. The remainder of his statement reports what Duglass told him about a schooner, an alleged bill of sale and a possible trading arrangement behind British lines. The papers also include Reed's failed petition to reopen a civil judgment. They do not establish Thomas's politics or conclusively connect this witness to every Thomas in a compiled family tree.",
        "terms": ("Thomas Beverage", "Fox Island", "Paul Reed"),
        "document": "thomas-1786",
    },
    {
        "id": "harold-radio",
        "title": "Harold Beverage and long-distance radio",
        "period": "Twentieth century",
        "summary": "The engineering work of Harold H. Beverage, including the antenna that bears his name.",
        "body": "The site's existing engineering and family sources record Harold Beverage's work in radio communications. Explore his biography, family connections and original engineering references rather than relying on a short invention anecdote.",
        "terms": ("Harold", "antenna", "radio"),
    },
    {
        "id": "beveridge-point",
        "title": "The history of Beveridge Point",
        "period": "North Haven, Maine",
        "summary": "Family memories, historical island life and records that may explain the Point's story.",
        "body": "A 1958 diary transcription references hauling wood from Beveridge's Point for Eliot Beveridge. This is evidence of the place name and activity, not by itself a deed or proof of exact property boundaries. Related island-registry and land records remain separate leads that require original documents.",
        "terms": ("Beveridge Point", "Point", "land"),
    },
    {
        "id": "islebuilt",
        "title": "IsleBuilt: boats made on North Haven",
        "period": "From 1955",
        "summary": "Eliot Beveridge's boatbuilding operation and the search for surviving boats.",
        "body": "Historical Society research associates Eliot Beveridge with IsleBuilt, a North Haven boat operation that reportedly produced more than 350 boats. Original advertisements, photographs, construction records and surviving vessels remain promising research targets.",
        "terms": ("IsleBuilt", "Eliot", "boats"),
    },
    {
        "id": "lowell-music",
        "title": "Lowell Beveridge: a life in music",
        "period": "Twentieth century",
        "summary": "Church music at Columbia and the reported Universal Harmony manuscript.",
        "body": "Lowell Pierson Beveridge served as an organist and music leader at Columbia. A memorial describes a large manuscript called Universal Harmony; its current archival location still needs verification. Recent review of a contemporary institutional record also affects the reported birthplace and remains explicitly labeled as a proposed correction.",
        "terms": ("Lowell", "music", "Universal Harmony"),
    },
    {
        "id": "island-life",
        "title": "Everyday life on North Haven",
        "period": "Nineteenth and twentieth centuries",
        "summary": "Farming, schools, island shipping, trades and families at work.",
        "body": "Historic photographs, diaries and accounts tell the story of island farms, freight, schoolrooms and waterfront labor. Item dates and person identifications should be checked against their original captions, rather than assumed from a surrounding historical narrative.",
        "terms": ("North Haven", "farms", "schools"),
    },
)

DOCUMENTS = {
    "thomas-1786": {
        "title": "Thomas Beverage's sworn testimony and the Paul Reed petition",
        "date": "June 1, 1786 (testimony); June 14–15, 1786 (legislative action)",
        "citation": "Documentary History of the State of Maine, vol. XXI (1916), printed pp. 214–222; Thomas Beverage's statement on pp. 221–222.",
        "url": "https://archive.org/details/documentaryhisto21mainuoft/page/220/mode/2up",
        "pdf_url": "https://sites.rootsweb.com/~mealhn/books/mehist_v21.pdf#page=241",
        "summary": "Paul Reed asked the Massachusetts General Court to set aside a £120 judgment arising from the schooner Ann. His petition was referred to a committee. Thomas testified at Reed's request; the committee recommended allowing Reed to withdraw his petition, rather than granting a new trial.",
        "excerpt": "I Thomas Beverage of Lawful Age do Testify and say ... Robert Duglass Then an Inhabitant of Fox Island, Procured a Pass of Capt Henry Mowit in my Presents, for Fishing ...",
        "limits": "The source is a 1916 printed transcription of historical papers, not the original handwritten affidavit or a verbatim trial transcript. Thomas personally observed the permit but repeated Duglass's account of the bill of sale and proposed trade. The identification of this witness with a particular Thomas in the family tree still requires corroboration.",
    },
}


def _year(value: object) -> int | None:
    """Extract an approximate year only for ordering, never display it as exact."""
    match = re.search(r"(?<!\d)(1[6-9]\d{2}|20\d{2})(?!\d)", str(value or ""))
    return int(match.group(1)) if match else None


def approved_assets() -> dict[str, dict]:
    """Read only local, explicitly licensed and reviewed image assets."""
    if not MEDIA_MANIFEST.is_file():
        return {}
    try:
        payload = json.loads(MEDIA_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    result: dict[str, dict] = {}
    for entry in payload if isinstance(payload, list) else []:
        if not isinstance(entry, dict) or entry.get("rights_status") not in {"permission", "public_domain"}:
            continue
        identifier = str(entry.get("item_identifier") or "")
        relative = str(entry.get("local_path") or "")
        if not identifier or not relative.startswith("static/approved_media/"):
            continue
        path = (ROOT / relative).resolve()
        if path != MEDIA_ROOT and MEDIA_ROOT not in path.parents:
            continue
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"} or not path.is_file():
            continue
        result[identifier] = {**entry, "path": str(path)}
    return result


SORT_OPTIONS = ("Surname A–Z", "First name A–Z", "Birth year (oldest first)", "Birth year (newest first)")


_DISAMBIGUATION = re.compile(r"\\s*\\([^()]*\\)\\s*$")
_GENERATION_SUFFIX = re.compile(r"^(?:jr\\.?|sr\\.?|ii|iii|iv|v)$",re.I)


def _name_parts(person: dict) -> tuple[str, str]:
    """Find the primary family name, ignoring year/alias and Jr/III suffixes.

    A displayed name such as 'John White (1748)' must sort under W, not
    under '(1748)'. The original display name is never changed.
    """
    full_name = str(person.get("full_name") or "").strip()
    base = full_name
    while True:
        trimmed = _DISAMBIGUATION.sub("", base).strip()
        if trimmed == base:
            break
        base = trimmed
    words = base.split()
    while words and _GENERATION_SUFFIX.fullmatch(words[-1]):
        words.pop()
    if not words:
        return "", full_name
    return words[-1].casefold(), " ".join(words[:-1]).casefold()


def surname_first_label(person: dict) -> str:
    """Make a surname-sorted dropdown visually obvious to people browsing it."""
    name = str(person.get("full_name") or "")
    surname, _ = _name_parts(person)
    if not surname:
        return name
    original = name
    # Remove trailing annotations from the name but keep them in the label.
    annotations = []
    while True:
        m = _DISAMBIGUATION.search(original)
        if m is None:
            break
        annotations.insert(0, m.group().strip())
        original = original[:m.start()].strip()
    words = original.split()
    suffixes = []
    while words and _GENERATION_SUFFIX.fullmatch(words[-1]):
        suffixes.insert(0, words.pop())
    if not words:
        return name
    family = words.pop()
    rest = " ".join(words)
    extra = " ".join([*suffixes, *annotations])
    return f"{family}, {rest}" + (f" {extra}" if extra else "")


def _surname_first_key(person: dict) -> tuple:
    surname, given = _name_parts(person)
    return (surname, given, str(person.get("full_name") or "").casefold(), str(person.get("id") or ""))


def order_people(people, order="Surname A–Z") -> list[dict]:
    if order == "First name A–Z":
        return sorted(people, key=lambda person: (str(person.get("full_name") or "").casefold(), str(person.get("id") or "")))
    if order == "Birth year (oldest first)":
        return sorted(people, key=lambda person: (year_from_date(person.get("birth_date")) or 9999, _surname_first_key(person)))
    if order == "Birth year (newest first)":
        return sorted(people, key=lambda person: (-(year_from_date(person.get("birth_date")) or 0), _surname_first_key(person)))
    return sorted(people, key=_surname_first_key)


def render_people_directory(people: list[dict], people_by_id: dict) -> None:
    """An index by name and birth period; it does not infer new relationships."""
    st.write("Browse a relative, or search a name without needing to know the exact spelling.")
    query = st.text_input("Find a person", placeholder="Name or alternate spelling…", key="directory_query").casefold().strip()
    period = st.selectbox("Birth period", ["Any period", "Before 1800", "1800s", "1900s", "2000s", "Unknown"], key="directory_period")
    from family_search import person_match
    order = st.selectbox("Sort people", SORT_OPTIONS, key="directory_sort")
    people = order_people(people, order)
    matches = []
    for person in people:
        if query and not person_match(query, person):
            continue
        birth = _year(person.get("birth_date"))
        if period == "Before 1800" and (birth is None or birth >= 1800):
            continue
        if period == "1800s" and (birth is None or not 1800 <= birth < 1900):
            continue
        if period == "1900s" and (birth is None or not 1900 <= birth < 2000):
            continue
        if period == "2000s" and (birth is None or birth < 2000):
            continue
        if period == "Unknown" and birth is not None:
            continue
        matches.append(person)
    st.caption(f"{len(matches)} of {len(people)} people")
    if not matches:
        st.info("No matching profiles. Try fewer letters, a different spelling or another period.")
        return
    page_count = max(1, (len(matches) + 15) // 16)
    chosen_page = st.selectbox("Directory page", range(1, page_count + 1), format_func=lambda n: f"{n} of {page_count}", key="directory_page")
    for start in range((chosen_page - 1) * 16, min(chosen_page * 16, len(matches)), 2):
        cols = st.columns(2)
        for col, person in zip(cols, matches[start:start + 2]):
            with col.container(border=True):
                st.markdown(f"**{person.get('full_name','Unknown')}**")
                st.caption(life_span(person))
                if person.get("birth_place"):
                    st.caption("Birthplace: " + str(person["birth_place"]))
                parent_ids = person.get("parents", [])
                if parent_ids:
                    st.caption("Parents: " + ", ".join(people_by_id.get(pid, {}).get("full_name", "Unresolved") for pid in parent_ids[:2]))
                route_link("Read profile", "?" + urlencode({"page": "people", "profile": person["id"]}), width="stretch")


def render_stories_page() -> None:
    collection = load_collection()
    st.title("Stories & Discoveries")
    st.write("Explore the lives and events behind the family tree. Each story leads back to the research and source records.")
    story_id = st.query_params.get("story", "")
    story = next((s for s in STORIES if s["id"] == story_id), None)
    if story_id and not story:
        st.warning("Story not found; choose one below.")
    if story:
        route_link("← Browse all stories", "?page=stories")
        st.title(story["title"])
        st.caption(story["period"])
        st.write(story["body"])
        if story.get("document"):
            route_link("Read the historical document", "?page=documents&doc=" + story["document"])
        st.subheader("Follow the evidence")
        seen = set()
        for term in story["terms"]:
            for finding in collection.select(query=term):
                rid = finding["Research ID"]
                if rid in seen:
                    continue
                seen.add(rid)
                with st.container(border=True):
                    st.markdown("**" + finding["Navigation"]["title"] + "**")
                    st.write(finding["Proposed fact or narrative"])
                    st.caption("Evidence: " + finding["Confidence"] + " · " + finding["Notes about uncertainty"])
                    route_link("Review evidence and original sources", "?page=collection&finding=" + rid)
                if len(seen) >= 5:
                    break
            if len(seen) >= 5:
                break
        if not seen:
            st.info("This story does not yet have a dedicated imported finding. Search the existing archive for supporting records.")
        route_link("Search this history", "?page=search&q=" + urlencode({"q": story["terms"][0]})[2:])
        return
    for index in range(0, len(STORIES), 2):
        cols = st.columns(2)
        for col, item in zip(cols, STORIES[index:index + 2]):
            with col.container(border=True):
                st.subheader(item["title"])
                st.caption(item["period"])
                st.write(item["summary"])
                route_link("Explore story", "?page=stories&story=" + item["id"], width="stretch")


def render_media_page() -> None:
    collection = load_collection()
    st.title("Photographs & Documents")
    st.write("Explore archival items and read historical records. We display original image files only when reuse rights and source identification are established.")
    images_tab, documents_tab = st.tabs(["Historical image catalog", "Historical documents"])
    with images_tab:
        search = st.text_input("Search images, captions, people or places", key="media_search").strip()
        order = st.selectbox("Order", ["Oldest associated year", "Newest associated year", "Holding institution"], key="media_order")
        rows = [r for r in collection.inventory_rows("Images and Maps")
                if not search or search.casefold() in json.dumps(r, ensure_ascii=False, default=str).casefold()]
        if order == "Holding institution":
            rows.sort(key=lambda r: str(r.get("Holding institution", "")).casefold())
        else:
            rows.sort(key=lambda r: _year(r.get("Date")) or 9999, reverse=order == "Newest associated year")
        st.caption(f"{len(rows)} archival item descriptions. An associated research year is not necessarily the photograph's capture date.")
        approved = approved_assets()
        if not approved:
            st.info("Original thumbnails will appear here after approved scans and rights information are added. Until then, use each item's holding-institution link.")
        page_count = max(1, (len(rows) + 7) // 8)
        page = st.selectbox("Catalog page", range(1, page_count + 1), format_func=lambda n: f"{n} of {page_count}", key="media_page")
        for index in range((page - 1) * 8, min(page * 8, len(rows)), 2):
            for col, record in zip(st.columns(2), rows[index:index+2]):
                key = str(record.get("Collection or item identifier") or record.get("Item ID") or "")
                asset = approved.get(key)
                with col.container(border=True):
                    if asset:
                        st.image(asset["path"], caption=asset.get("credit") or record.get("Holding institution"))
                    else:
                        st.caption("Original scan not hosted")
                    st.markdown("**" + str(record.get("Subject", "Untitled archival item")) + "**")
                    st.caption(str(record.get("Date", "Undated")) + " · " + str(record.get("Holding institution", "")))
                    st.write(str(record.get("Item or caption", "")))
                    link = record.get("Direct item page")
                    if isinstance(link, str) and link.startswith(("https://", "http://")):
                        route_link("View original at archive", link)
                        with st.expander("Show original archive page here"):
                            st.caption("The holding institution controls whether previews are permitted. If blocked, use the original link above.")
                            st.components.v1.iframe(link, height=520, scrolling=True)
                    with st.expander("Identification, rights & citation"):
                        st.write("Identifier: " + key)
                        st.write("Rights: " + str(record.get("Rights", "Unknown")))
                        st.write("Review: " + str(record.get("Viewed status", "Not reviewed")))
                        st.write("Resolution: " + str(record.get("High resolution", "Unknown")))
    with documents_tab:
        for id_, document in DOCUMENTS.items():
            with st.container(border=True):
                st.markdown("**" + document["title"] + "**")
                st.caption(document["date"])
                st.write(document["summary"])
                route_link("Read document and original pages", "?page=documents&doc=" + id_)


def render_document_page() -> None:
    doc_id = st.query_params.get("doc", "thomas-1786")
    item = DOCUMENTS.get(doc_id)
    if not item:
        st.warning("Unknown document.")
        route_link("Browse documents", "?page=media")
        return
    route_link("← Back to photographs and documents", "?page=media")
    st.title(item["title"])
    st.caption(item["date"])
    st.write(item["summary"])
    st.subheader("Original source")
    st.write(item["citation"])
    route_link("Open original scanned pages at Internet Archive", item["url"])
    route_link("Alternate PDF scan, page 241", item["pdf_url"])
    with st.expander("Preview external source within this page"):
        st.caption("The outside archive may prevent embedding. Use the direct links above if the preview is blank.")
        st.components.v1.iframe(item["pdf_url"], height=650, scrolling=True)
    st.subheader("Transcribed excerpt")
    st.write(item["excerpt"])
    st.caption("Excerpt only; consult the printed pages for exact wording and the complete deposition.")
    st.subheader("What this record does—and does not—prove")
    st.write(item["limits"])
    route_link("See the related family story", "?page=stories&story=thomas-revolution")
    route_link("Consult source-register entry SRC118", "?page=archive&source=SRC118")
