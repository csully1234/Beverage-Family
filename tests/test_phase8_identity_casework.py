"""Evidence display must never silently mutate canonical genealogical records."""
from __future__ import annotations
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from family_data import index_people, load_site_data, relationship_index
from family_books import book_page_connections
from identity_casework import cases_for_page, cases_for_profile, load_identity_cases
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class HistoricalIdentityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_identity_cases()
        cls.site = load_site_data(ROOT / "data")
        cls.people = index_people(cls.site["people"])
        cls.rel = relationship_index(cls.site["people"])

    def test_source_evidence_catalog_stable_and_all_links_usable(self):
        self.assertEqual(len(self.catalog), 8)
        self.assertEqual(len({row["id"] for row in self.catalog}), len(self.catalog))
        for item in self.catalog:
            self.assertTrue(item["name"])
            self.assertTrue(item["status"])
            self.assertTrue(item["known"])
            self.assertTrue(item["limits"])
            self.assertTrue(item["next_originals"])
            for page in item["book_pages"]:
                self.assertIsInstance(page, int)
                self.assertGreaterEqual(page, 1)
                self.assertLessEqual(page, 305)
            for source in item["sources"]:
                self.assertTrue(source["proves"])
                uri = urlsplit(source["url"])
                self.assertEqual(uri.scheme, "https")
                self.assertTrue(uri.hostname)

    def test_case_lookup_by_existing_stable_person_id_only(self):
        lowell = cases_for_profile("lowell_beveridge_1905")
        self.assertEqual(lowell, [])
        lyford = cases_for_profile("lyford_beveridge_brother_lowell")
        self.assertEqual([r["id"] for r in lyford], ["lyford-ruth-ann"])
        self.assertEqual(cases_for_profile("Lyford Pierson Beveridge"), [])
        self.assertTrue(cases_for_profile("arnold_beveridge_1903"))
        for row in self.catalog:
            if row.get("tree_profile_id"):
                self.assertIn(row["tree_profile_id"], self.people)

    def test_book_page_has_source_context_not_false_identity(self):
        cases = [r["id"] for r in cases_for_page(298)]
        self.assertIn("arnold-marion", cases)
        self.assertIn("eliot-dorothy", cases)
        self.assertIn("vernon-household", cases)
        self.assertFalse(cases_for_page(400))
        book = book_page_connections(298)
        self.assertTrue(isinstance(book["linked"], list))
        self.assertTrue(isinstance(book["unresolved"], list))
        self.assertEqual(cases_for_profile("vernon_linwood_beverage_1890"), [])

    def test_no_invented_parentage_spouses_or_old_genealogy_changes(self):
        self.assertEqual(validate_site_data(self.site).errors, [])
        self.assertEqual(self.people["lyford_beveridge_brother_lowell"]["parents"], [])
        self.assertEqual(self.people["arnold_beveridge_1903"].get("spouses", []), [])
        self.assertNotIn("marion_priscilla_delano", self.people)
        self.assertNotIn("florence_budlong", self.people)
        self.assertIn("elliot_beverage_1908",
                      self.rel["spouses"]["dorothy_jimmy_gattrell_beverage"])
        self.assertNotIn("ruth_bingham_reynolds", self.people)

    def test_family_memories_remain_distinct_from_primary_document(self):
        by_id = {item["id"]: item for item in self.catalog}
        self.assertIn("not", by_id["james-georgetown"]["limits"].lower())
        self.assertIn("not", by_id["matthew-nathaniel"]["limits"].lower())
        self.assertTrue(any(src["kind"] == "derivative_compilation"
                            for src in by_id["lyford-ruth-ann"]["sources"]))


if __name__ == "__main__":
    unittest.main()
