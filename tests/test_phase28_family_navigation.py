"""Phase 28: navigation, profile citation completeness, and mobile tree fit."""
from __future__ import annotations

import unittest
from pathlib import Path
from family_data import load_site_data, index_people, relationship_index
from family_navigation import (
    connected_relatives, connected_profile_ids, unresolved_relative_ids,
)
from family_exhibits import citation_page, visible_citations, CITATION_PAGE_SIZE

ROOT = Path(__file__).resolve().parents[1]
MATTHEW = "matthew_beveridge_hope_1837"
CLARISSA = "clarissa_beveridge_widow_1837"


class Phase28FamilyNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = load_site_data(ROOT / "data")
        cls.people = index_people(data["people"])
        cls.relationships = relationship_index(data["people"])

    def test_every_court_named_child_is_accessible_without_new_relationships(self):
        rows = connected_relatives(MATTHEW, self.people, self.relationships)
        children = [r for r in rows if r["relationship"] == "Child"]
        self.assertEqual(len(children), 8)
        self.assertEqual({r["person_id"] for r in children},
                         set(self.people[MATTHEW]["children"]))
        self.assertEqual(len(rows), len({r["person_id"] for r in rows}))
        self.assertEqual(rows[0]["relationship"], "Spouse")
        self.assertEqual(rows[0]["person_id"], CLARISSA)
        self.assertEqual(connected_profile_ids(MATTHEW, self.people, self.relationships)[0],
                         MATTHEW)
        self.assertNotIn("capt_thomas_beverage", connected_profile_ids(
            MATTHEW, self.people, self.relationships))

    def test_clarissa_parents_are_navigable_without_invented_child_maternity(self):
        rows = connected_relatives(CLARISSA, self.people, self.relationships)
        parents = {r["person_id"] for r in rows if r["relationship"] == "Parent"}
        self.assertEqual(parents, {"barnabas_cobb_clarissa_father",
                                   "jerusha_cobb_clarissa_mother"})
        self.assertFalse([r for r in rows if r["relationship"] == "Child"])
        self.assertEqual(self.people[CLARISSA]["children"], [])

    def test_unresolved_and_unknown_nodes_cannot_become_selectable_profiles(self):
        unknown = "name_only_reference"
        people = {"known": {"id": "known", "full_name": "Verified Source Person"}}
        rel = {"parents": {"known": {unknown}}, "spouses": {},
               "children": {}, "siblings": {}}
        self.assertEqual(connected_relatives("known", people, rel), [])
        self.assertEqual(unresolved_relative_ids("known", people, rel), [unknown])
        self.assertEqual(connected_profile_ids("known", people, rel), ["known"])
        self.assertEqual(connected_profile_ids(unknown, people, rel), [])

    def test_citation_reader_filters_links_without_hiding_or_mislabeling_sources(self):
        refs = [{"title": f"Record {i}", "url": "https://source.org/"+str(i)
                 if i % 2 == 0 else None} for i in range(19)]
        self.assertEqual(visible_citations(refs), refs)
        linked = visible_citations(refs, linked_only=True)
        self.assertEqual(len(linked), 10)
        self.assertEqual([x["title"] for x in linked],
                         [r["title"] for r in refs if r["url"]])
        pages = [citation_page(refs, i) for i in range(1, 5)]
        self.assertEqual([len(p) for p in pages], [6, 6, 6, 1])
        self.assertEqual([x["title"] for p in pages for x in p],
                         [x["title"] for x in refs])
        self.assertEqual(CITATION_PAGE_SIZE, 6)
        self.assertEqual(citation_page(refs, 0), [])

    def test_password_system_and_research_sources_not_changed(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("LEGACY_COMPATIBILITY_PASSWORD", app)
        self.assertIn("def configured_password()", app)
        tree = (ROOT / "full_tree.py").read_text(encoding="utf-8")
        self.assertIn("#shell {{ height:100%; min-height:0;", tree)
        self.assertIn("#viewport {{ min-height:120px;", tree)


if __name__ == "__main__":
    unittest.main()
