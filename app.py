import json
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from graphviz import Digraph


###############################################################
# Beverage Family Genealogy Application
#
# This Streamlit app lets visitors explore the Beverage family
# of North Haven, Maine.  It is designed to be easy to modify
# and extend.  To add or update family members or events,
# modify the JSON files in the `data/` directory.
###############################################################


def load_json(path: Path) -> List[Dict]:
    """Load a JSON file and return its contents.

    Parameters
    ----------
    path : Path
        Path to the JSON file.

    Returns
    -------
    list
        Parsed JSON data.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Error parsing {path}: {e}")
        return []


@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, List[Dict]]:
    """Load people and events data from JSON files.

    Returns
    -------
    dict
        Dictionary with 'people' and 'events' lists.
    """
    data_dir = Path(__file__).parent / "data"
    people = load_json(data_dir / "people.json")
    events = load_json(data_dir / "events.json")
    return {"people": people, "events": events}


def get_person_by_id(people: List[Dict], person_id: str) -> Optional[Dict]:
    """Retrieve a person dict by their ID.

    Parameters
    ----------
    people : list of dict
        List of all people.
    person_id : str
        Unique identifier of the person.

    Returns
    -------
    dict or None
        Person record if found, otherwise None.
    """
    for person in people:
        if person.get("id") == person_id:
            return person
    return None


def render_person_profile(person: Dict, people: List[Dict]):
    """Render a detailed profile for a person.

    Parameters
    ----------
    person : dict
        The person record to display.
    people : list of dict
        All people, used to look up related names.
    """
    st.header(person.get("full_name", "Unknown"))

    # Basic info
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Born:**")
        st.write(f"{person.get('birth_date', 'Unknown')} – {person.get('birth_place', 'Unknown')}")
    with cols[1]:
        st.markdown("**Died:**")
        st.write(f"{person.get('death_date', 'Unknown')} – {person.get('death_place', 'Unknown')}")

    def link_person(pid: str) -> str:
        """Return a clickable link for a person ID.

        If the person is missing from the dataset, return just the ID.
        """
        p = get_person_by_id(people, pid)
        # Build a link to the profile using the query parameter. Avoid nested f-strings.
        if p:
            profile_query = "?profile=" + p["id"]
            return f"[{p['full_name']}]({profile_query})"
        return pid

    # Parents
    if person.get("parents"):
        parent_links = [link_person(pid) for pid in person["parents"]]
        st.markdown(f"**Parents:** {'; '.join(parent_links)}")

    # Siblings
    if person.get("siblings"):
        sib_links = [link_person(sid) for sid in person["siblings"]]
        st.markdown(f"**Siblings:** {'; '.join(sib_links)}")

    # Spouses
    if person.get("spouses"):
        spouse_links = [link_person(spid) for spid in person["spouses"]]
        st.markdown(f"**Spouse(s):** {'; '.join(spouse_links)}")

    # Children
    if person.get("children"):
        child_links = [link_person(cid) for cid in person["children"]]
        st.markdown(f"**Children:** {'; '.join(child_links)}")

    # Residences
    if person.get("residences"):
        st.markdown("**Known residences:**")
        for residence in person["residences"]:
            loc = residence.get("location", "Unknown location")
            period = residence.get("period", "")
            st.write(f"- {loc} {f'({period})' if period else ''}")

    # Notes
    notes = person.get("notes")
    if notes:
        st.markdown("**Notes / Historical context:**")
        st.write(notes)

    # Sources
    sources = person.get("sources")
    if sources:
        st.markdown("**Sources / Evidence:**")
        for src in sources:
            st.write(f"- {src}")


def build_graph(people: List[Dict], start_id: str, max_generations: int = 4) -> Digraph:
    """Construct a Graphviz graph for a family tree starting from a person.

    Parameters
    ----------
    people : list of dict
        All people records.
    start_id : str
        Person ID to build the tree from.
    max_generations : int, optional
        How many generations upward to include (default: 4).

    Returns
    -------
    graphviz.Digraph
        The generated graph.
    """
    graph = Digraph(format="png")
    graph.attr(rankdir='TB')

    visited = set()

    def add_node(pid: str, generation: int):
        if pid in visited or generation > max_generations:
            return
        visited.add(pid)
        person = get_person_by_id(people, pid)
        label = person["full_name"] if person else pid
        graph.node(pid, label)
        if person:
            # add parents
            for parent_id in person.get("parents", []):
                graph.edge(parent_id, pid)
                add_node(parent_id, generation + 1)

    add_node(start_id, 0)
    return graph


def render_tree(people: List[Dict], start_person_id: str):
    """Render the family tree in Streamlit using Graphviz.

    Parameters
    ----------
    people : list of dict
        All people.
    start_person_id : str
        Person ID to build the tree from.
    """
    graph = build_graph(people, start_person_id, max_generations=20)
    st.graphviz_chart(graph)


def render_timeline(events: List[Dict], people: List[Dict]):
    """Render a chronological timeline of events.

    Parameters
    ----------
    events : list of dict
        Timeline events.
    people : list of dict
        All people (to resolve names).
    """
    # Sort events by date (string sort works if ISO format).
    sorted_events = sorted(events, key=lambda e: e.get("date", ""))
    for event in sorted_events:
        st.subheader(event.get("date", "Unknown date"))
        st.markdown(f"**{event.get('title', 'Untitled event')}**")
        st.write(event.get("description", ""))
        if event.get("people_involved"):
            links = []
            for pid in event["people_involved"]:
                person = get_person_by_id(people, pid)
                if person:
                    # Build a link using a query parameter; avoid nested f-strings.
                    profile_query = "?profile=" + person["id"]
                    links.append(f"[{person['full_name']}]({profile_query})")
            if links:
                st.markdown("Involved: " + ", ".join(links))
        if event.get("sources"):
            st.markdown("Sources:")
            for src in event["sources"]:
                st.write(f"- {src}")


def main():
    st.set_page_config(page_title="Beverage Family Genealogy", layout="wide")
    data = load_data()
    people = data.get("people", [])
    events = data.get("events", [])

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ("Home", "Family Tree", "Profiles", "Timeline", "Sources & Acknowledgments"),
    )

    # Determine if a profile query parameter is present (for linking within the app)
    query_params = st.query_params
    profile_param = query_params.get("profile")

    if page == "Home":
        st.title("Beverage Family of North Haven, Maine")
        st.markdown(
            """
            Welcome to the Beverage family genealogy site!  This project traces the
            lineage of the Beverage (Beveridge) family from modern-day members
            back to the 18th century founders on North Haven Island, Maine.
            """
        )

    elif page == "Family Tree":
        st.title("Family Tree")
        # Provide a selectbox to choose the starting person.
        ids = [p["id"] for p in people]
        names = {p["id"]: p["full_name"] for p in people}
        default_id = profile_param if profile_param else (ids[0] if ids else None)
        if not ids:
            st.warning("No people available to display the tree.")
        else:
            selected_id = st.selectbox(
                "Select a person to build the tree from:",
                options=ids,
                format_func=lambda x: names.get(x, x),
                index=ids.index(default_id) if default_id in ids else 0,
            )
            render_tree(people, selected_id)
            st.markdown(
                "Select a node in the sidebar or click a name in the tree to view a profile."
            )

    elif page == "Profiles":
        st.title("Person Profiles")
        # Determine which person to show: either from query param or selectbox
        ids = [p["id"] for p in people]
        names = {p["id"]: p["full_name"] for p in people}
        if not ids:
            st.warning("No people data available.")
        else:
            selected_id = profile_param if profile_param in ids else None
            selected_id = st.selectbox(
                "Select a person:",
                options=ids,
                format_func=lambda x: names.get(x, x),
                index=ids.index(selected_id) if selected_id else 0,
            )
            person = get_person_by_id(people, selected_id)
            if person:
                render_person_profile(person, people)
            else:
                st.error("Person not found.")

    elif page == "Timeline":
        st.title("Family Timeline")
        if not events:
            st.warning("No events available in the timeline.")
        else:
            render_timeline(events, people)

    elif page == "Sources & Acknowledgments":
        st.title("Sources & Acknowledgments")
        st.markdown(
            """
            ### Major Sources
            - Cemetery memorials and gravestone inscriptions (via Find A Grave)
            - Hancock and Knox County land deed abstracts
            - Obituaries from Maine newspapers and funeral homes
            - Family research notes compiled by descendants
            """
        )


if __name__ == "__main__":
    main()
