"""Verify release backups before treating them as recoverable family archives.

No automatic extraction of archive paths is permitted. A verified archive can
optionally be restored into a *new empty directory* for a recovery drill.
The script never reads Render environment credentials or external websites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

from tools.privacy_audit import blocked_source_path

MANIFEST_NAME = "BACKUP_MANIFEST.json"
MAX_FILES = 5000
MAX_TOTAL_UNCOMPRESSED = 1024 * 1024 * 1024
MAX_SINGLE_FILE = 300 * 1024 * 1024
MINIMUM_RECOVERY_FILES = {
    "app.py", "requirements.txt", "README.md",
    "data/people.json", "data/events.json",
}


class BackupVerificationError(ValueError):
    """The ZIP does not satisfy the site's disaster-recovery contract."""


def _safe_relative_path(name: str) -> bool:
    if not isinstance(name, str) or blocked_source_path(name) or name == MANIFEST_NAME:
        return False
    return PurePosixPath(name).as_posix() == name and len(name) <= 512


def inspect_backup(archive: Path, *, checkout: Path | None = None,
                   required: set[str] | None = None) -> dict:
    """Verify every member, manifest entry and checksum, with conservative limits."""
    if not archive.is_file():
        raise BackupVerificationError("Backup archive does not exist")
    with zipfile.ZipFile(archive, "r") as handle:
        infos = handle.infolist()
        names = [item.filename for item in infos]
        if not infos or len(infos) > MAX_FILES + 1 or len(set(names)) != len(names):
            raise BackupVerificationError("Backup has duplicate, empty or excessive entries")
        if names.count(MANIFEST_NAME) != 1:
            raise BackupVerificationError("Missing unique backup manifest")
        for info in infos:
            if info.is_dir() or info.flag_bits & 1:
                raise BackupVerificationError("Directories or encrypted members are prohibited")
            if info.filename != MANIFEST_NAME and not _safe_relative_path(info.filename):
                raise BackupVerificationError("Unsafe file name in release archive")
            # POSIX symbolic links can redirect extractions outside the target.
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise BackupVerificationError("Symbolic links are not source files")
            if info.file_size > MAX_SINGLE_FILE or info.file_size < 0:
                raise BackupVerificationError("Oversized or invalid backup member")
        if sum(info.file_size for info in infos) > MAX_TOTAL_UNCOMPRESSED:
            raise BackupVerificationError("Backup exceeds safe uncompressed size")
        raw_manifest = handle.read(MANIFEST_NAME)
        if len(raw_manifest) > 2_000_000:
            raise BackupVerificationError("Manifest exceeds the safe size")
        try:
            manifest = json.loads(raw_manifest)
        except (ValueError, UnicodeError) as exc:
            raise BackupVerificationError("Invalid JSON backup manifest") from exc
        if manifest.get("format") != "beverage-family-source-backup-v1":
            raise BackupVerificationError("Unexpected backup format")
        entries = manifest.get("files")
        if not isinstance(entries, dict) or len(entries) > MAX_FILES:
            raise BackupVerificationError("Invalid manifest file list")
        wanted = set(entries)
        present = set(names) - {MANIFEST_NAME}
        if not wanted or wanted != present:
            raise BackupVerificationError("Manifest and ZIP file inventories disagree")
        need = required if required is not None else MINIMUM_RECOVERY_FILES
        if not need <= wanted:
            raise BackupVerificationError("Required site recovery files are missing")
        file_count, total = 0, 0
        for name in sorted(wanted):
            if not _safe_relative_path(name):
                raise BackupVerificationError("Untrusted tracked path in manifest")
            record = entries[name]
            if not isinstance(record, dict):
                raise BackupVerificationError("Invalid checksum record")
            if not isinstance(record.get("size_bytes"), int):
                raise BackupVerificationError("Invalid expected file length")
            digest = record.get("sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise BackupVerificationError("Invalid checksum field")
            data = handle.read(name)
            if len(data) != record["size_bytes"] or hashlib.sha256(data).hexdigest() != digest:
                raise BackupVerificationError("Backup file checksum mismatch")
            if checkout is not None:
                original = (checkout / name).resolve()
                base = checkout.resolve()
                if base not in original.parents or not original.is_file():
                    raise BackupVerificationError("Backup entry does not exist in checkout")
                if hashlib.sha256(original.read_bytes()).hexdigest() != digest:
                    raise BackupVerificationError("Backup differs from the checked-out release")
            total += len(data)
            file_count += 1
    return {
        "format": manifest["format"],
        "verified_files": file_count,
        "verified_bytes": total,
        "has_family_book": any(name.startswith("static/books/") and
                               name.endswith(".pdf") for name in wanted),
        "checksum_validation": "passed",
        "verified_against_checkout": checkout is not None,
        "excluded_from_backup": manifest.get("excludes", []),
    }


def restore_verified_backup(archive: Path, target: Path,
                            *, required: set[str] | None = None) -> dict:
    """Restore only after full verification and only into an empty new directory."""
    result = inspect_backup(archive, required=required)
    target = target.resolve()
    if target.exists() and any(target.iterdir()):
        raise BackupVerificationError("Refusing to overwrite a nonempty restore directory")
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "r") as handle:
        for member in handle.namelist():
            if member == MANIFEST_NAME:
                continue
            destination = (target / member).resolve()
            if target not in destination.parents:
                raise BackupVerificationError("Unsafe restore destination")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(handle.read(member))
        (target / MANIFEST_NAME).write_bytes(handle.read(MANIFEST_NAME))
    return dict(result, restored_to_new_directory=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify/restore a checksum-pinned source backup")
    parser.add_argument("zip_file", type=Path)
    parser.add_argument("--against-checkout", type=Path)
    parser.add_argument("--restore-to", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        result = inspect_backup(args.zip_file, checkout=args.against_checkout)
        if args.restore_to:
            restore_verified_backup(args.zip_file, args.restore_to)
    except (BackupVerificationError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        # Report no filenames or archive payload in the output on failure.
        print("Family archive backup verification FAILED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
