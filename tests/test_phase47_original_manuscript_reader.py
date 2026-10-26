"""Regression tests for the seven newly obtained Massachusetts manuscript leaves."""
from __future__ import annotations

import unittest
import io
import zipfile
from pathlib import Path

from fox_islands_manuscript import (
    EXPECTED_LEAVES,
    IMAGE_STATUS,
    IMAGES_DIR,
    all_scans_zip,
    leaf_image_path,
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

    def test_live_optimized_images_are_published_with_original_tiff_provenance(self):
        record = load_fox_manuscripts()
        self.assertEqual(record["manuscript_images_status"], IMAGE_STATUS)
        self.assertEqual(len(record["leaves"]), 7)
        for row in record["leaves"]:
            with self.subTest(leaf=row["id"]):
                file = leaf_image_path(row)
                self.assertTrue(file.is_file(), file)
                self.assertTrue(file.is_relative_to(IMAGES_DIR))
                self.assertGreater(file.stat().st_size, 8000)
                with file.open("rb") as handle:
                    self.assertEqual(handle.read(3), b"\xff\xd8\xff")
                self.assertEqual(len(row["original_tiff_sha256"]), 64)
                self.assertEqual(row["image_status"], "published_optimized_scan")

    def test_downloadable_manuscript_bundle_contains_all_seven_images(self):
        record = load_fox_manuscripts()
        with zipfile.ZipFile(io.BytesIO(all_scans_zip(record))) as archive:
            files = archive.namelist()
            self.assertIn("MANIFEST.csv", files)
            self.assertEqual(len(files), 8)
            self.assertIn("fox_islands_1785/petition_page_3.jpg", files)
            self.assertIn("fox_islands_1785/resolve_page_3.jpg", files)
            self.assertIn("original_tiff_sha256", archive.read("MANIFEST.csv").decode())
        csv_content = manuscript_csv(record)
        self.assertIn("petition-3", csv_content)
        self.assertIn("resolve-3", csv_content)

    def test_gallery_prevents_file_path_traversal(self):
        with self.assertRaises(ValueError):
            leaf_image_path({"id": "petition-1", "image_file": "../leak.jpg"})
        with self.assertRaises(ValueError):
            leaf_image_path({"id": "petition-1", "image_file": "petition_page_2.jpg"})


if __name__ == "__main__":
    unittest.main()
