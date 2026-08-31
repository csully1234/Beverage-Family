from __future__ import annotations

import unittest
from pathlib import Path

from family_data import index_people, load_site_data, relationship_index


ROOT = Path(__file__).resolve().parents[1]

ADDED = {
    "julia_priscilla_miller_1888",
    "gerald_gibson_beverage_1914",
    "viola_joy_1914",
    "elston_albert_beverage_1916",
    "greta_morrison_1918",
    "john_miller_beverage_1927",
    "janet_kihlgren_beverage_1930",
    "raymond_albert_beverage",
    "sandra_beverage_snow",
    "michelle_beverage_campbell_1969",
    "jesse_ames_brown_1869",
    "marjorie_annette_brown_1912",
    "bernard_ray_mills_1903",
    "freda_rose_mills_smith_1930",
    "priscilla_jean_mills_dempsey_1932",
    "alden_ray_mills",
    "agnes_beverage_dailey_1935",
    "norwood_pierson_beveridge_jr_1936",
    "deborah_woodrow_beveridge_1935",
    "arthur_woodrow_beveridge_1943",
    "eldora_brown_beverage_alexander_1849",
    "everett_beverage_harrison_line",
}


class CollateralExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relationships = relationship_index(cls.data["people"])

    def test_all_verified_additions_load(self) -> None:
        self.assertTrue(ADDED.issubset(self.people))
        self.assertGreaterEqual(len(self.people), 159)

    def test_albert_lewis_branch_is_connected(self) -> None:
        self.assertIn(
            "julia_priscilla_miller_1888",
            self.relationships["spouses"]["albert_lewis_beverage_1888"],
        )
        for child in (
            "gerald_gibson_beverage_1914",
            "elston_albert_beverage_1916",
            "john_miller_beverage_1927",
        ):
            self.assertIn(child, self.relationships["children"]["albert_lewis_beverage_1888"])
            self.assertIn("albert_lewis_beverage_1888", self.relationships["parents"][child])

    def test_mills_branch_is_connected(self) -> None:
        for child in (
            "freda_rose_mills_smith_1930",
            "priscilla_jean_mills_dempsey_1932",
            "alden_ray_mills",
        ):
            self.assertIn(child, self.relationships["children"]["edith_etta_beverage_1900"])
            self.assertIn("edith_etta_beverage_1900", self.relationships["parents"][child])

    def test_norwood_branch_is_connected(self) -> None:
        for child in (
            "norwood_pierson_beveridge_jr_1936",
            "deborah_woodrow_beveridge_1935",
            "arthur_woodrow_beveridge_1943",
        ):
            self.assertIn(child, self.relationships["children"]["norwood_beveridge_1911"])

    def test_harrison_branch_is_conservative(self) -> None:
        everett = self.people["everett_beverage_harrison_line"]
        self.assertIsNone(everett.get("birth_date"))
        self.assertIsNone(everett.get("death_date"))
        self.assertEqual(
            set(everett["parents"]),
            {"harrison_beverage_1825", "eldora_brown_beverage_alexander_1849"},
        )

    def test_new_profiles_have_structured_source_urls(self) -> None:
        for person_id in ADDED:
            with self.subTest(person_id=person_id):
                sources = self.people[person_id].get("sources", [])
                structured = [
                    source
                    for source in sources
                    if isinstance(source, dict) and source.get("url")
                ]
                self.assertTrue(structured, person_id)
                self.assertTrue(all(source.get("evidence_level") for source in structured))

    def test_modern_obituary_descendants_are_not_added(self) -> None:
        deliberately_excluded = {
            "parker_joy_beverage",
            "clare_beverage_warner",
            "david_beverage_john_line",
            "peter_beverage_john_line",
            "raymond_m_beverage",
            "timothy_beverage_raymond_line",
            "judith_smith_fearing",
            "janice_smith_hopkins",
            "lynn_smith_peters",
        }
        self.assertTrue(deliberately_excluded.isdisjoint(self.people))


if __name__ == "__main__":
    unittest.main()
