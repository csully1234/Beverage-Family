"""Schema, reference, provenance, and privacy gates for archive additions."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from jsonschema import Draft202012Validator

from archive import historical_person, safe_url


def validate_archive(data, report) -> None:
    schema = json.loads((Path(__file__).parent / "schemas" / "archive.schema.json").read_text())
    keys = ("archive_sources", "places", "place_links")
    archive = {key: data.get(key, []) for key in keys}
    errors = sorted(Draft202012Validator(schema).iter_errors(archive), key=lambda e: str(list(e.path)))
    for error in errors:
        report.add("error", "archive_schema", f"{'/'.join(map(str, error.path))}: {error.message}")
    if errors:
        return  # Malformed input should produce a report, not crash reference checks.

    def fail(code, message):
        report.add("error", "archive_" + code, message)

    for key, records in archive.items():
        for identifier, count in Counter(r["id"] for r in records).items():
            if count > 1:
                fail("duplicate_id", f"{key}: {identifier}")

    places = {p["id"]: p for p in archive["places"]}
    sources = {s["id"]: s for s in archive["archive_sources"]}
    people = {p["id"]: p for p in data["people"]}
    events = {e["id"]: e for e in data["events"]}

    def refs(record, field, known):
        for identifier in record[field]:
            if identifier not in known:
                fail("missing_reference", f"{record['id']} {field}: {identifier}")

    def check_date(value, owner):
        if value is None:
            return
        try:
            datetime.strptime(value, {4: "%Y", 7: "%Y-%m", 10: "%Y-%m-%d"}[len(value)])
        except (ValueError, KeyError):
            fail("date", f"{owner}: invalid date {value}")

    def date_precision(value, precision, owner):
        check_date(value, owner)
        lengths = {"exact": 10, "month": 7, "year": 4, "approximate": 4}
        if (precision == "unknown" and value is not None) or (
            precision != "unknown" and (value is None or len(value) != lengths[precision])
        ):
            fail("date_precision", f"{owner}: {value!r} does not match {precision}")

    def check_person(pid, owner):
        if pid in people and not historical_person(people[pid]):
            fail("privacy", f"{owner}: possibly living person {pid} cannot be added to the historical archive")

    def check_event(eid, owner):
        if eid in events:
            for pid in events[eid].get("people_involved", []):
                if pid not in people:
                    fail("missing_reference", f"{owner}: mapped event {eid} has unresolved participant {pid}")
                else:
                    check_person(pid, owner)

    for source in sources.values():
        sid = source["id"]
        if not safe_url(source["url"]):
            fail("url", f"{sid}: only credential-free HTTP(S) source URLs are accepted")
        date_precision(source["date"], source["date_precision"], sid)
        check_date(source["accessed"], sid)
        if source["accessed"] > date.today().isoformat():
            fail("date", f"{sid}: accessed date is in the future")
        for field, known in (("people_ids", people), ("place_ids", places), ("event_ids", events)):
            refs(source, field, known)
        for pid in source["people_ids"]:
            check_person(pid, sid)
        for eid in source["event_ids"]:
            check_event(eid, sid)

    for place in places.values():
        pid = place["id"]
        refs(place, "sources", sources)
        if place["coordinate_source_id"] not in place["sources"]:
            fail("coordinate_source", f"{pid}: coordinate source must appear in sources")
        if (place["latitude"] is None) != (place["longitude"] is None):
            fail("coordinates", f"{pid}: coordinates must both be present or both be null")
        check_date(place["date_from"], pid)
        check_date(place["date_to"], pid)
        if place["date_from"] and place["date_to"] and place["date_from"] > place["date_to"]:
            fail("date_range", f"{pid}: reversed place dates")
        parent = place["parent_place_id"]
        if parent and parent not in places:
            fail("missing_reference", f"{pid}: unknown parent {parent}")
        visited = {pid}
        while parent in places:
            if parent in visited:
                fail("parent_cycle", f"{pid}: cyclic place hierarchy")
                break
            visited.add(parent)
            parent = places[parent]["parent_place_id"]
        for sid in place["sources"]:
            if sid in sources and pid not in sources[sid]["place_ids"]:
                fail("source_backlink", f"{pid}: {sid} must link back to this place")

    assertions = set()
    for link in archive["place_links"]:
        lid = link["id"]
        kind, subject, pid = link["subject_type"], link["subject_id"], link["place_id"]
        key = (kind, subject, pid, link["relation"], link["date_from"], link["date_to"])
        if key in assertions:
            fail("duplicate_link", f"Duplicate assertion: {lid}")
        assertions.add(key)
        known = people if kind == "person" else events
        if subject not in known or pid not in places:
            fail("missing_reference", f"{lid}: missing {kind} or place")
        if kind == "person":
            check_person(subject, lid)
        else:
            check_event(subject, lid)
        refs(link, "source_ids", sources)
        # Both-null = undated. Single-null = explicitly open interval.
        for value in (link["date_from"], link["date_to"]):
            if value is not None:
                date_precision(value, link["date_precision"], lid)
        if link["date_from"] is None and link["date_to"] is None and link["date_precision"] != "unknown":
            fail("date_precision", f"{lid}: undated link must have unknown precision")
        if link["date_from"] and link["date_to"] and link["date_from"] > link["date_to"]:
            fail("date_range", f"{lid}: reversed connection dates")
        for sid in link["source_ids"]:
            if sid not in sources:
                continue
            s = sources[sid]
            if subject not in s["people_ids" if kind == "person" else "event_ids"] or pid not in s["place_ids"]:
                fail("source_backlink", f"{lid}: {sid} must identify the subject and place")
            if pid in places and sid not in places[pid]["sources"]:
                fail("source_backlink", f"{lid}: place must reference supporting source {sid}")
        if link["evidence_level"] != "corroboration" and not any(
            sources[sid]["evidence_level"] in {"verified", "strongly_supported"}
            for sid in link["source_ids"] if sid in sources
        ):
            fail("evidence", f"{lid}: a factual link cannot rely solely on corroborative sources")
