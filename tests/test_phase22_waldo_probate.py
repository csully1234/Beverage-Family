"""Phase 22: original 1837 probate evidence is navigable without invented ancestry.

Scans were supplied by a probate office through the user, but permission to
redistribute them in this public repository has NOT yet been established.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from family_data import index_people, load_site_data
from family_research_index import build_index, search_index
from validation import validate_site_data
from waldo_probate import (available_scan_path, load_waldo_probate,
                           scan_by_number, source_summary)

ROOT = Path(__file__).resolve().parents[1]


class MatthewWaldoProbateEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probate = load_waldo_probate()
        cls.family_data = load_site_data(ROOT / "data")
        cls.people = index_people(cls.family_data["people"])

    def test_one_original_court_source_family_and_full_packet(self):
        data = self.probate
        stats = source_summary(data)
        self.assertEqual(stats["source_families"], 1)
        self.assertEqual(stats["received_scans"], 31)
        self.assertEqual(stats["unique_scans"], 30)
        self.assertEqual(stats["heirs_named"], 8)
        self.assertEqual(stats["documentary_claims"], 6)
        pages = [scan["review_page"] for scan in data["scans"]]
        self.assertEqual(pages, list(range(1, 32)))
        self.assertIn("ONE probate case", data["record_group"])
        self.assertIn("not probate docket sequence", data["crosswalk_note"])

    def test_exact_duplicate_and_filename_hash_provenance(self):
        data = self.probate
        a, duplicate = scan_by_number(9, data), scan_by_number(26, data)
        self.assertEqual(duplicate["duplicate_of"], 9)
        self.assertEqual(a["sha256"], duplicate["sha256"])
        self.assertNotEqual(a["original_zip_filename"], duplicate["original_zip_filename"])
        self.assertEqual(scan_by_number(10, data)["original_zip_filename"], "JGVLJGV")
        self.assertIsNone(scan_by_number(32, data))
        originals = [scan["original_zip_filename"] for scan in data["scans"]]
        self.assertEqual(len(set(originals)), 31)
        for scan in data["scans"]:
            self.assertRegex(scan["sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(scan["normalized_filename"], r"^images/[0-9]{2}_[a-z0-9_]+\.png$")
            self.assertEqual(scan["reproduction_status"], "not_published_pending_permission")

    def test_court_statements_not_promoted_to_vital_certificates(self):
        data = self.probate
        by_id = {claim["id"]: claim for claim in data["claims"]}
        self.assertEqual(by_id["death-1837"]["date"], "1837-02-14")
        self.assertIn(10, by_id["death-1837"]["review_pages"])
        self.assertIn("not a separately inspected civil death", by_id["death-1837"]["limits"])
        self.assertEqual(by_id["letters-1837"]["date"], "1837-03-06")
        self.assertIn("Clarissa", by_id["widow-clarissa"]["finding"])
        self.assertIn("maiden surname Cobb", by_id["widow-clarissa"]["limits"])
        self.assertIn("not", by_id["land-and-dower"]["limits"].lower())
        self.assertIn("not", by_id["heirs-1837"]["limits"].lower())

    def test_all_heirs_are_recorded_as_heirs_not_new_genealogy_edges(self):
        heirs = self.probate["heirs"]
        self.assertEqual(
            [h["name"] for h in heirs],
            ["Ezekiel G. Beverage", "Achsa Heald", "James M. Beverage",
             "Polly Tucker", "Thomas J. Beverage", "Sarah A. Beverage",
             "George W. Beverage", "Martha Beverage"])
        self.assertTrue(all(31 in h["review_pages"] for h in heirs))
        self.assertEqual(next(h for h in heirs if h["name"] == "Polly Tucker")["review_pages"], [31,14])
        self.assertTrue(all(h["published_alignment"] for h in heirs))
        self.assertIn("identity plausible", heirs[3]["published_alignment"])
        self.assertNotIn("capt_matthew_beverage", self.people)
        self.assertFalse(self.people["nathaniel_beverage_1804_rockland"]["parents"])
        self.assertEqual(validate_site_data(self.family_data).errors, [])

    def test_unlicensed_image_bytes_cannot_be_served_by_metadata(self):
        self.assertFalse(self.probate.get("image_publication_authorized", False))
        self.assertIn("not been confirmed", self.probate["licensing"])
        scan = scan_by_number(31, self.probate)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            allowed = root / Path(scan["normalized_filename"]).name
            allowed.write_bytes(b"temporary test file")
            self.assertIsNone(available_scan_path(scan, root=root))
            self.assertIsNone(available_scan_path(scan, publication_authorized=True, root=root))
            explicitly_approved = {**scan, "reproduction_status": "approved_for_publication"}
            self.assertEqual(available_scan_path(explicitly_approved,
                publication_authorized=True, root=root), allowed)
            malicious = {**explicitly_approved, "normalized_filename": "images/../../secrets.png"}
            self.assertIsNone(available_scan_path(malicious,
                publication_authorized=True, root=root))

    def test_archive_index_exposes_all_review_pages_and_claims(self):
        records = build_index(self.people)
        scans = [r for r in records if r["id"].startswith("waldo-probate-scan:")]
        claims = [r for r in records if r["id"].startswith("waldo-probate-claim:")]
        self.assertEqual(len(scans), 31)
        self.assertEqual(len(claims), 6)
        self.assertEqual(len({r["id"] for r in scans + claims}), 37)
        self.assertEqual(len({r["route"] for r in scans}), 31)
        self.assertTrue(all(not r["person_ids"] for r in scans + claims))
        self.assertTrue(all(not r["sources"] for r in scans + claims))
        self.assertTrue(all(not r["pages"] for r in scans + claims))
        for row in scans + claims:
            route = parse_qs(urlsplit(row["route"]).query)
            self.assertEqual(route["page"], ["collection"])
            self.assertEqual(route["view"], ["waldo-probate"])
            self.assertEqual(len(route["scan"]), 1)
        duplicate = next(r for r in scans if r["id"].endswith(":26"))
        self.assertIn("Exact duplicate", duplicate["status"])
        self.assertTrue(any(r["id"].startswith("waldo-probate")
                            for r in search_index(records, query="Polly Tucker")))


if __name__ == "__main__":
    unittest.main()
