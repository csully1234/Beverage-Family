from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
import tempfile
import unittest

from archive import ArchiveIndex, historical_person
from conflict_review import apply_review, load_review, validate_review
from family_data import (apply_date_precision, index_people, life_span, load_site_data,
                         merge_records, relationship_index)
from family_search import matches, person_match
from full_tree import build_full_tree_model
from research_collection import CollectionIndex

ROOT = Path(__file__).resolve().parents[1]


class EvidenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = load_site_data(ROOT / "data")
        cls.review = load_review()
        cls.people = index_people(cls.site["people"])
        cls.before = apply_date_precision(merge_records(cls.site["base_people"], cls.site["research_people"]),
                                          cls.site["date_precision"], "person")
        cls.old = index_people(cls.before)

    def test_ledger_covers_every_conflict_with_reopenable_evidence(self):
        self.assertEqual(validate_review(self.review, CollectionIndex.load(), self.site), [])
        self.assertEqual(len(self.review["resolutions"]), 11)
        self.assertEqual(len({s["url"] for s in self.review["sources"]}), len(self.review["sources"]))
        for r in self.review["resolutions"]:
            self.assertEqual(r["family_review_status"], "Not reviewed by family")
            self.assertTrue(r["existing_claims"])

    def test_corrections_reach_shared_people_archive_and_tree_with_audit(self):
        sarah = self.people["sarah_holman_1734"]
        diana = self.people["diana_daggett_1780"]
        lowell = self.people["lowell_beveridge_1905"]
        self.assertIsNone(sarah["birth_date"])
        self.assertNotIn("1734", life_span(sarah))
        self.assertIsNone(diana["birth_date"])
        self.assertEqual(diana["baptism_date"], "1780-12-31")
        self.assertNotIn("1780", life_span(diana))
        self.assertEqual(lowell["birth_place"], "Dorchester, Massachusetts")
        self.assertEqual(lowell["review_corrections"][0]["before"], "North Haven, Maine")
        archive = ArchiveIndex(self.site)
        self.assertEqual(archive.people[lowell["id"]]["birth_place"], lowell["birth_place"])
        model = build_full_tree_model(self.people, relationship_index(self.site["people"]))
        self.assertEqual(len(model["nodes"]), len(build_full_tree_model(self.old, relationship_index(self.before))["nodes"]))
        for node in model["nodes"]:
            if node["id"] in (sarah["id"], diana["id"]):
                self.assertNotIn("1734", node["life_span"])
                self.assertNotIn("1780", node["life_span"])

    def test_all_other_person_fields_and_relationships_remain_identical(self):
        self.assertEqual(set(self.people), set(self.old))
        changes = {(c["person_id"], c["field"]) for r in self.review["resolutions"] for c in r["changes"]}
        metadata = {"sources", "date_provenance", "review_corrections", "conflict_review_ids", "documented_activity"}
        for pid, p in self.people.items():
            for key in p.keys() | self.old[pid].keys():
                if key not in metadata and (pid, key) not in changes:
                    self.assertEqual(p.get(key), self.old[pid].get(key), (pid, key))
        self.assertEqual(relationship_index(self.site["people"]), relationship_index(self.before))
        self.assertIn("amelia_beverage_1833_child", self.people)
        self.assertIn("amelia_beverage_1833", self.people)

    def test_mismatched_baseline_and_disallowed_changes_fail_closed(self):
        for edit in (lambda c: c.update(before="unexpected"),
                     lambda c: c.update(field="residences", before=[]),
                     lambda c: c.update(field="parents", before=[]),
                     lambda c: c.update(field="notes", before="Third wife of James Beveridge Sr.")):
            review = copy.deepcopy(self.review)
            edit(review["resolutions"][0]["changes"][0])
            with self.assertRaises(ValueError):
                apply_review(self.before, review)
        review = copy.deepcopy(self.review)
        review["resolutions"][0]["confidence"] = "Probable"
        with self.assertRaises(ValueError):
            apply_review(self.before, review)
        review = copy.deepcopy(self.review)
        review["resolutions"][0]["changes"] *= 2
        with self.assertRaises(ValueError):
            apply_review(self.before, review)

    def test_loader_is_pure_and_ledger_optional(self):
        original = copy.deepcopy(self.before)
        apply_review(self.before, self.review)
        self.assertEqual(self.before, original)
        with tempfile.TemporaryDirectory() as tmp:
            empty = load_review(Path(tmp))
            self.assertEqual(apply_review(self.before, empty), self.before)

    def test_unknown_birth_does_not_bypass_living_person_protection(self):
        sarah = self.people["sarah_holman_1734"]
        self.assertTrue(historical_person(sarah))
        self.assertFalse(historical_person({"birth_date": None}))
        for flag in ("living", "is_living"):
            self.assertFalse(historical_person({**sarah, flag: True}))
        for year, confidence in ((2000, "Confirmed"), (1734, "Possible lead")):
            self.assertFalse(historical_person({"documented_activity": [
                {"year": year, "source_id": "CRS002", "confidence": confidence}]}, date(2026, 10, 15)))
        self.assertFalse(historical_person({"documented_activity": [{"year":1734,"confidence":"Confirmed"}]}))

    def test_variant_initial_and_fuzzy_matches_are_discovery_only(self):
        eliot = self.people["elliot_beverage_1908"]
        harold = self.people["harold_h_beverage_1893"]
        for q in ("Eliot Beveridge", "Elliot Bevridge", "E Bevrage"):
            self.assertEqual(person_match(q, eliot), "Name, initials or spelling variant")
        self.assertEqual(person_match("H H Beverage", harold), "Name, initials or spelling variant")
        self.assertTrue(matches("Harold antenna", harold))
        self.assertIn("Similar name", person_match("Harrold Beverage", harold))
        self.assertFalse(person_match("1924", {"full_name":"Harold Beverage", "birth_date":"1893"}))
        self.assertEqual(eliot["id"], "elliot_beverage_1908")
        self.assertFalse(matches("1734-02-07", self.people["sarah_holman_1734"]))
