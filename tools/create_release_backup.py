"""Create a checksum-verified archive of publicly tracked family-site source assets.

This is a disaster-recovery supplement to Git history, NOT a backup of Render
secret variables, private probate-office copies, or external archival sites.
The output is an Actions artifact, never committed to the repository.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

try:
    from tools.privacy_audit import blocked_source_path
except ModuleNotFoundError:  # Support python tools/create_release_backup.py too.
    from privacy_audit import blocked_source_path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files(root: Path) -> list[str]:
    results = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True, stdout=subprocess.PIPE,
    )
    # A working disaster-recovery checkout needs config, schemas and package
    # metadata as well as Python, histories and assets. Do not silently omit
    # tracked files simply because their extension is unfamiliar.
    return sorted(
        path for path in results.stdout.decode("utf-8").split("\0")
        if path and not blocked_source_path(path)
        and "secrets.toml" not in path.lower()
        and ".env" not in path.lower()
    )


def create_backup(destination: Path, root: Path = ROOT) -> dict:
    destination = destination.resolve()
    archive_files = tracked_files(root)
    manifest = {
        "format": "beverage-family-source-backup-v1",
        "scope": "all Git-tracked non-secret files needed to reconstruct a source checkout",
        "excludes": ["Render environment variables", "offline probate archive",
                     "untracked local files", "historical external websites"],
        "files": {},
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as backup:
        for relative in archive_files:
            file = (root / relative).resolve()
            if not file.is_file() or root.resolve() not in file.parents:
                raise ValueError("Invalid tracked source: " + relative)
            contents = file.read_bytes()
            manifest["files"][relative] = {
                "size_bytes": len(contents),
                "sha256": hashlib.sha256(contents).hexdigest(),
            }
            backup.writestr(relative, contents)
        backup.writestr("BACKUP_MANIFEST.json",
                        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "family-release-backup.zip"
    manifest = create_backup(destination)
    print(f"Snapshot {len(manifest['files'])} tracked source files into {destination} "
          f"({destination.stat().st_size} bytes).")
    print("This archive excludes secrets and unpublished probate-office scans.")


if __name__ == "__main__":
    main()
