"""Family-facing photograph gallery for The Colony's original historical images.

Photographs are rendered lazily from the authorized watermark-free 305-page
book already committed at static/books. Their caption summaries are attributed
to the published book; there is no inference of an unstated capture date.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from family_books import book_pdf_path, load_books, scanned_page_preview
from routing_ui import route_link

_CAPTIONS = Path(__file__).resolve().parent / "data" / "colony_photo_captions.json"
_PAGE_BATCH = 12


@st.cache_data(show_spinner=False)
def load_colony_photo_catalog() -> dict:
    return json.loads(_CAPTIONS.read_text(encoding="utf-8"))[0]


def show_more_photographs() -> None:
    st.session_state["colony_photo_visible"] = st.session_state.get("colony_photo_visible", _PAGE_BATCH) + _PAGE_BATCH


def reset_photograph_count() -> None:
    st.session_state["colony_photo_visible"] = _PAGE_BATCH


def render_colony_photographs() -> None:
    books = load_books()
    if not books:
        st.info("No family book has been cataloged.")
        return
    book = next((b for b in books if b["id"] == "colony-book-2016"), books[0])
    data = load_colony_photo_catalog()
    photos = data["photos"]
    st.write("Browse family portraits, gatherings, homes, boats, schools and island life photographed in "
             "*The Colony: Stories from a Down East Island* by Lowell P. Beveridge, Jr. (2016).")
    st.caption(
        f"{len(photos)} captioned photograph pages · The original source caption appears in each "
        "photograph preview. Summaries here are attributed to the book; unrecorded photo dates remain unknown."
    )
    categories = sorted({p["section"] for p in photos})
    search = st.text_input(
        "Search book photographs", key="colony_photo_search",
        placeholder="Orris, Red Cottage, wedding, boat, North Haven…",
        on_change=reset_photograph_count,
    ).strip().casefold()
    category = st.selectbox(
        "Photograph subject", ["All photographs", *categories],
        key="colony_photo_category", on_change=reset_photograph_count,
    )
    order = st.selectbox("Browse order", ["Book order", "Book order (last first)", "Subject A–Z"],
                         key="colony_photo_sort", on_change=reset_photograph_count)
    matches = [
        p for p in photos
        if (category == "All photographs" or category == p["section"])
        and (not search or search in " ".join((
            p["title"], p["caption_summary"], p["section"], str(p["pdf_page"])
        )).casefold())
    ]
    if order == "Book order (last first)":
        matches.reverse()
    elif order == "Subject A–Z":
        matches.sort(key=lambda item: (item["title"].casefold(), item["pdf_page"]))
    st.caption(f"{len(matches)} matching photographs — scroll to browse and load more as needed.")
    if not matches:
        st.info("No photographs matched. Try a person, place or broader subject.")
        return
    page_path = book_pdf_path(book)
    pdf_found = bool(page_path and page_path.is_file())
    if not pdf_found:
        st.warning("The book image file is unavailable in this deployment. The captions and source page references remain browseable.")
    show_count = max(_PAGE_BATCH, int(st.session_state.get("colony_photo_visible", _PAGE_BATCH)))
    visible = matches[:show_count]
    for i in range(0, len(visible), 2):
        for col, photo in zip(st.columns(2), visible[i:i+2]):
            with col.container(border=True):
                page = int(photo["pdf_page"])
                st.markdown("**" + photo["title"] + "**")
                if pdf_found:
                    # The captured image and original printed caption are in the
                    # page itself. No separately synthesized photograph is used.
                    st.image(
                        scanned_page_preview(str(page_path), page, 570, crop_content=True),
                        width="stretch",
                    )
                st.write(photo["caption_summary"])
                st.caption(
                    f"The Colony (2016), PDF page {page} · {photo['section']} · "
                    "Photograph date not independently verified"
                )
                route_link("View original scanned page and complete caption",
                           "?page=family-books&book_page="+str(page))
    if len(visible) < len(matches):
        st.button(
            f"Load 12 more photographs ({len(visible)} of {len(matches)} shown)",
            on_click=show_more_photographs,
            key="colony_photo_load_more",
            width="stretch",
        )
    else:
        st.caption("All matching book photographs are shown.")
    route_link("Read the complete 305-page illustrated family book", "?page=family-books")
