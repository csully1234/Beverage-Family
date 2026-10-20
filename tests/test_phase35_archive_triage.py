"""Phase 35: all-person source access and strict real-profile graph navigation."""
from __future__ import annotations

from pathlib import Path
import unittest

from archive_triage import (person_source_matrix, matrix_counts,
                            unresolved_reference_cases)
from family_data import (load_site_data, index_people, relationship_index,
                         shortest_relationship_path)
from family_research_index import build_index
from genealogy_integrity import audit_family_archive
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]


class Phase35EvidenceAccessAndIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.relationships = relationship_index(cls.data["people"])
        cls.audit = audit_family_archive(cls.people, cls.data["events"],
                                         cls.relationships)
        cls.access = person_source_matrix(cls.people, cls.data["events"],
                                          cls.relationships, edges=cls.audit["edges"],
                                          research_rows=build_index(cls.people))

    def test_every_real_profile_has_one_source_access_record(self):
        self.assertEqual(len(self.access), len(self.people))
        self.assertEqual({r["id"] for r in self.access}, set(self.people))
        self.assertGreater(len(self.access), 190)
        total = matrix_counts(self.access)
        self.assertEqual(total["people"], len(self.people))
        self.assertEqual(total["any_external_link"] +
                         total["no_external_link_in_indexed_contexts"],
                         len(self.people))
        self.assertTrue(all(row["direct_source_links"] == len(row["source_links"])
                            for row in self.access))
        self.assertTrue(all(row["reviewed_relationships"] <= row["total_relationships"]
                            for row in self.access))
        self.assertTrue(all(row["events_with_citations"] <= row["dated_events"]
                            for row in self.access))
        self.assertTrue(all(row["direct_source_links"] >= row["direct_profile_links"]
                            for row in self.access))

    def test_deduplicated_url_across_exact_person_source_families(self):
        people = {
            "known": {"id": "known", "full_name": "Known Example",
                      "sources": [{"title": "Catalog page",
                                   "url": "https://example.org/same"}]},
            "other": {"id": "other", "full_name": "Other Example", "sources": []},
        }
        events = [
            {"id": "one", "people_involved": ["known"],
             "sources": [{"title": "Event file",
                          "url": "https://example.org/event"}]},
            {"id": "no", "people_involved": ["other"],
             "sources": [{"title": "Unrelated event",
                          "url": "https://example.org/not-related"}]},
        ]
        catalog = [
            {"id": "curated", "title": "Curated repeat",
             "url": "https://example.org/same", "people_ids": ["known"]},
            {"id": "event-curated", "title": "Original event",
             "url": "https://example.org/event", "event_ids": ["one"]},
        ]
        research = [
            {"category": "Original source register", "person_ids": ["known"],
             "sources": [{"title": "Independent archive",
                          "url": "https://example.org/research"}],
             "route": "?page=archive"},
            {"category": "Scanned book photographs", "person_ids": ["known"],
             "pages": [47], "sources": []},
            {"category": "Scanned book OCR leads", "person_ids": ["known"],
             "sources": [{"title": "Misleading OCR",
                          "url": "https://example.org/unconfirmed"}]},
        ]
        edges = [
            {"from_id": "known", "to_id": "other",
             "status": "published_record",
             "sources": [{"title": "Reviewed family relationship",
                          "url": "https://example.org/relationship"}]},
        ]
        result = person_source_matrix(people, events,
                                      {"parents": {}, "children": {},
                                       "spouses": {}, "siblings": {}},
                                      catalog=catalog, research_rows=research,
                                      edges=edges)
        matched = next(row for row in result if row["id"] == "known")
        self.assertEqual(matched["direct_profile_links"], 1)
        self.assertEqual(matched["direct_event_links"], 1)
        self.assertEqual(matched["direct_research_links"], 1)
        self.assertEqual(matched["direct_relationship_links"], 1)
        self.assertEqual(matched["direct_source_links"], 4)
        self.assertEqual(matched["book_photo_pages"], [47])
        self.assertEqual(matched["research_routes"], ["?page=archive"])
        self.assertEqual(matched["events_with_citations"], 1)
        self.assertFalse(any("unconfirmed" in item["url"]
                             for item in matched["source_links"]))

    def test_source_link_is_access_not_original_manuscript_verification(self):
        one = {"known": {"id": "known", "full_name": "Known Example",
                         "sources": [{"title": "Index", "url": "https://example.org/index"},
                                     {"title": "Unpublished notes"},
                                     {"title": "Bad URL", "url": "javascript:alert(1)"}]}}
        rows = person_source_matrix(one, [], {"parents": {}, "children": {},
                                               "spouses": {}, "siblings": {}},
                                    research_rows=[], catalog=[], edges=[])
        self.assertEqual(rows[0]["profile_references"], 3)
        self.assertEqual(rows[0]["direct_source_links"], 1)
        self.assertNotIn("verified", rows[0])
        self.assertEqual(rows[0]["direct_profile_links"], 1)

    def test_unresolved_sources_are_all_visible_without_ghost_profile(self):
        cases = unresolved_reference_cases(self.people, self.relationships)
        self.assertEqual({item["id"] for item in cases},
                         {item["id"] for item in self.audit["unresolved"]})
        self.assertEqual(len(cases), 6)
        self.assertTrue(all(item["id"] not in self.people for item in cases))
        self.assertTrue(all(all(r["owner_id"] in self.people
                                for r in item["references"]) for item in cases))
        self.assertTrue(all(all(candidate["id"] in self.people
                                for candidate in item["potential_name_matches"])
                            for item in cases))
        # Similar first/last names are only flagged for manual record comparison.
        self.assertEqual(self.people["matthew_beveridge_hope_1837"]["parents"], [])
        self.assertEqual(self.people["clarissa_beveridge_widow_1837"]["children"], [])

    def test_graph_path_does_not_traverse_unknown_profiles(self):
        ghost_links = {
            "parents": {"one": {"missing_parent"},
                        "two": {"missing_parent"}},
            "children": {"missing_parent": {"one", "two"}},
            "spouses": {}, "siblings": {},
        }
        # Historical, permissive utility semantics remain for callers that
        # explicitly use it without a known-person whitelist.
        self.assertEqual(shortest_relationship_path(ghost_links, "one", "two"),
                         ["one", "missing_parent", "two"])
        self.assertEqual(shortest_relationship_path(
            ghost_links, "one", "two", known_ids={"one", "two"}), [])
        self.assertEqual(shortest_relationship_path(
            ghost_links, "one", "missing_parent", known_ids={"one", "two"}), [])
        self.assertEqual(shortest_relationship_path(
            ghost_links, "missing_parent", "missing_parent",
            known_ids={"one", "two"}), [])
        real = self.relationships
        self.assertEqual(shortest_relationship_path(
            real, "matthew_beveridge_hope_1837",
            "nathaniel_beverage_1804_rockland", known_ids=self.people), [])

    def test_integration_does_not_mutate_password_sources_or_tree(self):
        self.assertEqual(validate_site_data(self.data).errors, [])
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("known_ids=people_by_id", app)
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertNotIn("from family_access import", app)
        ui = (ROOT / "research_integrity_dashboard.py").read_text(encoding="utf-8")
        self.assertIn('section == "access"', ui) if 'section == "access"' in ui else self.assertIn('chosen == "access"', ui)


if __name__ == "__main__":
    unittest.main()
