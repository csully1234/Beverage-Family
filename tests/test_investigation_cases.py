"""Evidence case-file regression tests: never invent ancestry or collapse identities."""
from __future__ import annotations

import unittest
from pathlib import Path

from evidence_explorer import (
    evidence_catalog, investigation_catalog, for_person, for_event,
    safe_document_url,
)
from family_data import index_people, load_site_data
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class InvestigationCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.events = {x["id"]: x for x in cls.data["events"]}
        cls.cases = investigation_catalog()
        cls.sources = {x["id"]: x for x in evidence_catalog()}

    def test_all_case_links_point_to_genuine_source_records(self):
        self.assertEqual(len(self.cases), 4)
        self.assertEqual(len({case["id"] for case in self.cases}), 4)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case.get("known"))
                self.assertTrue(case.get("unresolved"))
                self.assertTrue(case.get("next_records"))
                self.assertTrue(case.get("status"))
                self.assertTrue(case.get("source_ids"))
                for sid in case["source_ids"]:
                    self.assertIn(sid, self.sources)
                    self.assertTrue(safe_document_url(self.sources[sid]["url"]))
                for pid in case["person_ids"]:
                    self.assertIn(pid, self.people)
                for eid in case["event_ids"]:
                    self.assertIn(eid, self.events)

    def test_franks_must_not_be_merged_or_assigned_unverified_1939_death(self):
        frank = self.people["frank_beverage_1861"]
        self.assertEqual(frank["birth_date"], "1861-01-14")
        self.assertNotEqual(frank.get("death_date"), "1939-02-05")
        cemetery = self.sources["frank-thomaston-cemetery-1939"]
        self.assertEqual(cemetery["people_ids"], [])
        self.assertEqual(self.events["event_thomaston_frank_plot_card_1939"]["people_involved"], [])
        self.assertEqual(self.events["event_thomaston_frank_orra_notice_1911"]["people_involved"], [])
        self.assertEqual(self.events["event_frank_autograph_at_north_haven_1954"]["people_involved"], ["frank_beverage_1861"])
        self.assertIn("1954-07-19", self.events["event_frank_autograph_at_north_haven_1954"]["date"])
        self.assertTrue(any(x["id"] == "frank-north-haven-autograph-1954"
                            for x in for_person("frank_beverage_1861", list(self.sources.values()))))
        self.assertEqual(len(for_event("event_thomaston_frank_plot_card_1939",
                                       list(self.sources.values()))), 1)

    def test_marriage_date_is_an_inference_not_hardcoded_into_legacy_person(self):
        case = next(x for x in self.cases if x["id"] == "frank-beverage-two-men")
        self.assertTrue(any("1887" in x and "inference" in x for x in case["known"]))
        self.assertFalse(any("1887-10-15" == x.get("date") and
                             "frank_beverage_1861" in x.get("people_involved", [])
                             for x in self.data["events"]))

    def test_nathaniel_parentage_still_missing_in_real_genealogy(self):
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"], [])
        self.assertNotIn("nathaniel_winslow_beverage_1776",
                         self.people["nathaniel_beverage_1804_rockland"]["parents"])
        case = next(x for x in self.cases if x["id"] == "nathaniel-rockland-line")
        self.assertTrue(any("probate" in x.lower() for x in case["next_records"]))
        self.assertIn("1865-matthew-nathaniel", case["source_ids"])
        self.assertIn("eaton-original-scanned-volume-ii-pdf", case["source_ids"])

    def test_harrison_and_james_land_bounds_remain_unmodified(self):
        self.assertEqual(self.events["event_1888_harrison_mill_stream_dam_purchase"]["people_involved"], [])
        self.assertEqual(self.data["base_people"][0]["id"], "sarah_beverage_1999")
        self.assertFalse(any(x["id"].startswith("phase6_mapped_parcel") for x in self.data["places"]))
        self.assertEqual(validate_site_data(self.data).errors, [])

    def test_eaton_free_scan_is_not_a_paid_or_derived_site(self):
        source = self.sources["eaton-original-scanned-volume-ii-pdf"]
        self.assertEqual(source["association"], "reported_history")
        self.assertTrue(source["url"].startswith("https://archive.org/download/"))
        self.assertTrue(source["preview_pdf"])
        self.assertIn("not the original", source["limits"].lower())
        
if __name__ == "__main__":
    unittest.main()
