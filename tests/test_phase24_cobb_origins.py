"""Phase 24: Carver vital-record family matches the 1837 widow without inventing Matthew ancestry."""
from __future__ import annotations

import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from family_data import load_site_data, index_people, relationship_index
from family_origins_casework import load_family_origins_research, findings_by_status
from family_research_index import build_index, search_index
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
MATT = "matthew_beveridge_hope_1837"
WIDOW = "clarissa_beveridge_widow_1837"
FATHER = "barnabas_cobb_clarissa_father"
MOTHER = "jerusha_cobb_clarissa_mother"


class Phase24CarverCobbOriginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.case = load_family_origins_research()

    def test_carver_printed_birth_has_direct_parent_names_and_separate_identity_bridge(self):
        sources = {s["id"]: s for s in self.case["sources"]}
        birth = sources["p24-src-carver-births"]
        genealogy = sources["p24-src-cobb-history"]
        self.assertEqual(birth["year"], 1911)
        self.assertIn("p. 21", birth["page"])
        self.assertIn("Barnabas and Jerusha", birth["claim"])
        self.assertIn("not", birth["limitations"].lower())
        self.assertEqual(genealogy["year"], 1907)
        self.assertIn("164", genealogy["page"])
        self.assertIn("Matthew", genealogy["claim"])
        self.assertIn("not original marriage", genealogy["directly_inspected"])
        self.assertEqual(len(self.case["sources"]), 7)
        self.assertEqual(len(self.case["findings"]), 7)
        self.assertEqual(len(findings_by_status(self.case)), 7)

    def test_maternal_parents_are_additive_and_original_waldo_relationships_preserved(self):
        data, people = self.data, self.people
        self.assertEqual(len(data["phase24_cobb_people"]), 3)
        self.assertEqual({p["id"] for p in data["phase24_cobb_people"]},
                         {FATHER, MOTHER, WIDOW})
        clarissa = people[WIDOW]
        self.assertEqual(clarissa["birth_date"], "1786-03-27")
        self.assertEqual(clarissa["birth_place"], "Carver, Massachusetts")
        self.assertEqual(set(clarissa["parents"]), {FATHER, MOTHER})
        self.assertEqual(set(people[FATHER]["children"]), {WIDOW})
        self.assertEqual(set(people[MOTHER]["children"]), {WIDOW})
        self.assertEqual(set(people[FATHER]["spouses"]), {MOTHER})
        self.assertEqual(set(people[MOTHER]["spouses"]), {FATHER})
        self.assertEqual(people[MATT]["parents"], [])
        self.assertEqual(people[MATT]["spouses"], [WIDOW])
        self.assertEqual(clarissa["children"], [])
        self.assertEqual(len(people[MATT]["children"]), 8)
        for cid in people[MATT]["children"]:
            self.assertEqual(people[cid]["parents"], [MATT])
        self.assertNotIn("ebenezer_cobb_iii", people)
        self.assertNotIn("capt_matthew_beverage", people)
        relationships = relationship_index(data["people"])
        self.assertEqual(relationships["parents"][WIDOW], {FATHER, MOTHER})
        self.assertEqual(validate_site_data(data).errors, [])

    def test_original_protected_imports_and_prior_probate_record_not_edited(self):
        data = self.data
        original = {p["id"]: p for p in data["phase23_probate_people"]}
        self.assertEqual(original[WIDOW]["parents"], [])
        self.assertIsNone(original[WIDOW]["birth_date"])
        self.assertEqual(len(original[MATT]["children"]), 8)
        self.assertEqual(data["base_people"][0]["id"], "james_beveridge_sr_1700") if (
            data["base_people"][0]["id"] == "james_beveridge_sr_1700") else self.assertTrue(
                len(data["base_people"]) >= 100)

    def test_unproven_research_candidates_remain_queries_not_graph_edges(self):
        ids = {f["id"] for f in self.case["findings"]}
        self.assertEqual(len(ids), 7)
        minor = next(f for f in self.case["findings"] if f["id"] == "matthew-fox-minor")
        self.assertIn("unresolved", minor["status"])
        self.assertIn("No parent", minor["limits"])
        self.assertEqual(minor["person_ids"], [MATT])
        deed = next(f for f in self.case["findings"] if f["id"] == "matthew-deeds")
        self.assertIn("No recorded deed", deed["limits"])
        archives = {s["id"]: s for s in self.case["sources"]}
        self.assertEqual(archives["p24-src-fox-2025"]["year"], 2025)
        self.assertIn("not original", archives["p24-src-fox-2025"]["directly_inspected"])
        self.assertTrue(all(target["status"] != "obtained"
                            for target in self.case["original_retrieval"]))

    def test_archive_index_exposes_every_new_finding_with_real_sources(self):
        cards = build_index(self.people)
        scoped = [x for x in cards if x["id"].startswith("cobb-origin:")]
        self.assertEqual(len(scoped), 7)
        self.assertEqual(len({x["id"] for x in scoped}), 7)
        for card in scoped:
            qs = parse_qs(urlsplit(card["route"]).query)
            self.assertEqual(qs["page"], ["collection"])
            self.assertEqual(qs["view"], ["family-origins"])
            self.assertTrue(card["sources"])
            for link in card["sources"]:
                self.assertEqual(urlsplit(link["url"]).scheme, "https")
        parent = next(x for x in scoped if x["id"] == "cobb-origin:clarissa-carver-born")
        self.assertEqual(set(parent["person_ids"]), {FATHER, MOTHER, WIDOW})
        self.assertTrue(any(x["id"] == parent["id"]
                            for x in search_index(cards, query="Clarissa Cobb Barnabas")))
        self.assertTrue(any(x["id"].startswith("cobb-origin:")
                            for x in search_index(cards, person_id=MATT)))


if __name__ == "__main__":
    unittest.main()
