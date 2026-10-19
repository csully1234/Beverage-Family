"""Phase 21: a relative remains selected across profile, tree and map links.

These tests focus on bookmarkable context and deliberately do not infer any
ancestry, add family edges or modify protected historical claims.
"""
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from app import (center_tree_on, navigate, sync_full_map_person,
                 sync_sidebar_route, sync_tree_person)
from visitor_journeys import current_person, suggested_paths


PERSON = "mercy_beveridge_henry_1753"
OTHER = "lowell_beveridge_1905"
PEOPLE = {
    PERSON: {"id": PERSON, "full_name": "Mercy Beveridge Henry"},
    OTHER: {"id": OTHER, "full_name": "Lowell Beveridge"},
}


class ShareablePersonNavigationTests(unittest.TestCase):
    def test_all_person_section_links_keep_exact_identifier(self):
        for page, expected in (
            ("People", ("tree", "full-tree")),
            ("Explore the Tree", ("full-tree", "people")),
            ("Full Family Map", ("tree", "people")),
        ):
            with self.subTest(page=page):
                choices = suggested_paths(page, PERSON)
                self.assertEqual(len(choices), 3)
                self.assertEqual(len({url for _, url in choices}), 3)
                for choice, slug in zip(choices[:2], expected):
                    parsed = parse_qs(urlsplit(choice[1]).query)
                    self.assertEqual(parsed["page"], [slug])
                    self.assertEqual(parsed["profile"], [PERSON])

    def test_direct_bookmark_wins_over_stale_session_selection(self):
        fake = SimpleNamespace(
            query_params={"profile": PERSON},
            session_state={"full_map_person": OTHER, "tree_person": OTHER,
                           "profile_selector": OTHER},
        )
        with patch("visitor_journeys.st", fake):
            for page in ("People", "Explore the Tree", "Full Family Map"):
                self.assertEqual(current_person(PEOPLE, page), PERSON)
            fake.query_params = {"profile": "unknown"}
            self.assertEqual(current_person(PEOPLE, "Explore the Tree"), OTHER)
            fake.session_state["tree_person"] = PERSON
            self.assertEqual(current_person(PEOPLE, "Explore the Tree"), PERSON)
            self.assertEqual(current_person(PEOPLE, "Full Family Map"), OTHER)

    def test_tree_and_map_selectors_update_cross_page_state_and_urls(self):
        fake = SimpleNamespace(
            query_params={"page": "tree"},
            session_state={"nav_page": "Explore the Tree", "tree_person": PERSON,
                           "full_map_person": OTHER, "profile_selector": OTHER},
        )
        with patch("app.st", fake):
            sync_tree_person()
            self.assertEqual(fake.query_params, {"page": "tree", "profile": PERSON})
            self.assertEqual(fake.session_state["full_map_person"], PERSON)
            self.assertEqual(fake.session_state["profile_selector"], PERSON)

            fake.session_state["full_map_person"] = OTHER
            sync_full_map_person()
            self.assertEqual(fake.query_params, {"page": "full-tree", "profile": OTHER})
            self.assertEqual(fake.session_state["tree_person"], OTHER)
            self.assertEqual(fake.session_state["profile_selector"], OTHER)

            fake.session_state["full_map_person"] = ""
            sync_full_map_person()
            self.assertNotIn("profile", fake.query_params)

    def test_navigation_preserves_person_in_trees_not_unrelated_pages(self):
        fake = SimpleNamespace(
            query_params={"page": "people", "profile": PERSON, "event": "sample"},
            session_state={"nav_page": "People", "profile_selector": PERSON,
                           "tree_person": OTHER, "full_map_person": OTHER},
        )
        with patch("app.st", fake):
            navigate("Full Family Map")
            self.assertEqual(fake.query_params["profile"], PERSON)
            self.assertNotIn("event", fake.query_params)
            fake.session_state["nav_page"] = "Explore the Tree"
            sync_sidebar_route()
            self.assertEqual(fake.query_params["profile"], PERSON)
            navigate("Timeline")
            self.assertNotIn("profile", fake.query_params)

            center_tree_on(PERSON)
            self.assertEqual(fake.query_params["page"], "tree")
            self.assertEqual(fake.query_params["profile"], PERSON)
            self.assertEqual(fake.session_state["full_map_person"], PERSON)


if __name__ == "__main__":
    unittest.main()
