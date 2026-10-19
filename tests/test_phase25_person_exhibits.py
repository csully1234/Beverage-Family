"""Phase 25: visitor-friendly person exhibits never manufacture source identities."""
from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from family_data import index_people, load_site_data, relationship_index
from family_exhibits import (SECTIONS, exhibit_route, exhibit_research_rows,
                             exhibit_overview)
from family_research_index import build_index
from profile_life_stories import linked_book_illustrations, profile_milestones
from visitor_journeys import current_person, suggested_paths
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
MATTHEW = "matthew_beveridge_hope_1837"
CLARISSA = "clarissa_beveridge_widow_1837"


class PersonExhibitExperienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.index = build_index(cls.people)
        cls.relations = relationship_index(cls.data["people"])

    def test_permalinks_have_exact_person_ids_and_supported_sections(self):
        for pid in (MATTHEW, CLARISSA, "lowell_pierson_beveridge_jr_1930"):
            route = parse_qs(urlsplit(exhibit_route(pid)).query)
            self.assertEqual(route, {"page": ["collection"],
                                     "view": ["person-exhibit"], "person": [pid]})
            for section in SECTIONS:
                deep = parse_qs(urlsplit(exhibit_route(pid, section)).query)
                self.assertEqual(deep["person"], [pid])
                self.assertEqual(deep["section"], [section])
                self.assertEqual(deep["view"], ["person-exhibit"])
        self.assertNotIn("section=", exhibit_route(MATTHEW, "invented-tab"))

    def test_exhibit_merges_timeline_and_source_attribution_but_not_name_hits(self):
        matthew = self.people[MATTHEW]
        view = exhibit_overview(matthew, self.data["events"], self.index)
        self.assertEqual(view["id"], MATTHEW)
        self.assertEqual(view["milestones"],
                         profile_milestones(matthew, self.data["events"]))
        self.assertTrue(view["research"])
        self.assertTrue(any("probate" in r["title"].lower() or
                            "Matthew" in r["title"]
                            for r in view["research"]))
        self.assertTrue(all(MATTHEW in r["person_ids"] for r in view["research"]))
        self.assertTrue(all(r["category"] not in {"Existing family profiles",
                                                  "Scanned book OCR leads"}
                            for r in view["research"]))
        self.assertEqual(len(view["research"]),
                         len({r["id"] for r in view["research"]}))
        self.assertLessEqual(view["linked_citations"], len(view["citations"]))
        self.assertLessEqual(view["linked_research"], len(view["research"]))

    def test_no_invented_identity_when_name_occurs_in_nonlinked_record(self):
        fake_rows = [
            {"id":"one", "category":"Historical investigations",
             "person_ids":[MATTHEW], "title":"Matthew's court evidence"},
            {"id":"two", "category":"Historical investigations",
             "person_ids":[CLARISSA], "title":"Matthew mentioned by name"},
            {"id":"three", "category":"Scanned book OCR leads",
             "person_ids":[MATTHEW], "title":"OCR word match"},
            {"id":"four", "category":"Existing family profiles",
             "person_ids":[MATTHEW], "title":"Self profile"},
            {"id":"five", "category":"Relationship evidence",
             "person_ids":[MATTHEW, CLARISSA], "title":"Parentage question"},
        ]
        found = exhibit_research_rows(MATTHEW, fake_rows)
        self.assertEqual({r["id"] for r in found}, {"one", "five"})

    def test_separate_people_with_same_surname_have_distinct_book_images(self):
        father = "lowell_beveridge_1905"
        son = "lowell_pierson_beveridge_jr_1930"
        self.assertIn(246, {item["page"] for item in linked_book_illustrations(father)})
        self.assertNotIn(246, {item["page"] for item in linked_book_illustrations(son)})
        self.assertIn(57, {item["page"] for item in linked_book_illustrations(son)})
        self.assertNotIn(57, {item["page"] for item in linked_book_illustrations(father)})

    def test_exhibit_navigation_persists_correct_relative_from_query(self):
        fake = SimpleNamespace(
            query_params={"page":"collection", "view":"person-exhibit",
                          "person": MATTHEW},
            session_state={"_active_person":CLARISSA, "tree_person":CLARISSA}
        )
        with patch("visitor_journeys.st", fake):
            self.assertEqual(current_person(self.people, "Historical Discoveries"), MATTHEW)
            fake.query_params["person"] = "unrelated_nonexistent_person"
            self.assertEqual(current_person(self.people, "Historical Discoveries"), CLARISSA)
        choices = suggested_paths("Historical Discoveries", MATTHEW)
        self.assertIn("profile=" + MATTHEW, choices[0][1])
        self.assertIn("profile=" + MATTHEW, choices[1][1])

    def test_no_original_image_or_new_genealogy_records_are_written(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        self.assertEqual(self.people[MATTHEW]["parents"], [])
        self.assertEqual(self.people[CLARISSA]["children"], [])
        self.assertEqual(set(self.relations["parents"][CLARISSA]),
                         {"barnabas_cobb_clarissa_father", "jerusha_cobb_clarissa_mother"})
        self.assertNotIn("nonexistent", self.people)


if __name__ == "__main__":
    unittest.main()
