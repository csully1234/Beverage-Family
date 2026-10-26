"""Phase 49: actual seven-page manuscript facsimiles and 1819 first-hand witness."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from fox_islands_manuscript import load_fox_manuscripts
from fox_islands_primary_bridge import load_fox_source_bridge, bridge_csv

ROOT = Path(__file__).resolve().parents[1]


class EarlyIslandPrimaryDocumentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuscript = load_fox_manuscripts()
        cls.bridge = load_fox_source_bridge()

    def test_all_seven_page_images_are_real_stable_local_assets(self):
        names = []
        for row in self.manuscript["leaves"]:
            name = row["site_scan_path"]
            names.append(name)
            self.assertTrue(name.startswith("static/fox_islands_manuscripts/"))
            self.assertTrue(name.endswith(".svg"))
            blob = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', blob)
            self.assertIn('href="data:image/jpeg;base64,', blob)
            self.assertGreater(len(blob), 100000)
            self.assertIn("TIFF", row["master_status"])
        self.assertEqual(len(set(names)), 7)
        self.assertEqual(len(names), 7)
        self.assertFalse((ROOT / "static" / "fox_islands_manuscripts" /
                          "source_original_master.tif").exists())

    def test_existing_1819_archive_identity_reused_not_duplicated(self):
        letter = self.bridge["letter_analysis"]
        self.assertEqual(letter["author_as_signed"], "Benjamin Beverage")
        self.assertEqual(letter["manuscript_pages"], 2)
        self.assertEqual(letter["manuscript_date"], "1819-12-20")
        self.assertEqual(letter["archive_item"], "Maine Memory Network 20801")
        sources = json.loads((ROOT / "data" / "archive_sources.json").read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in sources]
        self.assertIn(letter["existing_site_source_id"], ids)
        source = next(entry for entry in sources
                      if entry["id"] == letter["existing_site_source_id"])
        self.assertIn("20801", source["url"])
        self.assertIn("1819", source["date"])

    def test_source_labels_limits_and_reproduction_boundaries(self):
        sources = {source["id"]: source for source in self.bridge["sources"]}
        self.assertEqual(set(sources), {
            "mass-original", "benjamin-1819", "1790-thomas",
            "1800-origins", "putnam-1786"
        })
        self.assertIn("Maine Historical Society", sources["benjamin-1819"]["repository"])
        self.assertIn("20801", sources["benjamin-1819"]["url"])
        self.assertIn("/media/pdf/20801.pdf",
                      sources["benjamin-1819"]["transcript_url"])
        self.assertIn("Do not mirror", self.bridge["letter_analysis"]["image_reproduction"])
        self.assertTrue(self.bridge["no_tree_edges_modified"])
        self.assertTrue(self.bridge["no_outbound_messages_sent"])

    def test_all_observations_prioritized_by_evidence_not_inferred_kinship(self):
        rows = self.bridge["observations"]
        self.assertEqual([r["year"] for r in rows], [1765, 1785, 1786, 1790, 1800, 1819])
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["limits"] and row["source_ids"] for row in rows))
        self.assertFalse(any("person_ids" in row or "parents" in row for row in rows))
        export = bridge_csv(self.bridge)
        self.assertIn("original", export)
        self.assertIn("Benjamin", export)

    def test_original_census_population_is_not_genetic_family_claim(self):
        earlier = json.loads((ROOT / "data" / "phase45_early_island_census_settlement_context.json").read_text(encoding="utf-8"))[0]
        census = earlier["census_1790"]
        self.assertEqual(census["total_people"], 11)
        self.assertEqual(census["adult_males_16_plus_including_head"], 2)
        self.assertEqual(census["males_under_16"], 4)
        self.assertEqual(census["free_white_females_all_ages"], 5)
        self.assertFalse(census["original_handwritten_scheduled_inspected"])
        obs = next(row for row in self.bridge["observations"]
                   if row["id"] == "census-1790")
        self.assertIn("identity", obs["limits"])

if __name__ == "__main__":
    unittest.main()
