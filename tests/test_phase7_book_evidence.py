"""Research-first page navigation without inferred ancestral links."""
from pathlib import Path
import unittest
from family_books import book_page_connections, load_book_person_crosswalk, load_book_ocr_navigation
from family_data import load_site_data, index_people
from full_tree import build_full_tree_html
from family_associations import associations_for_person

ROOT = Path(__file__).resolve().parents[1]


class BookConnectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_book_person_crosswalk()
        cls.people = index_people(load_site_data(ROOT / "data")["people"])

    def test_page_links_exact_not_name_guesses(self):
        page = book_page_connections(49, self.catalog)
        self.assertTrue(any(row["person_id"] == "amelia_beverage_1833" for row in page["linked"]))
        self.assertTrue(any("Hanson" in row["name"] for row in page["unresolved"]))
        self.assertEqual(book_page_connections(305, self.catalog)["linked"], [])

    def test_casework_keeps_distinct_1923_photo_and_2016_author(self):
        self.assertTrue(any(row["person_id"] == "lowell_beveridge_1905"
                            for row in book_page_connections(246)["linked"]))
        self.assertFalse(any(row["person_id"] == "lowell_pierson_beveridge_jr_1930"
                             for row in book_page_connections(246)["linked"]))

    def test_newspaper_and_city_directory_do_not_forge_spouse_edges(self):
        cases = {row["name"]: row for row in self.catalog["unresolved_people"]}
        florence = cases["Florence Budlong"]
        self.assertEqual(len(florence["independent_sources"]), 2)
        self.assertIn("marriage", florence["issue"])
        self.assertIn("olive_beveridge_1890", self.people)
        self.assertNotIn("florence_budlong", self.people)
        self.assertIn("Hanson Beverage (Amelia's brother)", cases)
        self.assertEqual(len(cases), 16)

    def test_companion_not_labeled_legal_spouse_or_added_to_tree(self):
        associations = associations_for_person("olive_beveridge_1890")
        self.assertEqual(len(associations), 1)
        first = associations[0]
        self.assertEqual(first["associated_name"], "Florence N. Budlong")
        self.assertIn("Life partner", first["association_type"])
        self.assertEqual(len(first["sources"]), 3)
        self.assertNotIn("florence_budlong", self.people)
        self.assertFalse("florence_budlong" in self.people["olive_beveridge_1890"].get("spouses", []))

    def test_all_305_pages_indexed_for_navigation_not_identity_assertion(self):
        index = load_book_ocr_navigation()
        self.assertEqual(index["scanned_pages"], 305)
        self.assertGreaterEqual(len(index["hits"]), 30)
        self.assertIn(297, index["hits"]["Florence"])
        self.assertIn(298, index["hits"]["Priscilla"])
        self.assertIn(302, index["hits"]["Gattrell"])
        self.assertIn("OCR", index["verification"])
        for term, pages in index["hits"].items():
            self.assertTrue(term.strip())
            self.assertTrue(all(isinstance(p, int) and 1 <= p <= 305 for p in pages))
            self.assertEqual(pages, sorted(set(pages)))

    def test_appendix_name_leads_do_not_create_new_parentage(self):
        cases = {entry["name"]: entry for entry in self.catalog["unresolved_people"]}
        self.assertIn(298, cases["Vernon Beverage"]["pages"])
        self.assertIn("Marion Priscilla Delano", cases["Priscilla (Arnold's wife)"]["issue"])
        self.assertIn("Ruth Bingham Reynolds", cases["Ruth and Ann (Lyford family)"]["issue"])
        self.assertEqual(self.people["lyford_beveridge_brother_lowell"]["parents"], [])
        self.assertEqual(len(self.catalog["unresolved_people"]), 16)

    def test_tree_has_directional_modes_without_changing_relationship_data(self):
        from family_data import relationship_index
        data = load_site_data(ROOT / "data")
        html = build_full_tree_html(index_people(data["people"]), relationship_index(data["people"]))
        for marker in ("Trace ancestors", "Trace descendants",
                       "All documented generations", "function lineage(",
                       "parentsByChild", "childrenByParent"):
            self.assertIn(marker, html)


if __name__ == "__main__":
    unittest.main()
