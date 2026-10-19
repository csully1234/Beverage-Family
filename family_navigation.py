"""Person-first navigation helpers for the original documented family graph.

Never infer a relative from a shared name, OCR hit, probable relationship
or a missing profile. The ordered menu includes every *known* related profile
without inventing missing nodes.
"""
from __future__ import annotations

from typing import Mapping

RELATIONS = (
    ("parents", "Parent"),
    ("spouses", "Spouse"),
    ("children", "Child"),
    ("siblings", "Sibling"),
)


def connected_relatives(person_id: str, people: Mapping[str, dict],
                        relationships: Mapping[str, Mapping[str, set[str]]]) -> list[dict]:
    """Return stable, unique direct family links ordered by relationship and name."""
    if person_id not in people:
        return []
    listed = []
    seen = {person_id}
    for kind, label in RELATIONS:
        ids = sorted(
            relationships.get(kind, {}).get(person_id, set()),
            key=lambda id: (str(people.get(id, {}).get("full_name") or id).casefold(), str(id)),
        )
        for pid in ids:
            if pid in seen or pid not in people:
                continue
            seen.add(pid)
            listed.append({
                "person_id": pid, "relationship": label,
                "name": str(people[pid].get("full_name") or pid),
            })
    return listed


def connected_profile_ids(person_id: str, people: Mapping[str, dict],
                          relationships: Mapping[str, Mapping[str, set[str]]]) -> list[str]:
    """Stable profile IDs suitable for selectors; selected person stays first."""
    if person_id not in people:
        return []
    return [person_id, *(row["person_id"] for row in
                         connected_relatives(person_id, people, relationships))]


def unresolved_relative_ids(person_id: str, people: Mapping[str, dict],
                            relationships: Mapping[str, Mapping[str, set[str]]]) -> list[str]:
    """Keep unresolved identity pointers visible without making selectable profiles."""
    unknown = set()
    for kind, _label in RELATIONS:
        unknown.update(
            pid for pid in relationships.get(kind, {}).get(person_id, set())
            if pid not in people
        )
    return sorted(unknown)


def branch_context(person_id: str, people: Mapping[str, dict],
                   relationships: Mapping[str, Mapping[str, set[str]]]) -> dict | None:
    """Locate an indexed relative in the existing graph, without bridging gaps.

    Group numbering is deterministic and purely descriptive: being in the same
    component is not individualized proof of every relationship along the path.
    Unknown IDs are excluded from groups, not added as placeholder ancestors.
    """
    if person_id not in people:
        return None
    from genealogy_integrity import connected_components
    groups = connected_components(people, relationships)
    for number, member_ids in enumerate(groups, 1):
        if person_id in member_ids:
            return {"number": number, "total": len(groups), "size": len(member_ids),
                    "member_ids": member_ids}
    return None
