"""Phase 37: no predictable unauthenticated full-book URL on the family site."""
from __future__ import annotations

import ast
from pathlib import Path
import tomllib
import unittest

from family_books import (ROOT, BOOKS_DIR, book_pdf_path,
                          available_book_pdf)
from tools.privacy_audit import archive_privacy_report

BOOK = "static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf"


class Phase37FamilyBookStaticExposure(unittest.TestCase):
    def test_static_serving_disabled_without_breaking_local_book(self):
        configuration = tomllib.loads(
            (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        )
        self.assertIs(configuration["server"]["enableStaticServing"], False)
        self.assertTrue(available_book_pdf({"pdf_asset": BOOK}))
        full_path = book_pdf_path({"pdf_asset": BOOK})
        self.assertTrue(full_path and full_path.is_file())
        self.assertEqual(full_path.parent, BOOKS_DIR)
        self.assertEqual(full_path.stat().st_size, 22944649)

    def test_no_external_unrestricted_full_book_link_or_pdf_iframe(self):
        content = (ROOT / "family_books.py").read_text(encoding="utf-8")
        tree = ast.parse(content)
        declared = {node.name for node in tree.body
                    if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("full_book_url", declared)
        self.assertIn("display_authorized_book", declared)
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
        ]
        self.assertFalse(any(node.func.attr in {"iframe", "link_button"}
                             for node in calls))
        self.assertTrue(any(node.func.attr == "pdf" for node in calls))
        self.assertNotIn('"/app/static/"', content)
        self.assertNotIn("st.download_button(", content)

    def test_local_book_pdf_path_rejects_arbitrary_files(self):
        for path in (
            "../../private.jpg", "/tmp/unknown.pdf", "static/../data/people.json",
            "static/books/../../data/people.json",
            "static/books/source.txt", "data/people.json",
            "https://example.net/book.pdf",
        ):
            with self.subTest(path=path):
                self.assertIsNone(book_pdf_path({"pdf_asset": path}))
        self.assertTrue(available_book_pdf({"pdf_asset": BOOK}))

    def test_released_dependencies_have_embedded_pdf_viewer_extra(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("streamlit[pdf]==1.62.0", requirements)
        self.assertNotIn("streamlit==1.62.0\n", requirements)

    def test_login_still_first_and_public_repo_remains_explicitly_unfixed(self):
        report = archive_privacy_report(ROOT)
        self.assertTrue(report["web_login_precedes_archive_load"])
        self.assertFalse(report["streamlit_static_serving_enabled"])
        self.assertTrue(report["predictable_static_book_urls_disabled"])
        self.assertTrue(report["existing_legacy_password_fallback"])
        self.assertTrue(report["complete_family_book_committed_to_repository"])
        self.assertIn("GitHub repository visibility",
                      report["approval_required_before"])


if __name__ == "__main__":
    unittest.main()
