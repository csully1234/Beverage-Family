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

from family_data import index_people, load_site_data, relationship_index  # noqa: E402
from validation import PROTECTED_EVENT_HASHES, canonical_record_hash, validate_site_data  # noqa: E402


EXPECTED_BASE_FILE_HASHES = {
    "people.json": "78d5a0c04ee298d683d3b94de17ae9b430a7adde555d630ce59a99929a7f4aed",
    "events.json": "87959a115258736d379f6639782a4dba058368133daf970dd39994853dea154b",
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
            self.assertEqual(canonical_record_hash(effective[record_id]), expected_hash)

    def test_modern_home_event_is_not_replaced_by_research_overlay(self) -> None:
        overlay_ids = {record["id"] for record in self.data["research_events"]}
        self.assertNotIn("event_purchase_home_walliford_1997", overlay_ids)

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
