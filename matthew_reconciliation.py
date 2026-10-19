"""A precise comparison of the published Matthew family and missing original proof.

The 1865 Eaton family group ALREADY records both spouses and ten children.
This is a historical report, not proof of parentage or a genealogy mutation.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Mapping

import streamlit as st
from routing_ui import route_link

ROOT=Path(__file__).resolve().parent
CASES=ROOT/"data"/"phase19_matthew_reconciliation_cases.json"
FAMILY=ROOT/"research"/"matthew_nathaniel_family_1865.json"

def load_matthew_reconciliation() -> tuple[list[dict], dict]:
    cases=json.loads(CASES.read_text(encoding="utf-8"))
    family=json.loads(FAMILY.read_text(encoding="utf-8"))
    if not isinstance(cases,list) or len(cases)<5:
        raise ValueError("Missing individual Matthew evidence case files")
    return cases,family

def marriage_groups(family: dict) -> list[dict]:
    person=family["matthew"]
    groups=[]
    for pos,wife in enumerate(person["wives"],1):
        children=[item for item in person["children"] if item["by_wife"]==wife["name"]]
        groups.append({
            "number":pos,
            "wife":wife["name"],
            "children":children,
            "source":family["publication"]["url"],
            "limitation":"Eaton's printed assignment; original parentage and marriages not independently proved.",
        })
    return groups

def _source_note(case: dict, *, compact: bool = False) -> None:
    with st.container(border=True):
        st.markdown("**"+case["title"]+"**")
        st.caption(case["evidence_kind"]+" · "+case["status"])
        st.write(case["claim"])
        st.caption("Evidence limit: "+case["proof"])
        if case.get("url"):
            route_link("Inspect historical source",case["url"])
        if case.get("book_page"):
            route_link("Open the original book page", "?page=family-books&book_page="+str(case["book_page"]))
        st.caption(case["reference"]+" · "+case["locator"])
        if not compact:
            for link in case.get("supporting_links",[]):
                route_link(link["title"],link["url"])
            with st.expander("What original record would establish this?"):
                for step in case["next_originals"]:
                    st.write("• "+step)

def render_matthew_reconciliation(*, compact: bool=False) -> None:
    cases,family=load_matthew_reconciliation()
    st.subheader("Matthew Beverage: two marriages, one published family group")
    st.write("Cyrus Eaton's **1865** local history explicitly names **Abigail Dyer as "
             "Capt. Matthew's first wife** and **Clarissa Cobb as his second**, "
             "assigning five children to each marriage. This corrects an earlier "
             "apparent contradiction in our research notes.")
    st.caption("This reconciles the TWO WIFE NAMES *within Eaton's account*. "
               "It does not establish either original wedding date, the 1785 minor's "
               "identity, Matthew's parents, his relationship to Thomas, or whether "
               "the book and the earlier history discuss the identical man.")
    route_link("Read Eaton's original 1865 printed family group (vol. II, pp. 146–147)",
               family["publication"]["url"])
    route_link("Compare the Matthew–Abigail story on original book page 17",
               "?page=family-books&book_page=17")
    route_link("New: dated Hope Town Clerk evidence, 1811–1827, and the 1820 census lead",
               "?page=collection&view=hope-matthew")
    groups=marriage_groups(family)
    columns=st.columns(2)
    for col,group in zip(columns,groups):
        with col.container(border=True):
            st.markdown("**"+str(group["number"])+
                        (". First wife: " if group["number"]==1 else ". Second wife: ")+
                        group["wife"]+"**")
            st.caption("Five children attributed by the 1865 printed account; "
                       "not five independently certified births")
            for child in group["children"]:
                name=child["name"]
                life=child.get("birth_approx") or child.get("birth")
                st.write("• "+name+(f" (born around {life})" if life else ""))
                if child.get("information"):
                    st.caption(str(child["information"]))
    with st.expander("Source comparison and missing probate or marriage originals",
                     expanded=not compact):
        for case in cases:
            _source_note(case,compact=compact)
    route_link("Explore the full published household, grandchildren and Nathaniel's "
               "separate family story",
               "?page=stories&story=matthew-rockland-descendants-1865")

def render_matthew_case_from_book(page: int) -> None:
    if int(page)!=17:
        return
    with st.expander("Research correction: Eaton names Abigail FIRST, Clarissa SECOND",
                     expanded=True):
        st.write("The earlier two-Matthews interpretation was too strong: the 1865 "
                 "historical family register explicitly places Abigail Dyer and "
                 "Clarissa Cobb as first and second wife of one Capt. Matthew. "
                 "The 2016 book's statement about Matthew and Abigail is compatible "
                 "with that published account. His identity as Thomas Beverage's "
                 "brother still requires original evidence.")
        route_link("Study the full Matthew source comparison",
                   "?page=collection&view=matthew")
