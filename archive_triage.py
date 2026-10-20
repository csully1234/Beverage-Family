"""Whole-family evidence access and unresolved-reference triage (read-only).

A clickable link is not a verified manuscript. An ID/name resemblance is not
identity evidence. No function mutates people, events, source rights, or edges.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Mapping

from evidence_explorer import evidence_catalog, for_event, for_person, source_items
from family_research_index import build_index
from genealogy_integrity import missing_relatives
from relationship_evidence import audited_edges
from routing_ui import safe_external_url

EXCLUDED = {"Existing family profiles", "Scanned book OCR leads"}
FIELDS = ("parents", "spouses", "children", "siblings")


def _record_links(sources: list[dict], *, kind: str) -> list[dict]:
    """Only count source URLs the existing visitor link control will accept."""
    return [
        {"kind": kind, "title": str(source.get("title") or source.get("citation")
                                     or "Source record"), "url": url}
        for source in sources
        if isinstance(source, dict)
        for url in [source.get("url")]
        if safe_external_url(url)
    ]


def _unique_links(links: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for link in links:
        url = link["url"]
        if url not in seen:
            seen.add(url)
            result.append(link)
    return result


def person_source_matrix(
    people: Mapping[str, dict], events: list[dict], relationships: Mapping,
    *, research_rows: list[dict] | None = None,
    catalog: list[dict] | None = None, edges: list[dict] | None = None,
) -> list[dict]:
    """Connect existing evidence from five catalogs to every *exact* person ID.

    Different references may point to the same external URL: the combined link
    count deduplicates URLs. Internal route pointers and book-page links are
    counted separately. This is navigation coverage, not genealogical proof.
    """
    catalog = evidence_catalog() if catalog is None else catalog
    research_rows = build_index(dict(people)) if research_rows is None else research_rows
    edges = audited_edges(people, relationships) if edges is None else edges
    event_index: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        event_id = str(event.get("id") or "")
        if not event_id:
            continue
        for pid in set(str(v) for v in event.get("people_involved") or []):
            if pid in people:
                event_index[pid].append(event)
    research_index: dict[str, list[dict]] = defaultdict(list)
    for row in research_rows:
        if row.get("category") in EXCLUDED:
            continue
        for pid in set(str(v) for v in row.get("person_ids") or []):
            if pid in people:
                research_index[pid].append(row)
    edge_index: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        for pid in {edge["from_id"], edge["to_id"]}:
            if pid in people:
                edge_index[pid].append(edge)
    matrix = []
    for pid in sorted(people, key=lambda key: (str(people[key].get("full_name")
                                                 or key).casefold(), key)):
        person = people[pid]
        profile_refs = source_items(for_person(pid, catalog), person.get("sources") or [])
        profile_links = _unique_links(_record_links(profile_refs, kind="Profile / exhibit"))
        event_records = event_index[pid]
        event_links = []
        event_with_sources: set[str] = set()
        for event in event_records:
            sources = source_items(for_event(str(event["id"]), catalog),
                                   event.get("sources") or [])
            if sources:
                event_with_sources.add(str(event["id"]))
                event_links.extend(_record_links(sources, kind="Dated event"))
        event_links = _unique_links(event_links)
        research_records = research_index[pid]
        research_links = _unique_links([
            link for row in research_records
            for link in _record_links(row.get("sources") or [],
                                      kind="Attributed research")
        ])
        reviewed = [edge for edge in edge_index[pid]
                    if edge["status"] != "not_reviewed"]
        relationship_links = _unique_links([
            link for edge in reviewed
            for link in _record_links(edge.get("sources") or [],
                                      kind="Relationship review")
        ])
        external = _unique_links([*profile_links, *event_links,
                                  *research_links, *relationship_links])
        research_routes = sorted({
            str(row["route"]) for row in research_records
            if isinstance(row.get("route"), str) and row["route"].startswith("?")
        })
        photo_pages = sorted({
            page for row in research_records
            if row.get("category") == "Scanned book photographs"
            for page in row.get("pages") or [] if isinstance(page, int)
        })
        matrix.append({
            "id": pid,
            "name": str(person.get("full_name") or pid),
            "profile_references": len(profile_refs),
            "direct_profile_links": len(profile_links),
            "dated_events": len(event_records),
            "events_with_citations": len(event_with_sources),
            "direct_event_links": len(event_links),
            "attributed_research_items": len(research_records),
            "direct_research_links": len(research_links),
            "research_routes": research_routes,
            "reviewed_relationships": len(reviewed),
            "total_relationships": len(edge_index[pid]),
            "direct_relationship_links": len(relationship_links),
            "book_photo_pages": photo_pages,
            "direct_source_links": len(external),
            "source_links": external,
        })
    return matrix


def _name_tokens(text: str) -> list[str]:
    """Identity-comparison tokens only; inferred birth years are not matching keys."""
    tokens = [v.lower() for v in re.findall(r"[A-Za-z]+", text)]
    return [v for v in tokens if v not in {"jr", "sr", "unknown", "maybe"}]


def unresolved_reference_cases(people: Mapping[str, dict],
                               relationships: Mapping) -> list[dict]:
    """Every missing ID, who actually references it, and *comparison* leads.

    First/last name agreement only proposes records to inspect; it never
    generates a new profile, recodes an ID, or links connected components.
    """
    raw = missing_relatives(people, relationships)
    cases = []
    for missing in raw:
        identifier = missing["id"]
        name_parts = _name_tokens(identifier)
        given = name_parts[0] if len(name_parts) >= 2 else ""
        surname = name_parts[-1] if len(name_parts) >= 2 else ""
        candidates = []
        for pid, person in people.items():
            terms = _name_tokens(str(person.get("full_name") or ""))
            if len(terms) >= 2 and terms[0] == given and terms[-1] == surname:
                candidates.append({"id": pid, "name": str(person.get("full_name") or pid)})
        references = []
        for owner_id, owner in people.items():
            for field in FIELDS:
                if identifier in (owner.get(field) or []):
                    references.append({
                        "owner_id": owner_id,
                        "owner_name": str(owner.get("full_name") or owner_id),
                        "kind": field,
                    })
        cases.append({
            "id": identifier,
            "references": sorted(references, key=lambda row:
                                 (row["owner_name"].casefold(), row["kind"])),
            "potential_name_matches": sorted(candidates, key=lambda row:
                                             (row["name"].casefold(), row["id"])),
            "referenced_by": missing["referenced_by"],
        })
    return cases


def matrix_counts(rows: list[dict]) -> dict[str, int]:
    """Source *access* counts only, never a percentage of verified genealogy."""
    return {
        "people": len(rows),
        "any_external_link": sum(row["direct_source_links"] > 0 for row in rows),
        "no_external_link_in_indexed_contexts":
            sum(row["direct_source_links"] == 0 for row in rows),
        "with_dated_event_citations": sum(row["events_with_citations"] > 0
                                          for row in rows),
        "with_relationship_reviews": sum(row["reviewed_relationships"] > 0
                                          for row in rows),
        "with_book_photo_pages": sum(bool(row["book_photo_pages"])
                                     for row in rows),
    }
