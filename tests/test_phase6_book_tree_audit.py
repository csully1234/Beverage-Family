"""Source-backed Phase 6: complete identities for Lowell's branch and photo-page crosswalk."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from family_books import book_pages_for_person, load_book_person_crosswalk
from family_data import load_site_data, index_people, relationship_index
from full_tree import build_full_tree_model
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase6TreeAndBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.index = load_book_person_crosswalk()
        cls.captions = json.loads((ROOT / "data/colony_photo_captions.json").read_text())[0]["photos"]
        cls.events = {event["id"]: event for event in cls.data["events"]}

    def test_lowell_author_is_separate_from_father_and_has_supported_parents(self):
        father = self.people["lowell_beveridge_1905"]
        author = self.people["lowell_pierson_beveridge_jr_author"]
        mother = self.people["ida_louise_gattrell_beveridge"]
        self.assertNotEqual(author["id"], father["id"])
        self.assertEqual(set(author["parents"]), {father["id"], mother["id"]})
        self.assertIn(author["id"], father["children"])
        self.assertIn(author["id"], mother["children"])
        self.assertIn(mother["id"], father["spouses"])
        self.assertIn("2012", str(author["sources"]))
        self.assertEqual(author["death_date"], None)

    def test_wife_and_children_link_to_existing_verified_branch(self):
        relationships = relationship_index(self.data["people"])
        author = "lowell_pierson_beveridge_jr_author"
        tee = "hortense_tee_sie_beveridge"
        self.assertIn(tee, relationships["spouses"][author])
        self.assertIn(author, relationships["spouses"][tee])
        self.assertIn("thomas_gattrell_beveridge_1938", relationships["siblings"][author])
        self.assertEqual(self.people["lyford_beveridge_brother_lowell"]["parents"], [])
        self.assertIn("lyford_beveridge_brother_lowell",
                      relationships["siblings"]["lowell_beveridge_1905"])
        self.assertEqual(self.people["hortense_tee_sie_beveridge"]["death_date"], "1993")

    def test_family_photo_1954_marriage_2012_interview_have_attributed_events(self):
        marriage = self.events["event_pete_hortense_marriage_1954"]
        self.assertEqual(marriage["date"], "1954")
        self.assertEqual(marriage["date_precision"], "year")
        self.assertEqual(set(marriage["people_involved"]), {
            "lowell_pierson_beveridge_jr_author", "hortense_tee_sie_beveridge"
        })
        self.assertIn("not in 1953", marriage["description"])
        recollection = self.events["event_pete_brooklyn_oral_history_2012"]
        self.assertEqual(recollection["date"], "2012-05-23")
        self.assertIn("not proof", recollection["description"].lower())

    def test_book_crosswalk_honors_exact_profiles_and_82_page_scope(self):
        known_pages = {p["pdf_page"] for p in self.captions}
        self.assertEqual(len(known_pages), 82)
        self.assertEqual(self.index["scope"]["book_total_pages"], 305)
        self.assertEqual(self.index["scope"]["captioned_photo_pages"], 82)
        self.assertIn("NOT", self.index["scope"]["limitation"].upper())
        self.assertGreaterEqual(len(self.index["linked_people"]), 20)
        self.assertGreaterEqual(len(self.index["unresolved_people"]), 15)
        for person in self.index["linked_people"]:
            self.assertIn(person["person_id"], self.people)
            self.assertTrue(set(person["pdf_pages"]) <= known_pages)
        self.assertNotIn("samuel_hiram_beverage_1917",
                         {x["person_id"] for x in self.index["linked_people"]})

    def test_2016_portrait_pages_map_to_right_lowells(self):
        author = "lowell_pierson_beveridge_jr_author"
        father = "lowell_beveridge_1905"
        self.assertIn(57, book_pages_for_person(author, self.index))
        self.assertNotIn(57, book_pages_for_person(father, self.index))
        self.assertIn(246, book_pages_for_person(father, self.index))
        self.assertNotIn(246, book_pages_for_person(author, self.index))
        self.assertIn(248, book_pages_for_person("ida_louise_gattrell_beveridge", self.index))
        self.assertIn(257, book_pages_for_person("dorothy_jimmy_gattrell_beverage", self.index))

    def test_book_candidate_names_are_not_silent_new_father_links(self):
        unresolved = " ".join(x["name"] for x in self.index["unresolved_people"])
        for name in ("Hanson", "Florence Budlong", "Priscilla", "Ruth and Ann"):
            self.assertIn(name, unresolved)
        self.assertFalse(self.people["lyford_beveridge_brother_lowell"]["parents"])
        # Do not confuse Hanson Beverage's 1840s nickname with another
        # genealogical profile solely on matching initials.
        self.assertNotIn("Hanson", self.people["dana_hanson_beverage_1847"].get("alternate_names", []))

    def test_book_named_dorothy_tied_to_eliot_but_other_marriages_not_fabricated(self):
        dorothy = self.people["dorothy_jimmy_gattrell_beverage"]
        self.assertEqual(dorothy["parents"], [])
        self.assertIn("elliot_beverage_1908", dorothy["spouses"])
        self.assertIn(dorothy["id"], relationship_index(self.data["people"])["spouses"]["elliot_beverage_1908"])
        # Married-surname annotations do not invent an unidentified spouse.
        self.assertEqual(self.people["mary_beverage_1869"]["spouses"], [])
        self.assertEqual(self.people["jemima_beverage_1866"]["spouses"], [])
        self.assertEqual(self.people["harriet_beverage_1856"]["spouses"], [])

    def test_sibling_only_relation_is_visible_without_inferred_parents(self):
        relationships = relationship_index(self.data["people"])
        model = build_full_tree_model(self.people, relationships)
        lowell = "lowell_beveridge_1905"
        lyford = "lyford_beveridge_brother_lowell"
        pair = sorted([lowell, lyford])
        self.assertIn(pair, model["sibling_edges"])
        self.assertIn(pair, model["sibling_only_edges"])
        self.assertFalse(self.people[lyford]["parents"])
        self.assertNotIn([lowell, lyford], model["parent_edges"])
        self.assertNotIn([lyford, lowell], model["parent_edges"])
        self.assertEqual(model["positions"][lowell][1], model["positions"][lyford][1])

    def test_full_tree_includes_added_sourced_profiles_without_base_mutation(self):
        rel = relationship_index(self.data["people"])
        model = build_full_tree_model(self.people, rel)
        nodes = {node["id"] for node in model["nodes"]}
        for name in ("lowell_pierson_beveridge_jr_author", "thomas_gattrell_beveridge_1938",
                     "lyford_beveridge_brother_lowell", "dorothy_jimmy_gattrell_beverage"):
            self.assertIn(name, nodes)
        self.assertIn(["lowell_beveridge_1905", "lowell_pierson_beveridge_jr_author"],
                      model["parent_edges"])
        self.assertIn(["ida_louise_gattrell_beveridge", "lowell_pierson_beveridge_jr_author"],
                      model["parent_edges"])
        self.assertEqual(validate_site_data(self.data).errors, [])


if __name__ == "__main__":
    unittest.main()
