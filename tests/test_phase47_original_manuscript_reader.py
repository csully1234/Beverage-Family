"""Regression tests for the seven newly obtained Massachusetts manuscript leaves."""
from __future__ import annotations

import unittest

from fox_islands_manuscript import (
    EXPECTED_LEAVES,
    load_fox_manuscripts,
    manuscript_csv,
    name_mentions,
)


class OriginalManuscriptReaderTests(unittest.TestCase):
    def test_seven_original_leaves_in_order_with_provenance(self):
        record = load_fox_manuscripts()
        self.assertEqual(tuple(row["id"] for row in record["leaves"]), EXPECTED_LEAVES)
        self.assertEqual(len(record["leaves"]), 7)
        self.assertEqual(len([leaf for leaf in record["leaves"]
                              if leaf["group"] == "Petition"]), 4)
        self.assertEqual(len([leaf for leaf in record["leaves"]
                              if leaf["group"] == "Resolve"]), 3)
        self.assertTrue(all(leaf["source_file"].endswith(".tif")
                            for leaf in record["leaves"]))
        self.assertTrue(all(not leaf["full_transcription_verified"]
                            for leaf in record["leaves"]))

    def test_named_people_are_original_mentions_not_identified_relatives(self):
        record = load_fox_manuscripts()
        mentions = name_mentions(record)
        self.assertEqual([p["name"] for p in mentions], [
            "James Beveridge", "Thomas Beveridge", "Matthew Beveridge"
        ])
        self.assertEqual({p["leaf"] for p in mentions}, {3})
        self.assertEqual({p["column"] for p in mentions}, {"left", "right"})
        self.assertIn("minor", mentions[-1]["evidence"].lower())
        self.assertTrue(all("name-only" in p["identity_status"] for p in mentions))
        self.assertFalse(any("person_id" in p or "parents" in p
                             for p in mentions))

    def test_resolve_counts_and_cutoff_distinct_from_later_petition_headcount(self):
        record = load_fox_manuscripts()
        self.assertEqual(record["settler_count_in_resolve"], 72)
        self.assertEqual(record["survey_acres"], 16527)
        self.assertEqual(record["eligibility_date"], "1784-01-01")
        self.assertIn("material textual discrepancy", record["entry_note"])
        variants = record["primary_secondary_variants"]
        self.assertEqual(len(variants), 5)
        original = next(row for row in variants if row["id"] == "fox-count-original-72")
        printed = next(row for row in variants if row["id"] == "fox-count-1889-75")
        self.assertIn("seventy two", original["reading"])
        self.assertIn("seventy-five", printed["reading"])
        self.assertIn("same sentence", printed["notes"])

    def test_matthew_minor_and_possible_major_notation_remain_disputed(self):
        record = load_fox_manuscripts()
        matthew = name_mentions(record)[2]
        self.assertEqual(matthew["age_status"], "disputed_from_original_handwriting")
        self.assertIn("a minor", matthew["age_annotation_diplomatic"])
        self.assertIn("major", matthew["age_annotation_diplomatic"])
        self.assertIn("unverified", matthew["evidence"])
        leaf = next(x for x in record["leaves"] if x["id"] == "petition-3")
        self.assertIn("major", leaf["excerpt"])
        self.assertFalse(leaf["full_transcription_verified"])

    def test_online_reader_has_real_images_and_keeps_tiff_masters_distinct(self):
        record = load_fox_manuscripts()
        self.assertEqual(record["manuscript_images_status"],
                         "optimized_public_web_facsimiles_hosted_original_tiffs_retained_offline")
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for leaf in record["leaves"]:
            page = root / leaf["site_scan_path"]
            self.assertTrue(page.is_file())
            self.assertTrue(str(page).endswith(".svg"))
            self.assertTrue(page.read_text(encoding="utf-8").startswith("<svg"))
            self.assertIn("data:image/jpeg;base64,", page.read_text(encoding="utf-8"))
            self.assertIn("not hosted", leaf["master_status"])
        self.assertTrue(all(source["type"] for source in record["sources"]))
        self.assertTrue(any("not" in next_item.lower() for next_item in record["outstanding"]))
        csv_content = manuscript_csv(record)
        self.assertEqual(csv_content.count(".tif"), 7)
        self.assertIn("petition-3", csv_content)
        self.assertIn("resolve-3", csv_content)


if __name__ == "__main__":
    unittest.main()
