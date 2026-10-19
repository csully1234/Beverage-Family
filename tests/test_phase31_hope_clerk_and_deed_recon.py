"""Phase 31: preserve newly indexed original-era Hope clerk entries without inventing deeds."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit
import unittest

from hope_matthew_civic import load_hope_civic_records, evidence_counts, record_for_id
from family_data import load_site_data, index_people
from family_research_index import build_index

ROOT = Path(__file__).resolve().parents[1]


class Phase31HopeClerkDeedReconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new = json.loads((ROOT / "data/phase31_hope_earliest_clerk_research.json").read_text())[0]
        cls.hope = load_hope_civic_records()
        cls.people = index_people(load_site_data(ROOT / "data")["people"])

    def test_1806_and_1807_entries_are_preserved_as_ledger_transcription_only(self):
        early = self.new["records"]
        self.assertEqual(len(early), 3)
        self.assertEqual([r["date"] for r in early],
                         ["1806-06-23", "1807-04-09", "1807-06-19"])
        self.assertTrue(all("original" in r["limit"].lower() or
                            "manuscript" in r["verification"].lower() for r in early))
        self.assertTrue(all(urlsplit(r["source_url"]).scheme == "https" for r in early))
        self.assertIn("June 23, 1806", early[0]["claim"])
        self.assertEqual(evidence_counts(self.hope)["ledger_entries"], 10)
        self.assertEqual(evidence_counts(self.hope)["distinct_source_families"], 2)
        self.assertEqual(record_for_id("hope-1806-june-clerk", self.hope), early[0])
        self.assertIn("ONE Hope town clerk ledger", self.hope["source_family_warning"])

    def test_ledger_observation_does_not_become_verified_land_conveyance(self):
        self.assertIn("No Matthew-specific deed volume/page", self.new["land_search_result"])
        self.assertIn("ACCESS LIMIT", self.new["land_search_result"])
        self.assertIn("no authenticated viewer", self.new["research_not_done"])
        for row in self.new["records"]:
            self.assertNotIn("verified deed", row["claim"].lower())
        self.assertFalse(self.people["matthew_beveridge_hope_1837"]["parents"])

    def test_unified_research_search_includes_original_page_specific_entries(self):
        result = [r for r in build_index(self.people) if r["id"].startswith("hope-clerk:")]
        self.assertEqual(len(result), 11)
        early_ids = {"hope-clerk:" + row["id"] for row in self.new["records"]}
        self.assertTrue(early_ids.issubset({row["id"] for row in result}))
        for row in result:
            self.assertFalse(row["person_ids"])
            self.assertEqual(row["route"], "?page=collection&view=hope-matthew")
        self.assertEqual(len({r["id"] for r in result}), len(result))


if __name__ == "__main__":
    unittest.main()
