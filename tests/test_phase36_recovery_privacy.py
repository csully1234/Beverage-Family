"""Phase 36: test backup extraction against corruption, path tricks and privacy regressions."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from tools.create_release_backup import tracked_files
from tools.privacy_audit import (
    archive_privacy_report, blocked_source_path, gate_before_archive_load,
)
from tools.verify_release_backup import (
    BackupVerificationError, MINIMUM_RECOVERY_FILES,
    inspect_backup, restore_verified_backup,
)

ROOT = Path(__file__).resolve().parents[1]


class Phase36RecoveryAndPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = {
            name: ("fixture: " + name + "\n").encode("utf-8")
            for name in MINIMUM_RECOVERY_FILES
        }
        self.inputs["static/books/source.pdf"] = b"%PDF-1.7\nfixture only"
        self.archive = self.root / "snapshot.zip"
        self.checkout = self.root / "checkout"
        for name, contents in self.inputs.items():
            file = self.checkout / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(contents)

    def write_archive(self, items=None, manifest_files=None):
        items = self.inputs if items is None else items
        files = manifest_files if manifest_files is not None else {
            name: {"size_bytes": len(contents),
                   "sha256": hashlib.sha256(contents).hexdigest()}
            for name, contents in self.inputs.items()
        }
        metadata = {
            "format": "beverage-family-source-backup-v1",
            "scope": "safe read-only source",
            "files": files,
            "excludes": ["Render secrets", "offline originals"],
        }
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, payload in items.items():
                z.writestr(name, payload)
            z.writestr("BACKUP_MANIFEST.json", json.dumps(metadata).encode("utf-8"))

    def test_good_backup_restores_every_verified_file_to_empty_directory(self):
        self.write_archive()
        report = inspect_backup(self.archive, checkout=self.checkout)
        self.assertEqual(report["checksum_validation"], "passed")
        self.assertEqual(report["verified_files"], len(self.inputs))
        self.assertTrue(report["verified_against_checkout"])
        self.assertTrue(report["has_family_book"])
        dest = self.root / "restored"
        result = restore_verified_backup(self.archive, dest)
        self.assertTrue(result["restored_to_new_directory"])
        for name, payload in self.inputs.items():
            self.assertEqual((dest / name).read_bytes(), payload)
        self.assertTrue((dest / "BACKUP_MANIFEST.json").is_file())

    def test_tampering_after_manifest_creation_is_rejected(self):
        self.write_archive(items=dict(self.inputs, **{"data/people.json": b"ALTERED"}))
        with self.assertRaisesRegex(BackupVerificationError, "checksum mismatch"):
            inspect_backup(self.archive)

    def test_missing_required_file_or_unmanifested_extra_is_rejected(self):
        items = dict(self.inputs)
        items.pop("app.py")
        self.write_archive(items=items)
        with self.assertRaisesRegex(BackupVerificationError, "inventories disagree"):
            inspect_backup(self.archive)
        items = dict(self.inputs)
        items["unlisted.dat"] = b"not on manifest"
        self.write_archive(items=items)
        with self.assertRaisesRegex(BackupVerificationError, "inventories disagree"):
            inspect_backup(self.archive)

    def test_zip_slip_and_fake_secret_paths_are_rejected_without_writing(self):
        for bad in ("../outside.txt", "/absolute.txt", "data/../outside",
                    ".streamlit/secrets.toml", "private_scans/case.jpg",
                    "data\\unsafe.txt"):
            with self.subTest(bad=bad):
                self.write_archive(items=dict(self.inputs, **{bad: b"danger"}))
                with self.assertRaises(BackupVerificationError):
                    restore_verified_backup(self.archive, self.root / "restore-area")
                self.assertFalse((self.root / "outside.txt").exists())

    def test_existing_contents_cannot_be_overwritten(self):
        self.write_archive()
        target = self.root / "restore-area"
        target.mkdir()
        (target / "previous-work.txt").write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(BackupVerificationError, "nonempty"):
            restore_verified_backup(self.archive, target)
        self.assertEqual((target / "previous-work.txt").read_text(), "preserve")

    def test_cross_commit_backup_fails_checkout_checksum_review(self):
        self.write_archive()
        (self.checkout / "data" / "events.json").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(BackupVerificationError, "differs"):
            inspect_backup(self.archive, checkout=self.checkout)

    def test_duplicate_zip_members_are_never_restored(self):
        self.write_archive()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "a") as z:
                z.writestr("app.py", b"conflicting bytes")
        with self.assertRaisesRegex(BackupVerificationError, "duplicate"):
            inspect_backup(self.archive)

    def test_git_filename_guard_never_treats_example_as_real_secret(self):
        self.assertFalse(blocked_source_path(".streamlit/secrets.toml.example"))
        for danger in (".streamlit/secrets.toml", ".env", ".env.production",
                       "sub/.env.local", "keys/id_rsa", "offline_probate/01.jpg",
                       "private_scans/test.pdf", "../escape", "/etc/passwd",
                       "key.pem", "credentials.json", "notes\\escape"):
            with self.subTest(path=danger):
                self.assertTrue(blocked_source_path(danger))
        self.assertFalse(blocked_source_path("static/books/approved-family-book.pdf"))
        self.assertFalse(blocked_source_path("data/people.json"))

    def test_complete_site_recovery_includes_configs_and_build_files(self):
        paths = tracked_files(ROOT)
        must_restore = {
            "app.py", ".streamlit/config.toml",
            "schemas/archive.schema.json", "package.json", "package-lock.json",
            "requirements.txt", "data/people.json", "data/events.json",
            "static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf",
            "tools/verify_release_backup.py", ".github/workflows/validate.yml",
        }
        self.assertTrue(must_restore <= set(paths),
                        "A recoverable site must preserve runtime config and build inputs")
        self.assertFalse(any(blocked_source_path(p) for p in paths))
        self.assertFalse(any("secrets.toml" in p or ".env" in p for p in paths))
        self.assertGreater(len(paths), 200)

    def test_real_app_runs_family_gate_before_loading_any_archive(self):
        report = archive_privacy_report(ROOT)
        self.assertFalse(report["blocked_tracked_paths"])
        self.assertTrue(report["web_login_precedes_archive_load"])
        self.assertTrue(report["existing_legacy_password_fallback"])
        self.assertTrue(report["family_data_committed_to_repository"])
        self.assertTrue(report["complete_family_book_committed_to_repository"])
        self.assertTrue(report["streamlit_static_serving_enabled"])
        self.assertEqual(report["render_app_password_configuration"],
                         "not inspected; never print secret values")
        self.assertFalse(gate_before_archive_load(
            "def main():\n    load_data()\n    check_password()\n"))
        self.assertTrue(gate_before_archive_load(
            "def main():\n    check_password()\n    load_data()\n"))


if __name__ == "__main__":
    unittest.main()
