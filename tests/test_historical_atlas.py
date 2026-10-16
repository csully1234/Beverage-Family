"""Regression coverage for the publicly hosted 1859 Fox Islands scan viewer."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from historical_atlas import atlas_payload, build_historical_atlas_html, MAPS, SOURCE


ROOT = Path(__file__).resolve().parents[1]


class HistoricalAtlasTests(unittest.TestCase):
    def test_three_authentic_map_scans_from_original_collection(self):
        data = atlas_payload()
        self.assertEqual(len(data["maps"]), 3)
        self.assertEqual([m["id"] for m in data["maps"]], [
            "fox-islands", "north-haven-village", "carvers-harbor"
        ])
        self.assertEqual([m["file"] for m in MAPS], [
            "NorthHaven-Vinalhaven1859.jpg", "NorthHavenTown1859.jpg",
            "CarversHarbor1859.jpg"
        ])
        for map_record in data["maps"]:
            self.assertTrue(map_record["url"].startswith(SOURCE))
            self.assertTrue(map_record["url"].endswith(".jpg"))
            self.assertTrue(map_record["description"])
            self.assertTrue(map_record["note"])
            self.assertTrue(map_record["alt"])
        self.assertEqual(data["download"], SOURCE + "NorthHaven-Vinalhaven1859.zip")

    def test_embedded_json_is_valid_and_does_not_inject_markup(self):
        html = build_historical_atlas_html()
        self.assertNotIn("ATLAS_JSON", html)
        match = re.search(r'<script type="application/json" id="atlas-data">(.*?)</script>', html, flags=re.S)
        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1)), atlas_payload())
        self.assertIn('id="stage"', html)
        self.assertIn('id="zoom-in"', html)
        self.assertIn('id="zoom-out"', html)
        self.assertIn('id="open-original"', html)
        self.assertIn('id="download-all"', html)
        self.assertIn("pointermove", html)
        self.assertIn("image.onerror", html)
        self.assertIn("fit()", html)

    def test_provenance_and_landownership_are_not_misrepresented(self):
        from historical_atlas import render_historical_atlas
        self.assertTrue(callable(render_historical_atlas))
        html = build_historical_atlas_html()
        self.assertIn("not a deed boundary", html)
        self.assertNotIn("owned the entire island", html.lower())
        page = (ROOT / "archive_ui.py").read_text(encoding="utf-8")
        self.assertIn('st.tabs(["Interactive historical places", "Original 1859 maps"])', page)
        self.assertIn("render_historical_atlas()", page)


if __name__ == "__main__":
    unittest.main()
