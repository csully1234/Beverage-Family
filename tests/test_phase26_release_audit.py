"""Phase 26: release-readiness checks guard real media and safe routes."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.release_audit import (
    ROOT, official_page_slugs, safe_repo_file, verify_book_assets,
    literal_route_audit, media_status, report
)
from tools.create_release_backup import tracked_files


class Phase26ReleaseAuditTests(unittest.TestCase):
    def test_the_complete_authorized_family_book_is_really_present(self):
        rows = verify_book_assets(ROOT)
        self.assertEqual(len(rows), 1)
        book = rows[0]
        self.assertEqual(book["id"], "colony-book-2016")
        self.assertEqual(book["status"], "verified")
        self.assertEqual(book["actual_pages"], 305)
        self.assertEqual(book["expected_pages"], 305)
        self.assertGreater(book["size_bytes"], 20_000_000)
        self.assertRegex(book["sha256"], r"^[a-f0-9]{64}$")

    def test_page_slugs_and_internal_links_use_known_destinations(self):
        audit = literal_route_audit(ROOT)
        self.assertFalse(audit["unknown_literal_routes"])
        self.assertGreater(audit["literal_routes_checked"], 30)
        self.assertTrue({"home", "people", "tree", "full-tree", "collection",
                         "media", "family-books", "timeline"} <= official_page_slugs(ROOT))

    def test_probate_images_remain_unpublished_unless_reuse_authorized(self):
        media = media_status(ROOT)
        self.assertEqual(media["probate_received_scans"], 31)
        self.assertEqual(media["probate_unique_scans"], 30)
        self.assertFalse(media["probate_publication_authorized"])
        self.assertEqual(media["approved_original_images"], 0)
        self.assertEqual(media["unavailable_or_unapproved_media"], [])

    def test_untrusted_manifest_paths_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            self.assertIsNone(safe_repo_file(root, "../secrets.txt"))
            self.assertIsNone(safe_repo_file(root, "/etc/passwd"))
            self.assertIsNone(safe_repo_file(root, r"static\\..\\secrets.txt"))
            self.assertEqual(safe_repo_file(root, "static/books/a.pdf"), root / "static/books/a.pdf")

    def test_backup_scope_cannot_collect_credentials(self):
        paths = tracked_files(ROOT)
        self.assertGreater(len(paths), 100)
        self.assertTrue(any(p.startswith("research/") for p in paths))
        self.assertIn("static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf", paths)
        self.assertFalse(any(
            ".env" in p or "secrets.toml" in p or p.startswith(".git/")
            for p in paths
        ))
        self.assertTrue(all((ROOT / p).is_file() for p in paths))

    def test_report_flags_remaining_password_cutover_accurately(self):
        data = report(ROOT)
        self.assertIn("book_assets", data)
        self.assertIn("navigation", data)
        self.assertIn("media", data)
        self.assertTrue(data["security"]["public_repository_is_not_private_storage"])
        self.assertEqual(data["book_assets"][0]["status"], "verified")


if __name__ == "__main__":
    unittest.main()
