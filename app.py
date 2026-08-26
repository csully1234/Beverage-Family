"""Beverage Family — a searchable, source-first family archive."""

from __future__ import annotations

import hmac
import json
import os
from datetime import date
from html import escape
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote, urlparse

import streamlit as st
from graphviz import Digraph

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


# This remains the first Streamlit command for compatibility with older
# supported releases as well as current Streamlit versions.
st.set_page_config(
    page_title="Beverage Family of North Haven",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "A source-first archive of the Beverage family and its North Haven roots."
    },
)


DATA_DIR = Path(__file__).parent / "data"
LEGACY_COMPATIBILITY_PASSWORD = "BEVERAGE"

PAGE_SLUGS = {
    "Home": "home",
    "Search": "search",
    "Explore the Tree": "tree",
    "People": "people",
    "Timeline": "timeline",
    "Research Desk": "research",
    "Sources & Method": "sources",
}
SLUG_PAGES = {slug: page for page, slug in PAGE_SLUGS.items()}


def apply_theme() -> None:
    """Apply a restrained coastal-archive visual system."""

    st.markdown(
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
            padding-top: 2rem;
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
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background: var(--bev-navy);
            border-color: var(--bev-navy);
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
            .block-container { padding-top: 1rem; }
            .bev-hero { border-radius: 16px; padding: 2rem 1.35rem 2.5rem; }
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
        st.markdown("<div class='bev-eyebrow'>Private family archive</div>", unsafe_allow_html=True)
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


def markdown_escape(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def person_url(person_id: str) -> str:
    return f"?page=people&profile={quote(person_id)}"


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
        st.markdown(f"**{heading}**")
    for source in sources:
        st.markdown(f"- {source_markdown(source)}")


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
    st.query_params["page"] = PAGE_SLUGS[page]
    if page != "People" and "profile" in st.query_params:
        del st.query_params["profile"]
    if page != "Timeline" and "event" in st.query_params:
        del st.query_params["event"]


def open_profile(person_id: str) -> None:
    st.session_state["nav_page"] = "People"
    st.session_state["profile_selector"] = person_id
    st.query_params["page"] = "people"
    st.query_params["profile"] = person_id
    if "event" in st.query_params:
        del st.query_params["event"]


def sync_sidebar_route() -> None:
    page = st.session_state["nav_page"]
    st.query_params["page"] = PAGE_SLUGS[page]
    if page != "People" and "profile" in st.query_params:
        del st.query_params["profile"]
    if page != "Timeline" and "event" in st.query_params:
        del st.query_params["event"]


def sync_profile_route() -> None:
    person_id = st.session_state.get("profile_selector")
    if person_id:
        st.query_params["page"] = "people"
        st.query_params["profile"] = person_id


def sorted_people(people: list[Record]) -> list[Record]:
    return sorted(people, key=person_sort_key)


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
    st.session_state["_last_query_slug"] = query_slug

    with st.sidebar:
        st.markdown("### 🌊 Beverage Family")
        st.caption("North Haven genealogy archive")
        page = st.radio(
            "Navigation",
            list(PAGE_SLUGS),
            key="nav_page",
            on_change=sync_sidebar_route,
            label_visibility="collapsed",
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
                else person_name(people_by_id, person_id)
            ),
            key="sidebar_person_lookup",
        )
        if st.button("Open profile", disabled=quick_person is None, width="stretch"):
            if quick_person:
                open_profile(quick_person)
                st.rerun()

        st.divider()
        if st.button("Log out", width="stretch"):
            st.session_state.clear()
            st.rerun()
        st.caption(f"{len(people)} profiles indexed")
    return page


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

    st.markdown(
        """
        <section class="bev-hero">
          <div class="bev-kicker">North Haven · Maine · Family archive</div>
          <h1>The Beverage Family</h1>
          <p>Three centuries of people, places, work, and family connections—organized into one searchable, source-first record.</p>
          <p><em>Designed to make things less confusing but I'm slightly more confused now</em></p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    source_count = len(unique_sources(data))
    metric_columns = st.columns(6)
    metric_columns[0].metric("People", len(people))
    metric_columns[1].metric("Timeline records", len(events))
    metric_columns[2].metric("Places", len(unique_places(people)))
    metric_columns[3].metric("Sources", source_count)
    metric_columns[4].metric("Generations", generation_count(people_by_id, relationships))
    metric_columns[5].metric("Recorded span", span)

    st.write("")
    action_columns = st.columns(4)
    action_columns[0].button(
        "Explore the family tree",
        type="primary",
        width="stretch",
        on_click=navigate,
        args=("Explore the Tree",),
    )
    action_columns[1].button(
        "Browse all people",
        width="stretch",
        on_click=navigate,
        args=("People",),
    )
    action_columns[2].button(
        "Walk through the timeline",
        width="stretch",
        on_click=navigate,
        args=("Timeline",),
    )
    action_columns[3].button(
        "Search the whole archive",
        width="stretch",
        on_click=navigate,
        args=("Search",),
    )

    st.divider()
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown("<div class='bev-eyebrow'>Start with a name</div>", unsafe_allow_html=True)
        st.subheader("Find a family member")
        ordered = sorted_people(people)
        person_ids = [str(person["id"]) for person in ordered]
        chosen = st.selectbox(
            "Search the profile index",
            options=person_ids,
            format_func=lambda person_id: (
                f"{person_name(people_by_id, person_id)} · "
                f"{life_span(people_by_id[person_id])}"
            ),
            key="home_person_lookup",
            label_visibility="collapsed",
        )
        if st.button("View this profile", type="primary"):
            open_profile(chosen)
            st.rerun()

        st.markdown("<div class='bev-eyebrow'>Research standard</div>", unsafe_allow_html=True)
        st.subheader("Evidence stays visible")
        st.write(
            "Original records and institutional archives receive the most weight. "
            "Compiled genealogy remains useful, but provisional links are labeled "
            "until the underlying record image is reviewed."
        )

    with right:
        st.markdown("<div class='bev-eyebrow'>Featured records</div>", unsafe_allow_html=True)
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
                st.markdown(f"**{record.get('title', 'Research record')}**")
                st.write(record.get("why_it_matters") or record.get("summary", ""))
                st.caption(
                    f"{record.get('record_date', 'Undated')} · "
                    f"{record.get('evidence_level', 'Evidence not rated')}"
                )

    st.divider()
    today = date.today()
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
        st.markdown("<div class='bev-eyebrow'>On this day</div>", unsafe_allow_html=True)
        st.subheader("Beverage history today")
        if on_this_day:
            for event in sorted(on_this_day, key=date_sort_key)[:3]:
                st.markdown(f"[{event.get('title', 'Untitled event')}]({event_url(str(event['id']))})")
                st.caption(format_date(event.get("date"), event.get("date_precision")))
        else:
            st.caption("No exact-date event is recorded for this calendar day yet.")
    with relative_column:
        st.markdown("<div class='bev-eyebrow'>Random relative</div>", unsafe_allow_html=True)
        st.subheader(random_person.get("full_name") if random_person else "No profile")
        if random_person:
            st.caption(life_span(random_person))
            notes = str(random_person.get("notes") or random_person.get("biography") or "Profile ready to explore.")
            st.write(notes if len(notes) <= 220 else notes[:217] + "…")
            st.markdown(f"[Open profile →]({person_url(str(random_person['id']))})")
    with recent_column:
        st.markdown("<div class='bev-eyebrow'>Recently researched</div>", unsafe_allow_html=True)
        st.subheader("Newly documented")
        recent = sorted(
            research,
            key=lambda item: (str(item.get("checked_on", "")), str(item.get("record_date", ""))),
            reverse=True,
        )[:3]
        for record in recent:
            st.markdown(f"**{record.get('title', 'Research note')}**")
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
            st.markdown(
                f"**{format_date(event.get('date'), event.get('date_precision'))}**"
            )
            precision = event.get("date_precision")
            if precision and precision != "exact":
                st.caption(f"{str(precision).replace('_', ' ').title()} date")
        with story_column:
            st.markdown(f"### {event.get('title', 'Untitled event')}")
            if event.get("evidence_status"):
                label, provisional = evidence_label(str(event["evidence_status"]))
                st.caption(label)
            st.write(event.get("description", ""))
            involved = [
                person_link(people_by_id, str(person_id))
                for person_id in event.get("people_involved", [])
            ]
            if involved:
                st.markdown("**People:** " + ", ".join(involved))
            if event.get("sources"):
                if compact:
                    st.caption(f"{len(event['sources'])} cited source(s)")
                else:
                    with st.expander("View sources"):
                        render_sources(event["sources"])


def render_relation_group(
    title: str,
    related_ids: list[str],
    people_by_id: Mapping[str, Record],
) -> None:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        if not related_ids:
            st.caption("No relationship entered")
            return
        for related_id in related_ids:
            related = people_by_id.get(related_id)
            suffix = f" · {life_span(related)}" if related else " · unresolved profile"
            st.markdown(f"- {person_link(people_by_id, related_id)}{suffix}")


def render_person_profile(
    person: Record,
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
    events: list[Record],
    research: list[Record],
) -> None:
    person_id = str(person["id"])
    st.markdown(
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
        st.markdown("**Born**")
        st.write(
            f"{format_date(person.get('birth_date'), person.get('birth_date_precision'))} "
            f"— {person.get('birth_place') or 'Unknown'}"
        )
    with died:
        st.markdown("**Died**")
        if person.get("death_date") or person.get("death_place"):
            st.write(
                f"{format_date(person.get('death_date'), person.get('death_date_precision'))} "
                f"— {person.get('death_place') or 'Unknown'}"
            )
        else:
            st.write("No death record entered")

    render_evidence_status(person.get("evidence_status"))
    if person.get("needs_research"):
        st.warning("Needs more research — this profile contains one or more provisional leads.")
    if person.get("research_completeness"):
        st.caption(f"Research status: {person['research_completeness']}")

    story_tab, family_tab, places_tab, sources_tab = st.tabs(
        ["Story", "Family", "Places", "Sources & research"]
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
                        st.markdown(f"**{label}**")
                        for value in values:
                            st.markdown(f"- {markdown_escape(value)}")

        person_events = related_events(events, person_id)
        st.subheader(f"Timeline records involving this person ({len(person_events)})")
        if not person_events:
            st.caption("No linked timeline records yet.")
        for event in person_events[:8]:
            render_event_card(event, people_by_id, compact=True)
        if len(person_events) > 8:
            st.caption(f"{len(person_events) - 8} additional records are available on the Timeline page.")

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

        if st.button("Center this person in the family tree", type="primary"):
            st.session_state["tree_person"] = person_id
            navigate("Explore the Tree")
            st.rerun()

    with places_tab:
        residences = person.get("residences", [])
        if residences:
            st.subheader("Known residences")
            for residence in residences:
                with st.container(border=True):
                    st.markdown(f"**{residence.get('location', 'Unknown location')}**")
                    if residence.get("period"):
                        st.caption(str(residence["period"]))
        else:
            st.info("No residence history has been entered for this profile.")

    with sources_tab:
        st.subheader("Profile sources")
        render_sources(person.get("sources", []))

        date_provenance = person.get("date_provenance", {})
        if date_provenance:
            st.subheader("Date precision")
            for field_name, details in date_provenance.items():
                label = field_name.replace("_", " ").title()
                st.markdown(f"**{label}:** {person.get(field_name + '_precision', 'unknown').title()}")
                if details.get("determination"):
                    st.caption(str(details["determination"]))

        conflicts = person.get("conflicting_evidence", [])
        if conflicts:
            st.subheader("Evidence conflicts for family review")
            for conflict in conflicts:
                with st.container(border=True):
                    st.markdown(f"**{conflict.get('claim', 'Conflicting claim')}**")
                    st.write(f"Existing record: {conflict.get('existing_record', 'Not recorded')}")
                    st.write(f"Reviewed source: {conflict.get('reviewed_source', 'Not recorded')}")
                    st.caption(str(conflict.get("status", "Unresolved")))

        linked_research = [
            record
            for record in research
            if person_id in record.get("people_involved", [])
        ]
        st.subheader(f"Research notes ({len(linked_research)})")
        for record in linked_research:
            with st.expander(record.get("title", "Untitled research note")):
                st.caption(
                    f"{record.get('category', 'Uncategorized')} · "
                    f"{record.get('evidence_level', 'Evidence not rated')}"
                )
                st.write(record.get("summary", ""))
                if record.get("why_it_matters"):
                    st.markdown("**Why it matters**")
                    st.write(record["why_it_matters"])
                render_sources(record.get("sources", []), "Records and repositories")


def render_people_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    st.title("People")
    st.write("Search the complete profile index, then move directly through connected relatives and records.")

    ordered = sorted_people(data["people"])
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
            f"{person_name(people_by_id, person_id)} · {life_span(people_by_id[person_id])}"
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


def render_search_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
) -> None:
    st.title("Search the Whole Archive")
    st.write(
        "Search names and alternate spellings, places, dates, occupations, notes, "
        "events, repositories, and source titles from one place."
    )
    query = st.text_input(
        "Global search",
        placeholder="Try Beverage antenna, North Haven, nurse, 1921, or Columbia…",
    ).strip().casefold()
    if not query:
        st.info("Enter a word, name, place, year, occupation, event, or source.")
        return

    people_matches = [person for person in data["people"] if query in record_search_blob(person)]
    event_matches = [event for event in data["events"] if query in record_search_blob(event)]
    research_matches = [record for record in data["research"] if query in record_search_blob(record)]

    source_matches: list[tuple[Any, str, str]] = []
    for collection_name, records in (
        ("person", data["people"]),
        ("event", data["events"]),
        ("research", data["research"]),
    ):
        for record in records:
            for source in record.get("sources", []):
                if query in source_search_text(source).casefold():
                    source_matches.append((source, collection_name, str(record["id"])))

    metrics = st.columns(4)
    metrics[0].metric("People", len(people_matches))
    metrics[1].metric("Events", len(event_matches))
    metrics[2].metric("Research notes", len(research_matches))
    metrics[3].metric("Source links", len(source_matches))

    people_tab, events_tab, research_tab, sources_tab = st.tabs(
        ["People", "Events", "Research", "Sources"]
    )
    with people_tab:
        if not people_matches:
            st.caption("No people matched.")
        for person in sorted(people_matches, key=person_sort_key)[:30]:
            with st.container(border=True):
                st.markdown(f"### [{markdown_escape(person.get('full_name', 'Unnamed'))}]({person_url(str(person['id']))})")
                st.caption(life_span(person))
                context = str(person.get("biography") or person.get("notes") or "Profile available")
                st.write(context if len(context) < 280 else context[:277] + "…")
    with events_tab:
        if not event_matches:
            st.caption("No events matched.")
        for event in sorted(event_matches, key=date_sort_key)[:30]:
            with st.container(border=True):
                st.markdown(f"### [{markdown_escape(event.get('title', 'Untitled event'))}]({event_url(str(event['id']))})")
                st.caption(format_date(event.get("date"), event.get("date_precision")))
                description = str(event.get("description", ""))
                st.write(description if len(description) < 320 else description[:317] + "…")
    with research_tab:
        if not research_matches:
            st.caption("No research notes matched.")
        for record in research_matches[:30]:
            with st.container(border=True):
                st.markdown(f"### {markdown_escape(record.get('title', 'Research note'))}")
                st.caption(
                    f"{record.get('category', 'Uncategorized')} · "
                    f"{record.get('evidence_level', 'Evidence not rated')}"
                )
                st.write(record.get("summary", ""))
    with sources_tab:
        if not source_matches:
            st.caption("No sources matched.")
        seen_matches: set[tuple[str, str, str]] = set()
        for source, owner_type, owner_id in source_matches[:50]:
            key = (source_search_text(source), owner_type, owner_id)
            if key in seen_matches:
                continue
            seen_matches.add(key)
            if owner_type == "person":
                owner_link = person_link(people_by_id, owner_id)
            elif owner_type == "event":
                event = next((item for item in data["events"] if item.get("id") == owner_id), {})
                owner_link = f"[{markdown_escape(event.get('title', 'Timeline event'))}]({event_url(owner_id)})"
            else:
                record = next((item for item in data["research"] if item.get("id") == owner_id), {})
                owner_link = markdown_escape(record.get("title", "Research note"))
            st.markdown(f"- {source_markdown(source)}  \n  Supports: {owner_link}")


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


def render_tree_page(
    data: dict[str, list[Record]],
    people_by_id: Mapping[str, Record],
    relationships: dict[str, dict[str, set[str]]],
) -> None:
    st.title("Explore the Family Tree")
    st.write("Choose a person and switch between their ancestors, descendants, or immediate family.")

    ordered = sorted_people(data["people"])
    person_ids = [str(person["id"]) for person in ordered]
    if "tree_person" not in st.session_state or st.session_state["tree_person"] not in person_ids:
        st.session_state["tree_person"] = get_query_value("profile") if get_query_value("profile") in person_ids else person_ids[0]

    picker, mode, depth = st.columns([2, 1.15, 1])
    with picker:
        focus_id = st.selectbox(
            "Center person",
            options=person_ids,
            format_func=lambda person_id: person_name(people_by_id, person_id),
            key="tree_person",
        )
    with mode:
        view = st.selectbox(
            "Tree view",
            ("Ancestors", "Descendants", "Both", "Immediate family"),
            index=2,
        )
    with depth:
        generations = st.slider("Generations", 1, 8, 4, disabled=view == "Immediate family")

    graph = build_family_graph(people_by_id, relationships, focus_id, view, generations)
    st.graphviz_chart(graph, width="stretch")
    st.caption("Nodes include profile links where supported. The family navigator below always opens the selected profile.")

    focus = people_by_id[focus_id]
    with st.container(border=True):
        summary, action = st.columns([3, 1])
        with summary:
            st.markdown(f"**{focus.get('full_name')}** · {life_span(focus)}")
            if focus.get("notes"):
                notes = str(focus["notes"])
                st.write(notes if len(notes) <= 280 else notes[:277] + "…")
        with action:
            if st.button("Open full profile", type="primary", width="stretch"):
                open_profile(focus_id)
                st.rerun()

    st.divider()
    st.subheader("Relationship finder")
    st.write("Select two documented profiles to see the shortest connection supported by the current family graph.")
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
        st.success(f"Connected in {len(path) - 1} relationship step(s).")
        path_parts: list[str] = []
        for index, person_id in enumerate(path):
            path_parts.append(person_link(people_by_id, person_id))
            if index < len(path) - 1:
                step = relationship_step_label(relationships, person_id, path[index + 1])
                path_parts.append(f"— *{step}* →")
        st.markdown(" ".join(path_parts))


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
                st.markdown("**Why it matters**")
                st.write(record["why_it_matters"])
            involved = [
                person_link(people_by_id, str(person_id))
                for person_id in record.get("people_involved", [])
            ]
            if involved:
                st.markdown("**People:** " + ", ".join(involved))
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
            st.markdown(f"**{source_markdown(item['source'])}**")
            st.caption(f"{item['repository']} · {item['record_type']} · {item['evidence_level']}")
            st.write(item["supports"])
            if item["access_status"]:
                st.caption(f"Access check: {item['access_status']}")
            st.markdown(f"Linked record: {owner}")

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
            st.markdown(f"**{title}**")
            st.write(explanation)

    st.subheader("Core online repositories")
    st.markdown(
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
    st.markdown(
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
    st.markdown(
        "<div class='bev-footer'>Beverage Family Archive · North Haven, Maine</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
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

    if page == "Home":
        render_home(data, people_by_id, relationships)
    elif page == "Search":
        render_search_page(data, people_by_id)
    elif page == "Explore the Tree":
        render_tree_page(data, people_by_id, relationships)
    elif page == "People":
        render_people_page(data, people_by_id, relationships)
    elif page == "Timeline":
        render_timeline_page(data["events"], data["people"], people_by_id)
    elif page == "Research Desk":
        render_research_page(data, people_by_id)
    elif page == "Sources & Method":
        render_sources_page(data, people_by_id)

    render_footer()


if __name__ == "__main__":
    main()
