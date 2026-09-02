"""Command-line data audit used locally and by GitHub Actions."""

from __future__ import annotations

import argparse
from pathlib import Path

from family_data import load_site_data
from validation import validate_site_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Beverage Family data")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat research-quality warnings as failures",
    )
    args = parser.parse_args()

    data = load_site_data(Path(__file__).parent / "data")
    report = validate_site_data(data)

    print(
        f"Validated {len(data['people'])} people, {len(data['events'])} events, "
        f"and {len(data['research'])} research notes."
    )
    print(f"Archive: {len(data.get('places', []))} places, "
          f"{len(data.get('archive_sources', []))} sources, "
          f"{len(data.get('place_links', []))} place assertions.")
    for issue in report.issues:
        print(f"{issue.severity.upper():7} {issue.code}: {issue.message}")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 2
    print("PASS: no blocking data errors; protected records are unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
