"""Read-only, repeatable integrity scan over the site's *effective* family archive.

These counts describe documentation coverage, not historical truth. The scan
NEVER auto-merges matching names, infers parents, or modifies genealogy.
"""
from __future__ import annotations

import csv
import io
from collections import Counter, defaultdict
from typing import Any, Mapping
from urllib.parse import urlsplit

from family_data import year_from_date
from relationship_evidence import audited_edges, review_summary


def _known_url(source: Any) -> bool:
    if not isinstance(source, dict):
        return False
    link = str(source.get("url") or "").strip()
    try:
        parsed = urlsplit(link)
        return parsed.scheme in {"https", "http"} and bool(parsed.hostname)
    except ValueError:
        return False


def connected_components(people: Mapping[str, dict],
                         relationships: Mapping[str, Mapping[str, set[str]]]) -> list[list[str]]:
    """Graph components among known exact IDs, including explicit/inferred links."""
    adjacency: dict[str, set[str]] = {pid: set() for pid in people}
    for related in relationships.values():
        for person_id, others in related.items():
            if person_id not in adjacency:
                continue
            for other in others:
                if other in adjacency and other != person_id:
                    adjacency[person_id].add(other)
                    adjacency[other].add(person_id)
    unseen = set(adjacency)
    groups = []
    while unseen:
        root = min(unseen)
        queue = [root]
        unseen.remove(root)
        group = []
        for current in queue:
            group.append(current)
            for other in sorted(adjacency[current] & unseen):
                unseen.remove(other)
                queue.append(other)
        groups.append(sorted(group))
    return sorted(groups, key=lambda group: (-len(group), group[0]))


def missing_relatives(people: Mapping[str, dict],
                      relationships: Mapping[str, Mapping[str, set[str]]]) -> list[dict]:
    """Every unknown referenced ID is an incomplete profile, not a new person."""
    references: dict[str, set[str]] = defaultdict(set)
    for mapping in relationships.values():
        for pid, others in mapping.items():
            if pid not in people:
                references[pid].update(other for other in others if other in people)
            for other in others:
                if other not in people:
                    references[other].add(pid)
    return [{"id": pid, "referenced_by": sorted(parent for parent in refs if parent in people)}
            for pid, refs in sorted(references.items())]


def same_name_candidates(people: Mapping[str, dict]) -> list[dict]:
    """Text-equal names only. Same name is NOT proof of duplicate identity."""
    import re
    grouped: dict[str, list[str]] = defaultdict(list)
    for pid, person in people.items():
        key = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", str(person.get("full_name") or "").casefold())).strip()
        if key:
            grouped[key].append(pid)
    return [{"name": label, "ids": sorted(ids)}
            for label, ids in sorted(grouped.items())
            if len(ids) > 1]


def chronological_screening(people: Mapping[str, dict],
                            relationships: Mapping[str, Mapping[str, set[str]]]) -> list[dict]:
    """Only mechanical date screenings; approximate years are never 'errors'."""
    findings = []
    for pid, person in people.items():
        born, died = year_from_date(person.get("birth_date")), year_from_date(person.get("death_date"))
        if born and died and born > died:
            findings.append({"kind": "death_before_birth", "person_ids": [pid],
                             "note": "Recorded death year precedes recorded birth year. Check source/date precision."})
    for child_id, parents in relationships.get("parents", {}).items():
        child = people.get(child_id)
        if not child:
            continue
        child_year = year_from_date(child.get("birth_date"))
        if not child_year or str(child.get("birth_date_precision") or "").lower() in ("approximate", "unknown"):
            continue
        for parent_id in parents:
            parent = people.get(parent_id)
            if not parent:
                continue
            born = year_from_date(parent.get("birth_date"))
            if not born or str(parent.get("birth_date_precision") or "").lower() in ("approximate", "unknown"):
                continue
            difference = child_year - born
            if difference < 12 or difference > 80:
                findings.append({"kind": "parent_child_date_screening",
                                 "person_ids": [parent_id, child_id],
                                 "note": "Recorded birth-year gap: " + str(difference) +
                                 " years. Verify person identities, the underlying records and date precision; this is NOT proof of an incorrect link."})
    return sorted(findings, key=lambda row: (row["kind"], row["person_ids"]))


