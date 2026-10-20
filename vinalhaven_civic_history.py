"""Read-only civic history of Vinalhaven, published in the 1889 town centennial.

Fifty-five *annual office entries* belong to ONE retrospective printed
source. They do not represent 55 independent original records, verified
individual identities, parentage statements, or dates of election.
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link, safe_external_url

DATA = Path(__file__).resolve().parent / "data" / "phase43_vinalhaven_civic_officers.json"
NAMES = ("Thomas Beverage", "John Beverage", "Benjamin Beverage",
         "Nathaniel Beverage", "James Beverage", "Josiah Beverage")
ROLES = ("Town clerk", "Town treasurer", "Selectman")
STATUS = "printed_name_only_not_individual_identified"


def load_civic_roster(path: Path = DATA) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("Expected one sourced Vinalhaven historical roster")
    case = payload[0]
    rows = case.get("records") or []
    if not rows or len(rows) != 55:
        raise ValueError("Expected complete 55-entry Beverage civic roster")
    if not safe_external_url(case["source_url"]):
        raise ValueError("Unsafe historical civic-source link")
    if case["original_town_election_minutes_read"]:
        raise ValueError("Retrospective 1889 book is not original election minutes")
    ids = set()
    for row in rows:
        if row["id"] in ids or row["year"] not in range(1790, 1847):
            raise ValueError("Invalid or duplicate municipal office/year")
        ids.add(row["id"])
        if (row["printed_name"] not in NAMES or row["office"] not in ROLES
                or row["printed_page"] not in (35,36,37,38,39)):
            raise ValueError("Unknown printed officeholder or 1889 page locator")
        if row["source_url"] != case["source_url"]:
            raise ValueError("Office record must cite the same published volume")
        if (row["identity_status"] != STATUS or
                row["original_municipal_minute_inspected"]):
            raise ValueError("Do not promote name matches into identity evidence")
        page = 35 if row["year"] <= 1791 else 36 if row["year"] <= 1809 else (
            37 if row["year"] <= 1827 else 38 if row["year"] <= 1845 else 39)
        if row["printed_page"] != page:
            raise ValueError("Printed page/year alignment inconsistent")
    if rows != sorted(rows, key=lambda r: (r["year"],r["office"],r["printed_name"])):
        raise ValueError("Civic evidence must remain in printed year order")
    return case


def civic_summary(case: dict) -> dict:
    entries = case["records"]
    return {
        "annual_entries": len(entries),
        "distinct_years": len({row["year"] for row in entries}),
        "printed_names": len({row["printed_name"] for row in entries}),
        "offices": dict(sorted(Counter(row["office"] for row in entries).items())),
        "first_year": min(row["year"] for row in entries),
        "last_year": max(row["year"] for row in entries),
        "independent_source_families": 1,
    }


def _year(value) -> int | None:
    if not value:
        return None
    match = re.search(r"(1[6789]\d\d|20\d\d)",str(value))
    return int(match.group()) if match else None


def candidate_age_status(record: dict, people: dict[str,dict]) -> list[dict]:
    """Only flag chronological impossibilities; possibility is NOT identification."""
    year = record["year"]
    results = []
    for pid in record["candidate_person_ids"]:
        p = people.get(pid)
        if not p:
            continue
        birth = p.get("birth")
        death = p.get("death")
        birth_year = _year(birth.get("date") if isinstance(birth,dict) else birth)
        death_year = _year(death.get("date") if isinstance(death,dict) else death)
        age = year - birth_year if birth_year is not None else None
        if age is not None and age < 18:
            status = "excluded_by_youth"
            note = f"The indexed person's reported birth implies age {age} in {year}; this is not a credible adult municipal officer."
        elif death_year is not None and year > death_year:
            status = "excluded_after_death"
            note = f"The office year {year} comes after the indexed {death_year} death; identity cannot be assigned without correcting one of the dates."
        elif age is None:
            status = "not_assessable"
            note = "Birth year unavailable; name similarity cannot prove this identity."
        else:
            status = "chronologically_possible_only"
            note = f"Reported age approximately {age}; compatible ages do NOT establish this person held office."
        results.append({
            "id": pid, "name":str(p.get("full_name") or pid),
            "year":year, "status":status,"age":age,"explanation":note,
        })
    return results


def civic_for_candidate(pid: str, case: dict | None = None) -> list[dict]:
    """This is a candidate-lookup, not a source citation for that person."""
    roster = case or load_civic_roster()
    return [r for r in roster["records"] if pid in r["candidate_person_ids"]]


def civic_route(name: str = "", year: int | None = None) -> str:
    result = "?page=collection&view=source-expedition&civic=1"
    if name:
        result += "&officer=" + quote(name, safe="")
    if year is not None and 1790 <= int(year) <= 1846:
        result += "&office_year=" + str(int(year))
    return result


def civic_csv(records: list[dict]) -> str:
    stream = io.StringIO()
    writer = csv.DictWriter(stream,fieldnames=(
        "year","printed_name","office","printed_page","source_url",
        "identity_status","original_municipal_minute_inspected"))
    writer.writeheader()
    for row in records:
        writer.writerow({key:row[key] for key in writer.fieldnames})
    return stream.getvalue()


def render_vinalhaven_civic(people: dict, *, source_name: str = "",
                           focus_year: str = "") -> None:
    case = load_civic_roster()
    rows = case["records"]
    stats = civic_summary(case)
    st.subheader("Vinalhaven Beverage civic history · 1790–1846")
    st.write("Read the early islanders' local-government roles as recorded "
             "in Vinalhaven's **1889 centennial history**. This spans the era "
             "before North Haven became a separate town in 1847.")
    st.caption("All 55 annual office entries come from **ONE retrospective "
               "1889 publication**, not 55 original town election documents. "
               "The book prints surnames and given names only; exact family "
               "identities and parentage are NOT established.")
    metric = st.columns(3)
    metric[0].metric("Sourced office entries", stats["annual_entries"])
    metric[1].metric("Years with an entry", stats["distinct_years"])
    metric[2].metric("Distinct printed names", stats["printed_names"])
    st.caption("A person might appear in more than one municipal office in "
               "the same year. Counts represent entries, not different people.")
    route_link("Read the exact published 1889 source transcription (pp. 35–39)",
               case["source_url"])
    st.caption(case["publication"] if "publication" in case
               else "Vinalhaven Centennial Committee, 1889, pages 35–39.")
    names = sorted({row["printed_name"] for row in rows})
    requested = source_name if source_name in names else ""
    if st.session_state.get("_civic_last_route") != requested:
        st.session_state["civic_officer_filter"] = requested
        st.session_state["_civic_last_route"] = requested
    choice = st.selectbox("Which name appears in the historical list?",
                          ["",*names], key="civic_officer_filter",
                          format_func=lambda x:x or "All recorded Beverage names")
    office = st.selectbox("Municipal role",
                          ["All offices",*ROLES], key="civic_role_filter")
    matching = [r for r in rows if
                (not choice or r["printed_name"] == choice)
                and (office == "All offices" or r["office"] == office)]
    st.caption(f"{len(matching)} matching annual entries. Every matching "
               "record is listed below—no 25-item research cap.")
    st.dataframe([{
        "Year":r["year"],
        "Printed name":r["printed_name"],
        "Office":r["office"],
        "1889 book page":r["printed_page"],
    } for r in matching], hide_index=True, use_container_width=True,
        height=min(530,max(145,68+34*len(matching))))
    if not matching:
        st.info("No entries match these filters. Change the printed name or office.")
    else:
        years = sorted({r["year"] for r in matching})
        requested_year = int(focus_year) if focus_year.isdigit() and int(focus_year) in years else years[0]
        year = st.selectbox("Inspect one year and compare candidate identities",
                            years, index=years.index(requested_year),
                            key="civic_selected_year")
        year_records = [row for row in matching if row["year"] == year]
        for row in year_records:
            with st.container(border=True):
                st.markdown(f"**{row['year']} · {row['printed_name']} · {row['office']}**")
                st.caption(f"1889 Vinalhaven historical sketch, printed p. {row['printed_page']}. "
                           "Official named in the retrospective list; original election minutes not read.")
                st.markdown("**Possible family-tree name comparisons (NOT proven identities)**")
                comparisons = candidate_age_status(row, people)
                for candidate in comparisons:
                    st.write(candidate["name"] + " — " + candidate["explanation"])
                    if candidate["status"] not in ("excluded_by_youth","excluded_after_death"):
                        route_link("Compare profile only: " + candidate["name"],
                                   "?page=people&profile=" + quote(candidate["id"],safe=""),
                                   type="tertiary")
                route_link("Bookmark this exact printed officer/year",
                           civic_route(row["printed_name"], row["year"]), type="tertiary")
    st.warning("**Why the distinction matters:** Nathaniel named as a "
               "selectman in 1812 is not plausibly the Nathaniel reported born "
               "in 1803, who would have been about nine. Likewise, the "
               "Josiah Beverage listed in 1846 cannot be assigned to either "
               "the 1793 or the 1821 Josiah from the given name alone.")
    st.download_button("Download all 55 exact published-office entries (CSV)",
                       civic_csv(rows),mime="text/csv",
                       file_name="vinalhaven-beverage-town-offices-1790-1846.csv")
