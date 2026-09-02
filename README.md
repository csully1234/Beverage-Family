# Beverage Family of North Haven

A password-gated, source-first Streamlit archive for exploring the Beverage family tree, individual profiles, North Haven history, timeline events, and ongoing genealogical research.

## What the site now includes

- a coastal, mobile-responsive visual design with high-contrast controls and status messages;
- a global search across names, aliases, places, occupations, dates, events, notes, and sources;
- a searchable profile index with stable profile links;
- the original focused family-tree explorer with ancestor, descendant, combined, and immediate-family views;
- a separate **Full Family Map** containing every indexed profile plus unresolved relationship nodes, with drag-to-pan, wheel/button zoom, fit-to-screen, 100% reset, and person jump controls;
- a shortest-path relationship finder with readable, linked steps;
- reciprocal relationship navigation without silently rewriting source records;
- a filterable timeline with person, year, category, place, precision, evidence, and full-text filters;
- truthful display of exact, month-only, year-only, approximate, and unknown dates;
- an interactive source explorer and research desk with claim-level citations;
- a normalized **Source Archive**, **Historical Places** records, and a **Historical Map** with cited person/event connections, category and year filters, and person/event navigation;
- homepage statistics, a daily featured relative, exact-date “On This Day” records, and recent research;
- JSON and CSV archive exports;
- an automated data-quality report;
- regression guards for user-designated protected content and navigation-state bugs;
- GitHub Actions checks on Python 3.12 and 3.13 for syntax, data validity, and tests.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

## Configure the family password

The app reads `APP_PASSWORD` from either an environment variable or Streamlit secrets. For local development:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then replace the example value. The real `secrets.toml` file is ignored by Git. The existing password remains as a compatibility fallback so the current deployment does not break before a secret is configured.

## Data layout

The original family records remain in:

- `data/people.json`
- `data/events.json`

When separately reviewed research files are present, they are layered on top at runtime:

- `data/research_people.json`
- `data/research_events.json`
- `data/research.json`
- `data/date_precision.json`

These four files are optional and are not required to run the site. A same-ID research overlay patches only its explicitly supplied fields; it does not discard an existing profile's relationships, residences, notes, or citations unless that field is intentionally supplied by the overlay. Date metadata keeps the original stored string for provenance while controlling truthful visitor-facing precision. Base files are never edited during application startup.

Structured citations can include `title`, `repository`, `url`, `record_type`, `record_date`, `page`, `record_identifier`, `accessed`, `supports`, and `evidence_level`. Legacy source strings remain supported.

### Source archive and geographic history

The historical archive extends the overlays without changing them:

- `data/archive_sources.json`: stable bibliographic records, evidence summaries, conflicts, and people/event/place references;
- `data/places.json`: public historical places, parent places, modern representative coordinates, and coordinate provenance;
- `data/place_links.json`: dated, cited assertions connecting one existing person or event to one place;
- `schemas/archive.schema.json`: version 1 JSON Schema, enforced by the genealogy validator.

Open `?page=map`, `?page=places`, or `?page=archive`. Deep links support `?page=map&person=harold_h_beverage_1893`, `?page=map&event=event_north_haven_bridge_act_1848`, `?page=places&place=pulpit_harbor_me`, and `?page=archive&source=src_bridge_act_1848`. These use the existing Streamlit query routing and family-password gate.

The map uses locally vendored Leaflet 1.9.4 and OpenStreetMap tiles. It needs no API key or geocoder. Pins and a keyboard-accessible list share the same detail panel. Tiles require internet access; records remain usable if tiles fail. External map requests send only tile coordinates and the site origin, not profile IDs or residence data. Read the [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/) before materially scaling traffic or changing caching.

Place confidence describes the geographic reference, not certainty about every historical claim. Town/country points are not buildings, travel paths, or historical boundaries. Dates filter **documented connections**, not a person's inferred lifetime. Undated links have an explicit toggle. Event locations do not automatically become person locations: for example, a court petition's subject towns do not prove the petitioner's presence there.

For the seeded inventory, linking rules, provenance, testing limits, and Phase 2 work, see [the implementation report](research/source_archive_historical_map_2026-09-02.md).

## Validate changes

```bash
python validate_data.py
python -m unittest discover -s tests -v
python -m compileall -q app.py family_data.py full_tree.py validation.py validate_data.py
```

The map's DOM and interaction tests are development-only and require Node 22+:

```bash
npm ci --ignore-scripts
npm test
```

Node is not needed to run the Streamlit site. These tests execute the bundled map document and Leaflet in jsdom, with network fetching disabled. They complement Streamlit route tests; they do not substitute for a visual browser review on the normal Streamlit deployment.

Warnings identify open research or normalization work. Errors identify broken JSON, duplicate IDs, missing required fields, invalid precision metadata, or a change to protected content or existing residence data.

## Evidence policy

1. Prefer original institutional records.
2. Use institutional archives and published histories with clear citations.
3. Treat compiled trees and memorial pages as leads unless corroborated.
4. Mark provisional relationships **UNVERIFIED / PROVISIONAL**.
5. Do not invent a person or relationship to fill a visual gap.

## Project structure

```text
app.py                 Streamlit interface, navigation, and page rendering
family_data.py         Shared loading, formatting, and relationship logic
full_tree.py           Dependency-free full-family map layout and interactive HTML
validation.py          Structural and protected-content checks
validate_data.py       Command-line audit
data/                  Base records and optional reviewed research overlays
tests/                 Regression and data-integrity tests
.github/workflows/     Continuous validation on Python 3.12 and 3.13
.streamlit/            Theme, production client settings, and secrets example
```
