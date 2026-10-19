"""Site-wide visitor journeys remain reachable, personalized and evidence-safe."""
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from app import NAV_GROUPS, PAGE_SLUGS
from visitor_journeys import JOURNEYS, current_person, recent_people, suggested_paths, visit_person
from family_data import index_people, load_site_data, relationship_index
from full_tree import build_full_tree_html
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class VisitorJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.people=index_people(load_site_data(ROOT/"data")["people"])

    def test_all_real_sections_offer_three_distinct_valid_routes(self):
        known=set(PAGE_SLUGS.values())
        for page in JOURNEYS:
            self.assertIn(page, PAGE_SLUGS)
            choices=suggested_paths(page)
            self.assertEqual(len(choices),3)
            urls=[url for _,url in choices]
            self.assertEqual(len(set(urls)),3,page)
            for label,url in choices:
                self.assertTrue(label)
                parsed=urlsplit(url)
                self.assertEqual(parsed.path,"")
                self.assertEqual(parsed.scheme,"")
                target=parse_qs(parsed.query)["page"][0]
                self.assertIn(target,known)
                self.assertNotEqual(page, next(k for k,v in PAGE_SLUGS.items() if v==target))

    def test_exact_selected_identity_drives_shareable_profile_and_tree_links(self):
        pid="mercy_beveridge_henry_1753"
        person=suggested_paths("Explore the Tree",pid)
        self.assertEqual(person[0][1],"?page=people&profile="+pid)
        target=suggested_paths("People",pid)
        self.assertEqual(target[0][1],"?page=tree&profile="+pid)
        route=suggested_paths("Full Family Map",pid)[0][1]
        self.assertEqual(route,"?page=tree&profile="+pid)
        self.assertEqual(suggested_paths("Full Family Map",pid)[1][1],
                         "?page=people&profile="+pid)
        self.assertIn("profile="+pid,suggested_paths("Timeline",pid)[0][1])

    def test_recent_visits_use_only_ephemeral_valid_profile_ids(self):
        fake=SimpleNamespace(session_state={},query_params={})
        with patch("visitor_journeys.st",fake):
            ids=list(self.people)[:9]
            for pid in ids:
                visit_person(pid,self.people)
            self.assertEqual(recent_people(self.people),list(reversed(ids[-5:])))
            visit_person(ids[-3],self.people)
            self.assertEqual(recent_people(self.people)[0],ids[-3])
            self.assertEqual(len(recent_people(self.people)),5)
            visit_person("unknown-person",self.people)
            self.assertEqual(len(recent_people(self.people)),5)
            fake.query_params={"profile":ids[-2]}
            self.assertEqual(current_person(self.people,"People"),ids[-2])
            # A direct tree permalink must take priority over an older visit.
            self.assertEqual(current_person(self.people,"Explore the Tree"),ids[-2])
            fake.query_params={}
            self.assertEqual(current_person(self.people,"Explore the Tree"),ids[-3])

    def test_full_tree_supports_search_keyboard_and_full_overview(self):
        data=load_site_data(ROOT/"data")
        html=build_full_tree_html(self.people,relationship_index(data["people"]))
        for text in ('id="personSearch"','id="personSuggestions"',
                     'id="searchPerson"','function searchPerson()',
                     'role="status"','g.setAttribute("tabindex", "0")',
                     'function centerSelected()'):
            self.assertIn(text,html)
        self.assertIn("Whole family overview",html)
        self.assertIn("Trace ancestors",html)
        self.assertIn("Trace descendants",html)

if __name__=="__main__":
    unittest.main()
