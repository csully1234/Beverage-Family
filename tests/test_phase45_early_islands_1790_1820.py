"""Phase 45: surname-correct 1790 household and 1820 original reel, zero invented family links."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from early_fox_island_atlas import (
    load_early_islands,atlas_stats,source_atlas_for_candidate,
    early_islands_route,source_atlas_csv,
)
from family_data import load_site_data,index_people,relationship_index
from genealogy_integrity import connected_components
from family_research_index import build_index
from validation import validate_site_data

ROOT=Path(__file__).resolve().parents[1]


class Phase45EarlyFoxIslandsCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas=load_early_islands()
        cls.people=index_people(load_site_data(ROOT/"data")["people"])
        cls.all_data=load_site_data(ROOT/"data")
        cls.relationships=relationship_index(cls.all_data["people"])

    def test_1790_printed_name_exact_household_fields_and_total(self):
        row=self.atlas["census_1790"]
        self.assertEqual(row["person_name_as_printed"],"Thomas Beverege")
        self.assertEqual(row["printed_page"],32)
        self.assertEqual((row["adult_males_16_plus_including_head"],
                          row["males_under_16"],
                          row["free_white_females_all_ages"],
                          row["all_other_free_persons"],
                          row["enslaved_persons"]), (2,4,5,0,0))
        self.assertEqual(row["total_people"],11)
        self.assertFalse(row["original_handwritten_scheduled_inspected"])
        self.assertFalse(row["head_matches_canonical_profile"])
        self.assertEqual(atlas_stats(self.atlas)["household_size"],11)

    def test_1820_original_M33_roll_34_reel_found_not_handwritten_rows_read(self):
        reel=self.atlas["original_1820"]
        self.assertEqual((reel["nara_publication"],reel["roll"]),("M33",34))
        self.assertEqual(reel["archive_item"],"populationsc18200034unit")
        self.assertEqual(reel["archive_scanned_pages"],194)
        self.assertEqual((reel["manuscript_start"],reel["manuscript_end"]),(657,664))
        self.assertEqual(reel["known_head_names_from_modern_index"],[
            "John Beverage","Nathaniel Beverage","Thomas Beverage","Benjamin Beverage"
        ])
        self.assertTrue(reel["handwritten_heads_uninspected"])
        row=next(x for x in self.atlas["findings"] if x["id"]=="1820-m33-original-reel")
        self.assertIn("original",row["kind"])
        self.assertIn("do not",row["limits"].lower())

    def test_scholarly_Eames_research_not_automatically_assigned_to_Beverages(self):
        row=next(x for x in self.atlas["findings"] if x["id"]=="1769-eames-origins")
        self.assertEqual(row["name_as_printed"],"Ebenezer Eames")
        self.assertIn("58:29",row["manuscript_target"])
        self.assertEqual(row["profile_candidates"],[])
        source=next(x for x in self.atlas["sources"] if x["id"]=="scholar2025")
        self.assertIn("Barbara Beverage Reeves",source["title"])
        self.assertIn("Nov. 2025",source["title"])
        self.assertIn("copyrighted",source["limitations"])
        self.assertEqual(row["source_id"],"scholar2025")
        self.assertEqual(len(self.atlas["sources"]),6)
        self.assertTrue(self.atlas["no_copyrighted_journal_rehosting"])

    def test_1785_petition_and_1786_putnam_are_same_previously_catalogued_sources(self):
        rows={x["id"]:x for x in self.atlas["findings"]}
        self.assertEqual(rows["1785-settlement-petition-context"]["kind"],
                         "source_context_existing_record_crossreference")
        self.assertEqual(rows["1786-putnam-context"]["kind"],
                         "source_context_existing_original_target")
        self.assertIn("Box 001",rows["1786-putnam-context"]["manuscript_target"])
        prior=(ROOT/"data"/"phase30_fox_islands_original_source_access.json").read_text()
        self.assertIn("fox-1786-putnam-settler-report",prior)
        self.assertTrue(self.atlas["no_tree_edits"])

    def test_same_name_thomas_is_only_a_research_comparison(self):
        candidates=source_atlas_for_candidate("thomas_beverage_1750",self.atlas)
        self.assertEqual([p["id"] for p in candidates],["1790-thomas-household"])
        self.assertEqual(source_atlas_for_candidate("john_white_beverage_1774",self.atlas),[])
        self.assertEqual(source_atlas_for_candidate("invented",self.atlas),[])
        self.assertEqual(len(connected_components(self.people,self.relationships)),4)
        self.assertEqual(len(self.people),202)
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"],[])
        self.assertEqual(validate_site_data(self.all_data).errors,[])

    def test_search_index_adds_only_four_unduplicated_context_records(self):
        records=build_index(self.people)
        entries=[x for x in records if x["id"].startswith("early-islands:")]
        self.assertEqual(len(entries),4)
        self.assertEqual({x["id"] for x in entries},{
            "early-islands:1769-eames-origins",
            "early-islands:1790-thomas-household",
            "early-islands:1800-migration-question",
            "early-islands:1820-m33-original-reel",
        })
        self.assertTrue(all(x["person_ids"]==[] for x in entries))
        self.assertTrue(all("island_find=" in x["route"] for x in entries))
        self.assertTrue(all(x["sources"] and x["limits"] for x in entries))

    def test_all_six_findings_downloadable_and_permalinked(self):
        self.assertEqual([x["year"] for x in self.atlas["findings"]],
                         [1769,1785,1786,1790,1800,1820])
        with io.StringIO(source_atlas_csv(self.atlas)) as text:
            out=list(csv.DictReader(text))
        self.assertEqual(len(out),6)
        self.assertTrue(all(x["source_url"].startswith("https://") for x in out))
        self.assertTrue(all(x["manuscript_target"] for x in out))
        self.assertEqual(early_islands_route(),"?page=collection&view=source-expedition&early-islands=1")
        self.assertIn("island_find=1790-thomas-household",
                      early_islands_route("1790-thomas-household"))

    def test_provenance_guard_rejects_fabricated_1790_persons_and_1820_tallies(self):
        with TemporaryDirectory() as td:
            original=json.loads((ROOT/"data"/"phase45_early_island_census_settlement_context.json").read_text())
            original[0]["census_1790"]["total_people"]=12
            file=Path(td)/"bad.json";file.write_text(json.dumps(original))
            with self.assertRaises(ValueError):
                load_early_islands(file)
            original[0]["census_1790"]["total_people"]=11
            original[0]["original_1820"]["handwritten_heads_uninspected"]=False
            file.write_text(json.dumps(original))
            with self.assertRaises(ValueError):
                load_early_islands(file)

    def test_family_password_and_home_discovery_stay_intact(self):
        app=(ROOT/"app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD",app)
        self.assertIn("1790 Beverege household and original 1820 census",app)
        self.assertIn("render_early_island_atlas(",(ROOT/"primary_source_expedition.py").read_text())
        self.assertIn("source_atlas_for_candidate(person_id)",(ROOT/"family_exhibits.py").read_text())


if __name__=="__main__":
    unittest.main()
