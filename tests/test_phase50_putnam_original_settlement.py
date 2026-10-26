"""Phase 50: first-hand Thomas Beverage 15-year Putnam settlement statement."""
from __future__ import annotations

import unittest
from pathlib import Path

from family_data import index_people, load_site_data
from family_research_index import build_index, search_index
from putnam_original import load_putnam_original, putnam_csv

ROOT = Path(__file__).resolve().parents[1]


class Phase50PutnamOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_putnam_original()
        cls.people = index_people(load_site_data(ROOT / "data")["people"])

    def test_original_eight_pages_and_physical_authenticity_limits(self):
        c = self.case
        self.assertEqual(c["original_uploaded_file"], "4-29462-F012.pdf")
        self.assertEqual(c["pdf_page_count"], 8)
        self.assertEqual(len(c["page_inventory"]), 8)
        self.assertEqual(c["paper_part_dates"][0]["date"], "1785-12-16")
        self.assertEqual(c["paper_part_dates"][1]["date"], "1786-03-18")
        self.assertFalse(c["full_diplomatic_transcription_verified"])
        self.assertFalse(c["digital_facsimile_hosted_publicly"])
        self.assertEqual(c["related_source_targets"][0]["status"],
                         "likely_related_archive_record_not_exact_box_proven")

    def test_thomas_name_duration_and_inferred_year_not_birth_fact(self):
        o = self.case["observation"]
        self.assertEqual(o["name_as_written"], "Thomas Beverage")
        self.assertEqual(o["duration_as_written"], "15")
        self.assertEqual(o["pdf_page"], 7)
        self.assertEqual(o["division"], "Fox Island division of islands")
        self.assertEqual(o["interpreted_settlement_year"], "approximately 1771")
        self.assertIn("not an exact", o["precision"])
        self.assertTrue(o["firsthand_manuscript_read"])
        self.assertIn("parental", o["cannot_prove"])
        self.assertNotIn("person_id", o)
        self.assertTrue(self.case["no_new_relationships"])
        self.assertTrue(self.people)

    def test_searchable_original_does_not_promote_possible_profile_identity(self):
        index = build_index(self.people, ROOT / "data")
        hits = [x for x in index if x["id"].startswith("putnam-original:")]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["person_ids"], [])
        self.assertIn("fox-originals", hits[0]["route"])
        self.assertIn("15 years", hits[0]["title"])
        searched = search_index(index, query="Putnam Thomas Beverage settlement")
        self.assertTrue(any(x["id"].startswith("putnam-original:") for x in searched))
        self.assertIn("Thomas Beverage", putnam_csv(self.case))


if __name__ == "__main__":
    unittest.main()
