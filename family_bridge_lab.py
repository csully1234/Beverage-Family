"""Read-only connection laboratory for competing historical parentage theories.

The proposals below are research QUESTIONS, never changes to genealogy data.
No number of derivative sources proves an original record. The preview graph
is made from copies and cannot modify the family tree.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Mapping
from genealogy_integrity import connected_components

PROPOSALS = [
    {
        "id": "nathaniel-john-white",
        "title": "Nathaniel of Rockland — proposed father John White Beverage",
        "child": "nathaniel_beverage_1804_rockland",
        "parent": "john_white_beverage_1774",
        "research_case": "nathaniel-rockland-parentage",
        "basis": "One contributed New England genealogy explicitly names John White as Nathaniel's father. The 1865 Eaton history independently calls Nathaniel a nephew of Capt. Matthew but does not name his father.",
        "needed": "Original October 1803 North Haven/Vinalhaven birth entry explicitly naming father; compare the 1838 marriage return and 1839 John White probate heirs.",
        "status": "UNPROVED: DO NOT ADD TO FAMILY TREE",
    },
    {
        "id": "nathaniel-rachel-crosby",
        "title": "Nathaniel of Rockland — proposed mother Rachel Lucy Crosby",
        "child": "nathaniel_beverage_1804_rockland",
        "parent": "rachel_crosby_1778",
        "research_case": "nathaniel-rockland-parentage",
        "basis": "The same contributed New England genealogy names Rachel as mother. It is not a second independent source merely because it names both parents.",
        "needed": "Original 1803 birth register naming Rachel as mother, with dates and family identity checked against a separately documented household.",
        "status": "UNPROVED: DO NOT ADD TO FAMILY TREE",
    },
]


def bridge_preview(proposals: list[dict], people: Mapping[str, dict],
                   relationships: Mapping, selected: list[str]) -> dict:
    """Compare actual connected groups to a *hypothetical* graph in memory."""
    before = connected_components(people, relationships)
    valid = {item["id"]: item for item in proposals}
    chosen = [valid[key] for key in dict.fromkeys(selected) if key in valid]
    component_of = {pid: n + 1 for n, group in enumerate(before)
                    for pid in group}
    checks = []
    after_groups = {key: {pid: set(ids) for pid, ids in mapping.items()}
                    for key, mapping in relationships.items()}
    after_groups.setdefault("parents", {})
    after_groups.setdefault("children", {})
    for proposal in chosen:
        child, parent = proposal["child"], proposal["parent"]
        if child not in people or parent not in people:
            raise ValueError("Proposed genealogical endpoint is not a verified profile")
        if child == parent:
            raise ValueError("Person cannot be their own parent")
        checks.append({
            "proposal": proposal["id"],
            "child": child,
            "parent": parent,
            "current_components": [component_of[child], component_of[parent]],
            "crosses_components": component_of[child] != component_of[parent],
        })
        after_groups["parents"].setdefault(child, set()).add(parent)
        after_groups["children"].setdefault(parent, set()).add(child)
    after = connected_components(people, after_groups)
    return {
        "before": len(before), "hypothetical_after": len(after),
        "currently_separate": len(before) > 1,
        "edges_examined": checks, "unverified": True,
        "changed_canonical_data": False,
    }


def proposal_worklist(proposals: list[dict], people: Mapping[str, dict]) -> list[dict]:
    """Portable, correctly labeled research tickets, not automated ancestry."""
    return [
        {
            "id": p["id"], "title": p["title"], "status": p["status"],
            "child": people[p["child"]].get("full_name", p["child"]),
            "parent": people[p["parent"]].get("full_name", p["parent"]),
            "basis": p["basis"], "needed": p["needed"],
            "case": p["research_case"],
        }
        for p in proposals
    ]
