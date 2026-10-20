"""Early Fox Islands documentary atlas: six qualified findings, no invented kinship.

1790 Vinalhaven's eleven people are census CATEGORY COUNTS, not eleven
identified Beverage descendants. A 2025 journal article is a cited secondary
study, not permission to mirror its copyrighted 75-page journal PDF.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link,safe_external_url

DATA=Path(__file__).resolve().parent/"data"/"phase45_early_island_census_settlement_context.json"
ELIGIBLE_KINDS={
    "neighboring_settler_migration_context",
    "source_context_existing_record_crossreference",
    "source_context_existing_original_target",
    "positive_printed_census_household_totals",
    "settlement_origin_methodological_lead",
    "original_microfilm_reel_found_households_unread",
}


def load_early_islands(path: Path = DATA) -> dict:
    collection=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(collection,list) or len(collection)!=1:
        raise ValueError("Expected one reviewed early-island document collection")
    case=collection[0]
    rows=case.get("findings",[])
    sources=case.get("sources",[])
    if len(rows)!=6 or len(sources)!=6:
        raise ValueError("All six findings and six source/finding-aid cards must remain")
    if not case["no_tree_edits"] or not case["no_copyrighted_journal_rehosting"]:
        raise ValueError("Source atlas cannot alter ancestry or rehost the journal")
    by_source={s["id"]:s for s in sources}
    if len(by_source)!=6:
        raise ValueError("Repeated source identifier")
    for src in sources:
        if not safe_external_url(src["url"]) or not src.get("limitations"):
            raise ValueError("Invalid source URL or rights/provenance statement")
        if src["id"]=="scholar2025" and (
            not src["read_status"].startswith("published_scholarly_article") or
            "copyright" not in src["limitations"].lower()
        ):
            raise ValueError("Journal source must remain a linked secondary publication")
    ids=set()
    for item in rows:
        if item["id"] in ids or item["kind"] not in ELIGIBLE_KINDS:
            raise ValueError("Unsupported or repeated original-record finding")
        ids.add(item["id"])
        if (item["source_id"] not in by_source or not item["limits"] or
                not item["manuscript_target"]):
            raise ValueError("Every finding requires source and future manuscript check")
    if [r["year"] for r in rows]!=sorted(r["year"] for r in rows):
        raise ValueError("Published timeline is not chronological")
    census=case["census_1790"]
    count_fields=("adult_males_16_plus_including_head","males_under_16",
                  "free_white_females_all_ages","all_other_free_persons",
                  "enslaved_persons")
    if census["person_name_as_printed"]!="Thomas Beverege":
        raise ValueError("Preserve the original printed 1790 spelling")
    if sum(census[field] for field in count_fields)!=census["total_people"] or census["total_people"]!=11:
        raise ValueError("The 1790 headcount must equal the five period census categories")
    if (census["original_handwritten_scheduled_inspected"] or
            census["head_matches_canonical_profile"]):
        raise ValueError("Original and personal identity not established")
    reel=case["original_1820"]
    if not (reel["roll"]==34 and reel["nara_publication"]=="M33" and
            reel["archive_item"]=="populationsc18200034unit" and
            reel["archive_scanned_pages"]==194 and
            reel["manuscript_start"]==657 and
            reel["manuscript_end"]==664 and
            reel["handwritten_heads_uninspected"]):
        raise ValueError("1820 original census reel metadata or inspection state changed")
    return case


def source_atlas_for_candidate(pid: str,case:dict|None=None)->list[dict]:
    """Name-match research hints only; never confirmed person timeline events."""
    atlas=case or load_early_islands()
    return [row for row in atlas["findings"] if pid in row["profile_candidates"]]


def early_islands_route(finding_id: str = "") -> str:
    base="?page=collection&view=source-expedition&early-islands=1"
    return base+("&island_find="+quote(finding_id,safe="") if finding_id else "")


def atlas_stats(atlas: dict | None = None) -> dict:
    data=atlas or load_early_islands()
    return {"study_items":len(data["findings"]),
            "household_size":data["census_1790"]["total_people"],
            "direct_original_reels_located":1,
            "verified_household_genealogy_members":0}


def source_atlas_csv(atlas:dict|None=None)->str:
    data=atlas or load_early_islands()
    source_map={src["id"]:src for src in data["sources"]}
    f=io.StringIO()
    fields=("year","title","name_as_printed","kind","detail","source_url",
            "manuscript_target","limits")
    writer=csv.DictWriter(f,fieldnames=fields)
    writer.writeheader()
    for row in data["findings"]:
        writer.writerow({
            "year":row["year"],"title":row["title"],
            "name_as_printed":row["name_as_printed"],"kind":row["kind"],
            "detail":row["detail"],"source_url":source_map[row["source_id"]]["url"],
            "manuscript_target":row["manuscript_target"],"limits":row["limits"]
        })
    return f.getvalue()


def render_early_island_atlas(people:dict,*,selected:str="")->None:
    data=load_early_islands()
    rows=data["findings"]
    sources={src["id"]:src for src in data["sources"]}
    counts=atlas_stats(data)
    st.subheader("Fox Islands · 1769–1820 original-record atlas")
    st.write("Follow the earliest recorded island settlement history into an "
             "actual counted Beverage household in **1790** and the original "
             "**1820 federal census microfilm reel**. New modern scholarship "
             "identifies the original documents still required to establish "
             "where early settlers arrived from.")
    cols=st.columns(3)
    cols[0].metric("1790 Thomas-head household",counts["household_size"])
    cols[1].metric("Original 1820 census reel", "M33 · 34")
    cols[2].metric("New parentage proved",counts["verified_household_genealogy_members"])
    st.caption("The eleven people counted in 1790 are not eleven named "
               "individuals. Only the printed household HEAD is named. "
               "The original 1790 handwritten enumeration remains uninspected.")
    st.markdown("#### 1790 Vinalhaven census: Thomas Beverege")
    household=data["census_1790"]
    table=[
        {"Original 1790 enumeration category":"Males 16 and older, including head",
         "Count":household["adult_males_16_plus_including_head"]},
        {"Original 1790 enumeration category":"Males under age 16",
         "Count":household["males_under_16"]},
        {"Original 1790 enumeration category":"Free white females, all ages",
         "Count":household["free_white_females_all_ages"]},
        {"Original 1790 enumeration category":"All other free persons",
         "Count":household["all_other_free_persons"]},
        {"Original 1790 enumeration category":"Enslaved persons",
         "Count":household["enslaved_persons"]},
    ]
    st.dataframe(table,hide_index=True,use_container_width=True)
    st.caption("Sum: **11 recorded people**. 1908 official printed "
               "transcription p. 32 spells the head 'Thomas Beverege'; "
               "the original 1790 manuscript (M637, roll 2, Vinalhaven "
               "starting manuscript page 58) has not been directly read.")
    st.warning("Two adult men are NOT two proven fathers, and four younger "
               "boys are NOT necessarily sons. Never turn age categories "
               "into invented people or assign this head to Capt. Thomas "
               "solely because of name and chronology.")
    route_link("Read 1790 town census with the printed five-column values",
               sources["fed1790printed"]["url"])
    st.divider()
    st.markdown("#### Original 1820 census images now located")
    reel=data["original_1820"]
    st.write("The original NARA **M33, roll 34** scans comprise "
             f"{reel['archive_scanned_pages']} Internet Archive frames. "
             "Vinalhaven begins on handwritten census page **657** and "
             "continues through page **664**. The town-head index names "
             "John, Nathaniel, Thomas and Benjamin Beverage, but their "
             "handwriting, positions and household age tallies remain unread.")
    st.caption("Original MANUSCRIPT page 657 is not necessarily web "
               "viewer frame 657. Browse the reel and use page headings; "
               "do not guess a frame offset.")
    route_link("Open original 1820 Maine / Hancock census microfilm reel (M33–34)",
               sources["census1820reel"]["url"])
    route_link("Open town-indexed 1820 Vinalhaven household heads",
               sources["census1820index"]["url"])
    route_link("National Archives explanation of the original 1820 census",
               sources["nara1820guide"]["url"],type="tertiary")
    st.divider()
    options={r["id"]:r for r in rows}
    requested=selected if selected in options else ""
    if st.session_state.get("_early_islands_last_query")!=requested:
        st.session_state["early_islands_selected"]=requested
        st.session_state["_early_islands_last_query"]=requested
    chosen=st.selectbox("Explore six source-graded settlement findings",
                        ["",*(r["id"] for r in rows)],
                        key="early_islands_selected",
                        format_func=lambda rid:"All six findings — oldest to newest"
                        if not rid else f"{options[rid]['year']} · {options[rid]['title']}")
    for item in ([options[chosen]] if chosen else rows):
        src=sources[item["source_id"]]
        with st.expander(f"{item['year']} · {item['title']}",
                         expanded=bool(chosen)):
            st.write(item["detail"])
            route_link("Read the attributable published source",src["url"])
            st.caption("Source category: "+src["original_type"].replace("_"," "))
            st.warning("Limits: "+item["limits"])
            st.caption(src["limitations"])
            st.markdown("**Next original manuscript to inspect**")
            st.write(item["manuscript_target"])
            if item["profile_candidates"]:
                st.caption("Same-name profile comparison only. No individual has been identified.")
                for pid in item["profile_candidates"]:
                    if pid in people:
                        route_link("Compare potential matching profile: "+
                                   str(people[pid].get("full_name") or pid),
                                   "?page=people&profile="+quote(pid,safe=""),
                                   type="tertiary")
            route_link("Share this specific archival clue",
                       early_islands_route(item["id"]),type="tertiary")
    st.divider()
    st.markdown("#### Recent scholarly research and the original archival target")
    st.write("The 2025 genealogical study by **David Flanagan and Barbara "
             "Beverage Reeves** identifies **Rufus Putnam's 18 March 1786 "
             "settlers' report, paper Box 001 at Maine State Archives**, "
             "and cites a **15 May 1769 Plymouth County deed (58:29)** "
             "placing Ebenezer Eames at the Fox Islands. The Eames claim "
             "is valuable neighboring-settler context, NOT a confirmed "
             "Beverage ancestral relationship. The 1786 archival reference "
             "was already documented in the existing 1785–86 archive.")
    route_link("Read the scholarly 2025 article, pp. 170–182, on the publisher's site",
               sources["scholar2025"]["url"])
    st.caption("Only a summary and citation are shown here. The copyrighted "
               "journal PDF is not copied into the Beverage website.")
    st.download_button("Download all six evidence and original-record targets (CSV)",
                       source_atlas_csv(data),file_name="fox-islands-1769-1820-source-atlas.csv",
                       mime="text/csv")