def profile_coverage(people: Mapping[str, dict], events: list[dict],
                     relationships: Mapping[str, Mapping[str, set[str]]],
                     edges: list[dict]) -> list[dict]:
    """Person-by-person checklist; having a citation does not verify any claim."""
    event_counts: Counter = Counter()
    for event in events:
        for pid in set(event.get("people_involved") or []):
            if pid in people:
                event_counts[pid] += 1
    edge_counts: Counter = Counter()
    reviewed_counts: Counter = Counter()
    for row in edges:
        for pid in (row["from_id"], row["to_id"]):
            if pid in people:
                edge_counts[pid] += 1
                if row["status"] != "not_reviewed":
                    reviewed_counts[pid] += 1
    out = []
    for pid, person in people.items():
        sources = person.get("sources") or []
        out.append({
            "id": pid, "name": str(person.get("full_name") or pid),
            "birth_recorded": bool(person.get("birth_date")),
            "death_recorded": bool(person.get("death_date")),
            "citation_entries": len(sources),
            "direct_source_urls": sum(_known_url(s) for s in sources),
            "events": event_counts[pid],
            "relationship_links": edge_counts[pid],
            "individually_reviewed_links": reviewed_counts[pid],
            "needs_research": bool(person.get("needs_research")),
            "notes": str(person.get("research_completeness") or ""),
        })
    return sorted(out, key=lambda row: (row["name"].casefold(), row["id"]))


def audit_family_archive(people: Mapping[str, dict], events: list[dict],
                         relationships: Mapping[str, Mapping[str, set[str]]]) -> dict:
    """Single source of truth for overview, complete review queues and CSVs."""
    edges = audited_edges(people, relationships)
    components = connected_components(people, relationships)
    profiles = profile_coverage(people, events, relationships, edges)
    unresolved = missing_relatives(people, relationships)
    names = same_name_candidates(people)
    chronology = chronological_screening(people, relationships)
    missing_citations = [e for e in events if not e.get("sources")]
    event_without_link = [e for e in events
                          if not any(_known_url(s) for s in e.get("sources") or [])]
    missing_event_people = sorted({
        str(pid) for event in events for pid in (event.get("people_involved") or [])
        if str(pid) not in people
    })
    edge_summary = review_summary(edges)
    overview = {
        "people": len(people),
        "events": len(events),
        "distinct_relationships": len(edges),
        "individual_relationship_reviews": edge_summary["reviewed"],
        "relationships_awaiting_review": edge_summary["awaiting_review"],
        "parent_child_links": edge_summary["by_kind"].get("parent_child", 0),
        "spouse_links": edge_summary["by_kind"].get("spouses", 0),
        "sibling_links_including_inferred": edge_summary["by_kind"].get("siblings", 0),
        "connected_groups": len(components),
        "isolated_profiles": sum(len(group) == 1 for group in components),
        "unresolved_profile_references": len(unresolved),
        "same_name_groups_to_compare": len(names),
        "profile_citations_missing": sum(row["citation_entries"] == 0 for row in profiles),
        "profiles_without_direct_citation_url": sum(row["direct_source_urls"] == 0 for row in profiles),
        "birth_dates_unrecorded": sum(not row["birth_recorded"] for row in profiles),
        "death_dates_unrecorded": sum(not row["death_recorded"] for row in profiles),
        "events_without_citation": len(missing_citations),
        "events_without_direct_citation_url": len(event_without_link),
        "event_people_without_profile": len(missing_event_people),
        "chronology_screening_flags": len(chronology),
    }
    return {
        "summary": overview, "edge_summary": edge_summary, "edges": edges,
        "components": components, "profiles": profiles, "unresolved": unresolved,
        "same_names": names, "chronology": chronology,
        "events_no_citations": missing_citations,
        "events_no_direct_link": event_without_link,
        "missing_event_people": missing_event_people,
    }


def audit_csv(rows: list[dict], fields: tuple[str, ...]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: ("; ".join(str(item) for item in row[key])
                               if isinstance(row.get(key), list) else row.get(key, ""))
                         for key in fields})
    return buffer.getvalue()
