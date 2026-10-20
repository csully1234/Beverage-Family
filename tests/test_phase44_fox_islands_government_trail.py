"""Phase 44: three historical source families, no premature identity bridges."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from family_data import load_site_data,index_people,relationship_index
from genealogy_integrity import connected_components
from family_research_index import build_index
from fox_islands_government_trail import (
    load_government_trail,trail_for_candidate,trail_route,trail_counts,trail_csv
)
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]


class Phase44FoxIslandsGovernmentTrailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trail=load_government_trail()
        cls.rows=cls.trail["records"]
        cls.sources={s["id"]:s for s in cls.trail["sources"]}
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.relationships=relationship_index(cls.data["people"])

    def test_all_eight_source_observations_and_three_independent_publication_families(self):
        stats=trail_counts(self.trail)
        self.assertEqual(stats,{
            "source_families":3,
            "research_observations":8,
            "retrospective_meeting_mentions":3,
            "1820_census_head_names":4,
            "federal_ocr_mentions":1,
            "original_manuscripts_inspected":0,
            "confirmed_profile_identity_links":0,
        })
        self.assertEqual(len({row["id"] for row in self.rows}),8)
        self.assertEqual({s["source_family"] for s in self.sources.values()},{
            "1889-vinalhaven-historical-sketch",
            "2019-transcribed-1820-head-index",
            "federal-register-scanned-text-single-edition",
        })
        self.assertTrue(all(not s["original_manuscript_read"] for s in self.sources.values()))

    def test_1785_1788_1789_clerk_records_are_one_retrospective_source(self):
        meetings=[r for r in self.rows if r["source_id"]=="vinalhaven-1889-narrative"]
        self.assertEqual([r["date_label"] for r in meetings],[
            "March 11, 1785","October 28, 1788","March 1789 (day not reported)"
        ])
        self.assertTrue(all(r["printed_name"]=="Thomas Beverage" for r in meetings))
        self.assertEqual({r["page"] for r in meetings},{"printed page 11","printed page 12"})
        self.assertEqual({r["source_id"] for r in meetings},{"vinalhaven-1889-narrative"})
        self.assertTrue(all(r["identity_status"]=="printed_name_only_unassigned" for r in meetings))

    def test_1820_transcription_names_four_heads_but_no_household_member_claims(self):
        census=[r for r in self.rows if r["source_id"]=="vinalhaven-1820-index"]
        self.assertEqual({r["printed_name"] for r in census},{
            "John Beverage","Thomas Beverage","Nathaniel Beverage","Benjamin Beverage"
        })
        self.assertTrue(all(r["identity_status"]=="indexed_head_not_original_confirmed" for r in census))
        self.assertTrue(all("exact line and sheet unknown" in r["page"] for r in census))
        self.assertEqual(len([r for r in self.rows if r["printed_name"]=="John Beverage"]),2)
        self.assertEqual(trail_for_candidate("nonexistent",self.trail),[])

    def test_federal_customs_name_stays_office_and_publication_date_unresolved(self):
        fed=self.rows[-1]
        self.assertEqual(fed["id"],"register-1827-1829-john")
        self.assertEqual(fed["printed_name"],"John Beverage")
        self.assertIn("1827 OR 1829",fed["date_label"])
        self.assertIn("unresolved",fed["date_label"])
        self.assertIn("1829",self.sources[fed["source_id"]]["limits"])
        self.assertEqual(fed["identity_status"],
                         "OCR_office_name_unassigned_publication_year_inconsistent")
        self.assertTrue("Inspector" in fed["details"] or "inspector" in fed["details"])
        with TemporaryDirectory() as td:
            original=json.loads((ROOT/"data"/"phase44_fox_islands_government_census_crosswalk.json").read_text())
            original[0]["records"][-1]["date_label"]="1827 CONFIRMED"
            p=Path(td)/"bad.json"
            p.write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError,"Disputed"):
                load_government_trail(p)

    def test_person_profile_comparison_is_not_a_sourced_person_event(self):
        john=trail_for_candidate("john_white_beverage_1774",self.trail)
        self.assertEqual({r["id"] for r in john},{
            "census-1820-john","register-1827-1829-john"
        })
        thomas=trail_for_candidate("thomas_beverage_1750",self.trail)
        self.assertEqual(len(thomas),4)
        before=connected_components(self.people,self.relationships)
        self.assertEqual(len(before),4)
        self.assertEqual(len(self.people),202)
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"],[])
        self.assertEqual(self.people["josiah_b_beverage_1821"]["parents"],[
            "josiah_winslow_beverage_1793","mary_dyer_1795"
        ])
        self.assertEqual(connected_components(self.people,self.relationships),before)
        self.assertEqual(validate_site_data(self.data).errors,[])

    def test_all_eight_records_in_visitor_search_with_no_assumed_person_ids(self):
        indexed=build_index(self.people)
        rows=[r for r in indexed if r["id"].startswith("island-document:")]
        self.assertEqual(len(rows),8)
        self.assertTrue(all(r["category"]=="Historical record trails" for r in rows))
        self.assertTrue(all(r["person_ids"]==[] for r in rows))
        self.assertTrue(all("community_record=" in r["route"] for r in rows))
        self.assertTrue(all(r["sources"] and r["limits"] for r in rows))
        self.assertIn("community_record=meeting-1785-thomas",
                      trail_route("meeting-1785-thomas"))
        self.assertIn("community=1",trail_route())

    def test_csv_complete_and_publication_metadata_validated(self):
        with io.StringIO(trail_csv(self.trail)) as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),8)
        self.assertEqual(rows[0]["id"],"meeting-1785-thomas")
        self.assertEqual(rows[-1]["id"],"register-1827-1829-john")
        with TemporaryDirectory() as td:
            original=json.loads((ROOT/"data"/"phase44_fox_islands_government_census_crosswalk.json").read_text())
            original[0]["sources"][1]["original_manuscript_read"]=True
            p=Path(td)/"bad.json";p.write_text(json.dumps(original))
            with self.assertRaises(ValueError):
                load_government_trail(p)

    def test_password_and_all_historical_site_assets_remain_accessible(self):
        app=(ROOT/"app.py").read_text()
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD",app)
        self.assertIn("Fox Islands early government, 1820 census",app)
        self.assertIn("render_fox_islands_government_trail(",
                      (ROOT/"primary_source_expedition.py").read_text())
        self.assertIn("trail_for_candidate(person_id)",
                      (ROOT/"family_exhibits.py").read_text())


if __name__=="__main__":
    unittest.main()
