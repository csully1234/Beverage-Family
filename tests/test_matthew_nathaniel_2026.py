"""Evidence guards for the 2026 Matthew/Nathaniel and North Haven discoveries."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from family_data import index_people, load_site_data, relationship_index, shortest_relationship_path
from visitor_ui import STORIES
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FAMILY = ROOT / "research" / "matthew_nathaniel_family_1865.json"
EARLY = ROOT / "research" / "early_fox_islands_evidence.json"


class MatthewNathanielResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(DATA)
        cls.people = index_people(cls.data["people"])
        cls.events = {e["id"]: e for e in cls.data["events"]}
        cls.families = json.loads(FAMILY.read_text(encoding="utf-8"))

    def test_four_new_profiles_preserve_original_1776_nathaniel(self):
        required = {
            "nathaniel_beverage_1804_rockland",
            "sarah_alexander_beverage_1808",
            "henry_t_beverage_1841_rockland",
            "ella_allen_beverage_1854",
        }
        self.assertTrue(required.issubset(set(self.people)))
        self.assertIn("nathaniel_winslow_beverage_1776", self.people)
        rockland = self.people["nathaniel_beverage_1804_rockland"]
        self.assertEqual(rockland["parents"], [])
        self.assertEqual(rockland["birth_date_precision"], "approximate")
        self.assertIn("different", self.families["nathaniel"]["avoid_confusion"]["note"])
        self.assertEqual(self.people["nathaniel_winslow_beverage_1776"]["birth_date"],
                         "1776-01-17")

    def test_henry_has_recorded_parent_and_spouse_links_without_spurious_ancestry(self):
        henry = self.people["henry_t_beverage_1841_rockland"]
        self.assertEqual(set(henry["parents"]), {
            "nathaniel_beverage_1804_rockland", "sarah_alexander_beverage_1808"
        })
        self.assertEqual(henry["birth_date"], "1841-11-29")
        self.assertIn("ella_allen_beverage_1854", henry["spouses"])
        self.assertIn("henry_t_beverage_1841_rockland",
                      self.people["ella_allen_beverage_1854"]["spouses"])
        relationships = relationship_index(self.data["people"])
        self.assertTrue(shortest_relationship_path(
            relationships, "nathaniel_beverage_1804_rockland",
            "ella_allen_beverage_1854"))
        self.assertFalse(shortest_relationship_path(
            relationships, "nathaniel_beverage_1804_rockland",
            "james_beveridge_jr_1724"))

    def test_matthew_family_group_keeps_unproved_identity_and_all_ten_children(self):
        matthew = self.families["matthew"]
        self.assertEqual(len(matthew["children"]), 10)
        self.assertEqual(len(matthew["wives"]), 2)
        self.assertEqual(len(self.families["nathaniel"]["children"]), 3)
        self.assertIn("or c. from there", matthew["origin_exact"])
        self.assertIn("No proof", matthew["identity_caution"])
        self.assertIn("unverified", self.families["nathaniel"]["candidate_parentage"]["status"].lower())
        self.assertFalse("matthew_beverage_hope" in self.people)

    def test_1749_intention_has_an_exact_date_but_no_assumed_ceremony_or_identity(self):
        event = self.events["event_1749_james_jean_marriage_intention"]
        self.assertEqual(event["date"], "1749-02-06")
        self.assertEqual(event["people_involved"], [])
        self.assertIn("not a marriage ceremony", event["description"])
        self.assertIn("marriage intentions", event["sources"][0]["title"].lower())

    def test_additional_original_and_local_history_timeline_entries(self):
        ids = {
            "event_henry_ella_marriage_1898": ("1898-12-17", 2),
            "event_north_haven_first_high_school_graduates_1907": ("1907", 0),
            "event_1927_pulpit_harbor_auction_ad": ("1927-07-30", 0),
            "event_1975_north_haven_rescued_town_archives": ("1975-11-13", 1),
        }
        for eid, (date, people_count) in ids.items():
            event = self.events[eid]
            self.assertEqual(event["date"], date)
            self.assertEqual(len(event["people_involved"]), people_count)
            self.assertTrue(event["sources"] and event["evidence_status"])
        self.assertIn("NOT proof", self.events["event_1927_pulpit_harbor_auction_ad"]["description"])
        self.assertEqual(self.events["event_1975_north_haven_rescued_town_archives"]["people_involved"],
                         ["samuel_hiram_beverage_1917"])

    def test_stories_link_archived_images_without_copying_third_party_photos(self):
        indexed = {s["id"]: s for s in STORIES}
        self.assertIn("matthew-rockland-descendants-1865", indexed)
        self.assertTrue(indexed["matthew-rockland-descendants-1865"]["family_group"])
        self.assertIn("north-haven-preserving-family-history", indexed)
        links = indexed["north-haven-preserving-family-history"]["source_links"]
        self.assertTrue(any("northhavenmainehistoricalsociety.org/videos.html" in url
                            for _, url in links))
        self.assertIn("not proof", indexed["north-haven-preserving-family-history"]["body"])
        self.assertIn("Brunswick marriage-intention", str(indexed[
            "topsham-beveridge-before-fox-islands"]["source_links"]))

    def test_unchanged_original_people_and_no_blocking_validation_issues(self):
        self.assertEqual(self.data["base_people"][0]["id"], "sarah_beverage_1999")
        self.assertEqual(validate_site_data(self.data).errors, [])


if __name__ == "__main__":
    unittest.main()
