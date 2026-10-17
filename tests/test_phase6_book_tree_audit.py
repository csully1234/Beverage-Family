"""Resolved PR #26: exact book identities, novel relatives, no invented family links."""
from __future__ import annotations
import unittest
from pathlib import Path
from family_data import index_people, load_site_data, relationship_index
from family_books import book_pages_for_person, load_book_person_crosswalk
from full_tree import build_full_tree_model
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]

class ReconciledBookTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = load_site_data(ROOT / "data")
        cls.people = index_people(cls.site["people"])
        cls.links = relationship_index(cls.site["people"])
        cls.crosswalk = load_book_person_crosswalk()

    def test_main_lowell_family_ids_are_canonical_not_duplicated(self):
        self.assertEqual(len(self.site["phase7_people"]), 4)
        self.assertEqual(len(self.site["phase6_people"]), 2)
        for obsolete_id in (
            "lowell_pierson_beveridge_jr_author",
            "ida_louise_gattrell_beveridge",
            "hortense_tee_sie_beveridge",
        ):
            self.assertNotIn(obsolete_id, self.people)
        junior = self.people["lowell_pierson_beveridge_jr_1930"]
        self.assertEqual(set(junior["parents"]), {
            "lowell_beveridge_1905",
            "ida_louisa_gattrell_beveridge_1901",
        })

    def test_sibling_only_link_never_creates_unknown_parent(self):
        lyford = self.people["lyford_beveridge_brother_lowell"]
        self.assertEqual(lyford["parents"], [])
        self.assertIn("lowell_beveridge_1905", self.links["siblings"][lyford["id"]])
        tree = build_full_tree_model(self.people, self.links)
        expected = sorted((lyford["id"], "lowell_beveridge_1905"))
        self.assertIn(expected, tree["sibling_only_edges"])
        self.assertEqual(tree["positions"][lyford["id"]][1],
                         tree["positions"]["lowell_beveridge_1905"][1])
        self.assertNotIn(["lowell_beveridge_1905", lyford["id"]], tree["parent_edges"])

    def test_dorothy_is_a_documented_wife_with_unidentified_parents(self):
        dorothy = self.people["dorothy_jimmy_gattrell_beverage"]
        self.assertEqual(dorothy["parents"], [])
        self.assertIn("elliot_beverage_1908", self.links["spouses"][dorothy["id"]])

    def test_all_book_photo_links_have_actual_profiles(self):
        indexed = self.crosswalk["linked_people"]
        self.assertEqual(len(indexed), 23)
        self.assertTrue(all(item["person_id"] in self.people for item in indexed))
        self.assertGreaterEqual(len(self.crosswalk["unresolved_people"]), 16)
        self.assertIn(57, book_pages_for_person("lowell_pierson_beveridge_jr_1930", self.crosswalk))
        self.assertNotIn(57, book_pages_for_person("lowell_beveridge_1905", self.crosswalk))
        self.assertIn(246, book_pages_for_person("lowell_beveridge_1905", self.crosswalk))
        self.assertNotIn(246, book_pages_for_person("lowell_pierson_beveridge_jr_1930", self.crosswalk))

    def test_site_still_passes_integrity_validation(self):
        self.assertEqual(validate_site_data(self.site).errors, [])

if __name__ == "__main__":
    unittest.main()
