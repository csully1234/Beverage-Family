"""Authorized family-site edition of Lowell P. Beveridge Jr.'s illustrated book.

This is the full-book reader and an evidence-aware index. The user confirms
permission for reproducing the book and its images on their family website.
Scans retain the published captions, credit and original DEMO watermark.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from routing_ui import route_link

ROOT = Path(__file__).resolve().parent
BOOKS_DIR = (ROOT / "static" / "books").resolve()


def load_books() -> list[dict]:
    try:
        payload = json.loads((ROOT / "data" / "book_sources.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return payload if isinstance(payload, list) else []


def book_pdf_path(book: dict) -> Path | None:
    """Only read the single explicitly authorized local PDF folder."""
    asset = str(book.get("pdf_asset") or "")
    if not asset.startswith("static/books/") or not asset.lower().endswith(".pdf"):
        return None
    path = (ROOT / asset).resolve()
    return path if BOOKS_DIR in path.parents else None


def available_book_pdf(book: dict) -> bool:
    path = book_pdf_path(book)
    return bool(path and path.is_file())


def full_book_url(book: dict, page: int = 1) -> str:
    """Browser-native PDF with direct page navigation and user-visible credit."""
    asset = str(book.get("pdf_asset", "")).removeprefix("static/")
    # This is an allowlisted repository path, not a user-submitted external URL.
    if book_pdf_path(book) is None:
        return ""
    relative = "/app/static/" + asset
    try:
        parsed = urlsplit(str(st.context.url))
        origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""
    except Exception:
        origin = ""
    if not origin:
        origin = "https://beverage-family.onrender.com"
    return origin + relative + f"#page={int(page)}"


@st.cache_data(show_spinner=False, max_entries=42)
def scanned_page_preview(path: str, page: int, width: int = 760) -> bytes:
    """Render a single original book page, lazily, without replacing its captions."""
    import fitz
    doc = fitz.open(path)
    try:
        if page < 1 or page > doc.page_count:
            raise ValueError("Book page outside the supplied 305-page edition")
        selected = doc[page - 1]
        scale = min(1.7, width / selected.rect.width)
        pix = selected.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()


def jump_to_book_page(page: int) -> None:
    st.session_state["book_selected_page"] = int(page)
    st.query_params["page"] = "family-books"
    st.query_params["book_page"] = str(page)


def select_book_page() -> None:
    st.query_params["book_page"] = str(st.session_state["book_selected_page"])


def render_scanned_page(book: dict, page: int, *, width: int = 970) -> None:
    pdf = book_pdf_path(book)
    if pdf and pdf.is_file():
        st.image(scanned_page_preview(str(pdf), page, width), caption=(
            f"Source PDF p. {page} of {book['pdf_page_count']} · "
            f"Lowell P. Beveridge Jr., {book['title']} ({book['publication_year']}). "
            "Original caption and watermark preserved."
        ), width="stretch")
    else:
        st.info("The page image is ready to display as soon as the optimized PDF is uploaded to the repository.")
        st.caption(f"Source page {page} — the book image has not yet been published to this site's static directory.")


def illustrated_pages(book: dict) -> list[dict]:
    """Every visually identified image-bearing page, without invented descriptions."""
    curated = {entry["pdf_page"]: entry for entry in book.get("photo_leads", [])}
    return [
        {
            "pdf_page": page,
            "title": curated.get(page, {}).get("subject") or f"Illustration or archival item on PDF page {page}",
            "source_caption_verified": page in curated,
            "capture_date": curated.get(page, {}).get("capture_date"),
        }
        for page in sorted(set(book.get("image_page_numbers") or []))
    ]


def render_book_reader(book: dict) -> None:
    st.subheader("Read the complete 305-page book")
    st.caption("This is the entire edition, not selected extracts. Source PDF pages are numbered from 1.")
    path = book_pdf_path(book)
    page_count = int(book.get("pdf_page_count") or 305)
    raw_page = st.query_params.get("book_page")
    try:
        requested_page = int(raw_page) if raw_page else None
    except (ValueError, TypeError):
        requested_page = None
    if requested_page and 1 <= requested_page <= page_count and st.session_state.get("_book_last_query_page") != requested_page:
        st.session_state["book_selected_page"] = requested_page
    st.session_state["_book_last_query_page"] = requested_page
    if st.session_state.get("book_selected_page", 1) not in range(1, page_count + 1):
        st.session_state["book_selected_page"] = 1
    selected = st.number_input(
        "Go to PDF page", min_value=1, max_value=page_count,
        key="book_selected_page", step=1, on_change=select_book_page,
    )
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("← Previous page", disabled=selected <= 1, key="book_prev"):
            jump_to_book_page(selected - 1)
            st.rerun()
    with col2:
        if st.button("Next page →", disabled=selected >= page_count, key="book_next"):
            jump_to_book_page(selected + 1)
            st.rerun()
    with col3:
        if path and path.is_file():
            st.link_button("Open full book PDF in a new tab", full_book_url(book, selected), width="stretch")
    if path and path.is_file():
        st.components.v1.iframe(full_book_url(book, selected), height=720, scrolling=True)
        st.caption("Use browser PDF controls to zoom, search within any browser-indexed text, or navigate all 305 pages. The edition supplied is image-based and may not support full-text search.")
    else:
        st.warning("The full PDF is prepared but not yet committed to this website. Upload the 22 MB optimized PDF to the required static/books path; all 305 pages will then display here.")
        st.code(book.get("pdf_asset", ""), language=None)
    with st.expander("Large, readable scan of the selected page"):
        render_scanned_page(book, int(selected), width=1150)


def render_illustrations(book: dict) -> None:
    pages = illustrated_pages(book)
    st.subheader("Photographs, illustrations, maps and scanned records")
    st.write(f"{len(pages)} image-bearing pages identified across the complete book. "
             "Captions attributed to the book are marked; other images are indexed by page rather than assigned an invented identification.")
    if not pages:
        return
    page = st.selectbox("Jump to an illustrated page",
                        [item["pdf_page"] for item in pages],
                        format_func=lambda p: next(x["title"] for x in pages if x["pdf_page"] == p),
                        key="book_illustration_picker")
    entry = next(item for item in pages if item["pdf_page"] == page)
    st.markdown("**"+entry["title"]+"**")
    st.caption(f"Source PDF page {page} · Lowell P. Beveridge Jr. (2016)")
    render_scanned_page(book, page, width=950)
    st.button("Read this page in its original book context", on_click=jump_to_book_page,
              args=(page,), key="illustration_read_context")
    st.caption("The illustrated-page list includes charts, maps and decorative illustrations, not only photographs. A publication date is not a photograph's capture date.")
    with st.expander("Browse all indexed images and pages", expanded=False):
        for i in range(0, len(pages), 3):
            for col, item in zip(st.columns(3), pages[i:i+3]):
                with col.container(border=True):
                    st.markdown(f"**PDF p. {item['pdf_page']}**")
                    st.caption(item["title"])
                    st.button("View page", key=f"book_image_{item['pdf_page']}",
                              on_click=jump_to_book_page, args=(item["pdf_page"],))


def render_chapter_and_research_index(book: dict) -> None:
    st.subheader("Chapter guide")
    st.caption("Chapter titles follow the book's printed table of contents. Exact chapter-page starts are not inferred.")
    chapters = book.get("sections", [])
    for i in range(0, len(chapters), 3):
        for col, heading in zip(st.columns(3), chapters[i:i+3]):
            with col.container(border=True):
                st.write(heading)
    st.subheader("Cited historical details and family connections")
    for lead in book.get("research_leads", []):
        with st.container(border=True):
            st.markdown("**"+lead["title"]+"**")
            st.write(lead["summary"])
            st.caption(f"{book['author']}, {book['publication_year']}, source PDF p. {lead['pdf_page']}")
            with st.expander("Evidence and identity notes"):
                st.write(lead["evidence"])
            st.button("Open scanned source page", on_click=jump_to_book_page,
                      args=(lead["pdf_page"],), key="book_evidence_"+lead["id"])
    st.caption("Family memoirs are valuable primary accounts of what the author remembers, but dates and identifications should still be checked against original records when disputed.")


def render_family_books() -> None:
    st.title("Family Books & Illustrated Histories")
    for book in load_books():
        st.markdown("### " + book["title"])
        st.caption(f"{book['author']} · {book['publication_year']} · {book.get('pdf_page_count', 305)} scanned pages")
        st.write(book.get("subtitle", ""))
        st.caption("Reproduction for this family website authorized by the user; original © notice and DEMO VERSION watermark remain in the supplied scan.")
        tab_read, tab_photos, tab_chapters = st.tabs([
            "Read Entire Book", "Photographs & Illustrations", "Chapters & Historical Research"
        ])
        with tab_read:
            render_book_reader(book)
        with tab_photos:
            render_illustrations(book)
        with tab_chapters:
            render_chapter_and_research_index(book)
        route_link("Explore all family history in the timeline", "?page=timeline")


def render_book_profile_context(person: dict) -> None:
    """Relate a named source reference to a possible family profile cautiously."""
    name = str(person.get("full_name") or "").casefold()
    indexed = []
    if "amelia" in name and "bever" in name:
        indexed.append(("A photograph of Amelia and Hanson Beverage", 49))
    if "hanson" in name and "bever" in name:
        indexed.append(("A photograph of Amelia and Hanson Beverage", 49))
    if "eleazer" in name and "crabtree" in name:
        indexed.append(("A historic house attributed to Capt. Eleazer Crabtree", 21))
    if "lowell" in name and "bever" in name:
        indexed.append(("A portrait captioned Lowell Beveridge, Harvard 1925", 246))
    if "orris" in name:
        indexed.append(("An illustrated family memoir centered on Orris", 1))
    if not indexed:
        return
    with st.container(border=True):
        st.markdown("**Referenced in an illustrated family history**")
        st.write("Lowell P. Beveridge, Jr., *The Colony: Stories from a Down East Island* (2016).")
        for label, page in indexed:
            route_link(label+" · source page "+str(page),
                       "?page=family-books&book_page="+str(page))
        st.caption("Source captions are documented; identifying the person in a scanned image with this exact profile may still require corroboration.")
