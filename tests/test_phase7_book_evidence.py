"""Research-first page navigation without inferred ancestral links."""
from pathlib import Path
import unittest
from family_books import book_page_connections, load_book_person_crosswalk
from family_data import load_site_data, index_people
from full_tree import build_full_tree_html

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
