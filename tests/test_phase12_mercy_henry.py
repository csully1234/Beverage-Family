"""A sourced Mercy Beveridge gravestone record is not a fabricated parentage link."""
from __future__ import annotations
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from family_data import index_people, load_site_data
from research_collection import CollectionIndex
from mercy_henry_sources import load_mercy_henry_sources
from unified_timeline import build_chronology
from validation import validate_site_data
from historical_claims import reviewed_event_presentation

ROOT=Path(__file__).resolve().parents[1]


class MercyHenrySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site=load_site_data(ROOT/"data")
        cls.people=index_people(cls.site["people"])
        cls.cases=load_mercy_henry_sources()

    def test_two_sources_have_provenance_and_separate_certainty(self):
        self.assertEqual(len(self.cases),2)
        self.assertEqual([c["year"] for c in self.cases],[1776,1831])
        by_id={c["id"]:c for c in self.cases}
        marriage=by_id["topsham-mercy-marriage-candidate-1776"]
        death=by_id["topsham-mercy-henry-1831"]
        self.assertIn("probable",marriage["status"].lower()) if "probable" in marriage["status"].lower() else self.assertIn("probably",marriage["status"].lower())
        self.assertEqual(marriage["timeline_inclusion"],False)
        self.assertEqual(death["date"],"1831-10-26")
        self.assertTrue(death["timeline_inclusion"])
        self.assertIn("same gravestone", death["summary"].lower())
        self.assertIn("1930",death["source_title"])
        for case in self.cases:
            self.assertIn("not", case["limits"].lower())
            self.assertTrue(case["next_record"])
            self.assertEqual(urlsplit(case["source_url"]).scheme,"https")
            self.assertGreaterEqual(len(case["supporting_sources"]),2)

    def test_mercy_death_in_full_chronology_not_an_assumed_person(self):
        rows=build_chronology(self.site,self.people,CollectionIndex.load())
        matches=[x for x in rows if x["id"]=="mercy-henry:topsham-mercy-henry-1831"]
        self.assertEqual(len(matches),1)
        entry=matches[0]
        self.assertEqual(entry["type"],"Historical document")
        self.assertEqual(entry["date"],"1831-10-26")
        self.assertEqual(entry["year"],1831)
        self.assertEqual(entry["person_ids"],())
        self.assertIn("source",entry["extra"].lower())
        self.assertFalse(any(x["id"]=="mercy-henry:topsham-mercy-marriage-candidate-1776" for x in rows))

    def test_unverified_mercy_parentage_and_placeholder_spouse_are_corrected(self):
        mercy=self.people["mercy_beveridge_henry_1753"]
        husband=self.people["henry_henry_1750"]
        self.assertEqual(mercy["parents"],[])
        self.assertEqual(mercy["siblings"],[])
        self.assertEqual(mercy["death_date"],"1831-10-26")
        self.assertEqual(mercy["death_date_precision"],"exact")
        self.assertIsNone(mercy["death_place"])
        self.assertIsNone(mercy["birth_place"])
        self.assertEqual(mercy["birth_date_precision"],"approximate")
        self.assertEqual(husband["full_name"],"James Henry (Mercy's husband, died 1831)")
        self.assertEqual(husband["death_date"],"1831-11-02")
        self.assertIsNone(husband["birth_date"])
        self.assertIn("henry_henry_1750",mercy["spouses"])
        self.assertIn("mercy_beveridge_henry_1753",husband["spouses"])
        for pid in ("james_beveridge_jr_1724", "jean_mckinney_white_1725"):
            self.assertNotIn(mercy["id"],self.people[pid]["children"])
        self.assertNotIn(mercy["id"],self.people["thomas_beverage_1750"]["siblings"])
        self.assertEqual(validate_site_data(self.site).errors,[])

    def test_original_archive_is_preserved_for_reopening_the_claim(self):
        raw={p["id"]:p for p in self.site["base_people"]}
        self.assertEqual(raw["mercy_beveridge_henry_1753"]["parents"],
                         ["james_beveridge_jr_1724","jean_mckinney_white_1725"])
        self.assertEqual(raw["henry_henry_1750"]["full_name"],"Henry Henry")
        self.assertNotEqual(raw["mercy_beveridge_henry_1753"]["death_date"],
                            self.people["mercy_beveridge_henry_1753"]["death_date"])
        self.assertIn("same gravestone",
                      next(c for c in self.cases if c["year"]==1831)["summary"].lower())

    def test_original_birth_event_displays_source_limited_copy(self):
        original=next(e for e in self.site["events"]
                      if e["id"]=="event_birth_mercy_beveridge_henry_1753")
        public=reviewed_event_presentation(original)
        self.assertIn("parents unknown",public["title"])
        self.assertEqual(public["date"],"1753")
        self.assertEqual(public["date_precision"],"approximate")
        self.assertNotIn("daughter of James",public["description"])
        self.assertIn("daughter of James",original["description"])

if __name__=="__main__":
    unittest.main()
