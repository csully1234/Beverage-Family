"""Phase 29: inspect the entire current family graph and true source-specific reviews.

The ledger is a coverage audit. It must not infer Matthew's parents or merge
same-name historical identities simply to reduce disconnected components.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path
import unittest

from family_data import load_site_data, index_people, relationship_index
from genealogy_integrity import (
    audit_family_archive, audit_csv, connected_components, missing_relatives,
    same_name_candidates, chronological_screening,
)
from relationship_evidence import audited_edges, edge_key, review_lookup
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
MATTHEW = "matthew_beveridge_hope_1837"
CLARISSA = "clarissa_beveridge_widow_1837"
HEIRS = (
    "achsa_heald_matthew_child", "james_m_beverage_matthew_child",
    "polly_tucker_matthew_child", "thomas_j_beverage_matthew_child",
    "sarah_a_beverage_matthew_child", "george_w_beverage_matthew_child",
    "martha_beverage_matthew_child", "ezekiel_g_beverage_matthew_child",
)


class Phase29ArchiveIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relations = relationship_index(cls.data["people"])
        cls.audit = audit_family_archive(cls.people, cls.data["events"], cls.relations)
        cls.reviewed = review_lookup()

    def test_full_effective_tree_is_inventory_not_one_branch_sample(self):
        s = self.audit["summary"]
        self.assertEqual(s["people"], len(self.data["people"]))
        self.assertEqual(s["events"], len(self.data["events"]))
        self.assertEqual(s["distinct_relationships"], len(self.audit["edges"]))
        self.assertEqual(s["individual_relationship_reviews"],
                         sum(e["status"] != "not_reviewed" for e in self.audit["edges"]))
        self.assertEqual(s["distinct_relationships"],
                         s["individual_relationship_reviews"] +
                         s["relationships_awaiting_review"])
        self.assertGreater(s["people"], 190)
        self.assertGreater(s["distinct_relationships"], 650)
        self.assertEqual(set(r["id"] for r in self.audit["profiles"]), set(self.people))
        self.assertEqual(len(self.audit["profiles"]), len(self.people))
        self.assertEqual(set().union(*map(set, self.audit["components"])), set(self.people))
        self.assertEqual(sum(len(g) for g in self.audit["components"]), len(self.people))
        self.assertEqual(s["connected_groups"], len(self.audit["components"]))
        self.assertEqual(validate_site_data(self.data).errors, [])

    def test_no_hypothetical_connections_between_four_documentary_branches(self):
        comp = self.audit["components"]
        def index(pid):
            return next(i for i, group in enumerate(comp) if pid in group)
        self.assertNotEqual(index(MATTHEW), index("mercy_beveridge_henry_1753"))
        self.assertNotEqual(index(MATTHEW), index("nathaniel_beverage_1804_rockland"))
        self.assertNotEqual(index(MATTHEW), index("james_beveridge_jr_1724"))
        self.assertEqual(self.people[MATTHEW]["parents"], [])
        self.assertEqual(self.people[CLARISSA]["children"], [])
        self.assertFalse(self.relations["parents"].get(MATTHEW))

    def test_all_eight_court_children_reviewed_from_the_same_specific_warrant(self):
        for child in HEIRS:
            key = edge_key("parent_child", MATTHEW, child)
            with self.subTest(child=child):
                self.assertIn(key, self.reviewed)
                entry = self.reviewed[key]
                self.assertEqual(entry["status"], "original_probate_record")
                self.assertIn("October 1837", entry["finding"])
                self.assertIn("maternity", entry["limitations"])
                self.assertEqual(entry["sources"][0]["route"],
                                 "?page=collection&view=waldo-probate")
                self.assertNotIn("url", entry["sources"][0])
                self.assertEqual(self.people[child]["parents"], [MATTHEW])
        self.assertEqual(self.reviewed[edge_key("spouses", MATTHEW, CLARISSA)]
                         ["status"], "original_probate_record")

    def test_two_cobb_parents_are_record_derived_with_explicit_identity_limit(self):
        parents = ("barnabas_cobb_clarissa_father", "jerusha_cobb_clarissa_mother")
        for parent in parents:
            review = self.reviewed[edge_key("parent_child", parent, CLARISSA)]
            self.assertEqual(review["status"], "published_record")
            self.assertIn("1911", review["finding"])
            self.assertIn("marriage", review["limitations"])
            self.assertEqual(len(review["sources"]), 2)
        self.assertEqual(set(self.people[CLARISSA]["parents"]), set(parents))

    def test_all_unresolved_ids_remain_unchanged_and_are_not_ghost_profiles(self):
        unresolved = missing_relatives(self.people, self.relations)
        self.assertEqual(unresolved, self.audit["unresolved"])
        self.assertTrue(unresolved)
        self.assertTrue(all(r["id"] not in self.people for r in unresolved))
        self.assertTrue(all(r["referenced_by"] for r in unresolved))
        self.assertTrue(all(all(pid in self.people for pid in r["referenced_by"])
                            for r in unresolved))

    def test_same_name_candidates_are_not_merged(self):
        collisions = same_name_candidates(self.people)
        self.assertEqual(collisions, self.audit["same_names"])
        self.assertTrue(any("thomas beverage" == entry["name"] for entry in collisions))
        for row in collisions:
            self.assertGreater(len(row["ids"]), 1)
            self.assertEqual(len(row["ids"]), len(set(row["ids"])))
            self.assertTrue(all(pid in self.people for pid in row["ids"]))
        self.assertEqual(len(self.data["people"]), len(self.people))

    def test_event_citations_and_dates_are_descriptive_screenings(self):
        s = self.audit["summary"]
        self.assertEqual(s["events_without_citation"],
                         len(self.audit["events_no_citations"]))
        self.assertGreaterEqual(s["events_without_direct_citation_url"],
                                s["events_without_citation"])
        self.assertEqual(s["chronology_screening_flags"], len(self.audit["chronology"]))
        self.assertTrue(all("person_ids" in row and "note" in row
                            for row in chronological_screening(self.people, self.relations)))
        self.assertEqual(len(self.audit["profiles"]),
                         s["people"])

    def test_exports_include_every_relation_with_no_ghost_sources(self):
        text = audit_csv(self.audit["edges"],
                         ("kind","from_id","to_id","status","finding"))
        parsed = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(parsed), len(self.audit["edges"]))
        self.assertEqual(sum(r["status"] == "original_probate_record" for r in parsed), 9)
        self.assertFalse(any("http" in row["finding"] for row in parsed
                             if row["status"] == "not_reviewed"))

    def test_no_changes_to_live_authentication(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertNotIn("from family_access import", app)


if __name__ == "__main__":
    unittest.main()
