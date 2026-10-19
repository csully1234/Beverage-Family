"""Phase 30: distinguish digitized 1785 maps from unopened 1785/1786 manuscripts."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import urlsplit

from family_data import index_people, load_site_data
from family_research_index import build_index, search_index
from fox_islands_originals import (load_fox_islands_sources, original_access_register,
                                   request_note)

ROOT = Path(__file__).resolve().parents[1]


class Phase30FoxIslandOriginalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_fox_islands_sources()
        cls.groups = original_access_register(cls.case)
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.index = build_index(cls.people)

    def test_original_maps_and_two_manuscript_targets_are_not_conflated(self):
        self.assertEqual(len(self.case["sources"]), 7)
        self.assertEqual(len(self.groups["digitized_maps"]), 3)
        self.assertEqual(len(self.groups["original_requests"]), 2)
        self.assertEqual(len(self.groups["published_context"]), 2)
        ids = {r["id"] for r in self.case["sources"]}
        self.assertEqual(len(ids), 7)
        self.assertIn("fox-1785-petition-mass-resolve", ids)
        self.assertIn("fox-1786-putnam-settler-report", ids)
        self.assertTrue(all("does_not_establish" in record for record in self.case["sources"]))

    def test_survey_map_catalogs_are_precise_but_not_matthew_identity_proof(self):
        by_id = {row["id"]: row for row in self.case["sources"]}
        expected = {
            "fox-1785-knox-plan7": ("302962", "digitalmaine.com"),
            "fox-1785-planbook9-list": ("210870", "digitalmaine.com"),
            "fox-1785-planbook8-plan16": ("209714", "digitalmaine.com"),
        }
        for key, (number, host) in expected.items():
            row = by_id[key]
            with self.subTest(key=key):
                self.assertIn(number, row["identifier"])
                self.assertIn(host, urlsplit(row["url"]).netloc)
                self.assertEqual(row["category"], "digitized_historical_cartographic_copy")
                self.assertEqual(row["person_ids"], [])
                self.assertIn("not", row["does_not_establish"].lower())

    def test_archival_finding_aids_do_not_claim_to_have_manuscript_images(self):
        by_id = {row["id"]: row for row in self.case["sources"]}
        petition = by_id["fox-1785-petition-mass-resolve"]
        report = by_id["fox-1786-putnam-settler-report"]
        self.assertIn("Series 228", petition["identifier"])
        self.assertIn("Chapter 97", petition["identifier"])
        self.assertIn("Box 001", report["identifier"])
        self.assertIn("1786-03-18", report["date"])
        self.assertIn("not", report["does_not_establish"].lower())
        self.assertTrue(all(row["category"] == "located_original_document_not_inspected"
                            for row in (petition, report)))
        for row in (petition, report):
            note = request_note(row)
            self.assertIn("not sent", note)
            self.assertIn(row["identifier"], note)
            self.assertIn("No", row["does_not_establish"] or "No")

    def test_1889_minor_is_a_name_only_not_added_as_father_brother_or_same_matthew(self):
        petition = next(r for r in self.case["sources"]
                        if r["id"] == "fox-1785-petition-vinalhaven-1889")
        self.assertEqual(petition["person_ids"], [])
        self.assertIn("minor", petition["establishes"])
        self.assertIn("does not", petition["does_not_establish"].lower())
        matthew = self.people["matthew_beveridge_hope_1837"]
        self.assertEqual(matthew["parents"], [])
        self.assertEqual(matthew["siblings"], [])
        self.assertNotIn("fox-1785-petition-matthew", self.people)

    def test_unified_search_has_seven_documents_without_fuzzy_person_links(self):
        found = [row for row in self.index if row["id"].startswith("fox-original:")]
        self.assertEqual(len(found), 7)
        self.assertTrue(all(row["person_ids"] == [] for row in found))
        self.assertTrue(all(row["route"] == "?page=collection&view=fox-originals"
                            for row in found))
        self.assertTrue(all(row["sources"] for row in found))
        matching = search_index(self.index, query="Fox Islands survey")
        self.assertTrue(any(row["id"].startswith("fox-original:") for row in matching))

    def test_all_phase29_specific_relationship_source_reviews_are_in_workbench(self):
        reviewed = [row for row in self.index if row["id"].startswith("relationship:")]
        self.assertEqual(len(reviewed), 23)
        matthew_children = [row for row in reviewed
                            if "matthew_beveridge_hope_1837" in row["person_ids"] and
                            row["status"] == "original_probate_record"]
        self.assertEqual(len(matthew_children), 9)
        for row in matthew_children:
            self.assertFalse(row["sources"])
            self.assertIn("court", row["summary"].lower() if "court" in row["summary"].lower()
                          else row["limits"].lower())
        self.assertTrue(any(row["status"] == "published_record" and
                            "clarissa_beveridge_widow_1837" in row["person_ids"]
                            for row in reviewed))


if __name__ == "__main__":
    unittest.main()
