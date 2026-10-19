"""Reproducible, offline release audit for the Beverage family archive.

Reports what files are actually in the DEPLOYABLE repository: book pages,
approved media, probate rights gates, and navigation targets. Never tests
external archives with speculative HTTP requests or discloses credentials.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE_RE = re.compile(r"\?page=([a-z][a-z0-9-]*)")
SOURCE_FILES = (
    "app.py", "visitor_journeys.py", "visitor_ui.py", "family_discoveries.py",
    "family_exhibits.py", "profile_life_stories.py", "family_books.py",
    "waldo_probate.py", "matthew_deed_research.py", "family_origins_casework.py",
    "family_research_workbench.py", "event_source_access.py", "routing_ui.py",
)


def safe_repo_file(root: Path, relative: str) -> Path | None:
    """Never use a manifest filename to open anything outside the checkout."""
    if not relative or "\\" in relative or relative.startswith("/"):
        return None
    base = root.resolve()
    path = (base / relative).resolve()
    if path != base and base not in path.parents:
        return None
    return path


def official_page_slugs(root: Path) -> set[str]:
    """Read route names from the real app without executing Streamlit."""
    tree = ast.parse((root / "app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PAGE_SLUGS"
            for target in node.targets
        ):
            return set(ast.literal_eval(node.value).values()) | {"research", "sources"}
    raise ValueError("Application has no explicit PAGE_SLUGS table")


def verify_book_assets(root: Path) -> list[dict]:
    books = json.loads((root / "data/book_sources.json").read_text(encoding="utf-8"))
    rows = []
    for entry in books:
        relative = str(entry.get("pdf_asset") or "")
        path = safe_repo_file(root, relative)
        expected = int(entry.get("pdf_page_count") or 0)
        if not relative.startswith("static/books/") or not relative.endswith(".pdf"):
            rows.append({"id": entry.get("id"), "status": "invalid_path", "expected_pages": expected})
            continue
        if path is None or not path.is_file():
            rows.append({"id": entry.get("id"), "status": "missing", "expected_pages": expected})
            continue
        import fitz
        with fitz.open(path) as doc:
            actual = doc.page_count
        rows.append({
            "id": entry.get("id"), "status": "verified" if actual == expected else "page_count_mismatch",
            "expected_pages": expected, "actual_pages": actual,
            "size_bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return rows


def media_status(root: Path) -> dict:
    manifest = json.loads((root / "data/media_manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise ValueError("Approved media manifest must be a list")
    exposed, omitted = [], []
    for entry in manifest:
        relative = str(entry.get("local_path") or "")
        path = safe_repo_file(root, relative)
        approved = entry.get("rights_status") in {"permission", "public_domain"}
        exists = bool(path and path.is_file() and relative.startswith("static/approved_media/"))
        (exposed if approved and exists else omitted).append(str(entry.get("item_identifier") or relative))
    probate = json.loads((root / "data/phase22_matthew_waldo_probate.json").read_text(encoding="utf-8"))[0]
    return {
        "approved_original_images": len(exposed),
        "unavailable_or_unapproved_media": omitted,
        "probate_received_scans": len(probate["scans"]),
        "probate_unique_scans": len({r["sha256"] for r in probate["scans"]}),
        "probate_publication_authorized": bool(probate.get("image_publication_authorized", False)),
    }


def literal_route_audit(root: Path) -> dict:
    slugs = official_page_slugs(root)
    usages: dict[str, set[str]] = {}
    for filename in SOURCE_FILES:
        f = root / filename
        if not f.is_file():
            continue
        for match in PAGE_RE.finditer(f.read_text(encoding="utf-8")):
            usages.setdefault(match.group(1), set()).add(filename)
    return {
        "known_page_slugs": sorted(slugs),
        "literal_routes_checked": sum(len(v) for v in usages.values()),
        "unknown_literal_routes": {slug: sorted(files) for slug, files in usages.items()
                                   if slug not in slugs},
    }


def report(root: Path = ROOT) -> dict:
    return {
        "book_assets": verify_book_assets(root),
        "media": media_status(root),
        "navigation": literal_route_audit(root),
        "security": {
            "legacy_password_fallback_present": "LEGACY_COMPATIBILITY_PASSWORD" in
                (root / "app.py").read_text(encoding="utf-8"),
            "production_password_variable": "must be confirmed in Render; not inspected by this audit",
            "public_repository_is_not_private_storage": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit checked-in assets and static source routes")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = report()
    data = json.dumps(payload, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data, encoding="utf-8")
    print(data)
    bad_book = any(row["status"] != "verified" for row in payload["book_assets"])
    invalid_route = bool(payload["navigation"]["unknown_literal_routes"])
    if bad_book or invalid_route:
        print("Release blocked: a required book is missing/invalid or a known source route is unresolved.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
