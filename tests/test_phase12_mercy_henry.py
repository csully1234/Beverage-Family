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

    def test_no_unverified_mercy_parentage_or_duplicates_added_to_people(self):
        self.assertNotIn("mercy_beveridge_henry_1753",self.people)
        self.assertNotIn("james_henry_jr_1743",self.people)
        self.assertEqual(validate_site_data(self.site).errors,[])
        # The cemetery-index origin is explicit, not called two independent witnesses.
        self.assertIn("same", next(c for c in self.cases if c["year"]==1831)["summary"].lower())

if __name__=="__main__":
    unittest.main()
