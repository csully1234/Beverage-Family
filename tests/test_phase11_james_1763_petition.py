"""James in Topsham: document sightings must not turn into unproven kinship."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import urlsplit

from early_maine_sources import load_early_maine_record_leads, load_james_record_chain
from family_data import load_site_data, index_people
from unified_timeline import build_chronology
from research_collection import CollectionIndex

ROOT = Path(__file__).resolve().parents[1]


class ColonialJamesPetitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = load_site_data(ROOT / "data")
        cls.people = index_people(cls.site["people"])
        cls.records = load_early_maine_record_leads()
        cls.chain = load_james_record_chain()

    def test_1763_dated_petition_is_only_a_document_claim(self):
        petition = next(r for r in self.records if r["id"] == "topsham-1763-incorporation-petition")
        self.assertEqual(petition["date"], "1763-12-21")
        self.assertEqual(petition["year"], 1763)
        self.assertTrue(petition["timeline_inclusion"])
        self.assertIn("Pejepscot Papers", petition["next_record"])
        self.assertIn("original signed petition not examined", petition["status"])
        self.assertIn("NOT independently", petition["summary"])
        self.assertEqual(petition["related_existing_event_id"], "event_james_topsham_first_town_meeting_1764")
        self.assertNotIn(petition["id"], self.people)
        self.assertTrue(urlsplit(petition["source_url"]).hostname)

    def test_six_distinct_sightings_have_dates_provenance_and_limits(self):
        self.assertEqual(len(self.chain), 6)
        self.assertEqual([r["date"][:4] for r in self.chain],
                         sorted(r["date"][:4] for r in self.chain))
        self.assertEqual(len({r["id"] for r in self.chain}), 6)
        for r in self.chain:
            self.assertTrue(r["proof"] and r["link_status"])
            self.assertTrue(urlsplit(r["source_url"]).hostname)
        self.assertIn("not a", self.chain[3]["proof"].lower())
        self.assertIn("not", self.chain[4]["link_status"].lower())

    def test_complete_timeline_includes_1763_document_without_new_ancestor(self):
        timeline = build_chronology(self.site, self.people, CollectionIndex.load())
        rows = [r for r in timeline if r["id"] == "early-maine:topsham-1763-incorporation-petition"]
        self.assertEqual(len(rows), 1)
        entry = rows[0]
        self.assertEqual(entry["type"], "Historical document")
        self.assertEqual(entry["year"], 1763)
        self.assertEqual(entry["date"], "1763-12-21")
        self.assertEqual(entry["person_ids"], ())
        self.assertIn("original", entry["extra"].lower())
        self.assertEqual(entry["url"], "?page=stories&story=topsham-beveridge-before-fox-islands")
        old = next(r for r in self.site["events"]
                   if r["id"] == "event_james_topsham_first_town_meeting_1764")
        self.assertIn("James", old["title"])

    def test_preexisting_historical_and_modern_records_unchanged(self):
        # New editorial source records are not merged into core people or events.
        self.assertEqual(self.site["people"], load_site_data(ROOT / "data")["people"])
        self.assertFalse(any("topsham-1763-incorporation-petition" == p["id"]
                             for p in self.site["people"]))
        self.assertFalse(any("topsham-1763-incorporation-petition" == e["id"]
                             for e in self.site["events"]))


if __name__ == "__main__":
    unittest.main()
