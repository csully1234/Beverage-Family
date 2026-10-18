"""Audit ALL effective family edges, not the overall profile citation count."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
import unittest

from family_data import index_people, load_site_data, relationship_index
from relationship_evidence import (
    KIND_NAMES, STATUS_NAMES, audited_edges, edge_key, for_person,
    load_relationship_reviews, review_lookup, review_summary,
)
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class RelationshipEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relations = relationship_index(cls.data["people"])
        cls.edges = audited_edges(cls.people, cls.relations)
        cls.lookup = review_lookup()
        cls.summary = review_summary(cls.edges)

    def test_ledger_covers_every_current_edge_once(self):
        expected = set()
        for child_id, parent_ids in self.relations["parents"].items():
            for parent in parent_ids:
                expected.add(edge_key("parent_child", parent, child_id))
        for field in ("spouses", "siblings"):
            for person_id, others in self.relations[field].items():
                for other_id in others:
                    if person_id != other_id:
                        expected.add(edge_key(field, person_id, other_id))
        self.assertEqual({r["key"] for r in self.edges}, expected)
        self.assertEqual(len(expected), len(self.edges))
        self.assertGreater(len(expected), 200)
        self.assertEqual(self.summary["total"],
                         self.summary["reviewed"] + self.summary["awaiting_review"])
        self.assertGreater(self.summary["awaiting_review"], self.summary["reviewed"])

    def test_reviewed_claims_exist_in_effective_family_tree(self):
        self.assertEqual(len(self.lookup), 11)
        actual_keys = {row["key"] for row in self.edges}
        self.assertTrue(set(self.lookup).issubset(actual_keys),
                        sorted(set(self.lookup) - actual_keys))
        for key, review in self.lookup.items():
            self.assertEqual(key, edge_key(review["kind"], review["from_id"], review["to_id"]))
            self.assertIn(review["status"], STATUS_NAMES)
            self.assertIn(review["kind"], KIND_NAMES)
            self.assertTrue(review["finding"] and review["limitations"])
            self.assertTrue(review["sources"])
            for source in review["sources"]:
                self.assertTrue(source["title"] and source["type"])
                url = urlsplit(source["url"])
                self.assertEqual(url.scheme, "https")
                self.assertTrue(url.hostname)

    def test_original_records_are_preserved_and_review_does_not_add_people(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        self.assertFalse(any(row["kind"] == "parent_child"
                             and (row["from_id"] == "mercy_beveridge_henry_1753"
                                  or row["to_id"] == "mercy_beveridge_henry_1753")
                             for row in self.edges))
        self.assertEqual(self.people["mercy_beveridge_henry_1753"]["parents"], [])
        self.assertEqual(len(self.people), len({p["id"] for p in self.data["people"]}))
        self.assertNotIn("robert_beveridge_1776", self.people)

    def test_uncertain_colonial_marriage_not_independently_proven(self):
        james = edge_key("spouses", "james_beveridge_jr_1724", "jean_mckinney_white_1725")
        self.assertEqual(self.lookup[james]["status"], "identity_needs_verification")
        self.assertIn("intention", self.lookup[james]["finding"].lower())
        self.assertIn("does not document solemnization", self.lookup[james]["finding"].lower())
        for parent in ("james_beveridge_sr_1700", "sarah_bennett_1705"):
            key = edge_key("parent_child", parent, "james_beveridge_jr_1724")
            self.assertEqual(self.lookup[key]["status"], "identity_needs_verification")

    def test_contemporary_lowell_branch_is_source_specific(self):
        for parent in ("lowell_beveridge_1905", "ida_louisa_gattrell_beveridge_1901"):
            for child in ("lowell_pierson_beveridge_jr_1930",
                          "thomas_gattrell_beveridge_1938"):
                self.assertIn(edge_key("parent_child", parent, child), self.lookup)
                self.assertEqual(self.lookup[edge_key("parent_child", parent, child)]["status"],
                                 "corroborated_publication")
        lyford = edge_key("siblings", "lyford_beveridge_brother_lowell", "lowell_beveridge_1905")
        self.assertEqual(self.lookup[lyford]["status"], "contemporary_report")
        self.assertFalse(self.relations["parents"].get("lyford_beveridge_brother_lowell"))
        mercy_spouse = edge_key("spouses", "mercy_beveridge_henry_1753", "henry_henry_1750")
        self.assertIn("not exact 1776 ceremony",
                      self.lookup[mercy_spouse]["limitations"].lower())

    def test_default_claims_are_not_mislabeled_verified(self):
        unknown = next(row for row in self.edges if row["status"] == "not_reviewed")
        self.assertFalse(unknown["sources"])
        self.assertIn("not yet audited", STATUS_NAMES[unknown["status"]])
        self.assertIn("without any source specifically proving", unknown["limitations"].lower())
        self.assertEqual(len(for_person("lyford_beveridge_brother_lowell", self.edges)),
                         sum("lyford_beveridge_brother_lowell" in
                             (row["from_id"], row["to_id"]) for row in self.edges))

    def test_sibling_conclusions_explain_their_origin(self):
        explicit = [row for row in self.edges if row["kind"] == "siblings"
                    and "Explicitly listed" in row["origin"]]
        inferred = [row for row in self.edges if row["kind"] == "siblings"
                    and "Inferred from" in row["origin"]]
        self.assertTrue(explicit)
        self.assertTrue(inferred)
        for row in inferred:
            self.assertIn("not separate sibling proof", row["origin"])


if __name__ == "__main__":
    unittest.main()
