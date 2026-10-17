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
        self.assertEqual(len(self.records), 6)
        self.assertEqual(len({r["id"] for r in self.records}), len(self.records))
        self.assertEqual([r["year"] for r in self.records], sorted(r["year"] for r in self.records))
        for record in self.records:
            self.assertTrue(record["summary"] and record["status"])
            self.assertTrue(record["source_title"] and record["next_record"])
            url = urlsplit(record["source_url"])
            self.assertEqual(url.scheme, "https")
            self.assertTrue(url.hostname)

    def test_robert_is_not_fictitiously_linked_to_verified_family(self):
        service = [row for row in self.records if "robert" in row["id"]]
        self.assertEqual([r["year"] for r in service], [1776, 1777])
        self.assertIn("Lithgow", service[0]["summary"])
        self.assertIn("George White", service[1]["summary"])
        self.assertIn("DO NOT create", service[0]["person_status"])
        self.assertIn("unverified", service[1]["person_status"].lower())
        self.assertFalse(any(row["id"] in self.people for row in service))
        self.assertFalse(any("robert_beveridge_1776" == x for x in self.people))

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
