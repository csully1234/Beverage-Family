"""Claim-level family relationship audit, separate from the canonical tree.

A person citation does not verify all parent-child, spouse or sibling edges.
Only reviewed exact-ID pairs receive their documented qualification; the rest
are marked "Not individually reviewed" rather than presumed true or false.
This module has NO mutator for people, events or the existing relationship graph.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Mapping

import streamlit as st

from family_data import relationship_index
from routing_ui import route_link

FILE = Path(__file__).resolve().parent / "data" / "phase15_relationship_reviews.json"
PHASE29_FILE = Path(__file__).resolve().parent / "data" / "phase29_relationship_reviews.json"
STATUS_NAMES = {
    "original_probate_record": "Specifically named in a contemporary probate court record",
    "corroborated_publication": "Supported by corroborating published records",
    "contemporary_report": "Recorded in a contemporary or near-contemporary account",
    "published_record": "Reported in a published historical record",
    "identity_needs_verification": "Identity or relationship still requires proof",
    "not_reviewed": "Documentary support for this link not yet audited",
}
KIND_NAMES = {
    "parent_child": "Parent and child",
    "spouses": "Spouses / historically recorded partners",
    "siblings": "Siblings",
}


def edge_key(kind: str, a: str, b: str) -> tuple[str, str, str]:
    """The direction of a parent-child edge matters; a spouse/sibling edge does not."""
    if kind not in KIND_NAMES or not a or not b or a == b:
        raise ValueError("Invalid family relationship pair")
    a, b = str(a), str(b)
    if kind != "parent_child" and b < a:
        a, b = b, a
    return kind, a, b


def load_relationship_reviews() -> list[dict]:
    """Preserve old reviewed claims; append original-specific reviewed additions.

    Never modify a historic family link merely to change its source annotation.
    """
    records = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Relationship review register must contain a list")
    if PHASE29_FILE.exists():
        added = json.loads(PHASE29_FILE.read_text(encoding="utf-8"))
        if not isinstance(added, list):
            raise ValueError("Phase 29 relationship review register must contain a list")
        records.extend(added)
    return records


def review_lookup(records: list[dict] | None = None) -> dict[tuple[str, str, str], dict]:
    by_edge = {}
    for review in records if records is not None else load_relationship_reviews():
        key = edge_key(review["kind"], review["from_id"], review["to_id"])
        if key in by_edge:
            raise ValueError("Duplicate reviewed relationship: " + str(key))
        if review["status"] not in STATUS_NAMES or review["status"] == "not_reviewed":
            raise ValueError("Review needs a valid evidence status: " + str(key))
        if not review.get("finding") or not review.get("limitations") or not review.get("sources"):
            raise ValueError("Relationship review has missing claim or provenance: " + str(key))
        by_edge[key] = review
    return by_edge


def audited_edges(people_by_id: Mapping, relationships: Mapping) -> list[dict]:
    """List each current edge exactly once, with no implicit evidentiary upgrades."""
    reviews = review_lookup()
    edges: list[dict] = []
    parent_edges = {
        edge_key("parent_child", parent_id, child_id)
        for child_id, parent_ids in relationships["parents"].items()
        for parent_id in parent_ids
    }
    spouse_edges = {
        edge_key("spouses", pid, other)
        for pid, spouses in relationships["spouses"].items()
        for other in spouses if pid != other
    }
    sibling_edges = {
        edge_key("siblings", pid, other)
        for pid, siblings in relationships["siblings"].items()
        for other in siblings if pid != other
    }

    for key in sorted(parent_edges | spouse_edges | sibling_edges):
        kind, a, b = key
        review = reviews.get(key)
        if kind == "siblings":
            explicit = b in people_by_id.get(a, {}).get("siblings", []) or a in people_by_id.get(b, {}).get("siblings", [])
            origin = ("Explicitly listed in a profile (not independently checked)"
                      if explicit else "Inferred from currently recorded shared parent(s); not separate sibling proof")
        elif kind == "parent_child":
            explicit = a in people_by_id.get(b, {}).get("parents", []) or b in people_by_id.get(a, {}).get("children", [])
            origin = ("Entered in original/effective family profiles" if explicit else
                      "Runtime-repaired relationship; original direction needs audit")
        else:
            origin = "Entered on one or both family profiles"
        edges.append({
            "kind": kind, "from_id": a, "to_id": b, "key": key,
            "status": review["status"] if review else "not_reviewed",
            "origin": origin,
            "finding": review.get("finding", "") if review else "",
            "limitations": review.get("limitations", "") if review else
                           "A linked profile may have sources without any source specifically proving this relationship.",
            "sources": review.get("sources", []) if review else [],
        })
    return edges


def review_summary(edges: list[dict]) -> dict:
    """Counts are about research coverage, NOT a percentage of true family links."""
    counts = Counter(row["status"] for row in edges)
    by_kind = Counter(row["kind"] for row in edges)
    reviewed = sum(value for status, value in counts.items() if status != "not_reviewed")
    return {"total": len(edges), "reviewed": reviewed,
            "awaiting_review": counts["not_reviewed"],
            "needs_identity_proof": counts["identity_needs_verification"],
            "by_kind": dict(by_kind), "by_status": dict(counts)}


def for_person(person_id: str, edges: list[dict]) -> list[dict]:
    return [edge for edge in edges if person_id in (edge["from_id"], edge["to_id"])]


def _relative_name(people: Mapping, person_id: str) -> str:
    return str(people.get(person_id, {}).get("full_name") or person_id.replace("_", " "))


def _relationship_title(row: dict, people: Mapping) -> str:
    a, b = row["from_id"], row["to_id"]
    kind = row["kind"]
    if kind == "parent_child":
        return _relative_name(people, a) + " → " + _relative_name(people, b)
    return _relative_name(people, a) + " & " + _relative_name(people, b)


def _render_review(row: dict, people: Mapping) -> None:
    st.markdown("**" + _relationship_title(row, people) + "**")
    st.caption(KIND_NAMES[row["kind"]] + " · " + STATUS_NAMES[row["status"]])
    st.caption("Relationship origin: " + row["origin"])
    if row["finding"]:
        st.write(row["finding"])
    st.caption("What this does not prove: " + row["limitations"])
    for source in row["sources"]:
        destination = source.get("route") or source.get("url")
        if destination:
            route_link("Inspect record: " + source["title"], destination)
        else:
            st.caption("Citation only: " + str(source.get("title") or "Unlinked source"))
        if source.get("type"):
            st.caption(str(source["type"]))
        if source.get("route") and not source.get("url"):
            st.caption("The evidence notebook is available; the court's original scan is not published.")


def render_profile_relationship_review(person_id: str, people: Mapping, relationships: Mapping) -> None:
    """Every listed relation is inspectable, even if no claim-level source exists."""
    edges = for_person(person_id, audited_edges(people, relationships))
    if not edges:
        st.caption("No linked relatives recorded; relationship sources remain to be found.")
        return
    reviewed = sum(row["status"] != "not_reviewed" for row in edges)
    st.subheader("How are these family connections documented?")
    st.caption(f"{len(edges)} distinct relationships shown in the tree; "
               f"{reviewed} have an individually reviewed evidence note. "
               "A missing review is not evidence that a relationship is wrong.")
    types = (("Parents and children", "parent_child"), ("Spouses", "spouses"), ("Siblings", "siblings"))
    for group, kind in types:
        subset = [row for row in edges if row["kind"] == kind]
        if not subset:
            continue
        with st.expander(group + f" · {len(subset)} links"):
            for row in subset:
                with st.container(border=True):
                    _render_review(row, people)


def render_relationship_coverage(people: Mapping, relationships: Mapping) -> None:
    """Whole archive coverage in Sources & Method, with no implication of accuracy."""
    edges = audited_edges(people, relationships)
    summary = review_summary(edges)
    st.subheader("Family connections — evidence review")
    st.write("The tree includes inherited family links, historical source reports, and "
             "some connections whose proof has not been individually examined. "
             "We evaluate **each relationship**, not simply the number of citations on a person's profile.")
    a, b, c = st.columns(3)
    a.metric("Links in the tree", summary["total"])
    b.metric("Links individually reviewed", summary["reviewed"])
    c.metric("Awaiting source review", summary["awaiting_review"])
    st.caption("Relationship review coverage is not a truth score. Links awaiting review "
               "remain visible; they are not automatically rejected.")
    categories = ["All connections", "Awaiting review", "Identity questions", "Reviewed source notes"]
    category = st.selectbox("Show relationship evidence", categories, key="relationship_review_category")
    query = st.text_input("Find relatives to compare", key="relationship_review_query",
                          placeholder="James, Mercy, Lyford, Lowell…").strip().casefold()
    filtered = []
    for row in edges:
        if category == "Awaiting review" and row["status"] != "not_reviewed":
            continue
        if category == "Identity questions" and row["status"] != "identity_needs_verification":
            continue
        if category == "Reviewed source notes" and row["status"] == "not_reviewed":
            continue
        if query and query not in (_relationship_title(row, people) + " " + row["status"]).casefold():
            continue
        filtered.append(row)
    page_size = 12
    pages = max(1, (len(filtered) + page_size - 1)//page_size)
    selected = st.selectbox("Connection results page", range(1, pages + 1),
                            format_func=lambda n: f"{n} of {pages}", key="relationship_review_page")
    start = (selected - 1) * page_size
    st.caption(f"{len(filtered)} matching family links; all links remain reachable.")
    for row in filtered[start:start + page_size]:
        with st.container(border=True):
            _render_review(row, people)
            for pid in (row["from_id"], row["to_id"]):
                if pid in people:
                    route_link("View " + _relative_name(people, pid) + "'s profile",
                               "?page=people&profile=" + pid, type="tertiary")
