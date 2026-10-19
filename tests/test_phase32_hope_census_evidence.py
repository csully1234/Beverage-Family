"""Phase 32: census locator authenticity, negative evidence limits, and no invented household."""
from __future__ import annotations

import unittest
from pathlib import Path

from family_data import load_site_data, index_people, relationship_index
from family_research_index import build_index, search_index
from hope_census_records import load_hope_census_trail, census_evidence_counts
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase32HopeCensusEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_hope_census_trail()
        cls.rows = {row["year"]: row for row in cls.case["cases"]}
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])

    def test_every_census_year_has_its_own_qualified_ledger_entry(self):
        self.assertEqual(set(self.rows), {1790, 1800, 1810, 1820})
        self.assertEqual(census_evidence_counts(self.case), {
            "census_years": 4,
            "transcribed_absent_named_heads": 2,
            "named_head_transcriptions": 1,
            "original_person_lines_inspected": 0,
        })
        self.assertTrue(all(row["limitations"] and row["original_request"]
                            for row in self.rows.values()))
        self.assertTrue(all(not row["original_image_checked"]
                            for row in self.rows.values()))

    def test_1790_and_1800_negative_surname_index_does_not_equal_non_residence(self):
        for year in (1790, 1800):
            row = self.rows[year]
            self.assertEqual(row["named_matthew_head"], False)
            self.assertEqual(row["status"],
                             "surname_absent_from_published_head_transcription")
            self.assertIn("not", row["limitations"].lower())
            self.assertEqual(row["original_image_checked"], False)
        self.assertIn("544–548", self.rows[1800]["archive_locator"])
        self.assertIn("roll 6", self.rows[1800]["archive_locator"])
        self.assertIn("Appleton", self.rows[1800]["limitations"])
        self.assertIn("Whitney", self.rows[1800]["head_claim"])
        self.assertIn("Lucy Whitney", self.rows[1800]["head_claim"])

    def test_1810_microfilm_exists_but_matthew_is_not_inferred(self):
        row = self.rows[1810]
        self.assertIsNone(row["named_matthew_head"])
        self.assertIn("M252", row["archive_locator"])
        self.assertIn("roll 12", row["archive_locator"])
        self.assertIn("p. 136", row["archive_locator"])
        self.assertIn("archive.org/details/populationschedu0012unix",
                      row["source_url"])
        self.assertEqual(row["status"],
                         "original_reel_located_not_person_verified")
        self.assertNotIn("verified Matthew household", row["head_claim"])

    def test_1820_is_a_real_transcribed_head_but_original_tallies_unread(self):
        row = self.rows[1820]
        self.assertIs(row["named_matthew_head"], True)
        self.assertIn("M33", row["archive_locator"])
        self.assertIn("roll 36", row["archive_locator"])
        self.assertIn("sheet 276", row["archive_locator"])
        self.assertIn("Mathew Beveridge", row["head_claim"])
        self.assertIn("not", row["limitations"].lower())
        self.assertFalse(row["original_image_checked"])

    def test_all_four_are_findable_in_workbench_without_exact_person_links(self):
        records = build_index(self.people)
        found = [r for r in records if r["id"].startswith("hope-census:")]
        self.assertEqual(len(found), 4)
        self.assertEqual(len({r["id"] for r in found}), 4)
        self.assertTrue(all(r["person_ids"] == [] for r in found))
        self.assertTrue(all(r["route"] == "?page=collection&view=hope-census"
                            for r in found))
        self.assertTrue(all(r["sources"] for r in found))
        self.assertTrue(any(r["id"] == "hope-census:hope-census-1820-hope"
                            for r in search_index(records, query="1820 Mathew Hope")))

    def test_no_genealogy_relationship_source_or_password_modification(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        matthew = self.people["matthew_beveridge_hope_1837"]
        self.assertEqual(matthew["parents"], [])
        self.assertEqual(self.people["clarissa_beveridge_widow_1837"]["children"], [])
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertNotIn("from family_access import", app)


if __name__ == "__main__":
    unittest.main()
