"""Beverage Family — a searchable, source-first family archive."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote, urlparse, urlencode
from zoneinfo import ZoneInfo

import streamlit as st
from routing_ui import route_markdown, route_link, begin_routes
from graphviz import Digraph

from visitor_ui import render_stories_page, render_media_page, render_document_page, render_people_directory, order_people, SORT_OPTIONS, surname_first_label
from unified_timeline import render_unified_timeline
from full_tree import build_full_tree_html
from tree_component import show_full_tree
from family_books import render_family_books, render_book_profile_context
from identity_casework import render_profile_identity_evidence
from family_associations import render_documented_associations
from family_discoveries import render_family_discoveries
from archive import ArchiveIndex
from evidence_explorer import render_event_browser, render_profile_browser, render_profile_highlights
from archive_ui import (
    render_archive_page, render_places_page, render_map_page,
    render_person_archive, render_event_archive, source_link,
)
from family_data import (
    Record,
    date_sort_key,
    format_date,
    friendly_identifier,
    index_people,
    life_span,
    load_site_data,
    person_sort_key,
    records_to_csv,
    relationship_index,
    relationship_step_label,
    shortest_relationship_path,
    source_search_text,
    unique_places,
    year_from_date,
)
from validation import validate_site_data
from family_search import matches as archive_matches, person_match
from conflict_review_ui import render_profile_review, review_data, review_link
from research_collection import matches as research_matches_query
from research_collection_ui import (
    load_collection, render_collection_page, render_context, render_finding,
    register_link, render_timeline_research, paginate,
)


# This remains the first Streamlit command for compatibility with older
# supported releases as well as current Streamlit versions.
st.set_page_config(
    page_title="Beverage Family of North Haven",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": "A source-first archive of the Beverage family and its North Haven roots."
    },
)


def runtime_source_identity() -> tuple[str, str]:
    """Reveal which Python source files this running Streamlit process loads.

    This is intentionally based on the actual in-process source files, not
    GitHub's branch name or Render's deployment status. No secrets, paths,
    environment variables or customer data are exposed in the UI.
    """
    app_file = Path(__file__).resolve()
    directory_source_file = Path(render_people_directory.__code__.co_filename).resolve()
    app_hash = hashlib.sha256(app_file.read_bytes()).hexdigest()[:10]
    directory_code = directory_source_file.read_bytes()
    directory_hash = hashlib.sha256(directory_code).hexdigest()[:10]
    implementation = (
        "paginated" if b'Directory page' in directory_code
        else "continuous"
    )
    return (f"app {app_hash} / people {directory_hash}", implementation)


DATA_DIR = Path(__file__).parent / "data"
LEGACY_COMPATIBILITY_PASSWORD = "BEVERAGE"

PAGE_SLUGS = {
    "Home": "home",
    "Search": "search",
    "People": "people",
    "Explore the Tree": "tree",
    "Full Family Map": "full-tree",
    "Timeline": "timeline",
    "Stories & Discoveries": "stories",
    "Historical Discoveries": "collection",
    "Historical Places": "places",
    "Historical Map": "map",
    "Photographs & Documents": "media",
    "Family Books": "family-books",
    "Historical Sources": "archive",
    "Document Reader": "documents",
}
SLUG_PAGES = {slug: page for page, slug in PAGE_SLUGS.items()}
# Old bookmarked technical routes lead to family-friendly content, not raw logs.
SLUG_PAGES.update({"research": "Historical Discoveries", "sources": "Historical Sources"})
NAV_GROUPS = {
    "Home": ["Home"],
    "Search": ["Search"],
    "Family": ["People", "Explore the Tree", "Full Family Map"],
    "History": ["Timeline", "Stories & Discoveries", "Historical Discoveries"],
    "Places": ["Historical Places", "Historical Map"],
    "Archive": ["Photographs & Documents", "Family Books", "Historical Sources"],
}
PAGE_GROUP = {page: group for group, pages in NAV_GROUPS.items() for page in pages}
# The individual document reader is reached from its exhibit, not an empty menu.
PAGE_GROUP["Document Reader"] = "Archive"


def apply_theme() -> None:
    """Apply a restrained coastal-archive visual system."""

    route_markdown(
        """
        <style>
        :root {
            --bev-ink: #19313a;
            --bev-navy: #123542;
            --bev-sea: #39717d;
            --bev-sky: #dcebed;
            --bev-cream: #f7f3ea;
            --bev-paper: #fffdf8;
            --bev-brass: #aa7b3f;
            --bev-muted: #61747a;
            --bev-line: rgba(25, 49, 58, 0.16);
        }

        .stApp {
            background:
                radial-gradient(circle at 82% 4%, rgba(57,113,125,.10), transparent 24rem),
                linear-gradient(180deg, #fbfaf6 0%, var(--bev-cream) 100%);
            color: var(--bev-ink);
        }

        .block-container {
            max-width: 1240px;
            padding-top: 4.5rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: var(--bev-navy) !important;
            font-family: Georgia, "Times New Roman", serif !important;
            letter-spacing: -0.018em;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102f3b 0%, #173f4b 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f7f3ea;
        }

        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #f7f3ea !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background-color: #fffdf8;
        }
        [data-testid="stSidebar"] .stButton > button * {
            color: var(--bev-ink) !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height: 44px;
            align-items: center;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] * {
            color: var(--bev-ink) !important;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 253, 248, .82);
            border: 1px solid var(--bev-line);
            border-radius: 14px;
            padding: 1rem 1.15rem;
            box-shadow: 0 8px 28px rgba(18,53,66,.05);
        }

        [data-testid="stMetricValue"] {
            color: var(--bev-navy);
            font-family: Georgia, "Times New Roman", serif;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 253, 248, .78);
            border-color: var(--bev-line) !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 26px rgba(18,53,66,.045);
        }

        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
            border-radius: 999px;
            border-color: rgba(18,53,66,.32);
            font-weight: 650;
            min-height: 44px;
        }
        a:focus-visible, button:focus-visible, input:focus-visible,
        [tabindex]:focus-visible { outline: 3px solid #b57824 !important; outline-offset: 3px; }
        [data-testid="stMarkdownContainer"] { overflow-wrap: anywhere; }
        [data-testid="stTabs"] [role="tab"] { min-height: 44px; }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: var(--bev-navy);
            border-color: var(--bev-navy);
        }

        .stButton > button[kind="primary"] p,
        .stDownloadButton > button[kind="primary"] p {
            color: #fffdf8 !important;
        }

        [data-testid="stAlert"],
        [data-testid="stAlert"] * {
            color: var(--bev-ink) !important;
        }

        [data-testid="stAlert"] a {
            color: #0b5265 !important;
            text-decoration: underline;
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            background-color: var(--bev-paper) !important;
            color: var(--bev-ink) !important;
        }

        [data-baseweb="select"] input,
        [data-baseweb="input"] input,
        textarea {
            color: var(--bev-ink) !important;
            -webkit-text-fill-color: var(--bev-ink) !important;
        }

        [data-baseweb="popover"],
        [data-baseweb="popover"] * {
            color: var(--bev-ink) !important;
        }

        [role="option"] {
            background-color: var(--bev-paper) !important;
            color: var(--bev-ink) !important;
        }

        [role="option"]:hover,
        [role="option"][aria-selected="true"] {
            background-color: var(--bev-sky) !important;
            color: var(--bev-navy) !important;
        }

        .bev-hero {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            padding: clamp(2rem, 5vw, 4.5rem);
            margin-bottom: 1.4rem;
            color: #fffdf8;
            background:
                radial-gradient(circle at 88% 16%, rgba(220,235,237,.22), transparent 15rem),
                linear-gradient(135deg, #102f3b 0%, #1d5361 68%, #39717d 100%);
            box-shadow: 0 20px 50px rgba(18,53,66,.16);
        }

        .bev-hero:after {
            content: "";
            position: absolute;
            left: -5%; right: -5%; bottom: -3.2rem;
            height: 5.2rem;
            border-radius: 50%;
            background: rgba(247,243,234,.10);
            box-shadow: 0 -1.1rem 0 rgba(247,243,234,.06);
        }

        .bev-kicker {
            color: #d9c19d;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
        }

        .bev-hero h1 {
            color: #fffdf8 !important;
            font-size: clamp(2.45rem, 6vw, 5rem);
            line-height: .98;
            margin: .65rem 0 1rem;
            max-width: 850px;
        }

        .bev-hero p {
            color: #e7f0ef;
            font-size: 1.08rem;
            line-height: 1.7;
            max-width: 760px;
            margin-bottom: 0;
        }

        .bev-profile-banner {
            border-left: 5px solid var(--bev-brass);
            background: rgba(255,253,248,.78);
            border-radius: 0 16px 16px 0;
            padding: 1.2rem 1.45rem;
            margin: .4rem 0 1.2rem;
        }

        .bev-profile-banner h1 {
            margin: 0 0 .25rem;
            font-size: clamp(2rem, 4vw, 3.35rem);
        }

        .bev-profile-banner p {
            color: var(--bev-muted);
            margin: 0;
            font-size: 1.05rem;
        }

        .bev-eyebrow {
            color: var(--bev-brass);
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .bev-muted { color: var(--bev-muted); }

        .bev-footer {
            color: var(--bev-muted);
            text-align: center;
            padding-top: 2rem;
            font-size: .86rem;
        }

        @media (max-width: 700px) {
            .block-container { padding-top: 4.25rem; }
            .bev-hero { border-radius: 16px; padding: 2rem 1.35rem 2.5rem; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stColumn"] { min-width: min(100%, 18rem); flex: 1 1 18rem; }
            [data-testid="stTabs"] [role="tablist"] { overflow-x: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
def get_query_value(key: str) -> str | None:
    value = st.query_params.get(key)
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value is not None else None


def configured_password() -> str:
    """Use a deployment secret when present, with legacy access preserved."""

    environment_password = os.environ.get("APP_PASSWORD")
    if environment_password:
        return environment_password
    try:
        secret_password = st.secrets["APP_PASSWORD"]
        if secret_password:
            return str(secret_password)
    except (FileNotFoundError, KeyError):
        pass
    return LEGACY_COMPATIBILITY_PASSWORD


def check_password() -> None:
    """Gate the archive and provide a deliberate login experience."""

    if st.session_state.get("password_correct"):
        return

    left, center, right = st.columns([1, 1.35, 1])
    with center:
        route_markdown("<div class='bev-eyebrow'>Private family archive</div>", unsafe_allow_html=True)
        st.title("Beverage Family")
        st.write("Enter the family password to explore the tree, timeline, and research records.")
        with st.form("login_form", clear_on_submit=True):
            entered = st.text_input("Password", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Enter archive", type="primary", width="stretch")
        if submitted:
            if hmac.compare_digest(entered, configured_password()):
                st.session_state["password_correct"] = True
                st.session_state.pop("login_failed", None)
                st.rerun()
            st.session_state["login_failed"] = True
        if st.session_state.get("login_failed"):
            st.error("That password was not recognized.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, list[Record]]:
    return load_site_data(DATA_DIR)


@st.cache_data(show_spinner=False)
def load_archive() -> ArchiveIndex:
    return ArchiveIndex(load_data())


def markdown_escape(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def person_url(person_id: str) -> str:
    params = {"page": "people", "profile": person_id}
    for key in ("return_q", "return_where", "return_page"):
        if key in st.query_params:
            params[key] = st.query_params[key]
    return "?" + urlencode(params)


def event_url(event_id: str) -> str:
    return f"?page=timeline&event={quote(event_id)}"


def person_link(people_by_id: Mapping[str, Record], person_id: str) -> str:
    person = people_by_id.get(person_id)
    if not person:
        return f"*Unresolved: {markdown_escape(friendly_identifier(person_id))}*"
    name = markdown_escape(person.get("full_name", person_id))
    return f"[{name}]({person_url(person_id)})"


def source_markdown(source: Any) -> str:
    if isinstance(source, dict):
        title = markdown_escape(source.get("title", "Untitled source"))
        url = source.get("url")
        record_type = markdown_escape(source.get("record_type", ""))
        parsed = urlparse(str(url)) if url else None
        safe_url = (
            str(url).replace("(", "%28").replace(")", "%29")
            if parsed and parsed.scheme in {"http", "https"}
            else None
        )
        label = f"[{title}]({safe_url})" if safe_url else str(title)
        return f"{label} — {record_type}" if record_type else label
    return markdown_escape(source)


def unique_sources(data: dict[str, list[Record]]) -> list[Any]:
    """Return de-duplicated sources across profiles, events, and notes."""

    sources: list[Any] = []
    seen: set[str] = set()
    for collection in (data["people"], data["events"], data["research"]):
        for record in collection:
            for source in record.get("sources", []):
                key = (
                    str(source.get("url") or source.get("title") or source).strip().casefold()
                    if isinstance(source, dict)
                    else str(source).strip().casefold()
                )
                if key not in seen:
                    seen.add(key)
                    sources.append(source)
    return sources


def generation_count(
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> int:
    """Measure the longest known parent chain without looping on bad data."""

    def depth(person_id: str, trail: frozenset[str]) -> int:
        if person_id in trail:
            return 0
        parents = [
            parent_id
            for parent_id in relationships["parents"].get(person_id, set())
            if parent_id in people_by_id
        ]
        if not parents:
            return 1
        return 1 + max(depth(parent_id, trail | {person_id}) for parent_id in parents)

    return max((depth(person_id, frozenset()) for person_id in people_by_id), default=0)


def render_sources(sources: list[Any], heading: str | None = None) -> None:
    if not sources:
        st.caption("No source citation has been entered yet.")
        return
    if heading:
        route_markdown(f"**{heading}**")
    for source in sources:
        route_markdown(f"- {source_markdown(source)}")


def evidence_label(status: str) -> tuple[str, bool]:
    provisional_terms = (
        "compiled",
        "provisional",
        "not yet reviewed",
        "unverified",
        "corroboration required",
    )
    provisional = any(term in status.lower() for term in provisional_terms)
    prefix = "UNVERIFIED / PROVISIONAL — " if provisional else "Evidence — "
    return prefix + status, provisional


def render_evidence_status(status: Any) -> None:
    if not status:
        return
    label, provisional = evidence_label(str(status))
    if provisional:
        st.warning(label)
    else:
        st.info(label)


def navigate(page: str) -> None:
    st.session_state["nav_page"] = page
    st.session_state["nav_group"] = PAGE_GROUP[page]
    st.query_params["page"] = PAGE_SLUGS[page]
    if page != "People" and "profile" in st.query_params:
        del st.query_params["profile"]
    if page not in {"Timeline", "Historical Map"} and "event" in st.query_params:
        del st.query_params["event"]
    clear_archive_route(page)


def clear_archive_route(page: str) -> None:
    for parameter, allowed in (("place", {"Historical Map", "Historical Places", "Historical Discoveries"}),
                               ("person", {"Historical Map", "Historical Discoveries"}), ("source", {"Historical Sources"}),
                               ("q", {"Search", "Historical Discoveries"}),
                               *((key, {"Search"}) for key in ("results_page", "where")),
                               *((key, {"People"}) for key in ("return_q", "return_page", "return_where")),
                               *((key, {"Historical Discoveries"}) for key in
                                 ("finding", "target", "view", "topic", "status", "inventory", "location"))):
        if page not in allowed and parameter in st.query_params:
            del st.query_params[parameter]


def center_tree_on(person_id: str) -> None:
    """Safely move from a profile to the focused tree during a callback."""

    st.session_state["tree_person"] = person_id
    navigate("Explore the Tree")


def open_profile(person_id: str) -> None:
    st.session_state["nav_page"] = "People"
    st.session_state["nav_group"] = "Family"
    st.session_state["profile_selector"] = person_id
    st.query_params["page"] = "people"
    st.query_params["profile"] = person_id
    if "event" in st.query_params:
        del st.query_params["event"]
    clear_archive_route("People")


def sync_sidebar_route() -> None:
    page = st.session_state["nav_page"]
    st.query_params["page"] = PAGE_SLUGS[page]
    if page != "People" and "profile" in st.query_params:
        del st.query_params["profile"]
    if page not in {"Timeline", "Historical Map"} and "event" in st.query_params:
        del st.query_params["event"]
    clear_archive_route(page)


def sync_nav_group() -> None:
    navigate(NAV_GROUPS[st.session_state["nav_group"]][0])


def sync_profile_route() -> None:
    person_id = st.session_state.get("profile_selector")
    if person_id:
        st.query_params["page"] = "people"
        st.query_params["profile"] = person_id


def sync_full_map_person() -> None:
    """Update cross-page person selection when the parent dropdown changes."""
    person_id = st.session_state.get("full_map_person")
    if person_id:
        st.session_state["tree_person"] = person_id
        st.session_state["profile_selector"] = person_id


def sorted_people(people: list[Record]) -> list[Record]:
    return order_people(people)


def person_name(people_by_id: Mapping[str, Record], person_id: str) -> str:
    person = people_by_id.get(person_id)
    return str(person.get("full_name", person_id)) if person else friendly_identifier(person_id)


def render_sidebar(people: list[Record], people_by_id: Mapping[str, Record]) -> str:
    query_slug = get_query_value("page")
    requested_page = SLUG_PAGES.get(query_slug or "")
    if get_query_value("profile") and not requested_page:
        requested_page = "People"

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = requested_page or "Home"
    elif requested_page and st.session_state.get("_last_query_slug") != query_slug:
        st.session_state["nav_page"] = requested_page
    # The old research pages no longer exist in visitor navigation. Correct
    # prior browser sessions before attempting PAGE_GROUP lookup.
    if st.session_state["nav_page"] not in PAGE_GROUP:
        st.session_state["nav_page"] = requested_page or "Home"
    # Individual document pages remain reachable through source links, but
    # they are not separate sidebar destinations for everyday family browsing.
    showing_document = requested_page == "Document Reader"
    if st.session_state["nav_page"] == "Document Reader":
        st.session_state["nav_page"] = "Photographs & Documents"
    st.session_state["_last_query_slug"] = query_slug
    st.session_state["nav_group"] = PAGE_GROUP[st.session_state["nav_page"]]

    with st.sidebar:
        route_markdown("### 🌊 Beverage Family")
        st.caption("North Haven genealogy archive")
        group = st.radio("Explore", list(NAV_GROUPS), key="nav_group", on_change=sync_nav_group)
        page = st.radio(
            "In this section",
            NAV_GROUPS[group],
            key="nav_page",
            on_change=sync_sidebar_route,
            label_visibility="visible",
        )
        st.divider()

        ordered = sorted_people(people)
        person_ids = [str(person["id"]) for person in ordered]
        quick_person = st.selectbox(
            "Quick person lookup",
            options=[None, *person_ids],
            format_func=lambda person_id: (
                "Choose a person…"
                if person_id is None
                else surname_first_label(people_by_id[person_id]) + " · " + life_span(people_by_id[person_id])
            ),
            key="sidebar_person_lookup",
        )
        st.button(
            "Open profile",
            disabled=quick_person is None,
            width="stretch",
            on_click=open_profile if quick_person else None,
            args=(quick_person,) if quick_person else (),
        )

        st.divider()
        if st.button("Log out", width="stretch"):
            st.session_state.clear()
            st.rerun()
        st.caption(f"{len(people)} profiles indexed")
        runtime_id, directory_variant = runtime_source_identity()
        st.caption("Running source: " + runtime_id)
        st.caption("People directory implementation: " + directory_variant)
    return "Document Reader" if showing_document else page


def render_home(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    people = data["people"]
    events = data["events"]
    research = data["research"]
    years = [year_from_date(event.get("date")) for event in events]
    known_years = [year for year in years if year]
    span = f"{min(known_years)}–{max(known_years)}" if known_years else "Undated"

    route_markdown(
        """
        <section class="bev-hero">
          <div class="bev-kicker">North Haven · Maine · Family archive</div>
          <h1>The Beverage Family</h1>
          <p>Three centuries of people, places, work, and family connections—organized into one searchable, source-first record.</p>
          <p>Start with someone you know, follow a family connection, or explore the places and records behind the stories.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Where would you like to start?")
    actions = [
        ("Find a relative", "Search names, nicknames and spelling variants.", "?page=search"),
        ("Explore the family", "Follow parents, spouses and children.", "?page=tree"),
        ("Explore a place", "Visit the places behind family stories.", "?page=places"),
        ("Photographs & documents", "Browse original sources and historical image records.", "?page=media"),
        ("Read the family timeline", "Follow people and events through time.", "?page=timeline"),
        ("Discover family stories", "Explore remarkable people, places and discoveries.", "?page=stories"),
    ]
    for row in (actions[:3], actions[3:]):
        for col, (label, description, url) in zip(st.columns(3), row):
            with col.container(border=True):
                route_link(label, url, width="stretch")
                st.caption(description)
    with st.expander("About this family history"):
        st.write(f"{len(people)} relatives · {len(events)} recorded family events · {span}. Dates, identities and relationships may be incomplete or disputed; original historical sources are linked wherever possible.")
        route_link("Browse historical discoveries", "?page=collection")
        route_link("Read original historical sources", "?page=archive")

    st.divider()
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        route_markdown("<div class='bev-eyebrow'>Start with a name</div>", unsafe_allow_html=True)
        st.subheader("Find a family member")
        ordered = sorted_people(people)
        person_ids = [str(person["id"]) for person in ordered]
        chosen = st.selectbox(
            "Search the profile index",
            options=person_ids,
            format_func=lambda person_id: (
                f"{surname_first_label(people_by_id[person_id])} · "
                f"{life_span(people_by_id[person_id])}"
            ),
            key="home_person_lookup",
            label_visibility="collapsed",
        )
        st.button(
            "View this profile",
            type="primary",
            on_click=open_profile,
            args=(chosen,),
        )

        route_markdown("<div class='bev-eyebrow'>Research standard</div>", unsafe_allow_html=True)
        st.subheader("Evidence stays visible")
        st.write(
            "Original records and institutional archives receive the most weight. "
            "Compiled genealogy remains useful, but provisional links are labeled "
            "until the underlying record image is reviewed."
        )

    with right:
        route_markdown("<div class='bev-eyebrow'>Featured records</div>", unsafe_allow_html=True)
        st.subheader("Stories anchored to sources")
        featured_ids = (
            "research_civic_harrison_1859",
            "research_lowell_music_career",
            "research_harold_antenna",
        )
        research_by_id = {record.get("id"): record for record in research}
        for record_id in featured_ids:
            record = research_by_id.get(record_id)
            if not record:
                continue
            with st.container(border=True):
                route_markdown(f"**{record.get('title', 'Research record')}**")
                st.write(record.get("why_it_matters") or record.get("summary", ""))
                st.caption(
                    f"{record.get('record_date', 'Undated')} · "
                    f"{record.get('evidence_level', 'Evidence not rated')}"
                )

    st.divider()
    today = datetime.now(ZoneInfo("America/New_York")).date()
    on_this_day = [
        event
        for event in events
        if event.get("date_precision", "exact") == "exact"
        and isinstance(event.get("date"), str)
        and len(str(event["date"])) == 10
        and str(event["date"])[5:] == today.strftime("%m-%d")
    ]
    random_person = sorted_people(people)[today.toordinal() % len(people)] if people else None
    day_column, relative_column, recent_column = st.columns(3, gap="large")
    with day_column:
        route_markdown("<div class='bev-eyebrow'>On this day</div>", unsafe_allow_html=True)
        st.subheader("Beverage history today")
        if on_this_day:
            for event in sorted(on_this_day, key=date_sort_key)[:3]:
                route_markdown(f"[{event.get('title', 'Untitled event')}]({event_url(str(event['id']))})")
                st.caption(format_date(event.get("date"), event.get("date_precision")))
        else:
            st.caption("No exact-date event is recorded for this calendar day yet.")
    with relative_column:
        route_markdown("<div class='bev-eyebrow'>Random relative</div>", unsafe_allow_html=True)
        st.subheader(random_person.get("full_name") if random_person else "No profile")
        if random_person:
            st.caption(life_span(random_person))
            notes = str(random_person.get("notes") or random_person.get("biography") or "Profile ready to explore.")
            st.write(notes if len(notes) <= 220 else notes[:217] + "…")
            route_markdown(f"[Open profile →]({person_url(str(random_person['id']))})")
    with recent_column:
        route_markdown("<div class='bev-eyebrow'>Recently researched</div>", unsafe_allow_html=True)
        st.subheader("Newly documented")
        recent = sorted(
            research,
            key=lambda item: (str(item.get("checked_on", "")), str(item.get("record_date", ""))),
            reverse=True,
        )[:3]
        for record in recent:
            route_markdown(f"**{record.get('title', 'Research note')}**")
            st.caption(str(record.get("evidence_level", "Evidence not rated")))


def related_events(events: list[Record], person_id: str) -> list[Record]:
    return sorted(
        [event for event in events if person_id in event.get("people_involved", [])],
        key=date_sort_key,
    )


def render_event_card(
    event: Record,
    people_by_id: Mapping[str, Record],
    compact: bool = False,
) -> None:
    with st.container(border=True):
        date_column, story_column = st.columns([1, 3.4])
        with date_column:
            route_markdown(
                f"**{format_date(event.get('date'), event.get('date_precision'))}**"
            )
            precision = event.get("date_precision")
            if precision and precision != "exact":
                st.caption(f"{str(precision).replace('_', ' ').title()} date")
        with story_column:
            route_markdown(f"### {event.get('title', 'Untitled event')}")
            if event.get("evidence_status"):
                label, provisional = evidence_label(str(event["evidence_status"]))
                st.caption(label)
            st.write(event.get("description", ""))
            involved = [
                person_link(people_by_id, str(person_id))
                for person_id in event.get("people_involved", [])
            ]
            if involved:
                route_markdown("**People:** " + ", ".join(involved))
            render_event_archive(str(event["id"]), load_archive())
            render_event_browser(event, compact=compact)


def render_relation_group(
    title: str,
    related_ids: list[str],
    people_by_id: Mapping[str, Record],
) -> None:
    with st.container(border=True):
        route_markdown(f"**{title}**")
        if not related_ids:
            st.caption("No relationship entered")
            return
        for related_id in related_ids:
            related = people_by_id.get(related_id)
            suffix = f" · {life_span(related)}" if related else " · unresolved profile"
            route_markdown(f"- {person_link(people_by_id, related_id)}{suffix}")


def render_person_profile(
    person: Record,
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
    events: list[Record],
    research: list[Record],
) -> None:
    person_id = str(person["id"])
    route_markdown(
        f"""
        <section class="bev-profile-banner">
          <div class="bev-eyebrow">Person profile</div>
          <h1>{escape(str(person.get('full_name', 'Unknown')))}</h1>
          <p>{escape(life_span(person))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    alternate_names = person.get("alternate_names", [])
    if alternate_names:
        st.caption("Also recorded as: " + " · ".join(str(name) for name in alternate_names))

    born, died = st.columns(2)
    with born:
        route_markdown("**Born**")
        st.write(
            f"{format_date(person.get('birth_date'), person.get('birth_date_precision'))} "
            f"— {person.get('birth_place') or 'Unknown'}"
        )
    with died:
        route_markdown("**Died**")
        if person.get("death_date") or person.get("death_place"):
            st.write(
                f"{format_date(person.get('death_date'), person.get('death_date_precision'))} "
                f"— {person.get('death_place') or 'Unknown'}"
            )
        else:
            st.write("No death record entered")

    # Give visitors the important family connections before research terminology.
    close_relatives = (("Parents", "parents"), ("Spouses", "spouses"), ("Children", "children"))
    st.markdown("**Family at a glance**")
    summary_cols = st.columns(3)
    for column, (heading, relation) in zip(summary_cols, close_relatives):
        ids = sorted(relationships[relation].get(person_id, set()),
                     key=lambda pid: person_name(people_by_id, pid).casefold())
        with column.container(border=True):
            st.caption(heading)
            if not ids:
                st.caption("Not recorded")
            for pid in ids[:3]:
                if pid in people_by_id:
                    route_link(person_name(people_by_id, pid), person_url(pid))
                else:
                    # Preserve a referenced relative even without a full profile.
                    # This is an unresolved profile, not a false relationship.
                    st.caption(f"{person_name(people_by_id, pid)} · profile not yet entered")
            if len(ids) > 3:
                st.caption(f"+{len(ids)-3} more in the Family tab")
    route_link("Explore this person's family branch", "?page=tree&profile="+quote(person_id))
    route_link("View all records in the timeline", "?page=timeline")

    if person.get("baptism_date"):
        route_markdown("**Baptized**")
        st.write(format_date(person["baptism_date"]) + " — " + person.get("baptism_place", "Unknown"))
        st.caption("This is a baptism date. The birth date is not established; the recorded birthplace remains unverified.")
    render_book_profile_context(person)
    render_documented_associations(person_id)
    render_profile_identity_evidence(person_id)
    render_profile_review(person_id, load_collection(), people_by_id)
    render_evidence_status(person.get("evidence_status"))
    if person.get("needs_research"):
        st.warning("Needs more research — this profile contains one or more provisional leads.")
    if person.get("research_completeness"):
        st.caption(f"Research status: {person['research_completeness']}")
    # Place real source access at the top of a profile, not hidden behind an
    # unrelated research archive or an unclickable citation count.
    render_profile_highlights(person_id)

    story_tab, family_tab, places_tab, sources_tab = st.tabs(
        ["Story", "Family", "Places", "Historical records"]
    )

    with story_tab:
        if person.get("biography"):
            st.subheader("Biography")
            st.write(person["biography"])
        if person.get("notes"):
            st.subheader("Life and historical context")
            st.write(person["notes"])
        elif not person.get("biography"):
            st.info("A narrative biography has not been added yet.")

        detail_groups = (
            ("Occupations", "occupations"),
            ("Education", "education"),
            ("Military service", "military_service"),
            ("Civic and professional roles", "civic_offices"),
            ("Accomplishments", "accomplishments"),
        )
        populated = [(label, person.get(field, [])) for label, field in detail_groups if person.get(field)]
        if populated:
            st.subheader("At a glance")
            detail_columns = st.columns(2)
            for index, (label, values) in enumerate(populated):
                with detail_columns[index % 2]:
                    with st.container(border=True):
                        route_markdown(f"**{label}**")
                        for value in values:
                            route_markdown(f"- {markdown_escape(value)}")

        person_events = related_events(events, person_id)
        st.subheader(f"Timeline records involving this person ({len(person_events)})")
        if not person_events:
            st.caption("No linked timeline records yet.")
        for event in person_events[:8]:
            render_event_card(event, people_by_id, compact=True)
        if len(person_events) > 8:
            st.caption(f"{len(person_events) - 8} additional records are available on the Timeline page.")
        render_context("person", person_id, people_by_id, strong_only=False)

    with family_tab:
        relation_columns = st.columns(2)
        groups = (
            ("Parents", "parents"),
            ("Spouse(s)", "spouses"),
            ("Children", "children"),
            ("Siblings", "siblings"),
        )
        for position, (label, field_name) in enumerate(groups):
            related_ids = sorted(
                relationships[field_name].get(person_id, set()),
                key=lambda related_id: person_name(people_by_id, related_id).lower(),
            )
            with relation_columns[position % 2]:
                render_relation_group(label, related_ids, people_by_id)

        st.button(
            "Center this person in the family tree",
            type="primary",
            on_click=center_tree_on,
            args=(person_id,),
        )

    with places_tab:
        render_person_archive(person_id, load_archive())
        render_context("person", person_id, people_by_id, topic="Land and property")
        residences = person.get("residences", [])
        if residences:
            st.subheader("Known residences")
            for residence in residences:
                with st.container(border=True):
                    route_markdown(f"**{residence.get('location', 'Unknown location')}**")
                    if residence.get("period"):
                        st.caption(str(residence["period"]))
        else:
            st.info("No residence history has been entered for this profile.")

    with sources_tab:
        render_context("person", person_id, people_by_id, limit=5)
        archive_records = load_archive().sources_for("person", person_id)
        render_profile_browser(person, archive_records)

        date_provenance = person.get("date_provenance", {})
        if date_provenance:
            st.subheader("Date precision")
            for field_name, details in date_provenance.items():
                label = field_name.replace("_", " ").title()
                route_markdown(f"**{label}:** {person.get(field_name + '_precision', 'unknown').title()}")
                if details.get("determination"):
                    st.caption(str(details["determination"]))

        conflicts = person.get("conflicting_evidence", [])
        if conflicts:
            st.subheader("Earlier evidence conflicts for family review")
            st.caption("Preserved original notes. See Dates, identity and evidence notes above for the latest review; these earlier values may differ from the current proposed display.")
            for conflict in conflicts:
                with st.container(border=True):
                    route_markdown(f"**{conflict.get('claim', 'Conflicting claim')}**")
                    st.write(f"Existing record: {conflict.get('existing_record', 'Not recorded')}")
                    st.write(f"Reviewed source: {conflict.get('reviewed_source', 'Not recorded')}")
                    st.caption(str(conflict.get("status", "Unresolved")))

        # Research activity reports remain in GitHub, not in family profiles.


def render_people_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    st.title("People")
    st.write("Search the complete profile index, then move directly through connected relatives and records.")

    if not get_query_value("profile"):
        render_people_directory(data["people"], people_by_id)
        return

    if "return_q" in st.query_params or "return_where" in st.query_params:
        back = "?" + urlencode({"page": "search", "q": st.query_params.get("return_q", ""),
                                "where": st.query_params.get("return_where", ""),
                                "results_page": st.query_params.get("return_page", "1")})
        route_link("← Back to your search results", back)
    if get_query_value("profile") and get_query_value("profile") not in people_by_id:
        st.warning("That profile was not found. Choose a relative below or search by name.")
    sort_order = st.selectbox("People dropdown order", SORT_OPTIONS, key="profile_order")
    ordered = order_people(data["people"], sort_order)
    person_ids = [str(person["id"]) for person in ordered]
    query_profile = get_query_value("profile")
    if query_profile in person_ids and st.session_state.get("_last_query_profile") != query_profile:
        st.session_state["profile_selector"] = query_profile
    st.session_state["_last_query_profile"] = query_profile

    if "profile_selector" not in st.session_state or st.session_state["profile_selector"] not in person_ids:
        st.session_state["profile_selector"] = query_profile if query_profile in person_ids else person_ids[0]

    st.selectbox(
        "Find a person",
        options=person_ids,
        format_func=lambda person_id: (
            f"{surname_first_label(people_by_id[person_id]) if sort_order == 'Surname A–Z' else person_name(people_by_id, person_id)} · {life_span(people_by_id[person_id])}"
        ),
        key="profile_selector",
        on_change=sync_profile_route,
    )
    selected_id = st.session_state["profile_selector"]
    render_person_profile(
        people_by_id[selected_id],
        people_by_id,
        relationships,
        data["events"],
        data["research"],
    )


def record_search_blob(record: Record) -> str:
    """Flatten a curated record for case-insensitive archive search."""

    return json.dumps(record, ensure_ascii=False, default=str).casefold()


def sync_search_route() -> None:
    values = {"q": st.session_state.get("global_query", ""),
              "where": st.session_state.get("global_where", ""),
              "results_page": str(st.session_state.get("global_people_page", 1))}
    st.query_params["page"] = "search"
    for key, value in values.items():
        if value:
            st.query_params[key] = value
        elif key in st.query_params:
            del st.query_params[key]
    st.session_state["_search_memory"] = values
    st.session_state["_search_route"] = tuple(values.values())


def changed_search() -> None:
    for kind in ("people", "events", "research", "sources", "findings"):
        st.session_state["global_" + kind + "_page"] = 1
    sync_search_route()


def clear_search() -> None:
    st.session_state["global_query"] = ""
    st.session_state["global_where"] = ""
    changed_search()


def render_search_page(data, people_by_id) -> None:
    st.title("Find a relative")
    st.write("Search names, places, stories and sources. Known spellings and initials are included; similar names stay separate.")
    memory = st.session_state.get("_search_memory", {})
    route = tuple(st.query_params.get(k, memory.get(k, "" if k != "results_page" else "1"))
                  for k in ("q", "where", "results_page"))
    if st.session_state.get("_search_route") != route or "global_query" not in st.session_state:
        st.session_state["global_query"], st.session_state["global_where"] = route[:2]
        st.session_state["global_people_page"] = int(route[2]) if str(route[2]).isdigit() else 1
        st.session_state["_search_route"] = route
        st.session_state["_search_memory"] = dict(zip(("q", "where", "results_page"), route))
    query = st.text_input("Global search", placeholder="Try Eliot Beveridge, H H Beverage, or antenna…",
                          key="global_query", on_change=changed_search).strip()
    place = st.text_input("Place mentioned (optional)", placeholder="For example, North Haven or Marblehead",
                          key="global_where", on_change=changed_search).strip()
    st.button("Clear search", on_click=clear_search)
    if not query and not place:
        st.info("Enter a name or subject to search, or use a place to browse its records.")
        return
    def selected(record):
        return archive_matches(query, record) and archive_matches(place, record)
    reasons = {p["id"]: person_match(query, p) if query else "Place mentioned in profile"
               for p in data["people"] if archive_matches(place, p)}
    collection = load_collection()
    findings = [r for r in collection.findings.values() if selected(r)]
    for r in findings:
        for pid in r["Navigation"]["people_ids"]:
            if not reasons.get(pid):
                reasons[pid] = "Linked research — check the finding's identity notes"
    people = sorted((p for p in data["people"] if reasons.get(p["id"])),
                    key=lambda p: (reasons[p["id"]] != "Name, initials or spelling variant", person_sort_key(p)))
    events = sorted((r for r in data["events"] if selected(r)), key=date_sort_key)
    sources = [s for s in collection.sources.values() if selected(s)]
    review_sources = [s for s in review_data()["sources"] if selected(s)]
    legacy_sources = {}
    for kind, records in (("People", data["people"]), ("Timeline", data["events"])):
        for r in records:
            for source in r.get("sources", []):
                if selected(source):
                    legacy_sources.setdefault(source_search_text(source), source)
    tabs = st.tabs([f"People ({len(people)})", f"Events ({len(events)})",
                    f"Historical discoveries ({len(findings)})",
                    f"Original sources ({len(sources) + len(review_sources) + len(legacy_sources)})"])
    with tabs[0]:
        st.caption(f"{len(people)} matching profiles · Matching names do not establish a relationship.")
        pages = max(1, (len(people) + 11) // 12)
        value = st.session_state.get("global_people_page", 1)
        if value < 1 or value > pages:
            st.session_state["global_people_page"] = 1
        page = st.selectbox("People results page", range(1, pages + 1), key="global_people_page",
                            format_func=lambda n: f"{n} of {pages}", on_change=sync_search_route)
        if not people:
            st.info("No profiles match. Try a first name, fewer words or a broader place.")
        for person in people[(page - 1) * 12:page * 12]:
            url = "?" + urlencode({"page": "people", "profile": person["id"], "return_q": query,
                                     "return_where": place, "return_page": page})
            with st.container(border=True):
                route_markdown(f"### [{markdown_escape(person['full_name'])}]({url})")
                st.caption(life_span(person) + " · " + str(person.get("birth_place") or "Birthplace unknown"))
                relatives = [person_name(people_by_id, pid) for pid in person.get("parents", [])]
                if relatives:
                    st.caption("Parents: " + " · ".join(relatives))
                st.caption("Match: " + reasons[person["id"]])
                context = str(person.get("biography") or person.get("notes") or "Open this profile to explore family connections.")
                st.write(context if len(context) <= 240 else context[:237] + "…")
                if person.get("conflict_review_ids"):
                    st.caption("Evidence notes available on this profile.")
    with tabs[1]:
        if not events:
            st.info("No events match these words and place.")
        for event in paginate(events, "global_events_page"):
            render_event_card(event, people_by_id, compact=True)
    with tabs[2]:
        for record in paginate(findings, "global_findings_page"):
            with st.container(border=True):
                render_finding(record, collection, people_by_id)
        if not findings:
            st.info("No historical discoveries match. Try a surname or another subject.")
    with tabs[3]:
        for source in paginate(sources, "global_sources_page"):
            route_markdown(f"- {register_link(source)}")
        for source in review_sources:
            route_markdown(f"- [{source['title']}]({'?page=archive&source=' + source['id']})")
        with st.expander(f"Citations attached to profiles and events ({len(legacy_sources)})"):
            render_sources(list(legacy_sources.values()))
        if not sources and not review_sources and not legacy_sources:
            st.info("No source citations match.")


def graph_node_label(person: Record | None, person_id: str) -> str:
    if not person:
        return f"{friendly_identifier(person_id)}\nUnresolved profile"
    return f"{person.get('full_name', person_id)}\n{life_span(person)}"


def build_family_graph(
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
    focus_id: str,
    view: str,
    generations: int,
) -> Digraph:
    graph = Digraph(format="svg")
    graph.attr(
        rankdir="TB",
        bgcolor="transparent",
        pad="0.25",
        nodesep="0.35",
        ranksep="0.65",
        splines="polyline",
    )
    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#8ca1a5",
        fillcolor="#fffdf8",
        fontcolor="#19313a",
        fontname="Arial",
        fontsize="10",
        margin="0.14,0.09",
    )
    graph.attr("edge", color="#789097", arrowsize="0.65")
    rendered: set[str] = set()

    def add_node(person_id: str, role: str = "relative") -> None:
        if person_id in rendered:
            return
        rendered.add(person_id)
        palettes = {
            "focus": ("#123542", "#fffdf8", "#123542"),
            "ancestor": ("#dcebed", "#19313a", "#6f969f"),
            "descendant": ("#f4e8d4", "#19313a", "#aa7b3f"),
            "spouse": ("#ece5f3", "#19313a", "#8b779a"),
            "sibling": ("#eef0e7", "#19313a", "#879276"),
            "relative": ("#fffdf8", "#19313a", "#8ca1a5"),
        }
        fill, font, border = palettes.get(role, palettes["relative"])
        node_attributes = {
            "fillcolor": fill,
            "fontcolor": font,
            "color": border,
            "penwidth": "2" if role == "focus" else "1",
            "tooltip": person_name(people_by_id, person_id),
        }
        if person_id in people_by_id:
            node_attributes.update(
                URL=person_url(person_id),
                target="_self",
                tooltip=f"Open {person_name(people_by_id, person_id)}",
            )
        graph.node(
            person_id,
            graph_node_label(people_by_id.get(person_id), person_id),
            **node_attributes,
        )

    add_node(focus_id, "focus")
    visited_up: set[tuple[str, int]] = set()
    visited_down: set[tuple[str, int]] = set()

    def add_ancestors(person_id: str, depth: int) -> None:
        if depth > generations or (person_id, depth) in visited_up:
            return
        visited_up.add((person_id, depth))
        for parent_id in sorted(relationships["parents"].get(person_id, set())):
            add_node(parent_id, "ancestor")
            graph.edge(parent_id, person_id)
            add_ancestors(parent_id, depth + 1)

    def add_descendants(person_id: str, depth: int) -> None:
        if depth > generations or (person_id, depth) in visited_down:
            return
        visited_down.add((person_id, depth))
        for child_id in sorted(relationships["children"].get(person_id, set())):
            add_node(child_id, "descendant")
            graph.edge(person_id, child_id)
            add_descendants(child_id, depth + 1)

    if view in ("Ancestors", "Both"):
        add_ancestors(focus_id, 1)
    if view in ("Descendants", "Both"):
        add_descendants(focus_id, 1)

    if view == "Immediate family":
        for parent_id in sorted(relationships["parents"].get(focus_id, set())):
            add_node(parent_id, "ancestor")
            graph.edge(parent_id, focus_id)
        for child_id in sorted(relationships["children"].get(focus_id, set())):
            add_node(child_id, "descendant")
            graph.edge(focus_id, child_id)
        for sibling_id in sorted(relationships["siblings"].get(focus_id, set())):
            add_node(sibling_id, "sibling")
            graph.edge(sibling_id, focus_id, dir="none", style="dotted", label=" sibling ")

    if view in ("Immediate family", "Both"):
        for spouse_id in sorted(relationships["spouses"].get(focus_id, set())):
            add_node(spouse_id, "spouse")
            graph.edge(focus_id, spouse_id, dir="none", style="dashed", color="#8b779a")

    return graph


def available_generations(relationships, focus_id: str, view: str) -> int:
    """Farthest *recorded* relative in the selected direction; cycles are ignored."""
    kinds = ("parents", "children") if view == "Both" else (("parents",) if view == "Ancestors" else ("children",))
    if view == "Immediate family":
        return 1
    maximum = 0
    for kind in kinds:
        frontier = [(focus_id, 0)]
        visited = {focus_id}
        while frontier:
            node, steps = frontier.pop(0)
            maximum = max(maximum, steps)
            for relative in relationships[kind].get(node, set()):
                if relative not in visited:
                    visited.add(relative)
                    frontier.append((relative, steps + 1))
    return max(1, maximum)


def render_tree_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    st.title("Explore the Family Tree")
    st.write("Choose a person and switch between their ancestors, descendants, or immediate family.")
    st.button(
        "Open the full family map",
        on_click=navigate,
        args=("Full Family Map",),
    )

    ordered = sorted_people(data["people"])
    person_ids = [str(person["id"]) for person in ordered]
    if "tree_person" not in st.session_state or st.session_state["tree_person"] not in person_ids:
        st.session_state["tree_person"] = get_query_value("profile") if get_query_value("profile") in person_ids else person_ids[0]

    picker, mode, depth = st.columns([2, 1.15, 1])
    with picker:
        focus_id = st.selectbox(
            "Center person",
            options=person_ids,
            format_func=lambda person_id: surname_first_label(people_by_id[person_id]),
            key="tree_person",
        )
    with mode:
        view = st.selectbox(
            "Tree view",
            ("Ancestors", "Descendants", "Both", "Immediate family"),
            index=2,
        )
    maximum = available_generations(relationships, focus_id, view)
    tree_context = (focus_id, view)
    if st.session_state.get("_tree_depth_context") != tree_context:
        st.session_state["tree_depth"] = maximum
        st.session_state["_tree_depth_context"] = tree_context
    elif st.session_state.get("tree_depth", maximum) > maximum:
        st.session_state["tree_depth"] = maximum
    with depth:
        if maximum <= 1 or view == "Immediate family":
            generations = 1
            st.caption("One recorded step")
        else:
            generations = st.slider("Generations", 1, maximum, key="tree_depth")
    st.caption(f"Showing up to {generations} of {maximum} documented generation steps for this person and view.")

    st.caption("Prefer a readable list? Open the profile’s Family tab for linked relatives. Recorded links can include unresolved research questions.")
    render_profile_review(focus_id, load_collection(), people_by_id)
    graph = build_family_graph(people_by_id, relationships, focus_id, view, generations)
    st.graphviz_chart(graph, width="stretch")
    st.caption("Nodes include profile links where supported. The family navigator below always opens the selected profile.")

    focus = people_by_id[focus_id]
    with st.container(border=True):
        summary, action = st.columns([3, 1])
        with summary:
            route_markdown(f"**{focus.get('full_name')}** · {life_span(focus)}")
            if focus.get("notes"):
                notes = str(focus["notes"])
                st.write(notes if len(notes) <= 280 else notes[:277] + "…")
        with action:
            st.button(
                "Open full profile",
                type="primary",
                width="stretch",
                on_click=open_profile,
                args=(focus_id,),
            )

    st.divider()
    st.subheader("Relationship finder")
    st.write("Select two profiles to follow the recorded connections. These may include unresolved relationships; read the evidence notes on each profile.")
    relationship_columns = st.columns(2)
    with relationship_columns[0]:
        start_id = st.selectbox(
            "First person",
            person_ids,
            format_func=lambda person_id: person_name(people_by_id, person_id),
            key="relationship_start",
        )
    with relationship_columns[1]:
        default_end = 1 if len(person_ids) > 1 else 0
        end_id = st.selectbox(
            "Second person",
            person_ids,
            index=default_end,
            format_func=lambda person_id: person_name(people_by_id, person_id),
            key="relationship_end",
        )

    path = shortest_relationship_path(relationships, start_id, end_id)
    if not path:
        st.info("No connection is established by the current records.")
    elif len(path) == 1:
        st.success("You selected the same person twice.")
    else:
        st.success(f"Connected in {len(path) - 1} recorded relationship step(s).")
        if any(people_by_id.get(pid, {}).get("conflict_review_ids") for pid in path):
            st.info("This path includes a profile with an open or reviewed evidence question. A path shows recorded links, not proof of every relationship.")
        path_parts: list[str] = []
        for index, person_id in enumerate(path):
            path_parts.append(person_link(people_by_id, person_id))
            if index < len(path) - 1:
                step = relationship_step_label(relationships, person_id, path[index + 1])
                path_parts.append(f"— *{step}* →")
        route_markdown(" ".join(path_parts))


def render_full_tree_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    """Render a separate, interactive map containing the entire known tree."""

    st.title("Full Family Map")
    st.write(
        "This is an additional whole-family view. The existing focused tree remains unchanged. "
        "Use the map controls to fit everything on screen, zoom in without shrinking labels permanently, "
        "drag around the canvas, or jump directly to a person."
    )

    all_referenced = set(people_by_id)
    for mapping in relationships.values():
        for person_id, related_ids in mapping.items():
            all_referenced.add(str(person_id))
            all_referenced.update(str(item) for item in related_ids)
    unresolved_count = sum(person_id not in people_by_id for person_id in all_referenced)
    parent_edges = {
        (str(parent_id), str(child_id))
        for child_id, parent_ids in relationships["parents"].items()
        for parent_id in parent_ids
    }
    spouse_edges = {
        tuple(sorted((str(person_id), str(spouse_id))))
        for person_id, spouse_ids in relationships["spouses"].items()
        for spouse_id in spouse_ids
        if str(person_id) != str(spouse_id)
    }

    metrics = st.columns(4)
    metrics[0].metric("Profiles", len(data["people"]))
    metrics[1].metric("Unresolved relatives", unresolved_count)
    metrics[2].metric("Parent-child links", len(parent_edges))
    metrics[3].metric("Spouse links", len(spouse_edges))

    ordered = sorted_people(data["people"])
    person_ids = [str(person["id"]) for person in ordered]
    # Process component selections BEFORE creating the selectbox widget: Streamlit
    # does not permit mutating a widget's value after it has been instantiated.
    pending = st.session_state.pop("_pending_full_map_person", None)
    pending_action = st.session_state.pop("_pending_full_map_action", "select")
    if pending in people_by_id and pending_action == "profile":
        st.session_state["profile_selector"] = pending
        st.query_params["page"] = "people"
        st.query_params["profile"] = pending
        st.rerun()
    if pending in people_by_id:
        st.session_state["full_map_person"] = pending
        st.session_state["tree_person"] = pending
        st.session_state["profile_selector"] = pending
    elif st.session_state.get("full_map_person") not in person_ids:
        previous = st.session_state.get("tree_person")
        st.session_state["full_map_person"] = previous if previous in person_ids else ""

    st.write("Start with the complete map. Select any relative on the diagram or in the selector, then use Back to focused tree to continue with the same person.")
    st.selectbox(
        "Selected relative",
        options=["", *person_ids],
        format_func=lambda pid: (
            surname_first_label(people_by_id[pid]) + " · " + life_span(people_by_id[pid])
            if pid else "No person selected — show the whole family"
        ),
        key="full_map_person",
        on_change=sync_full_map_person,
    )

    controls, note = st.columns([1, 3])
    with controls:
        st.button(
            "Back to focused tree",
            on_click=navigate,
            args=("Explore the Tree",),
            width="stretch",
        )
    with note:
        st.caption(
            "Solid lines are parent-child relationships; dashed lines are spouses. "
            "Dashed-outline boxes are referenced relatives whose full profiles are still unresolved."
        )

    st.caption("The entire graph is available in Whole family overview; use Explore nearby relatives to zoom in on a branch. Selecting a box keeps the parent controls synchronized.")
    selection = show_full_tree(
        build_full_tree_html(people_by_id, relationships),
        selected_id=st.session_state.get("full_map_person", ""),
        height=850,
    )
    if isinstance(selection, dict):
        clicked_id = selection.get("person_id")
        clicked_action = selection.get("action", "select")
        event_id = selection.get("event_id")
        # Component values persist during unrelated Streamlit reruns. Handle
        # actual mouse-selection events ONCE, never replay a stale click over
        # a more recent choice made in the top person dropdown.
        is_new_event = (
            isinstance(event_id, str)
            and event_id
            and st.session_state.get("_last_full_map_event") != event_id
        )
        if is_new_event:
            st.session_state["_last_full_map_event"] = event_id
            if clicked_id in people_by_id and (
                clicked_id != st.session_state.get("full_map_person") or clicked_action == "profile"
            ):
                st.session_state["_pending_full_map_person"] = clicked_id
                st.session_state["_pending_full_map_action"] = clicked_action
                st.rerun()


def event_search_blob(event: Record, people_by_id: Mapping[str, Record]) -> str:
    involved_names = " ".join(
        person_name(people_by_id, str(person_id))
        for person_id in event.get("people_involved", [])
    )
    return " ".join(
        [
            str(event.get("date", "")),
            str(event.get("title", "")),
            str(event.get("description", "")),
            str(event.get("category", "")),
            str(event.get("place", "")),
            involved_names,
            " ".join(source_search_text(source) for source in event.get("sources", [])),
            str(event.get("evidence_status", "")),
        ]
    ).lower()


def render_timeline_page(
    events: list[Record],
    people: list[Record],
    people_by_id: Mapping[str, Record],
) -> None:
    st.title("Family Timeline")
    st.write("Filter more than three centuries of family and North Haven history without losing the source trail.")

    event_years = [year_from_date(event.get("date")) for event in events]
    known_years = [year for year in event_years if year]
    minimum_year, maximum_year = min(known_years), max(known_years)

    search = st.text_input(
        "Search timeline",
        placeholder="Person, place, event, occupation, or source…",
    ).strip().lower()
    requested_event_id = get_query_value("event")
    known_event_ids = {str(event.get("id")) for event in events}
    if requested_event_id in known_event_ids:
        selected_title = next(
            str(event.get("title", "Timeline event"))
            for event in events
            if str(event.get("id")) == requested_event_id
        )
        st.info(f"Direct link opened: {selected_title}")

    filter_columns = st.columns([1.5, 1.3, 1, 1])
    with filter_columns[0]:
        person_options = [None, *[str(person["id"]) for person in sorted_people(people)]]
        selected_person = st.selectbox(
            "Person",
            person_options,
            format_func=lambda person_id: "All people" if person_id is None else person_name(people_by_id, person_id),
        )
    with filter_columns[1]:
        year_range = st.slider(
            "Years",
            minimum_year,
            maximum_year,
            (minimum_year, maximum_year),
        )
    evidence_options = sorted(
        {str(event["evidence_status"]) for event in events if event.get("evidence_status")}
    )
    with filter_columns[2]:
        evidence = st.selectbox("Evidence", [None, *evidence_options], format_func=lambda value: "All levels" if value is None else value)
    with filter_columns[3]:
        direction = st.selectbox("Order", ("Oldest first", "Newest first"))

    categories = sorted({str(event.get("category")) for event in events if event.get("category")})
    places = sorted({str(event.get("place")) for event in events if event.get("place")})
    secondary_filters = st.columns(3)
    with secondary_filters[0]:
        category = st.selectbox(
            "Category",
            [None, *categories],
            format_func=lambda value: "All categories" if value is None else value,
        )
    with secondary_filters[1]:
        place = st.selectbox(
            "Place",
            [None, *places],
            format_func=lambda value: "All places" if value is None else value,
        )
    with secondary_filters[2]:
        precision_filter = st.selectbox(
            "Date precision",
            [None, "exact", "year", "month", "approximate", "unknown"],
            format_func=lambda value: "All precision levels" if value is None else value.title(),
        )

    filtered: list[Record] = []
    for event in events:
        year = year_from_date(event.get("date"))
        if year and not (year_range[0] <= year <= year_range[1]):
            continue
        if selected_person and selected_person not in event.get("people_involved", []):
            continue
        if evidence and event.get("evidence_status") != evidence:
            continue
        if category and event.get("category") != category:
            continue
        if place and event.get("place") != place:
            continue
        event_precision = str(event.get("date_precision", "exact"))
        if precision_filter and event_precision != precision_filter:
            continue
        if search and search not in event_search_blob(event, people_by_id):
            continue
        filtered.append(event)

    filtered.sort(key=date_sort_key, reverse=direction == "Newest first")
    if requested_event_id in known_event_ids:
        filtered.sort(key=lambda event: str(event.get("id")) != requested_event_id)
    display_limit = st.selectbox("Records shown", (10, 25, 50, "All"), index=1)
    visible = filtered if display_limit == "All" else filtered[: int(display_limit)]
    st.caption(f"Showing {len(visible)} of {len(filtered)} matching records · {len(events)} total")

    if not visible:
        st.info("No timeline records match these filters.")
    for event in visible:
        render_event_card(event, people_by_id)
        if str(event.get("id")) == requested_event_id:
            render_context("event", requested_event_id, people_by_id)
    render_timeline_research(people_by_id, selected_person, search, year_range,
                             newest=direction == "Newest first")


def research_search_blob(record: Record, people_by_id: Mapping[str, Record]) -> str:
    involved_names = " ".join(
        person_name(people_by_id, str(person_id))
        for person_id in record.get("people_involved", [])
    )
    return " ".join(
        [
            str(record.get("title", "")),
            str(record.get("summary", "")),
            str(record.get("why_it_matters", "")),
            str(record.get("category", "")),
            str(record.get("evidence_level", "")),
            involved_names,
            " ".join(source_search_text(source) for source in record.get("sources", [])),
        ]
    ).lower()


def render_research_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
) -> None:
    research = data["research"]
    report = validate_site_data(data)
    primary_count = sum(
        "primary" in str(record.get("evidence_level", "")).lower()
        or "tier 1" in str(record.get("evidence_level", "")).lower()
        for record in research
    )
    institutional_count = sum(
        "institution" in str(record.get("evidence_level", "")).lower()
        or "tier 2" in str(record.get("evidence_level", "")).lower()
        for record in research
    )

    st.title("Research Desk")
    st.write("The working evidence library: what is documented, what is provisional, and what still needs an original record.")
    links = st.columns(3)
    links[0].link_button("Browse new findings", "?page=collection", width="stretch")
    links[1].link_button("Review research conflicts", "?page=collection&status=Conflict", width="stretch")
    links[2].link_button("Open the retrieval plan", "?page=collection&view=Retrieval+plan", width="stretch")
    metrics = st.columns(4)
    metrics[0].metric("Research notes", len(research))
    metrics[1].metric("Primary-record notes", primary_count)
    metrics[2].metric("Institutional sources", institutional_count)
    metrics[3].metric("Open data cautions", len(report.warnings))

    search = st.text_input("Search research", placeholder="Census, mill, antenna, clerk, surname…").strip().lower()
    categories = sorted({str(record.get("category")) for record in research if record.get("category")})
    evidence_levels = sorted({str(record.get("evidence_level")) for record in research if record.get("evidence_level")})
    filters = st.columns(2)
    with filters[0]:
        category = st.selectbox("Category", [None, *categories], format_func=lambda value: "All categories" if value is None else value)
    with filters[1]:
        evidence = st.selectbox("Evidence level", [None, *evidence_levels], format_func=lambda value: "All evidence levels" if value is None else value)

    filtered = []
    for record in research:
        if search and search not in research_search_blob(record, people_by_id):
            continue
        if category and record.get("category") != category:
            continue
        if evidence and record.get("evidence_level") != evidence:
            continue
        filtered.append(record)

    st.caption(f"{len(filtered)} of {len(research)} research notes shown")
    if not research:
        st.info(
            "No optional research-note file is installed. The validation report "
            "and source-aware people and timeline views remain available."
        )
    for record in sorted(filtered, key=lambda item: str(item.get("record_date", ""))):
        with st.expander(f"{record.get('record_date', 'Undated')} — {record.get('title', 'Untitled')}"):
            st.caption(
                f"{record.get('category', 'Uncategorized')} · "
                f"{record.get('evidence_level', 'Evidence not rated')} · "
                f"reviewed {record.get('checked_on', 'date not recorded')}"
            )
            st.write(record.get("summary", ""))
            if record.get("why_it_matters"):
                route_markdown("**Why it matters**")
                st.write(record["why_it_matters"])
            involved = [
                person_link(people_by_id, str(person_id))
                for person_id in record.get("people_involved", [])
            ]
            if involved:
                route_markdown("**People:** " + ", ".join(involved))
            render_sources(record.get("sources", []), "Records and repositories")

    st.divider()
    with st.expander("Automated data-quality report"):
        if report.errors:
            st.error(f"{len(report.errors)} blocking data error(s) detected.")
        else:
            st.success("All JSON files are structurally valid and protected records are unchanged.")
        for issue in report.issues:
            icon = "🔴" if issue.severity == "error" else "🟡"
            st.write(f"{icon} **{issue.code.replace('_', ' ').title()}** — {issue.message}")
        st.caption("Warnings identify research leads; the app does not automatically rewrite historical assertions.")

    with st.expander("Download a research copy"):
        st.write("Exports contain the same merged records available inside this password-gated archive.")
        export_columns = st.columns(3)
        export_columns[0].download_button(
            "People JSON",
            json.dumps(data["people"], indent=2, ensure_ascii=False),
            file_name="beverage-family-people.json",
            mime="application/json",
            width="stretch",
        )
        export_columns[1].download_button(
            "People CSV",
            records_to_csv(
                data["people"],
                ["id", "full_name", "birth_date", "birth_place", "death_date", "death_place", "parents", "spouses", "children", "residences", "notes", "sources"],
            ),
            file_name="beverage-family-people.csv",
            mime="text/csv",
            width="stretch",
        )
        export_columns[2].download_button(
            "Timeline CSV",
            records_to_csv(
                data["events"],
                ["id", "date", "title", "description", "people_involved", "evidence_status", "sources"],
            ),
            file_name="beverage-family-timeline.csv",
            mime="text/csv",
            width="stretch",
        )


def render_sources_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
) -> None:
    st.title("Sources & Method")
    st.write("How the archive separates a documented fact, a published account, and a lead that still needs verification.")
    route_link("Open the expanded research source register", "?page=collection&view=Sources")
    route_link("Read research coverage and limitations", "?page=collection&view=Inventories&inventory=Source+Coverage")

    catalog: list[dict[str, Any]] = []
    for owner_type, records in (
        ("Person", data["people"]),
        ("Event", data["events"]),
        ("Research", data["research"]),
    ):
        for record in records:
            for source in record.get("sources", []):
                details = source if isinstance(source, dict) else {"title": str(source)}
                catalog.append(
                    {
                        "source": source,
                        "repository": str(details.get("repository", "Legacy citation")),
                        "record_type": str(details.get("record_type", "Unstructured source")),
                        "evidence_level": str(details.get("evidence_level", "Not rated")),
                        "access_status": str(details.get("access_status", "")),
                        "supports": str(details.get("supports", "See linked record")),
                        "owner_type": owner_type,
                        "owner_id": str(record.get("id")),
                        "owner_title": str(record.get("full_name") or record.get("title") or "Linked record"),
                    }
                )

    st.subheader("Research source explorer")
    search = st.text_input(
        "Search sources",
        placeholder="Repository, record type, person, event, or supported claim…",
    ).strip().casefold()
    repositories = sorted({item["repository"] for item in catalog})
    record_types = sorted({item["record_type"] for item in catalog})
    explorer_filters = st.columns(3)
    with explorer_filters[0]:
        repository = st.selectbox(
            "Repository",
            [None, *repositories],
            format_func=lambda value: "All repositories" if value is None else value,
        )
    with explorer_filters[1]:
        record_type = st.selectbox(
            "Record type",
            [None, *record_types],
            format_func=lambda value: "All record types" if value is None else value,
        )
    with explorer_filters[2]:
        owner_type = st.selectbox("Linked to", [None, "Person", "Event", "Research"], format_func=lambda value: "All records" if value is None else value)

    filtered_catalog = []
    for item in catalog:
        blob = " ".join(str(value) for value in item.values()).casefold()
        if search and search not in blob:
            continue
        if repository and item["repository"] != repository:
            continue
        if record_type and item["record_type"] != record_type:
            continue
        if owner_type and item["owner_type"] != owner_type:
            continue
        filtered_catalog.append(item)

    st.caption(f"Showing {min(len(filtered_catalog), 50)} of {len(filtered_catalog)} matching citations · {len(catalog)} linked citations total")
    for item in filtered_catalog[:50]:
        if item["owner_type"] == "Person":
            owner = person_link(people_by_id, item["owner_id"])
        elif item["owner_type"] == "Event":
            owner = f"[{markdown_escape(item['owner_title'])}]({event_url(item['owner_id'])})"
        else:
            owner = markdown_escape(item["owner_title"])
        with st.container(border=True):
            route_markdown(f"**{source_markdown(item['source'])}**")
            st.caption(f"{item['repository']} · {item['record_type']} · {item['evidence_level']}")
            st.write(item["supports"])
            if item["access_status"]:
                st.caption(f"Access check: {item['access_status']}")
            route_markdown(f"Linked record: {owner}")

    st.subheader("Evidence ladder")
    evidence_rows = (
        ("1 · Primary record", "A record created by an issuing institution, such as a patent, census publication, deed, or vital record."),
        ("2 · Institutional archive", "A curated biography, oral history, local-history report, or transcription maintained by a recognized repository."),
        ("3 · Published secondary source", "A town history or genealogy that remains subject to comparison with the underlying record."),
        ("4 · Compiled or user-contributed source", "Useful as a research lead, but marked provisional until an original record is reviewed."),
        ("5 · Family tradition", "Preserved as part of family history and identified by its source when independent documentation is incomplete."),
    )
    for title, explanation in evidence_rows:
        with st.container(border=True):
            route_markdown(f"**{title}**")
            st.write(explanation)

    st.subheader("Core online repositories")
    route_markdown(
        """
        - [U.S. National Archives: 1790 Census](https://www.archives.gov/research/census/1790)
        - [U.S. Census Bureau: 1790 Maine census publication](https://www2.census.gov/prod2/decennial/documents/1790c-01.pdf)
        - [Internet Archive: 1889 Vinalhaven town history](https://archive.org/stream/briefhistoricals00vina/briefhistoricals00vina_djvu.txt)
        - [North Haven Historical Society](https://www.northhavenmainehistoricalsociety.org/)
        - [IEEE Engineering and Technology History Wiki](https://ethw.org/Harold_H._Beverage)
        - [U.S. Patent 1,381,089](https://patents.google.com/patent/US1381089A/en)
        - [Maine Genealogy Archives](https://archives.mainegenealogy.net/)
        """
    )

    st.subheader("Editorial rules")
    route_markdown(
        """
        - No person is added solely to make a branch look complete.
        - Unconfirmed relationships remain labeled **UNVERIFIED / PROVISIONAL**.
        - A census household count does not identify unnamed household members.
        - Exact assertions should carry a usable citation whenever one is available.
        - Conflicting records stay visible as research questions instead of being silently reconciled.
        """
    )

    st.subheader("Acknowledgments")
    st.write(
        "This archive combines family research, cemetery and obituary records, local histories, "
        "land and civic records, and the work of historical and engineering repositories."
    )


def render_footer() -> None:
    route_markdown(
        "<div class='bev-footer'>Beverage Family Archive · North Haven, Maine</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    begin_routes()
    apply_theme()
    check_password()

    try:
        data = load_data()
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    people_by_id = index_people(data["people"])
    relationships = relationship_index(data["people"])
    page = render_sidebar(data["people"], people_by_id)
    if page != "Home":
        route_markdown(f"[Home](?page=home) / {PAGE_GROUP[page]} / {page}")

    if page == "Home":
        render_home(data, people_by_id, relationships)
    elif page == "Search":
        render_search_page(data, people_by_id)
    elif page == "Explore the Tree":
        render_tree_page(data, people_by_id, relationships)
    elif page == "Full Family Map":
        render_full_tree_page(data, people_by_id, relationships)
    elif page == "Historical Map":
        render_map_page(load_archive())
    elif page == "Historical Places":
        render_places_page(load_archive())
    elif page == "Historical Sources":
        render_archive_page(load_archive())
    elif page == "People":
        render_people_page(data, people_by_id, relationships)
    elif page == "Timeline":
        render_unified_timeline(data, people_by_id)
    elif page == "Historical Discoveries":
        render_family_discoveries(people_by_id)
    elif page == "Stories & Discoveries":
        render_stories_page()
    elif page == "Photographs & Documents":
        render_media_page()
    elif page == "Document Reader":
        render_document_page()
    elif page == "Family Books":
        render_family_books()

    render_footer()


if __name__ == "__main__":
    main()
