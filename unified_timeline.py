"""Unified archive chronology: evidence status never suppresses historical material."""
from __future__ import annotations

import json
import re
from urllib.parse import quote

import streamlit as st

from family_data import format_date, life_span, year_from_date
from research_collection_ui import load_collection
from routing_ui import route_link
from visitor_ui import STORIES, DOCUMENTS, approved_assets


def historical_year(value: object) -> int | None:
    text = str(value or "").strip()
    if not text or re.search(r"\b(?:17|18|19|20)\s*(?:th|st)\s+centur", text, re.I):
        return None
    # Distinguish broad source coverage (e.g. 1700s–1900s records)
    # from a dated historical occurrence.
    if re.search(r"\b(?:1[6-9]|20)00s\b", text, re.I):
        return None
    match = re.search(r"(?<!\d)(1[6-9]\d{2}|20\d{2})(?!\d)", text)
    return int(match.group(1)) if match else None


def build_chronology(data: dict, people_by_id: dict, collection=None) -> list[dict]:
    """Show historical people/events/discoveries, never research activity rows.

    Every evidence level of *historical* findings remains included; research
    logs, unexamined work queues and source-register administration live only
    in archived files for provenance.
    """
    collection = collection or load_collection()
    items = []
    def add(kind, identifier, title, date, description, link, person_ids=(), certainty="", date_kind="Event or source date", extra=""):
        year = historical_year(date)
        items.append({"type":kind,"id":identifier,"title":str(title),"date":str(date or "Undated"),
                      "year":year,"description":str(description or ""),"url":link,
                      "person_ids":tuple(person_ids or ()),"certainty":str(certainty or "Not rated"),
                      "date_kind":date_kind, "extra":str(extra or "")})
    for event in data.get("events", []):
        date = format_date(event.get("date"), event.get("date_precision"))
        add("Timeline event",event["id"],event.get("title","Event"),date,event.get("description",""),
            "?page=timeline&event="+quote(event["id"]),event.get("people_involved",[]),
            event.get("evidence_status",""), "Event date")
    for person in data.get("people", []):
        if person.get("birth_date"):
            add("Life event",person["id"]+":birth",str(person.get("full_name","Person"))+" — birth",
                format_date(person["birth_date"],person.get("birth_date_precision")),
                "Date as entered in this person's profile.",
                "?page=people&profile="+quote(person["id"]),[person["id"]],
                person.get("evidence_status",""),"Birth date")
        if person.get("death_date"):
            add("Life event",person["id"]+":death",str(person.get("full_name","Person"))+" — death",
                format_date(person["death_date"],person.get("death_date_precision")),
                "Date as entered in this person's profile.",
                "?page=people&profile="+quote(person["id"]),[person["id"]],
                person.get("evidence_status",""),"Death date")
        if person.get("baptism_date"):
            add("Life event",person["id"]+":baptism",str(person.get("full_name","Person"))+" — baptism",
                format_date(person["baptism_date"],person.get("baptism_date_precision")),
                "Baptism recorded separately from an unverified birth date.",
                "?page=people&profile="+quote(person["id"]),[person["id"]],
                person.get("evidence_status",""),"Baptism date")
    for finding in collection.findings.values():
        nav = finding.get("Navigation",{})
        raw = finding.get("Date or date range","")
        # Publication years, broad period labels and dates mentioned in prose
        # are preserved as research chronology, not upgraded to event dates.
        add("Research finding",finding["Research ID"],nav.get("title",finding["Research ID"]),
            raw, finding.get("Proposed fact or narrative",""),
            "?page=collection&finding="+quote(finding["Research ID"]),
            nav.get("people_ids",[]),finding.get("Confidence",""),
            "Research-associated date",finding.get("Notes about uncertainty",""))
    # Reviewed historical locations and provenance entries are also part of
    # the chronology, including approximate dates. Place links are not deeds.
    from archive import ArchiveIndex
    archive = ArchiveIndex(data)
    for link in archive.links:
        place = archive.places.get(link["place_id"])
        subject = (archive.people if link["subject_type"] == "person" else archive.events).get(link["subject_id"], {})
        subject_name = subject.get("full_name") or subject.get("title") or "Historical record"
        place_name = place["name"] if place else "Historical place"
        period = str(link.get("date_from") or "")
        if link.get("date_to") and link["date_to"] != link.get("date_from"):
            period += "–" + str(link["date_to"])
        add("Place / property connection",link["id"],str(subject_name)+" — "+place_name,
            period,link.get("summary",""),"?page=places&place="+quote(link["place_id"]),
            [link["subject_id"]] if link["subject_type"]=="person" else archive.events.get(link["subject_id"],{}).get("people_ids",[]),
            link.get("evidence_level",""),"Documented connection / period",
            "This locates a cited historical connection, not exact land ownership, a private address, or a surveyed boundary.")
    for index, row in enumerate(collection.inventory_rows("Images and Maps")):
        rid = row.get("Research ID","")
        key = str(row.get("Collection or item identifier") or index)
        add("Photo / scan / object",key+":"+str(index),row.get("Subject") or "Archival image",
            row.get("Date",""), row.get("Item or caption",""),
            "?page=media", collection.findings.get(rid,{}).get("Navigation",{}).get("people_ids",[]),
            row.get("Confidence",""),"Catalog date or associated period",
            "See catalog for image capture date, attribution, rights and original repository.")
    for story in STORIES:
        add("Family story",story["id"],story["title"],story["period"],story["summary"],
            "?page=stories&story="+quote(story["id"]),(), "Narrative with supporting sources",
            "Story period", "Its period does not necessarily identify a single event year.")
    for document_id, doc in DOCUMENTS.items():
        linked_findings = ("BF-R001", "BF-R002") if document_id == "thomas-1786" else ()
        doc_people = sorted({pid for rid in linked_findings for pid in collection.findings.get(rid, {}).get("Navigation", {}).get("people_ids", [])})
        add("Historical document",document_id,doc["title"],doc["date"],doc["summary"],
            "?page=documents&doc="+quote(document_id),doc_people,"Source transcription and historical context",
            "Document / testimony date",doc["limits"])
    # Bibliographic publication dates are not mistaken for events mentioned
    # inside the work; photo capture dates remain undated until corroborated.
    from family_books import load_books, illustrated_pages
    for book in load_books():
        add("Family-history book", book["id"], book["title"], str(book["publication_year"]),
            f"Complete 305-page illustrated book by {book['author']}. Themes include: {', '.join(book['sections'])}.",
            "?page=family-books", (), "Published family memoir and source compilation",
            "Book publication year", book["source_limit"])
        for finding in book.get("research_leads", []):
            add("Book-based research lead", finding["id"], finding["title"],
                finding.get("date") or "", finding["summary"],
                "?page=family-books&book_page="+str(finding["pdf_page"]), (),
                "Published family recollection; corroboration pending",
                "Book-described event date" if finding.get("date") else "Undated book recollection",
                finding["evidence"] + f" Source: {book['author']} (2016), PDF page {finding['pdf_page']}.")
        for entry in illustrated_pages(book):
            image_page = entry["pdf_page"]
            add("Book photograph or illustration",
                book["id"]+":p"+str(image_page), entry["title"],
                "", f"Original photographed/illustrated book page {image_page}. "
                    "The book's caption is retained in the page scan; its capture date is unconfirmed.",
                "?page=family-books&book_page="+str(image_page), (),
                "Book-published image; capture date unresolved", "Undated historical image",
                f"Credit: {book['author']}, {book['title']} ({book['publication_year']}), PDF page {image_page}. "
                "Family-website reproduction authorized by user; do not infer event dates from the 2016 publication year.")
    return items


