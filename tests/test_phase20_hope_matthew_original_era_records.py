"""Original-era municipal record trail; same historical ledger is one source family."""
from __future__ import annotations
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from family_data import load_site_data,index_people,relationship_index
from hope_matthew_civic import load_hope_civic_records,evidence_counts,record_for_id
from family_research_index import build_index,search_index
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]

class OriginalEraHopeClerkResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.hope=load_hope_civic_records()
        cls.records=cls.hope["records"]
        cls.stats=evidence_counts(cls.hope)

    def test_eight_separate_occurrences_two_underlying_source_families(self):
        self.assertEqual(self.stats["observations"],11)
        self.assertEqual(self.stats["ledger_entries"],10)
        self.assertEqual(self.stats["census_leads"],1)
        self.assertEqual(self.stats["distinct_source_families"],2)
        self.assertIn("ONE Hope town clerk ledger",self.hope["source_family_warning"])
        ids=[r["id"] for r in self.records]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len({r["date"] for r in self.records}),11)
        self.assertEqual(sorted(r["date"] for r in self.records),[r["date"] for r in self.records])
        self.assertIn("1806",self.records[0]["date"])
        self.assertIn("1827",self.records[-1]["date"])

    def test_original_ledger_transcription_not_overstated_as_original_autograph(self):
        for row in self.records:
            with self.subTest(id=row["id"]):
                self.assertEqual(record_for_id(row["id"],self.hope),row)
                self.assertTrue(row["claim"] and row["limit"] and row["verification"])
                self.assertTrue(row["source_page"] and row["source_title"])
                self.assertEqual(urlsplit(row["source_url"]).scheme,"https")
                self.assertTrue(urlsplit(row["source_url"]).hostname)
                self.assertIn("not",row["limit"].lower())
                self.assertIn(row["category"],{"town_clerk_transcription","census_index_secondary"})
        self.assertIsNone(record_for_id("missing",self.hope))
        self.assertIn("original",self.records[0]["limit"].lower())
        self.assertIn("NOT",self.records[3]["limit"])

    def test_census_index_does_not_pretend_original_sheet_was_seen(self):
        census=next(r for r in self.records if r["category"]=="census_index_secondary")
        self.assertIn("sheet 276",census["source_page"])
        self.assertIn("Mathew",census["claim"])
        self.assertIn("NOT",census["limit"])
        self.assertIn("not examined",census["verification"])
        self.assertIn("1820",census["date"])

    def test_1827_waldo_jurisdiction_not_a_claim_of_household_migration(self):
        august=record_for_id("hope-1827-aug-clerk",self.hope)
        self.assertIn("Waldo County",august["town"])
        self.assertIn("not be treated as evidence the family moved",august["limit"])
        prior=record_for_id("hope-1821-may-clerk",self.hope)
        self.assertIn("Lincoln County",prior["town"])
        final=record_for_id("hope-1827-dec-clerk",self.hope)
        self.assertIn("does not mean Matthew was elected",final["limit"])

    def test_original_state_county_history_distinguishes_boundary_change_from_migration(self):
        meta=self.hope["jurisdiction_context"]
        self.assertEqual(meta["dates"],["1827-07-03","1860-04-01"])
        self.assertIn("Lincoln County",meta["finding"])
        self.assertIn("Waldo County",meta["finding"])
        self.assertIn("Knox County",meta["finding"])
        self.assertIn("not a Matthew personal migration",meta["limit"])
        self.assertEqual(urlsplit(meta["url"]).scheme,"https")
        self.assertIn("legislative",meta["source"].lower())

    def test_originals_are_still_targets_not_fake_verified_proof(self):
        targets=self.hope["original_retrieval"]
        self.assertGreaterEqual(len(targets),4)
        self.assertTrue(all(x["status"]=="not_obtained" for x in targets))
        for t in targets:
            self.assertEqual(urlsplit(t["url"]).scheme,"https")
            self.assertTrue(t["instructions"])
        self.assertTrue(any("probate" in t["target"].lower() for t in targets))
        self.assertTrue(any("census" in t["target"].lower() for t in targets))

    def test_site_index_exposes_every_event_with_no_fabricated_person_links(self):
        all_records=build_index(self.people)
        cards=[r for r in all_records if r["id"].startswith("hope-clerk:")]
        self.assertEqual(len(cards),11)
        self.assertEqual(len({r["id"] for r in cards}),11)
        self.assertTrue(all(not r["person_ids"] for r in cards))
        self.assertTrue(all(r["route"]=="?page=collection&view=hope-matthew" for r in cards))
        self.assertTrue(all(r["sources"] for r in cards))
        search=search_index(all_records,query="Matthew Hope clerk")
        self.assertTrue(any(x["id"].startswith("hope-clerk:") for x in search))
        self.assertFalse(any(r["category"]=="Scanned book OCR leads" for r in cards))
        for row in cards:
            self.assertEqual(parse_qs(urlsplit(row["route"]).query)["view"][0],"hope-matthew")

    def test_genealogy_remains_unchanged_and_unknown_parentage_is_not_filled(self):
        self.assertEqual(validate_site_data(self.data).errors,[])
        self.assertNotIn("capt_matthew_beverage",self.people)
        for pid in ("nathaniel_beverage_1804_rockland",
                    "mercy_beveridge_henry_1753",
                    "lyford_beveridge_brother_lowell"):
            self.assertFalse(self.people[pid]["parents"])
        self.assertFalse(relationship_index(self.data["people"])["parents"].get(
            "nathaniel_beverage_1804_rockland"))

if __name__=="__main__":
    unittest.main()
