"""Audited, narrowly scoped corrections; original family data stays immutable."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUSES = ("Resolved with documented evidence", "Narrowed but unresolved",
            "Awaiting an inaccessible original", "Requiring family review")
# This review does not authorize relationship, residence, property or event edits.
ALLOWED_FIELDS = frozenset({"birth_date", "birth_date_precision", "birth_place",
                            "baptism_date", "baptism_place"})
CONFIDENCES = ("Confirmed", "Strongly supported", "Probable", "Possible lead", "Conflict", "Rejected")


def load_review(data_dir: Path = ROOT / "data") -> dict:
    path = data_dir / "reviews" / "conflicts_2026-10-15.json"
    return json.loads(path.read_text()) if path.exists() else {"sources": [], "resolutions": []}


def citation(source: dict) -> dict:
    return {"title": source["title"], "repository": source["repository"],
            "url": source["url"], "page": source["locator"], "accessed": source["accessed"],
            "supports": source["supports"], "evidence_level": source["quality"],
            "record_identifier": source["id"]}


def apply_review(people: list[dict], review: dict) -> list[dict]:
    """Apply only explicitly audited fields and fail closed if their baseline drifts."""
    result = deepcopy(people)
    by_id = {p["id"]: p for p in result}
    sources = {s["id"]: s for s in review["sources"]}
    changed = set()
    for resolution in review["resolutions"]:
        for pid in resolution["people_ids"]:
            if pid not in by_id:
                raise ValueError(f"Unknown conflict profile: {pid}")
            by_id[pid].setdefault("conflict_review_ids", []).append(resolution["research_id"])
        for activity in resolution.get("historical_activity", []):
            if (activity["person_id"] not in resolution["people_ids"]
                    or activity["source_id"] not in sources
                    or activity["confidence"] not in CONFIDENCES[:2]):
                raise ValueError("Historical activity requires identified, substantial evidence")
            by_id[activity["person_id"]].setdefault("documented_activity", []).append(deepcopy(activity))
        for change in resolution["changes"]:
            pid, field = change["person_id"], change["field"]
            if field not in ALLOWED_FIELDS or (pid, field) in changed:
                raise ValueError(f"Unauthorized or duplicate correction: {pid}.{field}")
            if pid not in resolution["people_ids"] or by_id[pid].get(field) != change["before"]:
                raise ValueError(f"Correction baseline differs: {pid}.{field}")
            if resolution["confidence"] not in CONFIDENCES[:2]:
                raise ValueError("Only strongly supported corrections may affect displayed facts")
            changed.add((pid, field))
            person = by_id[pid]
            person[field] = change["after"]
            person.setdefault("review_corrections", []).append({**change, "research_id": resolution["research_id"]})
            if field in ("birth_date", "birth_date_precision"):
                person.setdefault("date_provenance", {})["birth_date"] = {
                    "original_value": next((c["before"] for c in resolution["changes"]
                                            if c["person_id"] == pid and c["field"] == "birth_date"), None),
                    "determination": resolution["conclusion"], "checked_on": resolution["checked_on"],
                    "confidence": resolution["confidence"], "research_id": resolution["research_id"],
                }
            for sid in resolution["source_ids"]:
                if sid in sources:
                    entry = citation(sources[sid])
                    if entry not in person.setdefault("sources", []):
                        person["sources"].append(entry)
    return result


def validate_review(review: dict, collection, site: dict) -> list[str]:
    errors = []
    sources = {s["id"]: s for s in review["sources"]}
    ids = [r["research_id"] for r in review["resolutions"]]
    expected = {rid for rid, r in collection.findings.items() if r["Confidence"] == "Conflict"}
    if set(ids) != expected or len(ids) != len(set(ids)):
        errors.append("Resolution ledger must cover each original conflict exactly once")
    if len(sources) != len(review["sources"]):
        errors.append("Duplicate review source ID")
    known = sources.keys() | collection.sources.keys()
    for source in sources.values():
        for key in ("title", "repository", "url", "locator", "accessed", "viewed", "quality", "dependency", "supports", "rights"):
            if not source.get(key):
                errors.append(f"{source['id']}: missing {key}")
        if not source.get("url", "").startswith("https://"):
            errors.append(f"{source['id']}: invalid source URL")
    people = {p["id"]: p for p in site["people"]}
    for r in review["resolutions"]:
        rid = r["research_id"]
        if r["resolution_status"] not in STATUSES or r["confidence"] not in CONFIDENCES:
            errors.append(f"{rid}: invalid status or confidence")
        if not r["source_ids"] or not set(r["source_ids"]) <= known:
            errors.append(f"{rid}: unknown or missing evidence")
        for key in ("conclusion", "reasoning", "identity_reasoning", "remaining_question", "retrieval_request", "family_review_status", "existing_claims"):
            if not r.get(key):
                errors.append(f"{rid}: missing {key}")
        for change in r["changes"]:
            if people.get(change["person_id"], {}).get(change["field"]) != change["after"]:
                errors.append(f"{rid}: correction absent from shared data")
    return errors
