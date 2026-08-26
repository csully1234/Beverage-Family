import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
from graphviz import Digraph


# ---- PASSWORD PROTECTION ----
PASSWORD = "BEVERAGE"


def check_password() -> None:
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        entered = st.text_input("Enter Password:", type="password")
        if entered == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        elif entered:
            st.error("Incorrect password")
            st.stop()
        else:
            st.stop()


check_password()
# ---- END PASSWORD PROTECTION ----


def load_json(path: Path) -> List[Dict[str, Any]]:
    """Load a JSON list, reporting readable errors in the app."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"File not found: {path}")
    except json.JSONDecodeError as error:
        st.error(f"Error parsing {path}: {error}")
    return []


def merge_records(
    base_records: List[Dict[str, Any]],
    overlay_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Merge evidence-reviewed overlays by stable record ID."""
    merged = {record.get("id"): record for record in base_records if record.get("id")}
    for record in overlay_records:
        record_id = record.get("id")
        if record_id:
            merged[record_id] = record
    return list(merged.values())


@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, List[Dict[str, Any]]]:
    data_dir = Path(__file__).parent / "data"
    people = merge_records(
        load_json(data_dir / "people.json"),
        load_json(data_dir / "research_people.json"),
    )
    events = merge_records(
        load_json(data_dir / "events.json"),
        load_json(data_dir / "research_events.json"),
    )
    return {
        "people": people,
        "events": events,
        "research": load_json(data_dir / "research.json"),
    }


def get_person_by_id(
    people: List[Dict[str, Any]], person_id: str
) -> Optional[Dict[str, Any]]:
    return next((person for person in people if person.get("id") == person_id), None)


def person_link(people: List[Dict[str, Any]], person_id: str) -> str:
    person = get_person_by_id(people, person_id)
    if not person:
        return person_id
    return f"[{person.get('full_name', person_id)}](?profile={person_id})"


def source_markdown(source: Any) -> str:
    if isinstance(source, dict):
        title = source.get("title", "Untitled source")
        url = source.get("url")
        record_type = source.get("record_type")
        label = f"[{title}]({url})" if url else str(title)
        return f"{label} — {record_type}" if record_type else label
    return str(source)


def render_sources(sources: List[Any], heading: Optional[str] = None) -> None:
    if not sources:
        return
    if heading:
        st.markdown(f"**{heading}**")
    for source in sources:
        st.markdown(f"- {source_markdown(source)}")


def render_person_profile(
    person: Dict[str, Any], people: List[Dict[str, Any]]
) -> None:
    st.header(person.get("full_name", "Unknown"))

    columns = st.columns(2)
    with columns[0]:
        st.markdown("**Born**")
        st.write(
            f"{person.get('birth_date', 'Unknown')} — "
            f"{person.get('birth_place', 'Unknown')}"
        )
    with columns[1]:
        st.markdown("**Died**")
        st.write(
            f"{person.get('death_date', 'Unknown')} — "
            f"{person.get('death_place', 'Unknown')}"
        )

    evidence_status = person.get("evidence_status")
    if evidence_status:
        st.info(f"Evidence status: {evidence_status}")

    relationship_labels = (
        ("Parents", "parents"),
        ("Siblings", "siblings"),
        ("Spouse(s)", "spouses"),
        ("Children", "children"),
    )
    for label, field in relationship_labels:
        related_ids = person.get(field, [])
        if related_ids:
            links = [person_link(people, person_id) for person_id in related_ids]
            st.markdown(f"**{label}:** {'; '.join(links)}")

    residences = person.get("residences", [])
    if residences:
        st.markdown("**Known residences**")
        for residence in residences:
            location = residence.get("location", "Unknown location")
            period = residence.get("period")
            suffix = f" ({period})" if period else ""
            st.markdown(f"- {location}{suffix}")

    if person.get("notes"):
        st.markdown("**Notes and historical context**")
        st.write(person["notes"])

    render_sources(person.get("sources", []), "Sources and evidence")


def build_graph(
    people: List[Dict[str, Any]], start_id: str, max_generations: int = 20
) -> Digraph:
    graph = Digraph(format="png")
    graph.attr(rankdir="TB")
    visited = set()

    def add_node(person_id: str, generation: int) -> None:
        if person_id in visited or generation > max_generations:
            return
        visited.add(person_id)
        person = get_person_by_id(people, person_id)
        graph.node(person_id, person.get("full_name", person_id) if person else person_id)
        if person:
            for parent_id in person.get("parents", []):
                graph.edge(parent_id, person_id)
                add_node(parent_id, generation + 1)

    add_node(start_id, 0)
    return graph


