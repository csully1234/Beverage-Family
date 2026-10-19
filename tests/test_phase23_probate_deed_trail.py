"""Phase 23: Matthew probate children, deed trail, and cautious transcriptions."""
from __future__ import annotations
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from family_data import index_people, load_site_data, relationship_index
from family_research_index import build_index, search_index
from matthew_deed_research import (load_probate_deed_trail,
                                   recorded_children, priority_deed_targets)
from waldo_probate import load_waldo_probate
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
FATHER = "matthew_beveridge_hope_1837"
WIDOW = "clarissa_beveridge_widow_1837"


class Phase23ProbateCourtChildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load_probate_deed_trail()
        cls.probate = load_waldo_probate()
        cls.data = load_site_data(ROOT/"data")
        cls.people = index_people(cls.data["people"])
        cls.children = recorded_children(cls.source)

    def test_explicit_court_child_order_is_stronger_than_generic_heirship(self):
        self.assertEqual(len(self.children), 8)
        self.assertEqual(self.source["relationship_basis"]["record_scan"], 9)
        self.assertEqual(self.source["relationship_basis"]["supporting_scan"], 31)
        self.assertEqual(self.source["relationship_basis"]["court_date"], "1837-10-06")
        self.assertEqual(self.source["relationship_basis"]["quotation"],
                         "to and among his children viz.")
        self.assertEqual(self.source["land_clues"][0]["id"], "hope-homestead")
        self.assertIn("biological mother", self.source["relationship_basis"]["reading_limit"])
        self.assertEqual(len({x["person_id"] for x in self.children}), 8)

    def test_canonical_family_tree_adds_only_proved_father_and_widow_links(self):
        father = self.people[FATHER]
        widow = self.people[WIDOW]
        self.assertEqual(father["parents"], [])
        self.assertEqual(father["death_date"], "1837-02-14")
        self.assertEqual(father["spouses"], [WIDOW])
        self.assertEqual(widow["spouses"], [FATHER])
        self.assertEqual(widow["parents"], [])
        self.assertEqual(widow["children"], [])
        expected = {p["person_id"] for p in self.children}
        self.assertEqual(set(father["children"]), expected)
        for child_id in expected:
            with self.subTest(child=child_id):
                child = self.people[child_id]
                self.assertEqual(child["parents"], [FATHER])
                self.assertEqual(child["birth_date"], None)
                self.assertIn("biological", child["notes"].lower())
                self.assertTrue(any("probate" in x.lower() for x in child["sources"]))
        self.assertFalse(self.people["nathaniel_beverage_1804_rockland"]["parents"])
        edges = relationship_index(self.data["people"])
        self.assertEqual(set(edges["children"][FATHER]), expected)
        self.assertEqual(validate_site_data(self.data).errors, [])

    def test_probate_record_still_one_source_family_not_fake_deed(self):
        self.assertEqual(len(self.probate["scans"]), 31)
        self.assertEqual(len(set(s["sha256"] for s in self.probate["scans"])), 30)
        self.assertFalse(self.probate.get("image_publication_authorized", False))
        self.assertIn("not", self.source["source_rights"].lower())
        self.assertEqual(len(priority_deed_targets()), 5)
        self.assertTrue(all("certainty" in x and x["scan"] == 2
                            for x in self.source["land_clues"]))
        self.assertTrue(all("NOT IDENTIFIED" in lead["proof_status"] or
                            "NOT CHECKED" in lead["proof_status"] or
                            "NOT A PARCEL" in lead["proof_status"] or
                            "NOT LOCATED" in lead["proof_status"] or
                            "NOT PROVED" in lead["proof_status"]
                            for lead in self.source["source_leads"]))
        self.assertEqual(len(self.source["transcriptions"]), 8)
        self.assertFalse(any(x["status"].lower().startswith("full diplomatic transcription")
                             for x in self.source["transcriptions"]))
        self.assertIn("NOT official", self.source["source"])

    def test_archive_search_has_person_linked_court_evidence_but_no_fabricated_sources(self):
        cards = build_index(self.people)
        child_cards = [r for r in cards if r["id"].startswith("waldo-court-child:")]
        deed_cards = [r for r in cards if r["id"].startswith("waldo-deed-lead:")]
        reading_cards = [r for r in cards if r["id"].startswith("waldo-reading:")]
        self.assertEqual((len(child_cards), len(deed_cards), len(reading_cards)), (8,5,8))
        self.assertTrue(all(FATHER in r["person_ids"] for r in child_cards))
        self.assertTrue(all(len(r["person_ids"]) == 2 for r in child_cards))
        for row in child_cards + deed_cards + reading_cards:
            parsed = parse_qs(urlsplit(row["route"]).query)
            self.assertEqual(parsed["page"], ["collection"])
            self.assertEqual(parsed["view"], ["waldo-probate"])
            self.assertTrue(parsed["scan"])
            self.assertFalse(row["sources"])
        self.assertTrue(search_index(cards, query="Nathaniel Alford"))
        self.assertTrue(search_index(cards, person_id=FATHER))
        self.assertTrue(any(r["id"].startswith("waldo-court-child:")
                            for r in search_index(cards, person_id=FATHER)))

if __name__ == "__main__":
    unittest.main()
