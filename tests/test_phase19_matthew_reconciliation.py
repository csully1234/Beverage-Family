"""Correct prior Matthew ambiguity using the actual 1865 first/second wife paragraph."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import urlsplit

from family_data import index_people, load_site_data, relationship_index
from matthew_reconciliation import load_matthew_reconciliation, marriage_groups
from ancestry_bridge_casework import load_ancestry_bridge_dossiers
from colony_source_review import reviews_for_book_page
from family_research_index import build_index, search_index
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]


class MatthewFirstSecondWivesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases,cls.family=load_matthew_reconciliation()
        cls.by_id={case["id"]:case for case in cls.cases}
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])

    def test_1865_eaton_explicit_one_captain_two_wives_and_ten_named_children(self):
        groups=marriage_groups(self.family)
        self.assertEqual([g["wife"] for g in groups],["Abigail Dyer","Clarissa Cobb"])
        self.assertEqual([g["number"] for g in groups],[1,2])
        self.assertEqual([len(g["children"]) for g in groups],[5,5])
        self.assertEqual(len(self.family["matthew"]["children"]),10)
        self.assertEqual(len({p["name"] for g in groups for p in g["children"]}),10)
        self.assertIn("two groups of five",self.by_id["eaton-1865-two-marriages"]["claim"].lower())
        self.assertTrue(all("original" in g["limitation"] for g in groups))

    def test_publications_support_marriage_order_but_not_original_proof(self):
        self.assertEqual(len(self.by_id),6)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["title"] and case["claim"] and case["proof"])
                self.assertTrue(case["reference"] and case["locator"])
                self.assertGreaterEqual(len(case["next_originals"]),2)
                self.assertTrue(all(item.strip() for item in case["next_originals"]))
                self.assertTrue(all(pid in self.people for pid in case["person_ids"]))
                if case.get("url"):
                    url=urlsplit(case["url"])
                    self.assertEqual(url.scheme,"https")
                    self.assertTrue(url.hostname)
        book=self.by_id["colony-2016-abigail-1801"]
        self.assertEqual(book["book_page"],17)
        self.assertIn("compatible",book["claim"])
        self.assertIn("not uniquely identify",book["proof"])
        self.assertIn("marriage entry",self.by_id["eaton-1865-two-marriages"]["next_originals"][0].lower())

    def test_previous_book_and_casework_now_agree_without_proving_same_person(self):
        page=[x for x in reviews_for_book_page(17) if "first and second wives" in x["title"]]
        self.assertEqual(len(page),1)
        self.assertIn("Abigail Dyer first and Clarissa Cobb second",page[0]["observation"])
        self.assertIn("identity",page[0]["why_it_matters"].lower())
        case=next(x for x in load_ancestry_bridge_dossiers() if x["id"]=="matthew-clarissa-cobb-1851-1865")
        self.assertIn("FIRST",case["finding"])
        self.assertIn("SECOND",case["finding"])
        self.assertIn("SAME AUTHOR",case["limitations"])
        self.assertNotIn("two different Matthews",case["finding"])

    def test_explicit_probate_path_makes_no_unfounded_estate_claim(self):
        finding=self.by_id["probate-pre1860-waldo-index"]
        self.assertIn("Waldo County",finding["claim"])
        self.assertIn("not evidence that a probate packet",finding["proof"])
        self.assertIn("Waldo County",finding["locator"])
        self.assertIn("1826",finding["reference"])
        self.assertGreaterEqual(len(finding["supporting_links"]),3)
        for link in finding["supporting_links"]:
            self.assertEqual(urlsplit(link["url"]).scheme,"https")
        self.assertIn("index",finding["next_originals"][0].lower())

    def test_full_workbench_index_links_reconciliation_to_source_not_genealogy_mutation(self):
        records=build_index(self.people)
        related=[x for x in records if x["id"].startswith("matthew:")]
        self.assertEqual(len(related),6)
        self.assertTrue(all(x["route"]=="?page=collection&view=matthew" for x in related))
        self.assertIn(17,next(x for x in related if x["id"]=="matthew:colony-2016-abigail-1801")["pages"])
        self.assertTrue(search_index(records,query="Clarissa Cobb"))
        self.assertFalse(self.people["nathaniel_beverage_1804_rockland"]["parents"])
        self.assertNotIn("capt_matthew_beverage",self.people)
        self.assertEqual(validate_site_data(self.data).errors,[])
        self.assertFalse(relationship_index(self.data["people"])["parents"].get("nathaniel_beverage_1804_rockland"))

if __name__=="__main__":
    unittest.main()
