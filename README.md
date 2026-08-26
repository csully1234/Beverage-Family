# Beverage Family of North Haven

A password-gated, source-first Streamlit archive for exploring the Beverage family tree, individual profiles, North Haven history, timeline events, and ongoing genealogical research.

## What the site now includes

- a coastal, mobile-responsive visual design;
- a searchable profile index with stable profile links;
- ancestor, descendant, combined, and immediate-family tree views;
- reciprocal relationship navigation without silently rewriting source records;
- a filterable timeline with person, year, evidence, and full-text filters;
- a research desk with data-quality findings and support for optional sourced notes;
- JSON and CSV archive exports;
- an automated data-quality report;
- regression guards for user-designated protected content;
- GitHub Actions checks for syntax, data validity, and tests.

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

These three files are optional and are not required to run the site. An overlay with the same stable ID replaces that record only in the displayed dataset. Base files are never edited during application startup.

## Validate changes

```bash
python validate_data.py
python -m unittest discover -s tests -v
python -m compileall -q app.py family_data.py validation.py validate_data.py
```

Warnings identify open research or normalization work. Errors identify broken JSON, duplicate IDs, missing required fields, or a change to protected content.

## Evidence policy

1. Prefer original institutional records.
2. Use institutional archives and published histories with clear citations.
3. Treat compiled trees and memorial pages as leads unless corroborated.
4. Mark provisional relationships **UNVERIFIED / PROVISIONAL**.
5. Do not invent a person or relationship to fill a visual gap.

## Project structure

```text
app.py                 Streamlit interface and navigation
family_data.py         Shared loading, formatting, and relationship logic
validation.py          Structural and protected-content checks
validate_data.py       Command-line audit
data/                  Base records and optional reviewed research overlays
tests/                 Regression tests
.github/workflows/     Continuous validation
.streamlit/            Theme and secrets example
```
