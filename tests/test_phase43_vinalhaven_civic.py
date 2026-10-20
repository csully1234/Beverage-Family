"""Phase 43: 1889 sourced Vinalhaven civic service without surname-based identity merges."""
from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from family_data import load_site_data, index_people, relationship_index
from genealogy_integrity import connected_components
from family_research_index import build_index
from vinalhaven_civic_history import (load_civic_roster,civic_summary,
    candidate_age_status,civic_for_candidate,civic_route,civic_csv)
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase43VinalhavenCivicHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster=load_civic_roster()
        cls.rows=cls.roster["records"]
        cls.data=load_site_data(ROOT/"data")
        cls.people=index_people(cls.data["people"])
        cls.links=relationship_index(cls.data["people"])

    def test_exhaustive_printed_surname_entries_are_precisely_dated_and_sourced(self):
        stats=civic_summary(self.roster)
        self.assertEqual(stats["annual_entries"],55)
        self.assertEqual(stats["distinct_years"],41)
        self.assertEqual(stats["printed_names"],6)
        self.assertEqual(stats["first_year"],1790)
        self.assertEqual(stats["last_year"],1846)
        self.assertEqual(stats["independent_source_families"],1)
        self.assertEqual(stats["offices"],{
            "Selectman":25, "Town clerk":23,"Town treasurer":7
        })
        self.assertEqual({r["printed_page"] for r in self.rows},{35,36,37,38,39})
        self.assertEqual(len({r["id"] for r in self.rows}),55)
        self.assertTrue(all(not r["original_municipal_minute_inspected"] for r in self.rows))
        self.assertTrue(all(r["identity_status"]=="printed_name_only_not_individual_identified"
                            for r in self.rows))

    def test_1889_printed_names_not_given_specific_person_identity(self):
        names={r["printed_name"] for r in self.rows}
        self.assertEqual(names,{
            "Thomas Beverage","John Beverage","Benjamin Beverage",
            "Nathaniel Beverage","James Beverage","Josiah Beverage"
        })
        self.assertTrue(all("person_id" not in r for r in self.rows))
        self.assertTrue(all(r["candidate_person_ids"] for r in self.rows))
        self.assertTrue(all(all(pid in self.people for pid in r["candidate_person_ids"])
                            for r in self.rows))
        # A printed name like John Beverage doesn't prove which John.
        self.assertEqual({r["year"] for r in self.rows
                          if r["printed_name"]=="John Beverage"
                          and r["office"]=="Town clerk"},set(range(1799,1813)))

    def test_excludes_infant_nathaniel_but_not_unproven_adult_candidate(self):
        record=next(r for r in self.rows if r["year"]==1812 and
                    r["printed_name"]=="Nathaniel Beverage")
        outcomes={c["id"]:c for c in candidate_age_status(record,self.people)}
        self.assertEqual(outcomes["nathaniel_beverage_1804_rockland"]["status"],
                         "excluded_by_youth")
        self.assertEqual(outcomes["nathaniel_winslow_beverage_1776"]["status"],
                         "chronologically_possible_only")
        self.assertNotIn("confirmed", outcomes["nathaniel_winslow_beverage_1776"]["status"])
        both_josiah=next(r for r in self.rows if r["year"]==1846 and
                         r["printed_name"]=="Josiah Beverage")
        possible=candidate_age_status(both_josiah,self.people)
        self.assertEqual(len(possible),2)
        self.assertTrue(all(p["status"]=="chronologically_possible_only"
                            for p in possible))

    def test_printed_multiple_offices_not_deduplicated_as_people(self):
        both=[r for r in self.rows if r["year"]==1818 and
              r["printed_name"]=="Nathaniel Beverage"]
        self.assertEqual({r["office"] for r in both},
                         {"Town treasurer","Selectman"})
        same_year=[r for r in self.rows if r["year"]==1810]
        self.assertEqual({r["printed_name"] for r in same_year},
                         {"John Beverage","Thomas Beverage","Benjamin Beverage"})

    def test_civic_profile_links_are_only_candidate_search_not_family_events(self):
        candidates=civic_for_candidate("josiah_b_beverage_1821",self.roster)
        self.assertTrue(any(r["year"]==1846 for r in candidates))
        self.assertEqual(civic_for_candidate("not_a_person",self.roster),[])
        self.assertEqual(civic_route()," ?page=collection&view=source-expedition&civic=1".strip())
        self.assertIn("officer=Josiah%20Beverage",civic_route("Josiah Beverage",1846))
        self.assertIn("office_year=1846",civic_route("Josiah Beverage",1846))
        before=connected_components(self.people,self.links)
        self.assertEqual(len(before),4)
        self.assertEqual(self.people["nathaniel_beverage_1804_rockland"]["parents"],[])
        self.assertEqual(self.people["josiah_b_beverage_1821"]["parents"],
                         ["josiah_winslow_beverage_1793","mary_dyer_1795"])
        self.assertEqual(connected_components(self.people,self.links),before)
        self.assertEqual(validate_site_data(self.data).errors,[])

    def test_all_fifty_five_entries_searchable_without_unsupported_person_attribution(self):
        all_records=build_index(self.people)
        civic=[r for r in all_records if r["id"].startswith("vinalhaven-civic:")]
        self.assertEqual(len(civic),55)
        self.assertEqual({r["source_date"] for r in civic},
                         {str(row["year"]) for row in self.rows})
        self.assertTrue(all(r["category"]=="Historical record trails"
                            for r in civic))
        self.assertTrue(all(r["person_ids"]==[] for r in civic))
        self.assertTrue(all("office_year=" in r["route"] and "officer=" in r["route"]
                            for r in civic))
        self.assertTrue(all("1889" in r["limits"] for r in civic))

    def test_full_55_record_export_and_source_guard(self):
        with io.StringIO(civic_csv(self.rows)) as content:
            reader=list(csv.DictReader(content))
        self.assertEqual(len(reader),55)
        self.assertEqual(reader[0]["year"],"1790")
        self.assertEqual(reader[-1]["year"],"1846")
        with tempfile.TemporaryDirectory() as td:
            obj=json.loads((ROOT/"data"/"phase43_vinalhaven_civic_officers.json").read_text())
            obj[0]["records"][0]["original_municipal_minute_inspected"]=True
            p=Path(td)/"tampered.json"
            p.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                load_civic_roster(p)

    def test_existing_family_login_and_book_remain_unchanged(self):
        app=(ROOT/"app.py").read_text()
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD",app)
        self.assertIn("1790–1846 Vinalhaven Beverage town officers",app)
        self.assertIn("civic_for_candidate(person_id)",
                      (ROOT/"family_exhibits.py").read_text())
        self.assertIn("render_vinalhaven_civic(",
                      (ROOT/"primary_source_expedition.py").read_text())


if __name__=="__main__":
    unittest.main()
