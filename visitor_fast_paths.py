"""Fast visitor shortcuts: find a real relative, keep their context across pages.

This is navigation only. Fuzzy spelling suggestions are NOT ancestry or
photograph identity evidence; all results require an existing indexed ID.
"""
from __future__ import annotations

from urllib.parse import quote

import streamlit as st
from family_search import normalized,person_match
from family_data import life_span
from routing_ui import route_link


def find_relative_suggestions(query: str, people: dict,
                              limit: int = 7) -> list[dict]:
    """Stable ranking, no truncated underlying index or invented ID matches."""
    text = normalized(query).strip()
    if not text or limit < 1:
        return []
    ranked = []
    for pid, person in people.items():
        reason = person_match(query, person)
        if not reason:
            continue
        name = normalized(person.get("full_name") or "")
        alternate = " ".join(normalized(x)
                             for x in person.get("alternate_names", []))
        if name == text:
            rank = 0
        elif name.startswith(text + " ") or name.startswith(text):
            rank = 1
        elif all(token in name.split() for token in text.split()):
            rank = 2
        elif text in alternate:
            rank = 3
        elif reason == "Name, initials or spelling variant":
            rank = 4
        elif reason == "Similar name — check dates and relatives":
            rank = 6
        else:
            rank = 5
        ranked.append((rank, name, str(pid), reason))
    ranked.sort()
    return [
        {"id": pid, "name": str(people[pid].get("full_name") or pid),
         "life_span": life_span(people[pid]), "match": reason}
        for _, _, pid, reason in ranked[:limit]
    ]


def family_shortcuts(person_id: str, people: dict) -> list[tuple[str, str]]:
    """Four exact-ID routes, always the same selected person."""
    if person_id not in people:
        return []
    quoted = quote(person_id, safe="")
    return [
        ("Life profile", "?page=people&profile=" + quoted),
        ("Family tree", "?page=tree&profile=" + quoted),
        ("Family photos", "?page=media&person=" + quoted),
        ("Original records", "?page=collection&view=person-exhibit&person=" +
         quoted + "&section=Original%20records"),
    ]


def render_home_fast_find(people: dict) -> None:
    """Put find-a-relative above the old card grid on phone and desktop."""
    st.subheader("Find your relative")
    st.caption("Start typing a first name, last name or alternate spelling. "
               "Pick a family profile to see their story, connections and sources.")
    q = st.text_input("Search family members", key="visitor_fast_query",
                      placeholder="Try Thomas, Orris, Lowell, Beveridge…").strip()
    if q:
        matches = find_relative_suggestions(q, people)
        if matches:
            st.caption("Matching family profiles (best matches first)")
            for person in matches:
                label = person["name"] + " · " + person["life_span"]
                route_link(label, "?page=people&profile=" +
                           quote(person["id"], safe=""),
                           width="stretch")
                if person["match"].startswith("Similar name"):
                    st.caption("Similar spelling — compare dates and other relatives")
            route_link("Search all names, sources and historical dates",
                       "?page=search&q=" + quote(q, safe=""), type="tertiary")
            st.caption("These are browsing suggestions, not newly verified historical identities.")
        else:
            st.info("No matching family profile. Try a shorter name, "
                    "another spelling, or the full historical search.")
            route_link("Search the complete archive",
                       "?page=search&q=" + quote(q, safe=""))
    else:
        route_link("Browse the complete alphabetical family directory",
                   "?page=people",type="tertiary")
