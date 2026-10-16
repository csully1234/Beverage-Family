from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from family_data import load_site_data
from research_collection import CollectionIndex, REPORT_DIR, validate_collection
from tools.import_research_package import read_dossier, read_workbook, records

ROOT = Path(__file__).resolve().parents[1]


class ResearchCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.collection = CollectionIndex.load()
        cls.site = load_site_data(ROOT / "data")

    def test_all_research_ids_ratings_and_cells_preserved_from_supplied_workbooks(self):
        workbooks = read_workbook(REPORT_DIR / "Beverage_Family_Master_Research.xlsx")
        candidates = {t["name"]: t for t in read_workbook(REPORT_DIR / "Beverage_Family_Site_Candidates.xlsx")}
        self.assertEqual(len(self.collection.findings), 57)
        self.assertEqual(len(self.collection.sources), 163)
        self.assertEqual(len(self.collection.targets), 33)
        self.assertEqual(self.collection.raw["inventories"][:29], workbooks)
        self.assertEqual(self.collection.raw["sources"], records(candidates["Source Lookup"]))
        for expected in records(candidates["Site Candidates"]):
            actual = self.collection.findings[expected["Research ID"]]
            self.assertEqual({k: actual[k] for k in expected}, expected)

    def test_citations_links_living_person_boundary_and_snapshot_validate(self):
        self.assertEqual(validate_collection(self.collection, self.site), [])

    def test_validator_rejects_missing_evidence_and_unknown_references(self):
        raw = copy.deepcopy(self.collection.raw)
        raw["findings"][0]["Supporting sources"] = "SRC999"
        raw["findings"][0]["Confidence"] = "Verified without review"
        errors = validate_collection(CollectionIndex(raw), self.site)
        self.assertTrue(any("missing source" in e for e in errors))
        self.assertTrue(any("invalid confidence" in e for e in errors))

    def test_validator_rejects_new_links_to_living_people(self):
        raw = copy.deepcopy(self.collection.raw)
        raw["findings"][0]["Navigation"]["people_ids"].append("sarah_beverage_1999")
        self.assertTrue(any("possibly living" in e for e in validate_collection(CollectionIndex(raw), self.site)))

    def test_protected_baseline_files_are_byte_identical(self):
        for record in json.loads((REPORT_DIR / "baseline_hashes.json").read_text()):
            with self.subTest(file=record["file"]):
                self.assertEqual(hashlib.sha256((ROOT / record["file"]).read_bytes()).hexdigest(), record["sha256"])

    def test_original_reports_and_dossier_reader_preserved(self):
        self.assertEqual(len(self.collection.raw["reports"]), 5)
        for report in self.collection.raw["reports"]:
            self.assertEqual(hashlib.sha256((REPORT_DIR / report["filename"]).read_bytes()).hexdigest(), report["sha256"])
        self.assertEqual(self.collection.raw["dossier"], read_dossier(REPORT_DIR / "Beverage_Family_Research_Dossier.docx"))

    def test_identity_candidates_not_added_to_genealogy(self):
        people = {r["id"] for r in self.site["people"]}
        # The Oct 14 source snapshot is immutable; later separately-sourced
        # profiles and historical events are additive overlays.
        self.assertEqual(len(people), 180 + len(self.site["phase4_people"]))
        self.assertEqual(len(self.site["events"]), 127 + len(self.site["phase4_events"]))
        self.assertTrue({"amelia_beverage_1833", "amelia_beverage_1833_child"} <= people)
        self.assertFalse(any(pid.startswith("RQ-P") for pid in people))
        self.assertEqual(self.collection.findings["BF-R049"]["Confidence"], "Conflict")
        self.assertFalse(self.collection.findings["BF-R007"]["Navigation"]["people_ids"])

    def test_source_content_confirmation_does_not_overwrite_identity_limits(self):
        record = self.collection.findings["BF-R033"]
        self.assertIn("Registration dates are not deed dates", record["Notes about uncertainty"])
        self.assertIn("needs the deeds", record["Notes about uncertainty"])
        self.assertEqual(record["Human-review status"], "Not reviewed")
        testimony = self.collection.findings["BF-R001"]
        self.assertEqual(testimony["Confidence"], "Probable")
        self.assertIn("does not establish Tea Party participation or military service", testimony["Notes about uncertainty"])

    def test_context_source_and_topic_filters_do_not_guess_identity(self):
        records = self.collection.select(query="IsleBuilt", person_id="elliot_beverage_1908")
        self.assertTrue({"BF-R028", "BF-R029"} <= {r["Research ID"] for r in records})
        self.assertEqual(self.collection.select(query="IsleBuilt", person_id="arnold_beveridge_1903"), [])
        self.assertEqual({r["Research ID"] for r in self.collection.for_subject("event", "event_testimony_1781")}, {"BF-R001", "BF-R002"})
        self.assertEqual(len(self.collection.select(confidence="Conflict")), 11)
        self.assertTrue(self.collection.select(topic="Land and property", place_id="topsham_me"))
        self.assertEqual({r["Research ID"] for r in self.collection.for_source("SRC118")}, {"BF-R001", "BF-R002"})


if __name__ == "__main__":
    unittest.main()
