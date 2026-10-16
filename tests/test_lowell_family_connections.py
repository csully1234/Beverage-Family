"""Lowell father/son genealogy and 1954 marriage: source-verified public context."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from family_data import index_people, load_site_data, relationship_index, shortest_relationship_path
from family_books import load_books
from visitor_ui import STORIES
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class LowellFamilyRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.events = {row["id"]: row for row in cls.data["events"]}
        cls.sources = json.loads((ROOT / "data" / "evidence_exhibits.json").read_text())

    def test_father_and_author_are_separate_profiles_in_same_family_tree(self):
        father_id = "lowell_beveridge_1905"
        son_id = "lowell_pierson_beveridge_jr_1930"
        father = self.people[father_id]
        son = self.people[son_id]
        self.assertEqual(father["birth_date"][:4], "1905")
        self.assertEqual(son["birth_date"], "1930-04-07")
        self.assertIn(father_id, son["parents"])
        self.assertIn("ida_louisa_gattrell_beveridge_1901", son["parents"])
        self.assertEqual(self.people["thomas_gattrell_beveridge_1938"]["parents"], son["parents"])
        rel = relationship_index(self.data["people"])
        self.assertTrue(shortest_relationship_path(rel, "orris_beverage_1860", son_id))
        self.assertEqual(rel["children"][father_id], {son_id, "thomas_gattrell_beveridge_1938"})
        self.assertIn("hortense_tee_sie_beveridge_1923", rel["spouses"][son_id])

    def test_writer_identification_is_exact_not_name_match(self):
        book = load_books()[0]
        self.assertEqual(book["author_person_id"], "lowell_pierson_beveridge_jr_1930")
        self.assertNotEqual(book["author_person_id"], "lowell_beveridge_1905")
        content = (ROOT / "family_books.py").read_text(encoding="utf-8")
        self.assertIn('is_author = person_id == "lowell_pierson_beveridge_jr_1930"', content)
        self.assertIn('"lowell_beveridge_1905": [("Lowell Beveridge', content)
        self.assertNotIn('if "lowell" in name', content)

    def test_marriage_record_uses_firsthand_1954_not_google_1953(self):
        event = self.events["event_lowell_jr_hortense_marriage_1954"]
        self.assertEqual(event["date"], "1954")
        self.assertIn("JANUARY 1954", event["description"])
        self.assertIn("parents blessed the wedding", event["description"])
        self.assertEqual(set(event["people_involved"]), {
            "lowell_pierson_beveridge_jr_1930", "hortense_tee_sie_beveridge_1923"
        })
        self.assertTrue(any("2012" in s.get("title", "") for s in event["sources"]))
        self.assertNotIn("20-year banishment established", event["description"])

    def test_1960_sale_is_documented_as_report_not_imaginary_deed(self):
        event = self.events["event_lowell_1960_report_north_haven_sale"]
        self.assertEqual(event["date_precision"], "year")
        self.assertEqual(event["people_involved"], ["lowell_beveridge_1905"])
        self.assertIn("not a deed", event["description"])
        self.assertIn("neither the exact sale date", event["description"])

    def test_curated_primary_oral_history_is_linked_to_event_and_people(self):
        x = next(s for s in self.sources if s["id"] == "2012-pete-beveridge-oral-history")
        self.assertIn("event_lowell_jr_hortense_marriage_1954", x["event_ids"])
        self.assertIn("lowell_pierson_beveridge_jr_1930", x["people_ids"])
        self.assertIn("January 1954", x["claim"])
        self.assertIn("Google snippets", x["limits"])
        self.assertIn("no audio/transcript republication", x["rights"])

    def test_story_preserves_historical_parental_support_and_rights(self):
        story = next(s for s in STORIES if s["id"] == "lowell-pete-tee-firsthand-1954")
        self.assertIn("parents blessed", story["body"])
        self.assertIn("1954", story["body"])
        self.assertIn("shared ancestral North Haven", story["body"])
        self.assertTrue(any("s3.amazonaws.com" in u for _, u in story["source_links"]))

    def test_no_original_facts_changed_and_new_records_valid(self):
        self.assertEqual(len(self.data["phase7_people"]), 4)
        self.assertEqual(len(self.data["phase7_events"]), 3)
        self.assertEqual(validate_site_data(self.data).errors, [])
        for person in self.data["phase7_people"]:
            self.assertNotIn("email", person)
            self.assertEqual(person["residences"], [])
            self.assertFalse(person.get("living") is False and not person.get("death_date"))


if __name__ == "__main__":
    unittest.main()
