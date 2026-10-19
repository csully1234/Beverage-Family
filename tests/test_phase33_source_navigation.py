"""Phase 33: entire person-linked event evidence chain and disconnected groups.

These are read-only navigation tests. They must never create profiles, invent
identity equivalences, import unpublished images, or change family authentication.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from family_data import index_people, load_site_data, relationship_index
from family_exhibits import event_evidence_for_person, exhibit_overview
from family_navigation import branch_context, unresolved_relative_ids
from genealogy_integrity import audit_family_archive
from validation import validate_site_data

ROOT = Path(__file__).resolve().parents[1]
MATTHEW = "matthew_beveridge_hope_1837"
CLARISSA = "clarissa_beveridge_widow_1837"


class Phase33EvidenceNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.data["people"])
        cls.links = relationship_index(cls.data["people"])

    def test_exact_id_event_attribution_keeps_all_source_labels(self):
        examples = [
            {"id": "event_a", "title": "Earlier dated record",
             "date": "1806", "people_involved": [MATTHEW],
             "sources": [
                 {"title": "Town book", "url": "https://example.org/townbook"},
                 "Original ledger not yet digitized",
                 {"title": "Unsafe supplied address", "url": "javascript:alert(1)"},
             ]},
            {"id": "event_b", "title": "Matthew mentioned in text, not attributed",
             "date": "1799", "description": "Matthew Beveridge",
             "people_involved": [CLARISSA],
             "sources": [{"title": "Other record", "url": "https://example.org/other"}]},
            {"id": "event_c", "title": "Later record", "date": "1820",
             "people_involved": [MATTHEW],
             "sources": [{"title": "Index only", "url": "https://example.org/index"}]},
            {"id": "event_d", "title": "Not a documented source", "date": "1810",
             "people_involved": [MATTHEW], "sources": []},
        ]
        curated = [{"id": "curated-a", "event_ids": ["event_a"],
                    "title": "Curated town index", "url": "https://example.org/curated",
                    "access": "Published index", "limits": "Identity not proved"}]
        rows = event_evidence_for_person(MATTHEW, examples, curated)
        self.assertEqual([e["event_id"] for e in rows], ["event_a", "event_c"])
        self.assertEqual(rows[0]["linked"], 2)
        self.assertEqual(rows[0]["date"], "1806")
        self.assertEqual(len(rows[0]["sources"]), 4)
        self.assertTrue(any(s["url"] is None for s in rows[0]["sources"]))
        self.assertEqual(event_evidence_for_person("unknown-id", examples, curated), [])
        self.assertEqual(event_evidence_for_person(CLARISSA, examples, curated)[0]["event_id"],
                         "event_b")

    def test_real_events_reachable_from_documented_exact_person(self):
        known = "james_beveridge_sr_1700"
        events = event_evidence_for_person(known, self.data["events"], [])
        self.assertTrue(events)
        self.assertTrue(any("birth" in e["title"].lower() for e in events))
        self.assertTrue(all(e["sources"] for e in events))
        self.assertTrue(all(known in next(original for original in self.data["events"]
                                          if original["id"] == e["event_id"])["people_involved"]
                            for e in events))
        self.assertEqual(len({e["event_id"] for e in events}), len(events))

    def test_exhibit_counts_event_citations_without_pretending_they_are_scans(self):
        view = exhibit_overview(self.people[MATTHEW], self.data["events"], [],
                                catalog=[], pictures=[])
        self.assertIn("event_evidence", view)
        self.assertEqual(view["id"], MATTHEW)
        self.assertTrue(all(isinstance(row["linked"], int) for row in view["event_evidence"]))
        self.assertTrue(all(row["linked"] <= len(row["sources"])
                            for row in view["event_evidence"]))

    def test_all_components_named_without_inventing_missing_profiles(self):
        audit = audit_family_archive(self.people, self.data["events"], self.links)
        groups = audit["components"]
        self.assertGreater(len(groups), 1)
        for i, group in enumerate(groups, 1):
            for pid in group:
                context = branch_context(pid, self.people, self.links)
                self.assertEqual(context["number"], i)
                self.assertEqual(context["total"], len(groups))
                self.assertEqual(context["size"], len(group))
                self.assertEqual(context["member_ids"], group)
        self.assertIsNone(branch_context("unconfirmed_same_name", self.people, self.links))
        matthew = branch_context(MATTHEW, self.people, self.links)
        other = branch_context("nathaniel_beverage_1804_rockland",
                               self.people, self.links)
        self.assertNotEqual(matthew["number"], other["number"])
        self.assertEqual(self.people[MATTHEW]["parents"], [])
        self.assertEqual(self.people[CLARISSA]["children"], [])

    def test_unknown_reference_is_not_a_selectable_family_member(self):
        people = {"p": {"id": "p", "full_name": "Verified Person"}}
        links = {"parents": {"p": {"unverified_parent"}},
                 "children": {}, "spouses": {}, "siblings": {}}
        group = branch_context("p", people, links)
        self.assertEqual(group["member_ids"], ["p"])
        self.assertEqual(unresolved_relative_ids("p", people, links),
                         ["unverified_parent"])
        self.assertIsNone(branch_context("unverified_parent", people, links))

    def test_link_audit_matches_actual_clickable_url_policy(self):
        from genealogy_integrity import _known_url
        self.assertTrue(_known_url({"url": "https://example.org/archive.pdf"}))
        self.assertFalse(_known_url({"url": "javascript:alert(1)"}))
        self.assertFalse(_known_url({"url": "https://user:pass@example.org/private"}))
        self.assertFalse(_known_url({"url": "https://example.org:9999/file"}))
        self.assertFalse(_known_url({"url": "https://example.org/my file"}))
        self.assertFalse(_known_url({"title": "No digitized original"}))
        self.assertFalse(_known_url("Unlinked book citation"))

    def test_citation_queue_never_implies_original_scans_are_available(self):
        audit = audit_family_archive(self.people, self.data["events"], self.links)
        self.assertEqual(len(audit["events_no_direct_link"]),
                         audit["summary"]["events_without_direct_citation_url"])
        self.assertTrue(all(event.get("id") for event in audit["events_no_direct_link"]))
        self.assertEqual(validate_site_data(self.data).errors, [])
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)


if __name__ == "__main__":
    unittest.main()
