"""Visitor journeys across profiles, both trees, history, maps and source pages.

A single set of stable query routes keeps the family site useful when the
visitor switches devices, opens a bookmark or browses with a keyboard.
Session history is deliberately ephemeral: no account tracking or storage.
"""
from __future__ import annotations

from urllib.parse import quote

import streamlit as st

from routing_ui import route_link


JOURNEYS = {
    "Search": [("People directory", "?page=people"), ("Family tree", "?page=tree"),
               ("Original sources", "?page=archive")],
    "People": [("Focused tree", "?page=tree"), ("Full family map", "?page=full-tree"),
               ("Family photographs", "?page=media")],
    "Explore the Tree": [("Full family map", "?page=full-tree"),
                         ("People directory", "?page=people"),
                         ("Complete timeline", "?page=timeline")],
    "Full Family Map": [("Focused family tree", "?page=tree"),
                        ("People directory", "?page=people"),
                        ("Explore places", "?page=places")],
    "Timeline": [("Discover family stories", "?page=stories"),
                 ("Explore historical places", "?page=places"),
                 ("Original evidence", "?page=media")],
    "Stories & Discoveries": [("Complete timeline", "?page=timeline"),
                              ("Family books", "?page=family-books"),
                              ("Original photographs", "?page=media")],
    "Historical Discoveries": [("Original sources", "?page=archive"),
                               ("Family timeline", "?page=timeline"),
                               ("Family stories", "?page=stories")],
    "Historical Places": [("Historical map", "?page=map"),
                          ("Family stories", "?page=stories"),
                          ("Complete timeline", "?page=timeline")],
    "Historical Map": [("Historical places", "?page=places"),
                       ("Family timeline", "?page=timeline"),
                       ("Family photographs", "?page=media")],
    "Photographs & Documents": [("Read family books", "?page=family-books"),
                                ("Browse original sources", "?page=archive"),
                                ("Find relatives", "?page=search")],
    "Family Books": [("Photographs & documents", "?page=media"),
                     ("People directory", "?page=people"),
                     ("Original sources", "?page=archive")],
    "Historical Sources": [("Photographs & documents", "?page=media"),
                           ("Family timeline", "?page=timeline"),
                           ("Explore places", "?page=places")],
    "Document Reader": [("Photographs & documents", "?page=media"),
                        ("Complete timeline", "?page=timeline"),
                        ("Family books", "?page=family-books")],
}


def _id_route(page: str, person_id: str) -> str:
    if page == "People":
        return "?page=people&profile=" + quote(person_id, safe="")
    if page == "Explore the Tree":
        return "?page=tree&profile=" + quote(person_id, safe="")
    if page == "Full Family Map":
        return "?page=full-tree&profile=" + quote(person_id, safe="")
    return "?page=full-tree"


def suggested_paths(page: str, person_id: str | None = None) -> list[tuple[str, str]]:
    """Always return 3 distinct destinations that remain valid URL bookmarks."""
    choices = list(JOURNEYS.get(page, [
        ("Find relatives", "?page=search"),
        ("Family tree", "?page=tree"),
        ("Original evidence", "?page=media"),
    ]))
    if person_id and page not in {"Home", "Search"}:
        if page == "People":
            choices[0] = ("Explore this person's tree", _id_route("Explore the Tree", person_id))
            choices[1] = ("Find this person on the full map", _id_route("Full Family Map", person_id))
        elif page == "Explore the Tree":
            choices[0] = ("Find this person on the full map", _id_route("Full Family Map", person_id))
            choices[1] = ("Open selected person's profile", _id_route("People", person_id))
        elif page == "Full Family Map":
            choices[0] = ("Explore this person's tree", _id_route("Explore the Tree", person_id))
            choices[1] = ("Open selected person's profile", _id_route("People", person_id))
        elif page == "Historical Discoveries":
            choices[0] = ("View selected relative's profile", _id_route("People", person_id))
            choices[1] = ("Explore their family branch", _id_route("Explore the Tree", person_id))
        elif page in {"Timeline", "Family Books"}:
            choices[0] = ("Selected relative's profile", _id_route("People", person_id))
    return choices


def visit_person(person_id: str, people_by_id: dict | None = None) -> None:
    """Keep up to five recent valid profiles per visitor session."""
    if not person_id or (people_by_id is not None and person_id not in people_by_id):
        return
    recent = [pid for pid in st.session_state.get("_recent_people", [])
              if pid != person_id and (people_by_id is None or pid in people_by_id)]
    st.session_state["_recent_people"] = [person_id, *recent][:5]
    st.session_state["_active_person"] = person_id


def current_person(people_by_id: dict, page: str = "") -> str:
    """Query profile on People wins; otherwise retain a valid last selection."""
    direct = str(st.query_params.get("profile", "") or "")
    exhibit_person = str(st.query_params.get("person", "") or "")
    if (page == "Historical Discoveries"
            and str(st.query_params.get("view", "") or "") == "person-exhibit"
            and exhibit_person in people_by_id):
        return exhibit_person
    if page in {"People", "Explore the Tree", "Full Family Map"} and direct in people_by_id:
        return direct
    page_selector = {
        "People": "profile_selector",
        "Explore the Tree": "tree_person",
        "Full Family Map": "full_map_person",
    }.get(page)
    if page_selector and st.session_state.get(page_selector) in people_by_id:
        return str(st.session_state[page_selector])
    for key in ("full_map_person", "tree_person", "profile_selector", "_active_person"):
        person_id = st.session_state.get(key)
        if person_id in people_by_id:
            return str(person_id)
    return ""


def recent_people(people_by_id: dict) -> list[str]:
    return [p for p in st.session_state.get("_recent_people", []) if p in people_by_id][:5]


def render_journey_bar(page: str, people_by_id: dict) -> None:
    """Compact, accessible cross-section navigation without another heavy menu."""
    if page == "Home":
        return
    selected = current_person(people_by_id, page)
    with st.container(border=True):
        st.caption("KEEP EXPLORING · " + page)
        if selected:
            st.caption("Selected relative: " + str(people_by_id[selected].get("full_name") or selected))
        columns = st.columns(3)
        for col, (label, url) in zip(columns, suggested_paths(page, selected)):
            with col:
                route_link(label + " →", url, width="stretch")


def render_recent_profile_links(people_by_id: dict) -> None:
    people = recent_people(people_by_id)
    if not people:
        return
    st.markdown("**Pick up where you left off**")
    for person_id in people[:3]:
        person = people_by_id[person_id]
        route_link(str(person.get("full_name") or person_id),
                   _id_route("People", person_id), type="tertiary")
