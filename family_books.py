"""Authorized family-site edition of Lowell P. Beveridge Jr.'s illustrated book.

This is the full-book reader and an evidence-aware index. The user confirms
permission for reproducing the book and its images on their family website.
Scans retain published captions and credit; the uploaded edition has no demo overlay.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from routing_ui import route_link
from family_data import index_people, load_site_data
from identity_casework import cases_for_page, render_case_evidence, render_identity_explorer

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


def display_authorized_book(book: dict, *, height: int = 720) -> bool:
    """Render the complete book inside Streamlit, never via public /app/static.

    Called only from a password-gated family page. st.pdf uses the runtime media
    manager; its opaque media URLs are not a substitute for HTTP-layer access
    controls. Moving GitHub private and enforcing file-response authorization
    remain separate migration steps.
    """
    local = book_pdf_path(book)
    if not local or not local.is_file():
        return False
    st.pdf(local, height=height, key="family_original_book_pdf")
    return True


@st.cache_data(show_spinner=False, max_entries=42)
def scanned_page_preview(path: str, page: int, width: int = 760, crop_content: bool = False) -> bytes:
    """Render an original scanned book page. Crop only gallery preview whitespace."""
    import fitz
    from PIL import Image
    from io import BytesIO
    doc = fitz.open(path)
    try:
        if page < 1 or page > doc.page_count:
            raise ValueError("Book page outside the supplied edition")
        selected = doc[page - 1]
        scale = min(1.7, width / selected.rect.width)
        pix = selected.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        if not crop_content:
            return pix.tobytes("png")
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        dark_ink = image.convert("L").point(lambda v: 255 if v < 135 else 0)
        bounds = dark_ink.getbbox()
        if bounds:
            left, top, right, bottom = bounds
            pad = 22
            if right-left < image.width * .86 and bottom-top < image.height * .86:
                image = image.crop((max(0,left-pad),max(0,top-pad),
                                    min(image.width,right+pad),min(image.height,bottom+pad)))
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()
    finally:
        doc.close()


def jump_to_book_page(page: int) -> None:
    st.session_state["book_selected_page"] = int(page)
    st.query_params["page"] = "family-books"
    st.query_params["book_page"] = str(page)


def select_book_page() -> None:
    st.query_params["book_page"] = str(st.session_state["book_selected_page"])


def render_scanned_page(book: dict, page: int, *, width: int = 970, crop: bool = False) -> None:
    pdf = book_pdf_path(book)
    if pdf and pdf.is_file():
        st.image(scanned_page_preview(str(pdf), page, width, crop_content=crop), caption=(
            f"Source PDF p. {page} of {book['pdf_page_count']} · "
            f"Lowell P. Beveridge Jr., {book['title']} ({book['publication_year']}). "
            "Original printed caption preserved in the cleaned scan."
        ), width="stretch")
    else:
        st.info("The original PDF page is not present on this deployment. "
                "Please consult the archival source or notify the site maintainer.")
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
    # Streamlit runs button callbacks *before* constructing widgets on the
    # following rerun. Never assign book_selected_page from an if st.button()
    # block after its st.number_input has been instantiated.
    with col1:
        st.button(
            "← Previous page", disabled=selected <= 1, key="book_prev",
            on_click=jump_to_book_page, args=(int(selected) - 1,),
        )
    with col2:
        st.button(
            "Next page →", disabled=selected >= page_count, key="book_next",
            on_click=jump_to_book_page, args=(int(selected) + 1,),
        )
    with col3:
        st.caption("The complete illustrated edition is available in the reader below. The selected-page controls also display a large scan.")
    if path and path.is_file():
        st.caption("Full 305-page book viewer. Browse, zoom and use available PDF controls. For the exact page selected above, open the large source scan below.")
        display_authorized_book(book)
        st.caption("The book is image-based, so built-in text search may be limited. Scanned pages and photo captions remain searchable through the existing research index.")
    else:
        st.warning("The authorized book PDF is not available to this running deployment. "
                   "The source-file audit should verify the published asset before release.")
        st.code(book.get("pdf_asset", ""), language=None)
    with st.expander("Large, readable scan of the selected page"):
        render_scanned_page(book, int(selected), width=1150)
    render_book_page_connections(int(selected))
    from colony_source_review import render_page_review_notes
    render_page_review_notes(int(selected))
    route_link("Investigate every indexed source associated with this scanned page",
               "?page=collection&view=workbench&book_page=" + str(int(selected)))


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
    render_scanned_page(book, page, width=950, crop=True)
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
        if book.get("author_person_id"):
            route_link("Meet the author and explore his family connections",
                       "?page=people&profile=" + str(book["author_person_id"]))
        st.write(book.get("subtitle", ""))
        st.caption("Reproduction for this family website authorized by the user; original © notice remains and the source-page demo overlay was removed from the clean web edition.")
        tab_read, tab_photos, tab_chapters, tab_people, tab_search, tab_review = st.tabs([
            "Read Entire Book", "Photographs & Illustrations",
            "Chapters & Historical Research", "People & identity questions",
            "Search scanned pages", "Source review & expanded OCR"
        ])
        with tab_read:
            render_book_reader(book)
        with tab_photos:
            render_illustrations(book)
        with tab_chapters:
            render_chapter_and_research_index(book)
        with tab_people:
            render_identity_explorer()
            st.divider()
            render_book_people_index(expanded=False)
            render_book_identity_questions()
        with tab_search:
            render_book_ocr_navigation()
            route_link("Compare names and original sources throughout the entire family archive",
                       "?page=collection&view=workbench")
        with tab_review:
            from colony_source_review import render_source_review_notebook, render_expanded_ocr_finder
            render_expanded_ocr_finder()
            st.divider()
            render_source_review_notebook()
        route_link("Explore all family history in the timeline", "?page=timeline")


def render_book_profile_context(person: dict) -> None:
    """Link the book author and identified image subjects by stable person ID.

    Names alone are not sufficient: father and son are both Lowell Pierson
    Beveridge, but the 1923 Harvard portrait is of Lowell Sr. and the 2016
    author is Lowell Jr. Never infer an image match from shared name text.
    """
    person_id = str(person.get("id") or "")
    indexed = {
        "amelia_beverage_1833": [("A photograph of Amelia and Hanson Beverage", 49)],
        "amelia_beverage_1833_child": [("A photograph of Amelia and Hanson Beverage (verify identification)", 49)],
        "dana_hanson_beverage_1847": [("Photograph of Amelia with brother Hanson (identity to corroborate)", 49)],
        "eleazer_crabtree_1760": [("A historic house attributed to Capt. Eleazer Crabtree", 21)],
        "lowell_beveridge_1905": [("Lowell Beveridge's Harvard class picture, 1923", 246)],
        "orris_beverage_1860": [("An illustrated memoir about Orris", 1)],
    }.get(person_id, [])
    is_author = person_id == "lowell_pierson_beveridge_jr_1930"
    if not indexed and not is_author:
        return
    with st.container(border=True):
        if is_author:
            st.markdown("**Family-book author — Lowell P. Beveridge Jr.**")
            st.write("This person wrote *The Colony: Stories from a Down East Island* (2016). "
                     "He is the son of Lowell Pierson Beveridge (1905–1991), whose "
                     "Harvard student portrait is a different person's image.")
            route_link("Read Lowell Jr.'s entire illustrated family book", "?page=family-books")
        else:
            st.markdown("**Referenced in an illustrated family history**")
            st.write("Lowell P. Beveridge, Jr., *The Colony: Stories from a Down East Island* (2016).")
            for label, page in indexed:
                route_link(label + " · source page " + str(page),
                           "?page=family-books&book_page=" + str(page))
            st.caption("A captioned photograph may still require independent confirmation of its subject.")


def load_book_person_crosswalk() -> dict:
    """Read explicit family-photo-caption matches with their evidence limits."""
    path = ROOT / "data" / "colony_people_crosswalk.json"
    if not path.is_file():
        return {"linked_people": [], "unresolved_people": []}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw[0] if isinstance(raw, list) and raw else {"linked_people": [], "unresolved_people": []}


def book_pages_for_person(person_id: str, catalog: dict | None = None) -> list[int]:
    """Return only stable-ID matches, never a fuzzy name collision."""
    catalog = catalog if catalog is not None else load_book_person_crosswalk()
    pages = []
    for item in catalog.get("linked_people", []):
        if item.get("person_id") == person_id:
            pages.extend(int(page) for page in item.get("pdf_pages", []))
    return sorted(set(pages))


def render_book_profile_crosswalk_context(person: dict) -> None:
    """Original book-image citations for this profile, not inferred relatives."""
    person_id = str(person.get("id") or "")
    catalog = load_book_person_crosswalk()
    entries = [row for row in catalog.get("linked_people", [])
               if row.get("person_id") == person_id]
    if not entries:
        return
    pages = book_pages_for_person(person_id, catalog)
    with st.expander(f"See this relative in The Colony (2016) — {len(pages)} illustrated pages"):
        st.caption("Author-attributed image captions are family testimony, not independently "
                   "verified birth or marriage certificates. Not every name in the "
                   "305-page book has yet been individually reviewed.")
        for entry in entries:
            st.write(str(entry.get("summary") or ""))
            if str(entry.get("confidence") or "").startswith("candidate"):
                st.warning("The book photo may refer to a different person with this name.")
        for page in pages:
            route_link(f"Open original book page {page}",
                       "?page=family-books&book_page=" + str(page))
        if pages and st.toggle("View a scanned page here", value=False,
                               key="profile_scan_toggle_" + person_id):
            chosen = st.selectbox("Select original page", pages,
                                  key="profile_scan_page_" + person_id)
            books = load_books()
            if books:
                render_scanned_page(books[0], int(chosen), width=830)
                st.caption(f"The Colony (2016), PDF page {chosen}. The original "
                           "caption is shown in the scan; identifiers remain "
                           "subject to source review.")


def render_book_people_index(*, expanded: bool = False) -> None:
    """Index confirmed/candidate identity links and unresolved book names."""
    catalog = load_book_person_crosswalk()
    linked = catalog.get("linked_people", [])
    pending = catalog.get("unresolved_people", [])
    people_index = index_people(load_site_data(ROOT / "data")["people"])
    with st.expander("People in The Colony — tree matches and unresolved names", expanded=expanded):
        st.caption(
            f"{len(linked)} indexed person references and {len(pending)} pending name "
            "or relationship questions from 82 photograph-bearing pages. "
            "This is NOT a complete scan of all 305 pages."
        )
        for item in linked:
            person = people_index.get(str(item["person_id"]), {})
            label = str(person.get("full_name") or item["person_id"].replace("_", " "))
            if str(item.get("confidence") or "").startswith("candidate"):
                label += " · possible match only"
            route_link(label, "?page=people&profile=" + item["person_id"])
            pages = item.get("pdf_pages", [])
            if pages:
                st.caption("Source PDF pages: " + ", ".join(map(str, pages)))
        if pending:
            st.markdown("**Not yet safe to attach to the family tree**")
            for item in pending:
                with st.container(border=True):
                    st.markdown("**" + str(item.get("name") or "Unresolved person") + "**")
                    st.write(str(item.get("issue") or ""))
                    for page in item.get("pages", []):
                        route_link(f"Open original book page {page}",
                                   "?page=family-books&book_page=" + str(page))


# Add the photo-page crosswalk without losing the existing author biography,
# which distinguishes the father from the 2016 book author.
_original_book_profile_context = render_book_profile_context

def render_book_profile_context(person: dict) -> None:
    _original_book_profile_context(person)
    render_book_profile_crosswalk_context(person)



def book_page_connections(page: int, catalog: dict | None = None) -> dict:
    """Exact catalog page crosswalk; candidates never masquerade as confirmed."""
    catalog = catalog if catalog is not None else load_book_person_crosswalk()
    return {
        "linked": [row for row in catalog.get("linked_people", [])
                   if int(page) in [int(p) for p in row.get("pdf_pages", [])]],
        "unresolved": [row for row in catalog.get("unresolved_people", [])
                       if int(page) in [int(p) for p in row.get("pages", [])]],
    }


def render_book_page_connections(page: int) -> None:
    """Bring supporting and unresolved name evidence beside the original page."""
    matches = book_page_connections(page)
    research = cases_for_page(page)
    if not matches["linked"] and not matches["unresolved"] and not research:
        return
    st.subheader("Explore the people mentioned on this source page")
    st.caption("Page associations come from the book-photo index. A caption is "
               "a published attribution, not an independent identity record.")
    people = index_people(load_site_data(ROOT / "data")["people"])
    for entry in matches["linked"]:
        person_id = str(entry["person_id"])
        person = people.get(person_id)
        if not person:
            continue
        label = str(person.get("full_name") or person_id.replace("_", " "))
        if str(entry.get("confidence", "")).startswith("candidate"):
            label += " · candidate"
        route_link("Open family tree profile: " + label,
                   "?page=people&profile=" + person_id)
    for item in matches["unresolved"]:
        st.info(f"**Identity still under review: {item['name']}** — "
                f"{item.get('issue', 'Source identification requires corroboration.')}")
        for evidence in item.get("independent_sources", []):
            st.caption(str(evidence.get("finding", "")))
            if evidence.get("url"):
                route_link(str(evidence.get("title", "Inspect other original record")),
                           str(evidence["url"]))
    for case in research:
        with st.expander("More original evidence: " + str(case.get("name", ""))):
            render_case_evidence(case, show_book_links=False)


def render_book_identity_questions() -> None:
    """Searchable editorial workbench, without adding unproved genealogy edges."""
    cases = load_book_person_crosswalk().get("unresolved_people", [])
    st.subheader("Historical names requiring verification")
    st.caption(f"{len(cases)} remaining caption-index questions. Published names "
               "are research leads, not proof of kinship; non-family cottage "
               "occupants stay in the historical context rather than the tree.")
    search = st.text_input("Search unresolved names and places",
                           placeholder="Florence, Hanson, Priscilla, 1936…",
                           key="colony_case_search").strip().casefold()
    dispositions = sorted({str(item.get("disposition", "research_before_add"))
                           for item in cases})
    choice = st.selectbox("Research category", ["All questions", *dispositions],
                          key="colony_case_category")
    filtered = [item for item in cases if
                (choice == "All questions" or item.get("disposition") == choice)
                and (not search or search in (
                    str(item.get("name", "")) + " " +
                    str(item.get("issue", "")) + " " +
                    " ".join(str(page) for page in item.get("pages", []))
                ).casefold())]
    st.caption(f"{len(filtered)} matching questions")
    for item in filtered:
        with st.expander(str(item.get("name") or "Unresolved person")):
            st.write(str(item.get("issue") or "Identity not yet established."))
            st.caption("Research disposition: " +
                       str(item.get("disposition", "research_before_add")).replace("_", " "))
            for evidence in item.get("independent_sources", []):
                st.write(str(evidence.get("finding", "")))
                if evidence.get("url"):
                    route_link(str(evidence.get("title", "Inspect published record")),
                               str(evidence["url"]))
            for page in sorted(set(item.get("pages", []))):
                route_link(f"Review the original book page {page}",
                           "?page=family-books&book_page=" + str(page))


def load_book_ocr_navigation() -> dict:
    """Curated word/page presence only, not an OCR transcript or genealogy."""
    path = ROOT / "data" / "colony_ocr_navigation_index.json"
    if not path.exists():
        return {"scanned_pages": 0, "hits": {}}
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = raw[0] if isinstance(raw, list) and raw else raw
    return data if isinstance(data, dict) else {"scanned_pages": 0, "hits": {}}


def render_book_ocr_navigation() -> None:
    """Find likely scanned pages; visitors confirm all hits in original images."""
    nav = load_book_ocr_navigation()
    st.subheader("Find a name or topic across the scanned book")
    st.caption("These are *automatically detected word occurrences* in scanned pages, "
               "**not** verified genealogical identities, dates or transcriptions. "
               "OCR can misread names and miss printed words. Select any result "
               "to verify the original page and caption yourself.")
    if not nav.get("hits"):
        st.info("The research text index is not published yet; the original "
                "305-page scan remains fully available in Read Entire Book.")
        return
    st.caption(f"Coverage: {nav.get('scanned_pages', 0)} PDF page images. "
               "Original book scan is the authoritative evidence.")
    hits = nav["hits"]
    search = st.text_input("Find a name or historical topic",
                           placeholder="Orris, Priscilla, Rose, schooner, Point…",
                           key="colony_ocr_term_query").strip().casefold()
    matching = [term for term in sorted(hits, key=str.casefold)
                if not search or search in term.casefold()]
    st.caption(f"{len(matching)} matching indexed terms")
    if not matching:
        st.info("That name is not in the curated OCR navigation vocabulary. "
                "Absence does not prove it is absent from the book.")
        return
    term = st.selectbox("Indexed search term", matching, key="colony_ocr_term")
    pages = [int(page) for page in hits.get(term, [])]
    st.write(f"Possible printed occurrences for **{term}**: {len(pages)} pages")
    if pages:
        chosen = st.selectbox("Original PDF page", pages, key="colony_ocr_result_page")
        route_link(f"Open scanned page {chosen} and related identities",
                   "?page=family-books&book_page=" + str(chosen))
        st.caption("Search hits are tentative until visually checked on the "
                   "relevant scanned page. They do not create tree connections.")
