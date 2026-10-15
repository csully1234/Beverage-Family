"""Visitor-facing experience invariants. No archival claims are inferred by sorting."""
import unittest

from visitor_ui import _year, order_people, surname_first_label, approved_assets, DOCUMENTS, STORIES


class VisitorExperienceTests(unittest.TestCase):
    def setUp(self):
        self.people = [
            {"id": "z", "full_name": "Alice Beverage", "birth_date": "1900"},
            {"id": "a", "full_name": "Zoe Adams", "birth_date": "1750"},
            {"id": "u", "full_name": "Brian Beverage", "birth_date": ""},
            {"id": "c", "full_name": "Ben Carver", "birth_date": "1840"},
        ]

    def test_default_surname_order(self):
        self.assertEqual([p["id"] for p in order_people(self.people)], ["a", "z", "u", "c"])

    def test_year_disambiguators_do_not_sort_as_surnames(self):
        records = [
            {"id": "john", "full_name": "John White (1748)"},
            {"id": "sarah", "full_name": "Sarah Beverage (1802)"},
            {"id": "thomas", "full_name": "Thomas Beverage (1800)"},
            {"id": "james", "full_name": "James Beveridge Jr."},
            {"id": "betsy", "full_name": "Betsy Swiniarski (Beverage)"},
        ]
        actual = [p["id"] for p in order_people(records)]
        self.assertEqual(actual, ["sarah", "thomas", "james", "betsy", "john"])
        self.assertEqual(surname_first_label(records[0]), "White, John (1748)")
        self.assertEqual(surname_first_label(records[2]), "Beverage, Thomas (1800)")
        self.assertEqual(surname_first_label(records[3]), "Beveridge, James Jr.")

    def test_surname_sort_does_not_depend_on_birth_date(self):
        records = [
            {"id": "old", "full_name": "John White (1748)", "birth_date": "1748"},
            {"id": "young", "full_name": "Thomas Beverage (1800)", "birth_date": "1800"},
        ]
        self.assertEqual([p["id"] for p in order_people(records)], ["young", "old"])
        self.assertEqual([p["id"] for p in order_people(records, "Birth year (oldest first)")], ["old", "young"])

    def test_first_name_order(self):
        self.assertEqual([p["id"] for p in order_people(self.people, "First name A–Z")], ["z", "c", "u", "a"])

    def test_oldest_first_unknown_last(self):
        self.assertEqual([p["id"] for p in order_people(self.people, "Birth year (oldest first)")], ["a", "c", "z", "u"])

    def test_newest_first_unknown_last(self):
        self.assertEqual([p["id"] for p in order_people(self.people, "Birth year (newest first)")], ["z", "c", "a", "u"])

    def test_approximate_year_is_not_invented(self):
        self.assertEqual(_year("circa 1917"), 1917)
        self.assertIsNone(_year("Undated"))

    def test_stories_have_distinct_destinations(self):
        self.assertEqual(len({s["id"] for s in STORIES}), len(STORIES))
        self.assertIn("thomas-1786", DOCUMENTS)

    def test_no_unapproved_local_images_are_published(self):
        for asset in approved_assets().values():
            self.assertIn(asset["rights_status"], ("permission", "public_domain"))
            self.assertIn("/approved_media/", asset["path"])


if __name__ == "__main__":
    unittest.main()
