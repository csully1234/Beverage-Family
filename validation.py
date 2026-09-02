"""Data-integrity checks for the Beverage Family datasets."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from family_data import RELATIONSHIP_FIELDS, Record, index_people, merge_records


PROTECTED_EVENT_HASHES = {
    # User-directed regression guards.  Hashes protect the exact record content
    # without republishing private text in the validation code.
    "event_boston_tea_party_1773": (
        "7afb2dcf127fe313ca42f0657fcefae73d61a5df3c9e865e54db679196c53a3b"
    ),
    "event_purchase_home_walliford_1997": (
        "b1dd762ff1c6ace355dc8d72bb0da664a82f4ef792c20ab4193031c7d8ad9188"
    ),
    "event_property_record_2024": (
        "88e15c5b3eccf18287c31be3537f227e130cae94381ab4d8b3739fd88388449b"
    ),
}

PROTECTED_RESIDENCE_HASH = (
    "b62538ff644549b4f95106b2fd41abb5110fd28e0b04dbdbf1d93c20e1253a29"
)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str) -> None:
        self.issues.append(ValidationIssue(severity, code, message))

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def count(self, code: str) -> int:
        return sum(issue.code == code for issue in self.issues)


def canonical_record_hash(record: Record) -> str:
    """Hash a record using stable JSON serialization."""

    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _duplicates(records: Iterable[Record]) -> list[str]:
    counts = Counter(str(record.get("id")) for record in records if record.get("id"))
    return sorted(record_id for record_id, count in counts.items() if count > 1)


def _required_fields(
    report: ValidationReport,
    records: Iterable[Record],
    dataset: str,
    fields: tuple[str, ...],
) -> None:
    missing = []
    for record in records:
        absent = [field for field in fields if field not in record]
        if absent:
            missing.append(f"{record.get('id', '<missing id>')}: {', '.join(absent)}")
    if missing:
        report.add(
            "error",
            "missing_required_fields",
            f"{dataset} has {len(missing)} record(s) missing required fields: "
            + "; ".join(missing[:8]),
        )


def _validate_dates(
    report: ValidationReport,
    people: list[Record],
    events: list[Record],
) -> None:
    supported = re.compile(r"^\d{4}(?:-\d{2}-\d{2})?$")
    malformed: list[str] = []
    january_first = 0
    id_year_mismatches = 0

    for person in people:
        for field_name in ("birth_date", "death_date"):
            value = person.get(field_name)
            if value and value != "Unknown" and not supported.fullmatch(str(value)):
                malformed.append(f"{person.get('id')}:{field_name}")
            if (
                re.fullmatch(r"\d{4}-01-01", str(value or ""))
                and person.get(f"{field_name}_precision") not in {"year", "approximate"}
            ):
                january_first += 1
        birth_date = str(person.get("birth_date") or "")
        identifier_match = re.search(r"_(\d{4})$", str(person.get("id", "")))
        if identifier_match and re.match(r"\d{4}", birth_date):
            if identifier_match.group(1) != birth_date[:4]:
                id_year_mismatches += 1

    for event in events:
        value = event.get("date")
        if value and value != "Unknown" and not supported.fullmatch(str(value)):
            malformed.append(f"{event.get('id')}:date")
        if (
            re.fullmatch(r"\d{4}-01-01", str(value or ""))
            and event.get("date_precision") not in {"year", "approximate"}
        ):
            january_first += 1

    if malformed:
        report.add(
            "error",
            "malformed_dates",
            f"{len(malformed)} unsupported date value(s): {', '.join(malformed[:8])}",
        )
    if january_first:
        report.add(
            "warning",
            "possible_year_only_dates",
            f"{january_first} date values use January 1 without reviewed year-only or approximate metadata.",
        )
    if id_year_mismatches:
        report.add(
            "warning",
            "id_year_mismatch",
            f"{id_year_mismatches} profile ID(s) encode a different year than the recorded birth date.",
        )


def _validate_references(
    report: ValidationReport,
    people: list[Record],
    events: list[Record],
    research: list[Record],
) -> None:
    people_by_id = index_people(people)
    known_ids = set(people_by_id)
    missing_relationship_targets: set[str] = set()
    missing_event_targets: set[str] = set()
    missing_research_targets: set[str] = set()

    for person in people:
        for field_name in RELATIONSHIP_FIELDS:
            for related_id in person.get(field_name, []):
                if str(related_id) not in known_ids:
                    missing_relationship_targets.add(str(related_id))

    for event in events:
        for person_id in event.get("people_involved", []):
            if str(person_id) not in known_ids:
                missing_event_targets.add(str(person_id))

    for record in research:
        for person_id in record.get("people_involved", []):
            if str(person_id) not in known_ids:
                missing_research_targets.add(str(person_id))

    if missing_relationship_targets:
        report.add(
            "warning",
            "missing_relationship_profiles",
            f"{len(missing_relationship_targets)} referenced relative(s) do not yet have profiles.",
        )
    if missing_event_targets:
        report.add(
            "warning",
            "missing_event_profiles",
            f"{len(missing_event_targets)} timeline participant(s) do not yet have profiles.",
        )
    if missing_research_targets:
        report.add(
            "warning",
            "missing_research_profiles",
            f"{len(missing_research_targets)} research-note participant(s) do not yet have profiles.",
        )

    nonreciprocal: set[tuple[str, str, str]] = set()
    for person in people:
        person_id = str(person.get("id", ""))
        for parent_id in person.get("parents", []):
            parent = people_by_id.get(str(parent_id))
            if parent and person_id not in parent.get("children", []):
                nonreciprocal.add(("parent/child", person_id, str(parent_id)))
        for child_id in person.get("children", []):
            child = people_by_id.get(str(child_id))
            if child and person_id not in child.get("parents", []):
                nonreciprocal.add(("child/parent", person_id, str(child_id)))
        for sibling_id in person.get("siblings", []):
            sibling = people_by_id.get(str(sibling_id))
            if sibling and person_id not in sibling.get("siblings", []):
                nonreciprocal.add(("siblings", person_id, str(sibling_id)))
        for spouse_id in person.get("spouses", []):
            spouse = people_by_id.get(str(spouse_id))
            if spouse and person_id not in spouse.get("spouses", []):
                nonreciprocal.add(("spouses", person_id, str(spouse_id)))

    if nonreciprocal:
        report.add(
            "warning",
            "nonreciprocal_relationships",
            f"{len(nonreciprocal)} relationship link(s) are recorded on only one profile; the site repairs these links at runtime without rewriting the source data.",
        )


def _validate_protected_records(
    report: ValidationReport,
    base_events: list[Record],
    research_events: list[Record],
) -> None:
    base_by_id = {str(record.get("id")): record for record in base_events}
    effective_by_id = {
        str(record.get("id")): record
        for record in merge_records(base_events, research_events)
    }

    for record_id, expected_hash in PROTECTED_EVENT_HASHES.items():
        base_record = base_by_id.get(record_id)
        effective_record = effective_by_id.get(record_id)
        if not base_record or not effective_record:
            report.add(
                "error",
                "protected_record_missing",
                f"Protected event {record_id} is missing.",
            )
            continue
        if canonical_record_hash(base_record) != expected_hash:
            report.add(
                "error",
                "protected_base_changed",
                f"Protected base event {record_id} changed unexpectedly.",
            )
        if canonical_record_hash(effective_record) != expected_hash:
            report.add(
                "error",
                "protected_overlay_changed",
                f"An overlay changes protected event {record_id}.",
            )


def _validate_residences(
    report: ValidationReport,
    base_people: list[Record],
    research_people: list[Record],
) -> None:
    """Protect every existing residence array while allowing new profiles."""

    base_snapshot = [
        {"id": person.get("id"), "residences": person.get("residences", [])}
        for person in base_people
    ]
    payload = json.dumps(base_snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if hashlib.sha256(payload.encode("utf-8")).hexdigest() != PROTECTED_RESIDENCE_HASH:
        report.add("error", "protected_residences_base_changed", "One or more base residence entries changed.")

    effective = {person["id"]: person for person in merge_records(base_people, research_people)}
    changed = [
        str(person.get("id"))
        for person in base_people
        if effective.get(person.get("id"), {}).get("residences", []) != person.get("residences", [])
    ]
    if changed:
        report.add(
            "error",
            "protected_residences_overlay_changed",
            f"Research overlays change {len(changed)} existing residence record(s): {', '.join(changed[:8])}",
        )


def _validate_date_precision(
    report: ValidationReport,
    data: dict[str, list[Record]],
) -> None:
    allowed = {"exact", "month", "year", "approximate", "unknown"}
    base_lookup = {
        (kind, str(record.get("id"))): record
        for kind, records in (("person", data["base_people"]), ("event", data["base_events"]))
        for record in records
    }
    seen: set[tuple[str, str, str]] = set()
    for item in data.get("date_precision", []):
        key = (str(item.get("record_type")), str(item.get("record_id")), str(item.get("field")))
        if key in seen:
            report.add("error", "duplicate_date_precision", f"Duplicate date precision entry: {key}")
        seen.add(key)
        if item.get("precision") not in allowed:
            report.add("error", "invalid_date_precision", f"Unsupported precision for {key}")
        base = base_lookup.get((key[0], key[1]))
        if not base:
            report.add("error", "unknown_date_precision_record", f"Date precision references unknown record {key[:2]}")
        elif base.get(key[2]) != item.get("original_value"):
            report.add("error", "date_precision_provenance_mismatch", f"Original value mismatch for {key}")


def validate_site_data(data: dict[str, list[Record]]) -> ValidationReport:
    """Run structural, referential, and protected-content checks."""

    report = ValidationReport()
    datasets = (
        ("people.json", data["base_people"]),
        ("events.json", data["base_events"]),
        ("research_people.json", data["research_people"]),
        ("research_events.json", data["research_events"]),
        ("research.json", data["research"]),
    )
    for dataset_name, records in datasets:
        duplicates = _duplicates(records)
        if duplicates:
            report.add(
                "error",
                "duplicate_ids",
                f"{dataset_name} contains duplicate IDs: {', '.join(duplicates)}",
            )

    _required_fields(
        report,
        data["people"],
        "effective people",
        ("id", "full_name", *RELATIONSHIP_FIELDS, "sources"),
    )
    _required_fields(
        report,
        data["events"],
        "effective events",
        ("id", "date", "title", "description", "people_involved", "sources"),
    )
    _validate_dates(report, data["people"], data["events"])
    _validate_references(report, data["people"], data["events"], data["research"])
    _validate_protected_records(
        report,
        data["base_events"],
        data["research_events"],
    )
    _validate_residences(
        report,
        data["base_people"],
        data["research_people"],
    )
    _validate_date_precision(report, data)
    from archive_validation import validate_archive
    validate_archive(data, report)
    return report
