"""Family-facing photograph gallery for The Colony's original historical images.

Photographs are rendered lazily from the authorized watermark-free 305-page
book already committed at static/books. Their caption summaries are attributed
to the published book; there is no inference of an unstated capture date.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from family_books import book_pdf_path, load_books, load_book_person_crosswalk
from family_data import index_people, load_site_data
from routing_ui import route_link
from family_photo_navigation import (photo_gallery_route, exact_photo_pages,
                                     photo_matches, selected_photo)

_CAPTIONS = Path(__file__).resolve().parent / "data" / "colony_photo_captions.json"
_PAGE_BATCH = 12


@st.cache_data(show_spinner=False, max_entries=100)
def source_photo_preview(path: str, page_number: int, crop: tuple[float, float, float, float]) -> bytes:
    """Render a cataloged photographic region without changing the original scan."""
    import fitz

    document = fitz.open(path)
    try:
        page = document[page_number - 1]
        bounds = page.rect
        x0, y0, x1, y1 = crop
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise ValueError("Catalog has invalid book photograph coordinates")
        clip = fitz.Rect(
            bounds.x0 + x0 * bounds.width, bounds.y0 + y0 * bounds.height,
            bounds.x0 + x1 * bounds.width, bounds.y0 + y1 * bounds.height,
        )
        zoom = min(2.6, 650 / clip.width)
        return page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False).tobytes("png")
    finally:
        document.close()


@st.cache_data(show_spinner=False)
def load_colony_photo_catalog() -> dict:
    return json.loads(_CAPTIONS.read_text(encoding="utf-8"))[0]


def show_more_photographs() -> None:
    st.session_state["colony_photo_visible"] = st.session_state.get("colony_photo_visible", _PAGE_BATCH) + _PAGE_BATCH


def reset_photograph_count() -> None:
    st.session_state["colony_photo_visible"] = _PAGE_BATCH


def _photo_person_changed() -> None:
    """Keep person selection bookmarkable and reset stale gallery filters."""
    selected = str(st.session_state.get("colony_photo_person") or "")
    if selected:
        st.query_params["person"] = selected
    elif "person" in st.query_params:
        del st.query_params["person"]
    if "photo_page" in st.query_params:
        del st.query_params["photo_page"]
    st.session_state["_colony_photo_last_query_person"] = selected
    st.session_state["colony_photo_search"] = ""
    st.session_state["colony_photo_category"] = "All photographs"
    reset_photograph_count()


def _photo_card(photo: dict, *, book: dict, people_by_page: dict,
                people_index: dict, page_path: Path | None,
                featured: bool = False) -> None:
    """Both featured and ordinary cards show original sources and honest identity labels."""
    page = int(photo["pdf_page"])
    st.markdown("**" + str(photo["title"]) + "**")
    if page_path and page_path.is_file():
        source = source_photo_preview(str(page_path), page, tuple(photo["preview_crop"]))
        st.image(source, width="stretch")
    st.write(photo["caption_summary"])
    capture = photo.get("reported_capture_date")
    date_note = (f"Book caption dates image {capture}; independently unverified"
                 if capture else "Photograph date not documented in the catalog")
    st.caption(f"The Colony (2016), PDF p. {page} · {photo['section']} · {date_note}")
    route_link("View original scanned page and complete printed caption",
               "?page=family-books&book_page=" + str(page))
    route_link("Share this photograph's direct gallery link",
               photo_gallery_route(pdf_page=page), type="tertiary")
    linked = people_by_page.get(page, [])
    if linked:
        st.caption("Profiles mentioned by the book's photo index (not independently verified identities)")
        for match in linked:
            pid = str(match.get("person_id") or "")
            if pid not in people_index:
                continue
            record = people_index[pid]
            label = str(record.get("full_name") or pid)
            confidence = str(match.get("confidence") or "").lower()
            if "candidate" in confidence or "uncertain" in confidence:
                label += " · identity needs verification"
            route_link(label, "?page=people&profile=" + quote(pid, safe=""))
            route_link("See this relative's other attributed photographs",
                       photo_gallery_route(person_id=pid), type="tertiary")


def render_colony_photographs() -> None:
    books = load_books()
    if not books:
        st.info("No family book has been cataloged.")
        return
    book = next((b for b in books if b["id"] == "colony-book-2016"), books[0])
    data = load_colony_photo_catalog()
    photos = data["photos"]
    people_index = index_people(load_site_data(_CAPTIONS.parent)["people"])
    crosswalk = load_book_person_crosswalk()
    exact_pages = exact_photo_pages(crosswalk, set(people_index))
    # Author-attributed identity candidates stay labeled; never infer a person
    # from OCR or a name in a visually similar family photograph.
    people_by_page: dict[int, list[dict]] = {}
    for person in crosswalk.get("linked_people", []):
        pid = str(person.get("person_id") or "")
        if pid not in people_index:
            continue
        for page_num in exact_pages.get(pid, set()):
            people_by_page.setdefault(page_num, []).append(person)

    st.write("Browse family portraits, gatherings, homes, boats, schools and island life "
             "photographed in *The Colony* by Lowell P. Beveridge, Jr. (2016). "
             "Follow any photograph back to its printed caption or a related person.")
    st.caption(str(len(photos)) + " cataloged photo-bearing pages; the author's "
               "identifications are historical source attributions, not independent "
               "proof of identity or photograph date.")
    selected_from_url = str(st.query_params.get("person", "") or "")
    if selected_from_url and selected_from_url not in people_index:
        st.warning("That relative isn't indexed in this family archive. The complete photo gallery is available below.")
        selected_from_url = ""
    # Update the Streamlit widget state only BEFORE the selectbox is created.
    if st.session_state.get("_colony_photo_last_query_person") != selected_from_url:
        st.session_state["colony_photo_person"] = selected_from_url
        st.session_state["colony_photo_search"] = ""
        st.session_state["colony_photo_category"] = "All photographs"
        reset_photograph_count()
        st.session_state["_colony_photo_last_query_person"] = selected_from_url

    photo_person_ids = sorted(exact_pages, key=lambda pid:
                             (str(people_index[pid].get("full_name") or pid).casefold(), pid))
    if selected_from_url and selected_from_url not in photo_person_ids:
        # A real relative without attributed photo pages is valid; don't
        # silently apply a misleading different-person gallery filter.
        options = ["", selected_from_url, *photo_person_ids]
    else:
        options = ["", *photo_person_ids]
    focus = st.selectbox(
        "Show photographs of a relative",
        options, key="colony_photo_person", on_change=_photo_person_changed,
        format_func=lambda pid: (str(people_index[pid].get("full_name") or pid)
                                  if pid else "Everyone / all photographs"),
    )
    if focus:
        route_link("Open this relative's complete life and original records",
                   "?page=collection&view=person-exhibit&person=" + quote(focus, safe=""))
        number = len(exact_pages.get(focus, set()) &
                     {int(photo["pdf_page"]) for photo in photos})
        st.caption(f"{number} photographed source page(s) explicitly attributed "
                   "to this profile in the book index. This is a historical "
                   "attribution, not an independent identity determination.")
        if not number:
            st.info("No cataloged photograph is attributed to this relative by exact "
                    "profile ID. That doesn't mean they never appeared in a historical "
                    "photo. Browse all photographs or search the complete scanned book.")
            route_link("Return to all family photographs", photo_gallery_route())
            route_link("Research this relative in the entire scanned family book",
                       "?page=collection&view=workbench&person=" + quote(focus, safe=""))
    categories = sorted({p["section"] for p in photos})
    search = st.text_input(
        "Search book photographs", key="colony_photo_search",
        placeholder="Orris, Red Cottage, wedding, boat, North Haven…",
        on_change=reset_photograph_count,
    ).strip()
    category = st.selectbox(
        "Photograph subject", ["All photographs", *categories],
        key="colony_photo_category", on_change=reset_photograph_count,
    )
    order = st.selectbox(
        "Browse order", ["Book order", "Book order (last first)", "Subject A–Z"],
        key="colony_photo_sort", on_change=reset_photograph_count,
    )
    names = {pid: str(p.get("full_name") or pid) for pid, p in people_index.items()}
    matches = photo_matches(photos, crosswalk, person_id=focus,
                            search=search, category=category, order=order, names=names)
    st.caption(f"{len(matches)} matching photo-bearing source pages · browse every "
               "result by loading more. A photo's printed source caption is always "
               "accessible through its original book page.")

    page_path = book_pdf_path(book)
    if not page_path or not page_path.is_file():
        st.warning("The book image file is unavailable on this deployment; its "
                   "catalog descriptions and source references remain browseable.")
    requested = st.query_params.get("photo_page")
    target = selected_photo(photos, requested)
    if requested and target is None:
        st.caption("That page is not a cataloged standalone photograph. "
                   "Open the original book to read all illustrations and text.")
        if str(requested).isdigit() and 1 <= int(requested) <= 305:
            route_link("Read source book page " + str(requested),
                       "?page=family-books&book_page=" + str(requested))
    # A bookmarked photograph is presented FIRST, independent of pagination.
    # A person's filter never silently implies a selected photo belongs to
    # them. Keep the target even if the person-filter currently excludes it.
    if target is not None:
        page = int(target["pdf_page"])
        attributed_to_focus = not focus or page in exact_pages.get(focus, set())
        if focus and not attributed_to_focus:
            st.info("This bookmarked photo is not attributed to the selected relative "
                    "in the book's person crosswalk. Showing it separately, "
                    "not as proof of a family connection.")
        st.subheader("Selected historical photograph · source page " + str(page))
        with st.container(border=True):
            _photo_card(target, book=book, people_by_page=people_by_page,
                        people_index=people_index, page_path=page_path, featured=True)
        route_link("Browse all photographs without a pinned page",
                   photo_gallery_route(person_id=focus))
        st.divider()
    remaining = [photo for photo in matches
                 if target is None or int(photo["pdf_page"]) != int(target["pdf_page"])]
    count = max(_PAGE_BATCH, int(st.session_state.get("colony_photo_visible", _PAGE_BATCH)))
    visible = remaining[:count]
    if not remaining:
        if target is None:
            st.info("No photographs matched. Try another relative, place, "
                    "subject, or clear the search.")
    for i in range(0, len(visible), 2):
        for col, photo in zip(st.columns(2), visible[i:i + 2]):
            with col.container(border=True):
                _photo_card(photo, book=book, people_by_page=people_by_page,
                            people_index=people_index, page_path=page_path)
    if len(visible) < len(remaining):
        st.button(
            f"Load 12 more photographs ({len(visible)} of {len(remaining)} shown)",
            on_click=show_more_photographs,
            key="colony_photo_load_more",
            width="stretch",
        )
    elif visible:
        st.caption("All matching photographs are shown.")
    route_link("Read the complete 305-page illustrated family book", "?page=family-books")
