"""Security guard for external citations and authenticated internal links."""
from __future__ import annotations

import unittest

from routing_ui import safe_external_url


class ExternalCitationLinkTests(unittest.TestCase):
    def test_only_standard_uncredentialed_web_urls_are_accepted(self):
        allowed = (
            "https://maineroots.org/images/Nov25TMG2.pdf",
            "https://archive.org/details/historyofcobbfam13cobb",
            "http://example.com/records?q=Matt%20Beveridge",
        )
        blocked = (
            None, "", "?page=people", "javascript:alert(1)", "data:text/html,hi",
            "file:///etc/passwd", "ftp://example.com/records",
            "https://user:password@example.com/", "https://example.com:8080/unsafe",
            "https://example.com/path with spaces",
            "https://example.com/<script>",
            "https://example.com\\attacker.invalid",
            "https:///missinghost",
        )
        for url in allowed:
            with self.subTest(url=url):
                self.assertTrue(safe_external_url(url))
        for url in blocked:
            with self.subTest(url=url):
                self.assertFalse(safe_external_url(url))


if __name__ == "__main__":
    unittest.main()
