"""Fail-closed source-file guard and *non-secret* family privacy readiness audit.

This checks what Git makes publishable, not who can currently fetch a URL.
Do not serialize passwords, env var values, family names or living-person rows.
Changing repository visibility and authentication requires a coordinated cutover.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_FILES = {".streamlit/secrets.toml.example", ".env.example"}
BLOCKED_SEGMENTS = {".ssh", ".aws", "credentials", "private_scans", "offline_probate"}
BLOCKED_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".jks", ".kdbx", ".sqlite", ".db"}
BLOCKED_NAMES = {"secrets.toml", ".env", ".env.local", ".env.production",
                 "id_rsa", "id_ed25519", "service-account.json",
                 "credentials.json", "passwords.csv", "passwords.txt"}


def tracked_repo_files(root: Path = ROOT) -> list[str]:
    command = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], check=True,
        capture_output=True,
    )
    return sorted(p for p in command.stdout.decode("utf-8").split("\0") if p)


def blocked_source_path(path: str) -> bool:
    """Prohibit accidental tracking of usual credential/private-file names.

    A named allowlisted *example* contains dummy instructions, never secrets.
    A filename check cannot detect arbitrary private information in harmless-
    sounding files or the old hardcoded legacy password already in app.py.
    """
    if not isinstance(path, str) or not path or "\\" in path or path.startswith("/"):
        return True
    if any(seg in {"", ".", ".."} for seg in path.split("/")):
        return True
    lower = path.lower()
    if lower in EXAMPLE_FILES:
        return False
    name = lower.rsplit("/", 1)[-1]
    return (name in BLOCKED_NAMES or name.startswith(".env.") or
            Path(name).suffix in BLOCKED_SUFFIXES or
            any(segment in BLOCKED_SEGMENTS for segment in lower.split("/")))


def gate_before_archive_load(app_source: str) -> bool:
    """Ensure normal Streamlit main flow checks login before loading data."""
    try:
        tree = ast.parse(app_source)
    except SyntaxError:
        return False
    main = next((node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and node.name == "main"), None)
    if main is None:
        return False
    def direct_call(node):
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            return ""
        f = node.value.func
        return f.id if isinstance(f, ast.Name) else ""
    calls = [direct_call(node) for node in main.body]
    try:
        gate = calls.index("check_password")
        load = next(i for i, item in enumerate(calls)
                    if item in {"load_data", "render_sidebar"})
    except (StopIteration, ValueError):
        # load_data is usually nested in a try statement in this app.
        load_nodes = [node.lineno for node in ast.walk(main)
                      if isinstance(node, ast.Call) and
                      isinstance(node.func, ast.Name) and
                      node.func.id in {"load_data", "render_sidebar"}]
        check_nodes = [node.lineno for node in ast.walk(main)
                       if isinstance(node, ast.Call) and
                       isinstance(node.func, ast.Name) and
                       node.func.id == "check_password"]
        return bool(load_nodes and check_nodes and max(check_nodes) < min(load_nodes))
    return gate < load


def archive_privacy_report(root: Path = ROOT, paths: list[str] | None = None) -> dict:
    paths = tracked_repo_files(root) if paths is None else paths
    failures = [p for p in paths if blocked_source_path(p)]
    app = (root / "app.py").read_text(encoding="utf-8")
    config = (root / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    # This is a source-code risk inventory, NOT an internet penetration test.
    published_pdf = any(p.startswith("static/books/") and p.lower().endswith(".pdf")
                        for p in paths)
    return {
        "format": "family-archive-privacy-readiness-v1",
        "tracked_file_count": len(paths),
        "blocked_tracked_paths": failures,
        "web_login_precedes_archive_load": gate_before_archive_load(app),
        "existing_legacy_password_fallback": "LEGACY_COMPATIBILITY_PASSWORD" in app,
        "family_data_committed_to_repository": "data/people.json" in paths,
        "complete_family_book_committed_to_repository": published_pdf,
        "streamlit_static_serving_enabled":
            bool(re.search(r"(?m)^\s*enableStaticServing\s*=\s*true\b", config,
                           flags=re.IGNORECASE)),
        "repository_visibility": "check GitHub repository settings; not inferred from checkout",
        "render_app_password_configuration": "not inspected; never print secret values",
        "approval_required_before":
            ["changing GitHub repository visibility",
             "modifying Render GitHub linkage or file hosting",
             "replacing the current family login/password",
             "moving or republishing copyright-controlled family materials"],
        "notes": [
            "The current website password gates the app UI, not a public Git repository.",
            "Static file serving may expose book PDF files without the Streamlit login; "
            "verify actual direct URLs and migrate assets to an authenticated path.",
            "Existing legacy password fallback must be migrated without changing family access.",
            "A filename audit cannot certify that living-family data are safe to publish.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check tracked-source privacy safeguards")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = archive_privacy_report()
    text = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    if result["blocked_tracked_paths"] or not result["web_login_precedes_archive_load"]:
        print("Privacy guard failed: tracked restricted file or login gate regression.")
        return 1
    print("Safe-source filename and login-order guard passed. Full privacy cutover remains outstanding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
