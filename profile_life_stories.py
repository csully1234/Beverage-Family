"""Turn existing indexed family records into transparent, source-linked life stories.

A synopsis is a guide to recorded fields, NEVER a newly researched biography.
Source and identity limits are inherited unchanged. No AI-generated genealogy,
inferred parents, marriage dates or reconstructed places are stored here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from family_data import format_date, year_from_date
from historical_claims import reviewed_event_presentation
from family_books import book_pages_for_person, load_book_person_crosswalk
from routing_ui import route_link
from family_photo_navigation import photo_gallery_route


def _known_date(person: Mapping[str, Any], field: str) -> str:
    value = person.get(field)
    if not value or person.get(field + "_precision") == "unknown":
        return ""
    return format_date(value, person.get(field + "_precision"))


def life_record_overview(person: Mapping[str, Any]) -> list[str]:
    """Conservative plain-language statements of existing record fields only."""
    sentences: list[str] = []
    name = str(person.get("full_name") or "This relative")
    birth, death = _known_date(person, "birth_date"), _known_date(person, "death_date")
    born_at = str(person.get("birth_place") or "").strip()
    died_at = str(person.get("death_place") or "").strip()
    if birth:
        line = f"The family index records {name}'s birth as {birth}"
        if born_at:
            line += f", with {born_at} as the recorded birthplace"
        sentences.append(line + ".")
    elif born_at:
        sentences.append(f"The archive lists {born_at} as a birthplace for {name}, but no birth date is established.")
    if death:
        line = f"The recorded death date is {death}"
        if died_at:
            line += f", with {died_at} recorded as the death place"
        sentences.append(line + ".")
    elif died_at:
        sentences.append(f"The recorded death place is {died_at}; the date remains unknown.")
    occupations = [str(v).strip() for v in person.get("occupations", [])
                   if str(v).strip()]
    if occupations:
        sentences.append("Listed occupations and roles: " + ", ".join(occupations[:5]) + ".")
    education = [str(v).strip() for v in person.get("education", [])
                 if str(v).strip()]
    if education:
        sentences.append("Education listed in this profile: " + "; ".join(education[:3]) + ".")
    return sentences


def profile_milestones(person: Mapping[str, Any], events: list[dict]) -> list[dict]:
    """Preserve dates and event IDs, using the latest source-reviewed display copy."""
    person_id = str(person["id"])
    items: list[dict] = []
    for field, label in (("birth_date", "Birth recorded"), ("death_date", "Death recorded")):
        date = person.get(field)
        if not date or person.get(field + "_precision") == "unknown":
            continue
        items.append({
            "id": person_id + ":" + field,
            "date": str(date),
            "date_label": _known_date(person, field),
            "title": label,
            "url": "?page=people&profile=" + person_id,
            "status": "From the current profile; inspect the underlying sources before treating the date as independently verified",
            "kind": "profile",
        })
    for raw in events:
        if person_id not in raw.get("people_involved", []):
            continue
        reviewed = reviewed_event_presentation(raw)
        event_id = str(raw.get("id") or "")
        if not event_id:
            continue
        items.append({
            "id": event_id,
            "date": str(reviewed.get("date") or ""),
            "date_label": format_date(reviewed.get("date"), reviewed.get("date_precision")),
            "title": str(reviewed.get("title") or "Historical event"),
            "url": "?page=timeline&event=" + event_id,
            "status": str(reviewed.get("evidence_status") or "Source status not rated"),
            "kind": "event",
        })
    return sorted(items, key=lambda row: (
        year_from_date(row["date"]) if year_from_date(row["date"]) is not None else 9999,
        row["date"], row["title"].casefold(), row["id"],
    ))


def linked_book_illustrations(person_id: str, captioned_photos: list[dict] | None = None,
                              crosswalk: dict | None = None) -> list[dict]:
    """Page-by-page exact-ID book association; never infer identity by name."""
    catalog = crosswalk if crosswalk is not None else load_book_person_crosswalk()
    pages = set(book_pages_for_person(person_id, catalog))
    if captioned_photos is None:
        from colony_photos import load_colony_photo_catalog
        captioned_photos = load_colony_photo_catalog()["photos"]
    rows = []
    for photo in captioned_photos:
        if int(photo["pdf_page"]) not in pages:
            continue
        rows.append({
            "page": int(photo["pdf_page"]),
            "title": str(photo["title"]),
            "caption": str(photo["caption_summary"]),
            "section": str(photo.get("section") or "Family photograph"),
            "crop": tuple(photo["preview_crop"]),
            "url": "?page=family-books&book_page=" + str(photo["pdf_page"]),
            "attribution": "Author-attributed caption; not independently certified identity",
        })
    return sorted(rows, key=lambda x: x["page"])


def render_profile_life_record(person: dict, events: list[dict]) -> None:
    """Evidence-aware overview for profiles with OR without written biographies."""
    st.subheader("Life at a glance")
    has_biography = bool(str(person.get("biography") or "").strip())
    summary = life_record_overview(person)
    if has_biography:
        st.caption("The written biography follows below. These dates and roles come from the current family index.")
    elif summary:
        st.write(" ".join(summary))
        st.caption("This is a record-based overview, not a verified biographical essay. "
                   "Names, dates, places and family connections require their individual sources.")
    else:
        st.write("A biographical account is still being assembled from the existing historical records.")
        st.caption("No missing dates or relationships are inferred to fill the gaps.")

    milestones = profile_milestones(person, events)
    st.markdown("**Follow this life through the original records**")
    if not milestones:
        st.caption("No dated life events are yet associated with this relative.")
    else:
        st.caption(f"{len(milestones)} dated profile or event entries. "
                   "Original source links and evidence limitations remain attached.")
        with st.expander(f"Explore the recorded milestones ({len(milestones)})",
                         expanded=not has_biography):
            for item in milestones[:8]:
                st.markdown("**" + item["date_label"] + " · " + item["title"] + "**")
                st.caption(item["status"])
                if item["kind"] == "event":
                    route_link("Open event and citations", item["url"], type="tertiary")
            if len(milestones) > 8:
                st.caption(f"{len(milestones)-8} additional entries are available in the complete person timeline.")
    route_link("See all of this relative's timeline records",
               "?page=timeline&person=" + str(person["id"]))


def render_profile_photo_story(person_id: str) -> None:
    """Give the permitted book's associated photographs a place within the story."""
    linked = linked_book_illustrations(person_id)
    route_link("Explore all photographs attributed to this person in the family gallery",
               photo_gallery_route(person_id=person_id))
    if not linked:
        return
    from family_books import book_pdf_path, load_books
    from colony_photos import source_photo_preview

    st.subheader("This relative in The Colony")
    st.caption(f"{len(linked)} photo-bearing book pages linked to this person by "
               "the existing editorial cross-reference. The book's caption is "
               "the attribution; identification is not a separate vital record.")
    books = load_books()
    asset_path = book_pdf_path(books[0]) if books else None
    shown = linked[:3]
    cols = st.columns(len(shown))
    for col, photo in zip(cols, shown):
        with col.container(border=True):
            if asset_path and asset_path.is_file():
                st.image(source_photo_preview(str(asset_path), photo["page"], photo["crop"]),
                         width="stretch")
            st.markdown("**" + photo["title"] + "**")
            st.caption("The Colony (2016), PDF page " + str(photo["page"]))
            st.write(photo["caption"])
            route_link("Open original page & printed caption", photo["url"])
    if len(linked) > len(shown):
        with st.expander(f"See all {len(linked)} linked book-photo pages"):
            for photo in linked[len(shown):]:
                route_link(str(photo["page"]) + " · " + photo["title"], photo["url"])
