"""Streamlit smoke test for all-or-nothing archive login configuration."""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class Phase27LoginSmokeTests(unittest.TestCase):
    def test_no_deployment_secret_fails_closed_without_prompting_for_old_default(self):
        with patch.dict(os.environ, {"APP_PASSWORD": ""}):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception, [x.value for x in app.exception])
        self.assertEqual(len(app.text_input), 0)
        self.assertTrue(any(
            "temporarily unavailable" in str(element.message if hasattr(element, "message")
                                               else element.value)
            for element in app.error
        ))

    def test_one_family_password_opens_archive_home_and_source_navigation(self):
        with patch.dict(os.environ, {"APP_PASSWORD": "test-family-access-secret-strong"}):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception, [x.value for x in app.exception])
            self.assertEqual(len(app.text_input), 1)
            app.text_input[0].input("test-family-access-secret-strong")
            app.button[0].click()
            app.run()
            self.assertFalse(app.exception, [x.value for x in app.exception])
            self.assertTrue(app.session_state["password_correct"])
            self.assertTrue(app.session_state["_family_access_revision"])
            self.assertTrue(any("Start exploring" in str(e.value) for e in app.subheader))


if __name__ == "__main__":
    unittest.main()
