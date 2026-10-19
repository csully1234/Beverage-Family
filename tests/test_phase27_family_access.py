"""Phase 27: one family login, no role tiers, and a fail-closed secret cutover."""
from __future__ import annotations

import unittest

from family_access import (
    matches_family_password,
    session_authorized,
    session_password_fingerprint,
    valid_deployment_password,
)

TEST_SECRET = "separate-strong-family-secret-2026"


class FamilyAccessPolicyTests(unittest.TestCase):
    def test_shared_family_login_grants_all_sections_without_role_tiers(self):
        self.assertTrue(valid_deployment_password(TEST_SECRET))
        self.assertTrue(matches_family_password(TEST_SECRET, TEST_SECRET))
        self.assertFalse(matches_family_password("incorrect", TEST_SECRET))
        self.assertFalse(matches_family_password(TEST_SECRET + "!", TEST_SECRET))
        session = {"password_correct": True,
                   "_family_access_revision": session_password_fingerprint(TEST_SECRET)}
        self.assertTrue(session_authorized(session, TEST_SECRET))
        # This policy is deliberately agnostic to page, relative and document.
        for page in ("home", "people", "tree", "full-tree", "family-books",
                     "archive", "collection", "media", "timeline"):
            with self.subTest(page=page):
                self.assertTrue(session_authorized(session, TEST_SECRET))

    def test_legacy_and_missing_credentials_cannot_unlock_site(self):
        for secret in (None, "", " ", "BEVERAGE", "beverage", "password",
                       "12345678901", " long-secret-with-initial-space",
                       "long-secret-with-trailing-space "):
            with self.subTest(secret=secret):
                self.assertFalse(valid_deployment_password(secret))
                self.assertIsNone(session_password_fingerprint(secret))
                self.assertFalse(matches_family_password(secret or "", secret))
                self.assertFalse(session_authorized({"password_correct": True}, secret))

    def test_rotation_invalidates_previous_authenticated_sessions(self):
        previous = "previously-configured-strong-secret"
        successor = "newly-configured-strong-secret"
        old_session = {
            "password_correct": True,
            "_family_access_revision": session_password_fingerprint(previous)
        }
        self.assertTrue(session_authorized(old_session, previous))
        self.assertFalse(session_authorized(old_session, successor))
        self.assertFalse(session_authorized({"password_correct": True}, successor))
        self.assertFalse(session_authorized({
            "password_correct": False,
            "_family_access_revision": session_password_fingerprint(successor),
        }, successor))


if __name__ == "__main__":
    unittest.main()
