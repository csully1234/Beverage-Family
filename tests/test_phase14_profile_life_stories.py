"""Evidence-first life records: never turn an indexed fact into a false genealogy."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from family_data import index_people, load_site_data
from profile_life_stories import (
    life_record_overview, profile_milestones, linked_book_illustrations,
)
from family_books import load_book_person_crosswalk
from colony_photos import load_colony_photo_catalog

ROOT = Path(__file__).resolve().parents[1]


class ProfileLifeStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.book = load_book_person_crosswalk()
        cls.photos = load_colony_photo_catalog()["photos"]

    def test_every_profile_builds_a_safe_life_story_and_milestones(self):
        self.assertGreaterEqual(len(self.people), 185)
        self.assertLess(sum(bool(person.get("biography")) for person in self.people.values()),
                        len(self.people) // 2)
        for person in self.people.values():
            with self.subTest(id=person["id"]):
                overview = life_record_overview(person)
                self.assertIsInstance(overview, list)
                self.assertTrue(all(isinstance(text, str) and text.endswith(".") for text in overview))
                milestones = profile_milestones(person, self.data["events"])
                self.assertEqual(len(milestones), len({m["id"] for m in milestones}))
                for m in milestones:
                    route = parse_qs(urlsplit(m["url"]).query)
                    self.assertIn(route.get("page", [None])[0], {"people", "timeline"})
                    self.assertTrue(m["date_label"] and m["title"])
                    self.assertTrue(m["status"])

    def test_parentage_and_memoir_claims_are_not_generated_into_prose(self):
        fake = {
            "id": "test", "full_name": "Pat Sample",
            "birth_date": "1753", "birth_date_precision": "approximate",
            "death_date": "1831-10-26", "death_date_precision": "exact",
            "parents": ["james_beveridge_jr_1724"],
            "spouses": ["henry_henry_1750"],
            "notes": "An unverified claim naming a father.",
        }
        paragraph = " ".join(life_record_overview(fake))
        self.assertIn("Pat Sample", paragraph)
        self.assertNotIn("James Beveridge", paragraph)
        self.assertNotIn("father", paragraph)
        self.assertNotIn("spouse", paragraph)
        self.assertNotIn("January 1", paragraph)
        # In the reviewed database Mercy has genuinely unknown parents.
        mercy = self.people["mercy_beveridge_henry_1753"]
        self.assertFalse(mercy.get("parents"))
        self.assertNotIn("Jean White", " ".join(life_record_overview(mercy)))

    def test_inherited_1749_marriage_event_is_not_claimed_as_confirmed(self):
        james = self.people["james_beveridge_jr_1724"]
        ids = {item["id"]: item for item in profile_milestones(james, self.data["events"])}
        historic = ids["event_marriage_james_jr_jean_white_1749"]
        self.assertIn("intention", historic["title"].lower())
        self.assertIn("unverified", historic["title"].lower())
        self.assertIn("marriage intention", historic["status"].lower())
        self.assertEqual(historic["url"], "?page=timeline&event=event_marriage_james_jr_jean_white_1749")

    def test_book_photo_gallery_uses_only_explicit_identity_crosswalk(self):
        photo_pages = {int(photo["pdf_page"]) for photo in self.photos}
        self.assertEqual(len(photo_pages), len(self.photos))
        self.assertGreaterEqual(len(self.book["linked_people"]), 20)
        links = {int(r["page"]) for r in linked_book_illustrations(
            "lowell_pierson_beveridge_jr_1930", self.photos, self.book)}
        father = {int(r["page"]) for r in linked_book_illustrations(
            "lowell_beveridge_1905", self.photos, self.book)}
        self.assertIn(57, links)
        self.assertNotIn(57, father)
        self.assertIn(246, father)
        self.assertNotIn(246, links)
        self.assertEqual(linked_book_illustrations("not-a-real-profile", self.photos, self.book), [])
        for person in self.book["linked_people"]:
            for photo in linked_book_illustrations(person["person_id"], self.photos, self.book):
                self.assertIn(photo["page"], photo_pages)
                self.assertEqual(photo["url"], "?page=family-books&book_page=" + str(photo["page"]))
                self.assertEqual(len(photo["crop"]), 4)
                self.assertIn("attributed", photo["attribution"])

    def test_unknown_dates_are_not_replaced_with_made_up_timelines(self):
        person = {"id": "unknown", "full_name": "Unknown Person",
                  "birth_place": None, "birth_date": None, "death_date": None,
                  "parents": ["unverified"], "children": []}
        self.assertEqual(life_record_overview(person), [])
        self.assertEqual(profile_milestones(person, []), [])

if __name__ == "__main__":
    unittest.main()