def render_tree(people: List[Dict[str, Any]], start_person_id: str) -> None:
    st.graphviz_chart(build_graph(people, start_person_id))


def render_timeline(
    events: List[Dict[str, Any]], people: List[Dict[str, Any]]
) -> None:
    query = st.text_input(
        "Search timeline",
        placeholder="Try a person, place, occupation, or source",
    ).strip().lower()

    evidence_options = sorted(
        {
            event.get("evidence_status")
            for event in events
            if event.get("evidence_status")
        }
    )
    selected_evidence = st.selectbox(
        "Evidence filter", ["All evidence levels", *evidence_options]
    )

    filtered_events = []
    for event in events:
        haystack = " ".join(
            [
                str(event.get("date", "")),
                str(event.get("title", "")),
                str(event.get("description", "")),
                " ".join(str(source) for source in event.get("sources", [])),
            ]
        ).lower()
        matches_query = not query or query in haystack
        matches_evidence = (
            selected_evidence == "All evidence levels"
            or event.get("evidence_status") == selected_evidence
        )
        if matches_query and matches_evidence:
            filtered_events.append(event)

    st.caption(f"{len(filtered_events)} of {len(events)} events shown")
    for event in sorted(filtered_events, key=lambda item: item.get("date", "")):
        st.subheader(event.get("date", "Unknown date"))
        st.markdown(f"**{event.get('title', 'Untitled event')}**")
        if event.get("evidence_status"):
            st.caption(f"Evidence: {event['evidence_status']}")
        st.write(event.get("description", ""))

        involved = [
            person_link(people, person_id)
            for person_id in event.get("people_involved", [])
            if get_person_by_id(people, person_id)
        ]
        if involved:
            st.markdown("**People:** " + ", ".join(involved))
        render_sources(event.get("sources", []), "Sources")
        st.divider()


def render_research_library(
    research: List[Dict[str, Any]], people: List[Dict[str, Any]]
) -> None:
    st.title("Research Library")
    st.write(
        "A record-by-record audit trail for new findings, corrected claims, "
        "and questions that still need original-document review."
    )

    search = st.text_input(
        "Search research",
        placeholder="Try census, antenna, clerk, or a surname",
    ).strip().lower()
    categories = sorted(
        {record.get("category") for record in research if record.get("category")}
    )
    selected_category = st.selectbox("Category", ["All categories", *categories])

    filtered_records = []
    for record in research:
        involved_names = " ".join(
            (
                get_person_by_id(people, person_id) or {}
            ).get("full_name", person_id)
            for person_id in record.get("people_involved", [])
        )
        haystack = " ".join(
            [
                str(record.get("title", "")),
                str(record.get("summary", "")),
                str(record.get("why_it_matters", "")),
                involved_names,
            ]
        ).lower()
        if search and search not in haystack:
            continue
        if (
            selected_category != "All categories"
            and record.get("category") != selected_category
        ):
            continue
        filtered_records.append(record)

    st.caption(f"{len(filtered_records)} of {len(research)} research notes shown")
    for record in sorted(
        filtered_records, key=lambda item: item.get("record_date", ""), reverse=True
    ):
        label = f"{record.get('record_date', 'Undated')} — {record.get('title', 'Untitled')}"
        with st.expander(label):
            st.caption(
                f"Category: {record.get('category', 'Uncategorized')} · "
                f"Evidence: {record.get('evidence_level', 'Not rated')} · "
                f"Reviewed: {record.get('checked_on', 'Not recorded')}"
            )
            st.write(record.get("summary", ""))
            if record.get("why_it_matters"):
                st.markdown("**Why it matters**")
                st.write(record["why_it_matters"])

            involved = [
                person_link(people, person_id)
                for person_id in record.get("people_involved", [])
                if get_person_by_id(people, person_id)
            ]
            if involved:
                st.markdown("**People:** " + ", ".join(involved))
            render_sources(record.get("sources", []), "Records and repositories")


