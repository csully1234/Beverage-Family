from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from family_data import index_people, load_site_data, relationship_index, shortest_relationship_path
from validation import validate_site_data


class VerifiedCollateralPhase2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relationships = relationship_index(cls.data["people"])

    def test_expansion_reaches_at_least_180_profiles(self):
        self.assertGreaterEqual(len(self.people), 180)

    def test_marblehead_sarah_bridge(self):
        sarah = self.people["sarah_beveridge_1727"]
        self.assertEqual(sarah["birth_date"], "1727-06-01")
        self.assertEqual(set(sarah["parents"]), {"james_beveridge_sr_1700", "sarah_bennett_1705"})

    def test_obsolete_child_ids_are_repaired(self):
        obsolete = {"thomas_beverage_1800", "sarah_beverage_1802", "abigail_beverage_1805"}
        for person in self.people.values():
            for field in ("parents", "siblings", "spouses", "children"):
                self.assertTrue(obsolete.isdisjoint(person.get(field, [])), (person["id"], field))

    def test_samuel_ruth_twelve_child_dates(self):
        expected = {
            "florence_mertice_beverage_1883": "1883-06-03",
            "chester_josiah_beverage_1884": "1884-09-25",
            "hiram_stone_beverage_1886": "1886-05-13",
            "albert_lewis_beverage_1888": "1888-11-12",
            "marston_leadbetter_beverage_1890": "1890-12-26",
            "olive_mary_beverage_1892": "1892-08-17",
            "nett_ie_ellen_beverage_1894": "1894-04-22",
            "elroy_victor_beverage_1896": "1896-03-05",
            "george_dewey_beverage_1898": "1898-02-28",
            "edith_etta_beverage_1900": "1900-05-12",
            "wilson_freemont_beverage_1902": "1902-03-23",
            "alma_marie_beverage_1905": "1905-10-02",
        }
        for pid, birth in expected.items():
            self.assertEqual(self.people[pid]["birth_date"], birth, pid)
            self.assertEqual(self.people[pid].get("birth_date_precision"), "exact", pid)

    def test_fremont_thurston_chain(self):
        path = shortest_relationship_path(self.relationships, "harold_h_beverage_1893", "carl_lyman_thurston_1910")
        self.assertTrue(path)
        self.assertIn("alida_beverage_thurston_1887", path)

    def test_elroy_branch_chain(self):
        cynthia = self.people["cynthia_e_libby_tuplin_1952"]
        self.assertEqual(set(cynthia["parents"]), {"malcolm_plummer_libby", "estelle_nettie_beverage_libby_1922"})
        path = shortest_relationship_path(self.relationships, "elroy_victor_beverage_1896", "cynthia_e_libby_tuplin_1952")
        self.assertTrue(path)
        self.assertIn("estelle_nettie_beverage_libby_1922", path)

    def test_helen_barclay_merolla_chain(self):
        norma = self.people["norma_helen_barclay_merolla"]
        self.assertEqual(set(norma["parents"]), {"robert_w_t_barclay", "helen_barclay_1896"})
        self.assertIn("amedeo_c_merolla_1929", norma["spouses"])

    def test_living_modern_descendants_not_profiled(self):
        withheld_names = {
            "barry_libby", "alan_libby", "dennis_libby", "douglas_libby",
            "hartley_g_beverage_jr", "kenneth_beverage_hartley_branch",
            "katherine_merolla", "julie_merolla", "sandra_merolla", "steven_merolla",
        }
        self.assertTrue(withheld_names.isdisjoint(self.people))

    def test_data_validator_still_has_no_blocking_errors(self):
        self.assertEqual(validate_site_data(self.data).errors, [])


if __name__ == "__main__":
    unittest.main()
