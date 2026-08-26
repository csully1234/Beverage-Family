"""Pure data utilities for the Beverage Family genealogy application.

This module deliberately has no Streamlit dependency.  The web app, validation
script, and automated tests all use the same loading and relationship logic.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


Record = dict[str, Any]
RELATIONSHIP_FIELDS = ("parents", "siblings", "spouses", "children")


def load_json_records(path: Path) -> list[Record]:
    """Load a JSON array of objects from *path*.

    Raising a useful exception here keeps malformed data from silently turning
    into an empty family tree.
    """

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Required data file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON array")
    if any(not isinstance(record, dict) for record in payload):
        raise ValueError(f"Every entry in {path} must be a JSON object")
    return payload


def load_optional_json_records(path: Path) -> list[Record]:
    """Load an optional JSON array, returning an empty collection if absent.

    Research overlays are deliberately optional. This lets the public codebase
    run against the repository's existing records without publishing private or
    separately reviewed research files.
    """

    if not path.exists():
        return []
    return load_json_records(path)


def merge_records(base_records: Iterable[Record], overlays: Iterable[Record]) -> list[Record]:
    """Merge reviewed overlays by stable ID while preserving base ordering."""

    merged: dict[str, Record] = {}
    for record in base_records:
        record_id = record.get("id")
        if record_id:
            merged[str(record_id)] = dict(record)
    for record in overlays:
        record_id = record.get("id")
        if record_id:
            merged[str(record_id)] = dict(record)
    return list(merged.values())


def load_site_data(data_dir: Path) -> dict[str, list[Record]]:
    """Load the base datasets, reviewed overlays, and effective site records."""

    base_people = load_json_records(data_dir / "people.json")
    base_events = load_json_records(data_dir / "events.json")
    research_people = load_optional_json_records(data_dir / "research_people.json")
    research_events = load_optional_json_records(data_dir / "research_events.json")
    research = load_optional_json_records(data_dir / "research.json")

    return {
        "base_people": base_people,
        "base_events": base_events,
        "research_people": research_people,
        "research_events": research_events,
        "people": merge_records(base_people, research_people),
        "events": merge_records(base_events, research_events),
        "research": research,
    }


def index_people(people: Iterable[Record]) -> dict[str, Record]:
    """Return an O(1) lookup table keyed by stable person ID."""

    return {
        str(person["id"]): person
        for person in people
        if person.get("id") is not None
    }


def relationship_index(people: Iterable[Record]) -> dict[str, dict[str, set[str]]]:
    """Build reciprocal relationship lookups without rewriting source records.

    A parent listed on a child's profile also implies that the child can appear
    in the parent's descendants view.  The same principle is applied to spouse
    and sibling links.  This fixes navigation gaps while leaving historical JSON
    assertions untouched.
    """

    indexes: dict[str, defaultdict[str, set[str]]] = {
        field: defaultdict(set) for field in RELATIONSHIP_FIELDS
    }

    for person in people:
        person_id = str(person.get("id", ""))
        if not person_id:
            continue

        for parent_id in person.get("parents", []):
            parent_id = str(parent_id)
            indexes["parents"][person_id].add(parent_id)
            indexes["children"][parent_id].add(person_id)

        for child_id in person.get("children", []):
            child_id = str(child_id)
            indexes["children"][person_id].add(child_id)
            indexes["parents"][child_id].add(person_id)

        for spouse_id in person.get("spouses", []):
            spouse_id = str(spouse_id)
            indexes["spouses"][person_id].add(spouse_id)
            indexes["spouses"][spouse_id].add(person_id)

        for sibling_id in person.get("siblings", []):
            sibling_id = str(sibling_id)
            indexes["siblings"][person_id].add(sibling_id)
            indexes["siblings"][sibling_id].add(person_id)

    return {
        field: {person_id: set(related) for person_id, related in mapping.items()}
        for field, mapping in indexes.items()
    }


def friendly_identifier(identifier: str) -> str:
    """Turn an unresolved stable ID into a readable, explicitly unresolved label."""

    match = re.match(r"^(.*)_(\d{4})$", identifier)
    if match:
        name, year = match.groups()
        return f"{name.replace('_', ' ').title()} ({year})"
    return identifier.replace("_", " ").title()


def year_from_date(value: Any) -> int | None:
    """Extract a four-digit year from supported date strings."""

    if not isinstance(value, str):
        return None
    match = re.match(r"^(\d{4})", value.strip())
    return int(match.group(1)) if match else None


def format_date(value: Any) -> str:
    """Display ISO dates naturally without altering the underlying value."""

    if value in (None, "", "Unknown"):
        return "Unknown"
    text = str(value)
    if re.fullmatch(r"\d{4}", text):
        return text
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d")
            return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"
        except ValueError:
            return text
    return text


def life_span(person: Mapping[str, Any]) -> str:
    """Return a compact lifespan label."""

    birth_year = year_from_date(person.get("birth_date"))
    death_year = year_from_date(person.get("death_date"))
    if birth_year and death_year:
        return f"{birth_year}–{death_year}"
    if birth_year:
        return f"b. {birth_year}"
    if death_year:
        return f"d. {death_year}"
    return "Dates unknown"


def unique_places(people: Iterable[Record]) -> list[str]:
    """Collect unique named birth, death, and residence locations."""

    places: set[str] = set()
    for person in people:
        for field in ("birth_place", "death_place"):
            place = person.get(field)
            if place and str(place).strip().lower() != "unknown":
                places.add(str(place).strip())
        for residence in person.get("residences", []):
            if isinstance(residence, dict) and residence.get("location"):
                places.add(str(residence["location"]).strip())
    return sorted(places)


def source_search_text(source: Any) -> str:
    """Flatten either legacy string sources or structured source objects."""

    if isinstance(source, dict):
        return " ".join(str(value) for value in source.values() if value)
    return str(source)


def person_sort_key(person: Mapping[str, Any]) -> tuple[str, int, str]:
    """Sort profiles by surname, then birth year, then full name."""

    name = str(person.get("full_name", person.get("id", ""))).strip()
    surname = name.split()[-1].lower() if name else ""
    return surname, year_from_date(person.get("birth_date")) or 9999, name.lower()


def records_to_csv(records: Iterable[Record], fields: list[str]) -> str:
    """Serialize selected record fields for a user download."""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        row: dict[str, Any] = {}
        for field in fields:
            value = record.get(field)
            if isinstance(value, (list, dict)):
                row[field] = json.dumps(value, ensure_ascii=False)
            elif value is None:
                row[field] = ""
            else:
                row[field] = value
        writer.writerow(row)
    return buffer.getvalue()
