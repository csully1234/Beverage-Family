"""Original-record navigation is source-led, not a way to invent ancestors."""
from __future__ import annotations

import unittest
from urllib.parse import urlsplit
from pathlib import Path

from early_maine_sources import load_early_maine_record_leads
from family_data import load_site_data, index_people
from visitor_ui import STORIES
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class TopshamArchivalLeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_early_maine_record_leads()
        cls.site = load_site_data(ROOT / "data")
        cls.people = index_people(cls.site["people"])

    def test_every_original_source_link_is_explicit_and_statused(self):
        self.assertEqual(len(self.records), 8)
        self.assertEqual(len({r["id"] for r in self.records}), len(self.records))
        self.assertEqual([r["year"] for r in self.records], sorted(r["year"] for r in self.records))
        for record in self.records:
            self.assertTrue(record["summary"] and record["status"])
            self.assertTrue(record["source_title"] and record["next_record"])
            url = urlsplit(record["source_url"])
            self.assertEqual(url.scheme, "https")
            self.assertTrue(url.hostname)

    def test_state_compilation_links_topsham_robert_military_service_not_parentage(self):
        by_id = {row["id"]: row for row in self.records}
        a = by_id["topsham-1776-robert"]
        b = by_id["topsham-1777-robert"]
        self.assertIn("March 11, 1776", a["summary"])
        self.assertIn("March 22", a["summary"])
        self.assertIn("August 9", a["summary"])
        self.assertIn("commissioned February 3, 1777", b["summary"])
        self.assertIn("Massachusetts", a["source_title"])
        self.assertEqual(a["source_url"], b["source_url"])
        self.assertIn("NOT his parents", a["person_status"])
        self.assertNotIn("robert_beveridge_1776", self.people)

    def test_separate_robert_soldiers_not_combined_into_one_identity(self):
        ids = {record["id"] for record in self.records}
        self.assertIn("georgetown-1775-robert-fifer", ids)
        self.assertIn("massachusetts-1777-robert-seaman", ids)
        by_id = {r["id"]: r for r in self.records}
        self.assertIn("UNPROVEN", by_id["georgetown-1775-robert-fifer"]["status"])
        self.assertIn("unproven", by_id["massachusetts-1777-robert-seaman"]["status"])
        self.assertNotIn("robert_beveridge_1775", self.people)

    def test_1752_and_1758_references_do_not_prove_deeds(self):
        by_id = {row["id"]: row for row in self.records}
        self.assertIn("NOT a deed", by_id["topsham-1752-samuel"]["status"])
        self.assertIn("settler", by_id["topsham-1758-james"]["summary"])
        self.assertIn("fee-simple deed", by_id["topsham-1758-james"]["summary"])
        self.assertIn("not proven", by_id["topsham-1749-intention"]["person_status"])

    def test_story_is_family_facing_and_archival_data_unchanged(self):
        story = next(s for s in STORIES if s["id"] == "topsham-beveridge-before-fox-islands")
        self.assertIn("Robert Beveridge", story["body"])
        self.assertIn("not an original deed", story["body"])
        self.assertEqual(validate_site_data(self.site).errors, [])
        original = next(event for event in self.site["events"]
                        if event["id"] == "event_marriage_james_jr_jean_white_1749")
        self.assertIn("Marriage of", original["title"])

if __name__ == "__main__":
    unittest.main()
