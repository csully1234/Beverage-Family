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
    """Preserve records and source meanings; no confidence-level filter."""
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
    for research in data.get("research", []):
        add("Research note", research["id"],research.get("title","Research"),
            research.get("record_date",""), research.get("summary",""),
            "?page=research", research.get("people_involved",[]),
            research.get("evidence_level",""),"Record / publication date",
            "This may date the source or review rather than the historical activity.")
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
        add("Historical document",document_id,doc["title"],doc["date"],doc["summary"],
            "?page=documents&doc="+quote(document_id),(),"Source transcription and historical context",
            "Document / testimony date",doc["limits"])
    return items


def render_unified_timeline(data: dict, people_by_id: dict) -> None:
    st.title("Complete Family Timeline")
    st.write("All family events, births, deaths, research discoveries (including probable and unresolved leads), photos, documents and historical stories are included. Their labels distinguish established events from research and source dates.")
    collection = load_collection()
    all_items = build_chronology(data, people_by_id, collection)
    dated = [i for i in all_items if i["year"] is not None]
    undated = [i for i in all_items if i["year"] is None]
    st.caption(f"{len(all_items)} linked entries · {len(dated)} with an associated year · {len(undated)} undated or not precisely placed")
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
    count=st.selectbox("Entries per page",[20,40,80,160],index=1,key="whole_timeline_page_size")
    total=(len(dated_results)+len(undated_results))
    pages=max(1,(total+count-1)//count)
    page=st.selectbox("Results page",range(1,pages+1),format_func=lambda n:f"{n} of {pages}",key="whole_timeline_page")
    for index,item in enumerate((dated_results+undated_results)[(page-1)*count:page*count]):
        with st.container(border=True):
            st.caption(f"{item['date']} · {item['date_kind']} · {item['type']}")
            st.markdown("**"+item["title"]+"**")
            if item["description"]:
                st.write(item["description"])
            if item["certainty"] and item["certainty"]!="Not rated":
                st.caption("Evidence / research status: "+item["certainty"])
            if item["extra"]:
                with st.expander("Context and interpretation notes"):
                    st.write(item["extra"])
            route_link("Open full record",item["url"])
    if not filtered:
        st.info("Nothing matches these filters. The original archive records remain available; broaden the years, content types or person.")
