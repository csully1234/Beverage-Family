from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from family_data import (  # noqa: E402
    date_sort_key,
    format_date,
    index_people,
    load_site_data,
    merge_records,
    relationship_index,
    shortest_relationship_path,
)
from validation import (  # noqa: E402
    PROTECTED_EVENT_HASHES,
    PROTECTED_RESIDENCE_HASH,
    canonical_record_hash,
    validate_site_data,
)


EXPECTED_BASE_FILE_HASHES = {
    "people.json": "88284bd5f254a9a43ab4f6c1d3abbba58cb4d192f567eeb2bacd868411e8acbd",
    "events.json": "0eb342fcdef5a449dab36b38c85885de70f40e6948d277d8e6301b76612858e8",
}


class DataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = ROOT / "data"
        cls.data = load_site_data(cls.data_dir)

    def test_base_datasets_are_byte_for_byte_unchanged(self) -> None:
        for filename, expected_hash in EXPECTED_BASE_FILE_HASHES.items():
            actual = hashlib.sha256((self.data_dir / filename).read_bytes()).hexdigest()
            self.assertEqual(actual, expected_hash, filename)

    def test_protected_events_are_unchanged_after_overlays(self) -> None:
        effective = {
            record["id"]: record
            for record in self.data["events"]
        }
        for record_id, expected_hash in PROTECTED_EVENT_HASHES.items():
            self.assertIn(record_id, effective)
            semantic_record = {
                key: value
                for key, value in effective[record_id].items()
                if key not in {"date_precision", "date_provenance"}
            }
            self.assertEqual(canonical_record_hash(semantic_record), expected_hash)

    def test_modern_home_event_is_not_replaced_by_research_overlay(self) -> None:
        overlay_ids = {record["id"] for record in self.data["research_events"]}
        self.assertNotIn("event_purchase_home_walliford_1997", overlay_ids)
        self.assertNotIn("event_property_record_2024", overlay_ids)

    def test_existing_residences_are_identical_after_overlays(self) -> None:
        base = {person["id"]: person.get("residences", []) for person in self.data["base_people"]}
        effective = {person["id"]: person.get("residences", []) for person in self.data["people"]}
        self.assertEqual({person_id: effective[person_id] for person_id in base}, base)
        snapshot = [
            {"id": person["id"], "residences": person.get("residences", [])}
            for person in self.data["base_people"]
        ]
        payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(hashlib.sha256(payload.encode("utf-8")).hexdigest(), PROTECTED_RESIDENCE_HASH)

    def test_all_dataset_ids_are_unique_within_each_file(self) -> None:
        for key in (
            "base_people",
            "base_events",
            "research_people",
            "research_events",
            "research",
        ):
            ids = [record.get("id") for record in self.data[key]]
            self.assertEqual(len(ids), len(set(ids)), key)

    def test_research_expansion_counts(self) -> None:
        base_people_ids = {record["id"] for record in self.data["base_people"]}
        base_event_ids = {record["id"] for record in self.data["base_events"]}
        new_people = [record for record in self.data["research_people"] if record["id"] not in base_people_ids]
        new_events = [record for record in self.data["research_events"] if record["id"] not in base_event_ids]
        self.assertEqual(len(new_people), 20)
        self.assertEqual(len(new_events), 11)

    def test_validation_has_no_blocking_errors(self) -> None:
        report = validate_site_data(self.data)
        self.assertEqual(report.errors, [])

    def test_research_notes_have_sources(self) -> None:
        missing = [record["id"] for record in self.data["research"] if not record.get("sources")]
        self.assertEqual(missing, [])

    def test_research_note_people_resolve(self) -> None:
        people_by_id = index_people(self.data["people"])
        missing = {
            person_id
            for record in self.data["research"]
            for person_id in record.get("people_involved", [])
            if person_id not in people_by_id
        }
        self.assertEqual(missing, set())

    def test_runtime_relationships_are_reciprocal(self) -> None:
        relationships = relationship_index(self.data["people"])
        for child_id, parent_ids in relationships["parents"].items():
            for parent_id in parent_ids:
                self.assertIn(child_id, relationships["children"].get(parent_id, set()))
        for person_id, spouse_ids in relationships["spouses"].items():
            for spouse_id in spouse_ids:
                self.assertIn(person_id, relationships["spouses"].get(spouse_id, set()))

    def test_json_files_parse_as_arrays(self) -> None:
        for path in self.data_dir.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(payload, list, path.name)

    def test_date_precision_prevents_placeholder_display(self) -> None:
        self.assertEqual(len(self.data["date_precision"]), 142)
        grace = index_people(self.data["people"])["grace_reed_1909"]
        self.assertEqual(format_date(grace["birth_date"], grace["birth_date_precision"]), "October 31, 1909")
        year_only = index_people(self.data["people"])["olive_beveridge_1890"]
        self.assertEqual(format_date(year_only["birth_date"], year_only["birth_date_precision"]), "1890")
        self.assertEqual(format_date("1890-01-01", "approximate"), "circa 1890")

    def test_date_sorting_supports_mixed_precision(self) -> None:
        records = [
            {"date": None, "date_precision": "unknown"},
            {"date": "1921-06-07", "date_precision": "exact"},
            {"date": "1859", "date_precision": "year"},
            {"date": "1890-01-01", "date_precision": "approximate"},
        ]
        ordered = sorted(records, key=date_sort_key)
        self.assertEqual([record["date"] for record in ordered], ["1859", "1890-01-01", "1921-06-07", None])

    def test_overlay_is_a_patch_not_a_replacement(self) -> None:
        merged = merge_records(
            [{"id": "person", "full_name": "Name", "residences": [{"location": "Kept"}]}],
            [{"id": "person", "birth_date": "1900"}],
        )
        self.assertEqual(merged[0]["full_name"], "Name")
        self.assertEqual(merged[0]["residences"], [{"location": "Kept"}])
        self.assertEqual(merged[0]["birth_date"], "1900")

    def test_relationship_finder_returns_supported_path(self) -> None:
        relationships = relationship_index(self.data["people"])
        path = shortest_relationship_path(
            relationships,
            "harold_h_beverage_1893",
            "albert_glover_beverage_1827",
        )
        self.assertEqual(path[0], "harold_h_beverage_1893")
        self.assertEqual(path[-1], "albert_glover_beverage_1827")
        self.assertGreaterEqual(len(path), 3)

    def test_optional_research_files_can_be_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_data = Path(temporary_directory)
            shutil.copyfile(self.data_dir / "people.json", temporary_data / "people.json")
            shutil.copyfile(self.data_dir / "events.json", temporary_data / "events.json")

            data = load_site_data(temporary_data)

            self.assertEqual(data["research_people"], [])
            self.assertEqual(data["research_events"], [])
            self.assertEqual(data["research"], [])
            self.assertEqual(len(data["people"]), len(data["base_people"]))
            self.assertEqual(len(data["events"]), len(data["base_events"]))
            self.assertEqual(validate_site_data(data).errors, [])


if __name__ == "__main__":
    unittest.main()
