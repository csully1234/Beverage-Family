"""Stable, evidence-limited navigation between people, photographs and book pages.

The photo catalog describes photographed *pages*, not identities proved by
face recognition. Only the manually attributed exact-person crosswalk may
drive the person filter. Do not match people by OCR text or surnames.
"""
from __future__ import annotations

from urllib.parse import quote


def photo_gallery_route(person_id: str = "", pdf_page: int | None = None) -> str:
    """A shareable route that preserves precise selected person and source page."""
    url = "?page=media"
    if person_id:
        url += "&person=" + quote(str(person_id), safe="")
    if pdf_page is not None and int(pdf_page) > 0:
        url += "&photo_page=" + str(int(pdf_page))
    return url


def exact_photo_pages(crosswalk: dict, valid_person_ids: set[str] | None = None
                      ) -> dict[str, set[int]]:
    """Page-ID indexes include candidates as *attributions*, not confirmations."""
    result: dict[str, set[int]] = {}
    for link in crosswalk.get("linked_people", []):
        pid = str(link.get("person_id") or "")
        if not pid or (valid_person_ids is not None and pid not in valid_person_ids):
            continue
        pages = result.setdefault(pid, set())
        for number in link.get("pdf_pages", []):
            try:
                page = int(number)
            except (ValueError, TypeError):
                continue
            if page > 0:
                pages.add(page)
    return result


def photo_matches(
    photos: list[dict], crosswalk: dict,
    *, person_id: str = "", search: str = "",
    category: str = "All photographs", order: str = "Book order",
    names: dict[str, str] | None = None,
) -> list[dict]:
    """All matching photo pages, without a first-12 or first-25 search cap."""
    names = names or {}
    attributed = exact_photo_pages(crosswalk)
    pages = attributed.get(person_id, set()) if person_id else None
    page_people: dict[int, list[str]] = {}
    for pid, linked_pages in attributed.items():
        for page in linked_pages:
            page_people.setdefault(page, []).append(names.get(pid, ""))
    term = str(search).strip().casefold()
    rows = [
        p for p in photos
        if (pages is None or int(p["pdf_page"]) in pages)
        and (category == "All photographs" or p["section"] == category)
        and (not term or term in " ".join((
            str(p.get("title") or ""),
            str(p.get("caption_summary") or ""),
            str(p.get("section") or ""),
            str(p.get("pdf_page") or ""),
            *page_people.get(int(p["pdf_page"]), []),
        )).casefold())
    ]
    if order == "Book order (last first)":
        return sorted(rows, key=lambda p: int(p["pdf_page"]), reverse=True)
    if order == "Subject A–Z":
        return sorted(rows, key=lambda p: (str(p["title"]).casefold(),
                                            int(p["pdf_page"])))
    return sorted(rows, key=lambda p: int(p["pdf_page"]))


def selected_photo(photos: list[dict], pdf_page: str | int | None) -> dict | None:
    """Bookmarks can select a real cataloged photo page, never an invented item."""
    try:
        number = int(pdf_page) if pdf_page is not None else 0
    except (ValueError, TypeError):
        return None
    return next((p for p in photos if int(p["pdf_page"]) == number), None)
