"""Careful, bibliographic display of a privately supplied family-history ebook.

The scanned book includes a restrictive 2016 copyright notice. This module
publishes original bibliographic metadata and nonverbatim topic/illustration
leads, NEVER source pages or embedded book photos without explicit clearance.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from routing_ui import route_link


def load_books() -> list[dict]:
    path=Path(__file__).resolve().parent / "data" / "book_sources.json"
    try:
        books=json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return books if isinstance(books,list) else []


def render_family_books() -> None:
    st.title("Family Books & Illustrated Histories")
    st.write("Find published family stories, chapter topics and original-photo leads. Book pages and copyrighted photographs are reproduced here only after reuse permission is recorded.")
    for book in load_books():
        with st.container(border=True):
            st.subheader(book["title"])
            st.caption(f"{book['author']} · {book['publication_year']}")
            st.write(book["subtitle"])
            st.markdown("**What the book covers**")
            st.write(", ".join(book["sections"]) + ".")
            st.info("This is a bibliographic and research index, not a publicly shared ebook. " +
                    "The family-provided digital edition restricts redistribution; permission is required before hosting pages or images.")
            with st.expander("Historical interpretation and source details"):
                st.write(book["source_limit"])
                st.caption(book["digital_copy"])
                st.caption(book["rights"])
            st.markdown("**Historically interesting passages to cross-check**")
            for lead in book.get("research_leads", []):
                with st.expander(f"PDF p. {lead['pdf_page']} · {lead['title']}"):
                    st.write(lead["summary"])
                    st.caption(lead["evidence"])
            st.markdown("**Photographs and illustrations to source**")
            st.caption("The pages below identify items in the private edition. Their original image files are not yet licensed for website display.")
            for lead in book["photo_leads"]:
                with st.container(border=True):
                    st.markdown(f"**PDF page {lead['pdf_page']} — {lead['subject']}**")
                    st.caption(lead["certainty"])
                    st.caption(lead["status"])
            route_link("Browse all family photographs and archive references", "?page=media")

def render_book_profile_context(person: dict) -> None:
    """Connect named book subjects without asserting uncertain identity matches."""
    name = str(person.get("full_name") or "").casefold()
    if not any(token in name for token in ("orris", "amelia beverage", "hanson beverage", "eleazer crabtree")):
        return
    with st.container(border=True):
        st.markdown("**Related published family-history book**")
        st.write("Lowell P. Beveridge, Jr., *The Colony: Stories from a Down East Island* (2016) includes family recollections and images involving this name or family context.")
        st.caption("A shared name or recollection is not an independently established genealogical identification.")
        route_link("Explore the book's chapters and photograph leads", "?page=family-books")
