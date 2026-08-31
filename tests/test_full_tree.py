from __future__ import annotations

import unittest
from pathlib import Path

from family_data import index_people, load_site_data, relationship_index
from full_tree import build_full_tree_html, build_full_tree_model


ROOT = Path(__file__).resolve().parents[1]


class FullTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_site_data(ROOT / "data")
        cls.people_by_id = index_people(cls.data["people"])
        cls.relationships = relationship_index(cls.data["people"])

    def test_full_tree_contains_every_profile(self) -> None:
        model = build_full_tree_model(self.people_by_id, self.relationships)
        node_ids = {node["id"] for node in model["nodes"]}
        self.assertTrue(set(self.people_by_id).issubset(node_ids))
        self.assertGreaterEqual(len(node_ids), len(self.people_by_id))

    def test_full_tree_edges_are_deduplicated(self) -> None:
        model = build_full_tree_model(self.people_by_id, self.relationships)
        parent_edges = [tuple(edge) for edge in model["parent_edges"]]
        spouse_edges = [tuple(edge) for edge in model["spouse_edges"]]
        self.assertEqual(len(parent_edges), len(set(parent_edges)))
        self.assertEqual(len(spouse_edges), len(set(spouse_edges)))
        self.assertGreater(len(parent_edges), 0)

    def test_full_tree_canvas_is_large_and_navigable(self) -> None:
        model = build_full_tree_model(self.people_by_id, self.relationships)
        self.assertGreaterEqual(model["width"], 1180)
        self.assertGreaterEqual(model["height"], 720)
        html = build_full_tree_html(self.people_by_id, self.relationships)
        self.assertIn("Fit whole tree", html)
        self.assertIn("Find and center a person", html)
        self.assertIn("pointerdown", html)
        self.assertIn("wheel", html)
        self.assertNotIn("window.parent.location.assign", html)
        self.assertNotIn("<script src=", html)

    def test_full_tree_marks_unresolved_relationship_nodes(self) -> None:
        model = build_full_tree_model(self.people_by_id, self.relationships)
        unresolved = [node for node in model["nodes"] if node["unresolved"]]
        self.assertGreater(len(unresolved), 0)
        self.assertTrue(all(node["life_span"] == "Unresolved profile" for node in unresolved))


if __name__ == "__main__":
    unittest.main()