def render_home(
    people: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    research: List[Dict[str, Any]],
) -> None:
    st.title("Beverage Family")
    st.subheader("North Haven roots, family connections, and documented history")
    st.write(
        "Explore a sourced family tree, individual profiles, a chronological "
        "timeline, and a research audit trail that separates records from inference."
    )

    columns = st.columns(3)
    columns[0].metric("People", len(people))
    columns[1].metric("Timeline events", len(events))
    columns[2].metric("Research notes", len(research))

    st.info(
        "Evidence policy: original records and institutional archives receive the "
        "most weight. Published genealogies, memorials, and family traditions remain "
        "visible but are labeled when original records have not been reviewed."
    )

    st.subheader("Research highlights")
    highlight_ids = {
        "research_census_1790",
        "research_harold_antenna",
    }
    for record in research:
        if record.get("id") in highlight_ids:
            st.markdown(
                f"**{record.get('title')}**  \\n"
                f"{record.get('why_it_matters', record.get('summary', ''))}"
            )


def render_sources_page() -> None:
    st.title("Sources, Method, and Acknowledgments")
    st.markdown(
        """
### How evidence is labeled

- **Primary record:** a record created by an issuing institution, such as a patent or census publication.
- **Institutional archive or transcription:** a curated biography, oral history, local-history report, or transcription maintained by a recognized repository.
- **Published secondary source:** a town history or genealogy that must still be checked against the original record where possible.
- **Compiled or user-contributed source:** useful as a lead, but not treated as proof by itself.

Dates marked only by a year may be approximate. A household count does not identify unnamed household members, and a relationship copied from a compiled tree remains provisional until an original record is reviewed.

### Core online repositories

- [U.S. National Archives: 1790 Census](https://www.archives.gov/research/census/1790)
- [U.S. Census Bureau: 1790 Maine census publication](https://www2.census.gov/prod2/decennial/documents/1790c-01.pdf)
- [Internet Archive: 1889 Vinalhaven town history](https://archive.org/stream/briefhistoricals00vina/briefhistoricals00vina_djvu.txt)
- [North Haven Historical Society](https://www.northhavenmainehistoricalsociety.org/)
- [IEEE Engineering and Technology History Wiki](https://ethw.org/Harold_H._Beverage)
- [U.S. Patent 1,381,089](https://patents.google.com/patent/US1381089A/en)
- [Maine Genealogy Archives](https://archives.mainegenealogy.net/)

### Privacy

The public site omits street-level property details and sensitive source documents for living relatives. Private family records are cited in general terms when the underlying material should not be published.
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Beverage Family Genealogy",
        page_icon="🌊",
        layout="wide",
    )
    data = load_data()
    people = data["people"]
    events = data["events"]
    research = data["research"]

    profile_param = st.query_params.get("profile")
    if isinstance(profile_param, list):
        profile_param = profile_param[0] if profile_param else None

    pages = (
        "Home",
        "Family Tree",
        "Profiles",
        "Timeline",
        "Research Library",
        "Sources & Acknowledgments",
    )
    default_page = "Profiles" if profile_param else "Home"

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", pages, index=pages.index(default_page))

    if page == "Home":
        render_home(people, events, research)

    elif page == "Family Tree":
        st.title("Family Tree")
        sorted_people = sorted(people, key=lambda item: item.get("full_name", ""))
        ids = [person["id"] for person in sorted_people]
        names = {
            person["id"]: person.get("full_name", person["id"])
            for person in sorted_people
        }
        if not ids:
            st.warning("No people available to display the tree.")
        else:
            default_id = profile_param if profile_param in ids else ids[0]
            selected_id = st.selectbox(
                "Build an ancestor tree from",
                options=ids,
                format_func=lambda person_id: names.get(person_id, person_id),
                index=ids.index(default_id),
            )
            render_tree(people, selected_id)

    elif page == "Profiles":
        st.title("Person Profiles")
        sorted_people = sorted(people, key=lambda item: item.get("full_name", ""))
        ids = [person["id"] for person in sorted_people]
        names = {
            person["id"]: person.get("full_name", person["id"])
            for person in sorted_people
        }
        if not ids:
            st.warning("No people data available.")
        else:
            selected_id = profile_param if profile_param in ids else ids[0]
            selected_id = st.selectbox(
                "Select a person",
                options=ids,
                format_func=lambda person_id: names.get(person_id, person_id),
                index=ids.index(selected_id),
            )
            person = get_person_by_id(people, selected_id)
            if person:
                render_person_profile(person, people)
            else:
                st.error("Person not found.")

    elif page == "Timeline":
        st.title("Family Timeline")
        if events:
            render_timeline(events, people)
        else:
            st.warning("No events available in the timeline.")

    elif page == "Research Library":
        render_research_library(research, people)

    elif page == "Sources & Acknowledgments":
        render_sources_page()


if __name__ == "__main__":
    main()
