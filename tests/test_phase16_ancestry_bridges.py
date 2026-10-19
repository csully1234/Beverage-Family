"""Historic bridge dossiers link sources, not unproven family members."""
import unittest
from urllib.parse import urlsplit
from family_data import index_people, load_site_data, relationship_index
from ancestry_bridge_casework import STATUS, load_ancestry_bridge_dossiers, linked_dossiers
from relationship_evidence import review_lookup, edge_key
from validation import validate_site_data
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class AncestryBridgeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.relationships=relationship_index(cls.data["people"])
        cls.cases=load_ancestry_bridge_dossiers()
        cls.by_id={x["id"]: x for x in cls.cases}

    def test_all_four_investigations_are_source_specific(self):
        self.assertEqual(len(self.cases),4)
        self.assertEqual(len(self.by_id),4)
        for x in self.cases:
            with self.subTest(id=x["id"]):
                self.assertIn(x["status"], STATUS)
                self.assertTrue(x["finding"] and x["limitations"])
                self.assertGreaterEqual(len(x["next_originals"]),2)
                for p in x["person_ids"]:
                    self.assertIn(p,self.people)
                for src in x["sources"]:
                    self.assertEqual(urlsplit(src["url"]).scheme,"https")
                    self.assertTrue(urlsplit(src["url"]).hostname)
                    self.assertTrue(src["title"] and src["locator"] and src["claim"])

    def test_new_clarissa_cobb_wife_report_has_two_dependent_books(self):
        x=self.by_id["matthew-clarissa-cobb-1851-1865"]
        self.assertIn("Clarissa Cobb",x["named_people"])
        self.assertIn("Captain Barnabas Cobb",x["named_people"])
        self.assertIn("SAME AUTHOR",x["limitations"])
        self.assertIn("not independent original marriage returns",x["limitations"])
        self.assertIn("1851",x["sources"][0]["title"])
        self.assertIn("1865",x["sources"][1]["title"])
        self.assertFalse(x["person_ids"])

    def test_uncle_report_does_not_add_parents(self):
        x=self.by_id["nathaniel-and-sarah-nephew-niece-1865"]
        self.assertIn("nephew of Capt. Matthew",x["finding"])
        self.assertIn("niece of the same captain",x["finding"])
        self.assertIn("not to Nathaniel",x["limitations"])
        self.assertEqual(set(x["person_ids"]),{
          "nathaniel_beverage_1804_rockland","sarah_alexander_beverage_1808"})
        for pid in x["person_ids"]:
            self.assertFalse(self.people[pid]["parents"])
        self.assertNotIn("capt_matthew_beverage",self.people)

    def test_manuscript_map_77_not_claimed_as_beveridge_property(self):
        x=self.by_id["topsham-maps-1760-1764"]
        self.assertIn("Map 77",x["finding"])
        self.assertIn("Map 40",x["finding"])
        self.assertIn("NOT identified a Beveridge label",x["limitations"])
        self.assertIn("james_beveridge_jr_1724",x["person_ids"])

    def test_correct_one_existing_nathaniel_sarah_spouse_link(self):
        key=edge_key("spouses","nathaniel_beverage_1804_rockland",
                     "sarah_alexander_beverage_1808")
        reviews=review_lookup()
        self.assertEqual(len(reviews),23)
        self.assertEqual(reviews[key]["status"],"published_record")
        self.assertIn("not the original marriage",reviews[key]["limitations"])
        self.assertFalse(self.relationships["parents"].get("nathaniel_beverage_1804_rockland"))
        self.assertEqual(validate_site_data(self.data).errors,[])

    def test_exact_profile_case_connections(self):
        self.assertEqual(len(linked_dossiers("nathaniel_beverage_1804_rockland",self.cases)),2)
        self.assertEqual(len(linked_dossiers("sarah_alexander_beverage_1808",self.cases)),1)
        self.assertEqual(len(linked_dossiers("james_beveridge_jr_1724",self.cases)),1)
        self.assertEqual(linked_dossiers("not-real",self.cases),[])

if __name__ == "__main__":
    unittest.main()
