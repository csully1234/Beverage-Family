"""Early Beveridge verification queue must not silently overwrite genealogy."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from historical_atlas import load_early_evidence
from visitor_ui import STORIES

ROOT = Path(__file__).resolve().parents[1]


class EarlyFamilyPhase3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = json.loads(
            (ROOT / "research" / "phase3_research_cases.json").read_text(encoding="utf-8")
        )
        cls.book = load_early_evidence()
        cls.people = json.loads((ROOT / "data" / "people.json").read_text(encoding="utf-8"))

    def test_six_provenance_tracked_research_cases(self):
        self.assertEqual(len(self.queue["cases"]), 6)
        self.assertEqual(len({c["id"] for c in self.queue["cases"]}), 6)
        sources = {s["id"] for s in self.queue["source_register"]}
        self.assertGreaterEqual(len(sources), 11)
        for case in self.queue["cases"]:
            self.assertTrue(case["question"] and case["action"] and case["expected_evidence"])
            self.assertTrue(set(case["source_ids"]).issubset(sources))
            self.assertLessEqual(case["priority"], 2)
            self.assertTrue(case["certainty"])
        self.assertIn("Do not send", " ".join(self.queue["constraints"]))

    def test_distinguish_1786_testimony_from_archival_island_map(self):
        src = {s["id"]: s for s in self.queue["source_register"]}
        self.assertIn("Box 001", src["maine_putnam_return"]["detail"])
        self.assertIn("NOT verified online", src["maine_putnam_return"]["detail"])
        self.assertIn("Box 001", src["mgs_2025_eames"]["detail"])
        self.assertEqual(src["maine_1785_map"]["url"], src["maine_putnam_return"]["url"])
        self.assertIn("not examined", str(self.book["findings"]).lower())

    def test_new_1752_and_1776_leads_not_made_fact_in_family_tree(self):
        people = {p["id"]: p for p in self.people}
        self.assertEqual(people["mercy_beveridge_henry_1753"]["spouses"],
                         ["henry_henry_1750"])
        self.assertEqual(people["samuel_beveridge_1702"]["parents"], [])
        self.assertFalse(any(p.get("full_name") == "Capt. Matthew Beverage of Hope"
                             for p in self.people))
        self.assertTrue(any("probably" in s["detail"].lower()
                            for s in self.book["sources"] if s["id"] == "wheeler_mercy_1776"))

    def test_new_findings_have_citations_and_research_labels(self):
        sources = {s["id"] for s in self.book["sources"]}
        needed = {"first_settler_statement", "topsham1750s",
                  "mercy_henry_1776", "matthew_courthouse"}
        found = {f["id"] for f in self.book["findings"]}
        self.assertTrue(needed.issubset(found))
        for f in self.book["findings"]:
            self.assertTrue(set(f["source_ids"]).issubset(sources))
            self.assertTrue(f["confidence"] and f["status"])
        conflict = next(f for f in self.book["findings"] if f["id"] == "petitioner_dates")
        self.assertIn("1 June", conflict["date"])
        self.assertIn("March 1785", conflict["summary"])

    def test_visitor_stories_link_to_actual_sources_and_mark_uncertainty(self):
        story = next(s for s in STORIES if s["id"] == "topsham-beveridge-before-fox-islands")
        self.assertIn("original", story["body"])
        self.assertIn("not", story["body"])
        self.assertGreaterEqual(len(story["source_links"]), 3)
        fox = next(s for s in STORIES if s["id"] == "fox-islands-land-matthew")
        self.assertIn("2025", fox["body"])
        self.assertTrue(any("maineroots.org" in url for _, url in fox["source_links"]))

    def test_archival_requests_are_drafts_and_not_sends(self):
        text = (ROOT / "research" / "phase3_archival_requests_not_sent.md").read_text()
        self.assertIn("NOTHING HAS BEEN SENT", text)
        self.assertIn("18 March 1786", text)
        self.assertIn("registerofprobate@waldocountyme.gov", text)
        self.assertIn("June 1785", text)


if __name__ == "__main__":
    unittest.main()