def render_unified_timeline(data: dict, people_by_id: dict) -> None:
    st.title("Complete Family Timeline")
    st.write("Explore family lives, historical discoveries, photographs, documents, places and stories together in chronological order. Probable and disputed historical findings are included; internal research search logs and work queues are not family-history events.")
    collection = load_collection()
    all_items = build_chronology(data, people_by_id, collection)
    dated = [i for i in all_items if i["year"] is not None]
    undated = [i for i in all_items if i["year"] is None]
    st.caption(f"{len(all_items)} linked entries · {len(dated)} with an associated year · {len(undated)} undated or not precisely placed")
    route_link("Thomas Beverage's 1786 sworn testimony and related legal papers", "?page=documents&doc=thomas-1786")
    q = st.text_input("Search the complete timeline",placeholder="Person, place, document, boat, story…",key="whole_timeline_query").casefold().strip()
    first, second, third = st.columns([1.2, 1, 1.4])
    types = sorted({entry["type"] for entry in all_items})
    with first:
        chosen_types=st.multiselect("Content types", types, default=types, key="whole_timeline_types")
    with second:
        direction=st.selectbox("Order",["Oldest first","Newest first"],key="whole_timeline_direction")
    with third:
        person_options=["",*sorted(people_by_id,key=lambda p:people_by_id[p].get("full_name","").casefold())]
        person=st.selectbox("Relative",person_options,format_func=lambda id_: people_by_id[id_]["full_name"] if id_ else "Everyone",key="whole_timeline_person")
    min_year=min((i["year"] for i in dated),default=1700)
    max_year=max((i["year"] for i in dated),default=2026)
    years=st.slider("Year range",min_year,max_year,(min_year,max_year),key="whole_timeline_years")
    show_undated=st.checkbox("Include undated and broad-period material",value=True,key="whole_timeline_undated")
    # Direct event URL should be visible even when outside the chosen range.
    requested=st.query_params.get("event","")
    filtered=[]
    for i in all_items:
        if i["type"] not in chosen_types or (person and person not in i["person_ids"]):
            continue
        if i["year"] is None and not show_undated:
            continue
        if i["year"] is not None and not years[0]<=i["year"]<=years[1] and i["id"]!=requested:
            continue
        if q and q not in json.dumps(i,ensure_ascii=False).casefold():
            continue
        filtered.append(i)
    dated_results=sorted((i for i in filtered if i["year"] is not None),
                         key=lambda i:(i["year"],i["date"],i["title"]),
                         reverse=direction=="Newest first")
    undated_results=sorted((i for i in filtered if i["year"] is None),key=lambda i:(i["type"],i["title"]))
    if requested:
        dated_results.sort(key=lambda i:i["id"]!=requested)
    st.caption(f"{len(filtered)} matching entries. All evidence levels are included by default.")
    # No records-per-page setting, cap or pagination. A single interactive
    # virtualized table renders ALL matching records without creating hundreds
    # of heavyweight Streamlit buttons on initial page load.
    ordered_items = dated_results + undated_results
    st.caption(f"Showing all {len(ordered_items)} matching entries, not a 25-record sample. "
               "The table scrolls through every record. Select any row to see its complete entry and original link.")
    if ordered_items:
        rows = [
            {
                "Date / period": item["date"] if item["year"] is not None else "Undated · "+item["date"],
                "Record": item["title"],
                "Type": item["type"],
                "Evidence": item["certainty"] if item["certainty"] != "Not rated" else "",
            }
            for item in ordered_items
        ]
        import pandas as pd
        choice = st.dataframe(
            pd.DataFrame(rows),
            hide_index=True, width="stretch", height=720,
            on_select="rerun", selection_mode="single-row", key="complete_timeline_table",
        )
        selected_rows = choice.selection.rows
        selected_index = selected_rows[0] if selected_rows else None
        if selected_index is not None and selected_index < len(ordered_items):
            item = ordered_items[selected_index]
            with st.container(border=True):
                st.subheader(item["title"])
                st.caption(f"{item['date']} · {item['date_kind']} · {item['type']}")
                if item["description"]:
                    st.write(item["description"])
                if item["certainty"] and item["certainty"] != "Not rated":
                    st.caption("Evidence / research status: " + item["certainty"])
                if item["extra"]:
                    with st.expander("Evidence limits and interpretation"):
                        st.write(item["extra"])
                route_link("Open full record and source material", item["url"])
        else:
            st.caption("Select a row to read its description and follow the original source.")
    if not filtered:
        st.info("Nothing matches these filters. The original archive records remain available; broaden the years, content types or person.")
