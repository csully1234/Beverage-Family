"""Regression coverage for the publicly hosted 1859 Fox Islands scan viewer."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from historical_atlas import atlas_payload, build_historical_atlas_html, MAPS, SOURCE


ROOT = Path(__file__).resolve().parents[1]


class HistoricalAtlasTests(unittest.TestCase):
    def test_ten_authentic_map_scans_and_existing_1859_set(self):
        data = atlas_payload()
        self.assertEqual(len(data["maps"]), 10)
        self.assertEqual([m["id"] for m in data["maps"][:3]], [
            "fox-islands", "north-haven-village", "carvers-harbor"
        ])
        self.assertEqual([m["file"] for m in MAPS[:3]], [
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
        self.assertEqual(
            [m["file"] for m in MAPS[3:]],
            ["DesBarres1776-Org.jpg", "NorthHaven1867.jpg",
             "FoxIslandsThoroughfare_1868.jpg", "NorthernIslands1873-74.jpg",
             "NorthHaven-VinalHaven-HurricaneIsle1890.jpg",
             "FoxIslands1901.jpg", "FoxIslands1941.jpg"]
        )

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

    def test_early_record_links_are_cited_without_inventing_family_relationships(self):
        from historical_atlas import load_early_evidence
        info = load_early_evidence()
        sources = {source["id"]: source for source in info["sources"]}
        self.assertGreaterEqual(len(sources), 8)
        self.assertTrue(all(src["url"].startswith("https://") for src in sources.values()))
        self.assertEqual(sources["putnam_1785"]["url"],
                         "https://digitalmaine.com/planbook_knox_county/8/")
        self.assertEqual(sources["fox_outline_1786"]["url"],
                         "https://digitalmaine.com/planbook_8/17/")
        self.assertIn("Matthew Beveridge", str(info["findings"]))
        self.assertIn("ten named children", str(info["findings"]))
        self.assertIn("do not merge", str(info["findings"]).lower())
        self.assertIn("not a family property award", info["caveat"])
        self.assertEqual(len({finding["id"] for finding in info["findings"]}), len(info["findings"]))
        for finding in info["findings"]:
            self.assertTrue(set(finding["source_ids"]) <= sources.keys())
            self.assertTrue(finding["confidence"] and finding["status"])

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
