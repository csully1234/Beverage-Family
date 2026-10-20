# Phase 35 — Whole-family evidence-access atlas and identity-reference casework

**Date:** 19 October 2026  
**Starting point:** Phase 34 merged and confirmed live on Render; GitHub `main` has no open pull requests.  
**Scope:** One substantial cross-archive usability and genealogical-integrity release, without modifying original imported records or identity claims.

## The verified structural problem

This phase begins from the **effective** people records (base, reviewed research overlays, period-specific corrections), rather than an assumed old database: **202 indexed profiles, four disconnected connected components and six referenced relationship IDs that are not indexed people**. Of 202 profiles, 109 had no direct HTTP(S) URL in their own `sources` entries before checking the other sections of the archive. That number should not be presented as 109 undocumented people: source pointers may be attached to events, edited exhibits, relationship review cards and the family book.

The full tree has around 700 distinct parent-child, spouse and explicit/inferred sibling links. The Phase 29 audit found only 23 **individual link-specific** evidence reviews. Review coverage is different from genealogical correctness. None of the four separate branch groups should be connected because names or locations resemble each other.

## What Phase 35 implements

### 1. Exact-person evidence access across the whole archive

New pure Python `archive_triage.py` produces an inventory **for every effective person ID** from the existing source catalogs:

- Direct profile citations and curated source exhibits attached by exact person ID.
- Original-event citations attached to dated events by exact `people_involved` ID, including event-scoped curated exhibits.
- Research Workbench results attached by exact person IDs, **excluding OCR-only matches and ordinary profile search hits**.
- Individual family-link review sources from the entire relationship audit.
- Book-photo page references attached via the existing exact-person crosswalk.

It deduplicates external URLs within each category and across the entire person's display, applying the same safe-URL policy used by the visitor link control. It also keeps valid internal research destinations and book PDF pages accessible. Source links are access **routes**, not a representation that every source has been inspected, that its contents prove kinship, that links are live today, or that images may be republished.

### 2. Usable visitor source atlas

New `research_triage_ui.py`, integrated in the established **Historical Discoveries → Family history evidence dashboard → Source access for all**, offers a searchable/filterable complete person index:

- Everyone or relative-specific cases with **no external URL in any indexed category**.
- Cases with no direct URL in their profile bibliography but accessible links somewhere else.
- Profiles with source-reviewed relationships, or exact-attributed book photo pages.
- Every qualifying direct source link for the selected person, with source category and the exact original research, record and book routes.
- One click to profile, original-record/event reader, and individual family relationship evidence.
- A CSV of all 202 people and documentation/access counts, never a percentage of historically proven ancestors.

This is a full index rather than an arbitrary first-25 or first-100 truncation, while displaying one person's complete linked sources at a time to keep phones usable. Visitors can enter it from the homepage or a person's profile.

### 3. Six unresolved-identity case packets instead of ghost relatives

The earlier dashboard simply listed each missing ID and a referencing person. The new **Disconnected branches** case desk additionally shows:

- **Exactly which extant person profile explicitly references the missing ID and whether as parent, spouse, child or sibling**.
- Potential *same-first-name and same-last-name* indexed entries for **side-by-side source comparison only**. Middle names and year qualifiers may differ; the suggestion is NOT an identity assertion or family relationship.
- For each unresolved ID, an exact-profile route and a CSV research handoff queue.
- No insertion into `people.json`, no merging, no inferred parentage, and no replacement of uncertain placeholders.

Historical illustrative leads include the unresolved `benjamin_crabtree_beverage_1810?` reference versus the existing Benjamin Crabtree Beverage record, and the unresolved `olive_carver_1780` identifier versus an existing Olive Carver profile. They must **not** be silently equated; birth dates or spouse/parent records may disagree. Other unresolved identifiers can have no candidates.

### 4. Prevent ghost ID shortcuts in relationship paths

`family_data.shortest_relationship_path` now accepts an optional explicit `known_ids` whitelist. The actual site relationship finder passes **all current real profile IDs** into that argument. Thus two known people cannot appear connected *only through an unindexed ghost profile*. Existing general utility behavior is retained for other callers for backward compatibility. Actual canonical family edges and their evidence statuses remain untouched.

### 5. Tests and protected data

New `tests/test_phase35_archive_triage.py` checks:

- Every actual person appears exactly once in the atlas.
- Source URLs deduplicate and retain the correct category origin; OCR-only name hits do not assert person-level source association.
- External-link navigation never implies original manuscript verification; unsafe web addresses are not counted.
- Every missing reference still exists without a fabricated profile, parent or child.
- Graph paths cannot use unknown profile IDs when the visitor whitelist is supplied.
- The existing site password and historical protected data stay unchanged.

Run existing full Python 3.12/3.13 validations, 300+ tests, JS tree/map interactions and release audit before merging. After merge, Render needs a separate manual deployment because its autoDeploy is off. Authenticated browser walkthrough on desktop and mobile remains necessary for final UI verification.

## Separate security / privacy decision that must not be silently changed

**Important:** GitHub currently reports this repository as **public**, and it contains family data as well as the complete authorized `static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf`. The Streamlit password protects the **website user interface**, not the public GitHub repository or its raw assets. Earlier code reviews also identified a built-in legacy family-password compatibility fallback. These are separate from Phase 35's visitor UX fixes and warrant a coordinated security/privacy migration.

A future privacy milestone should evaluate a private GitHub repository and restricted document serving, followed by coordinated Render deployment and a planned replacement of the legacy fallback, **while retaining the same single-family-login experience**. Do not change the current password or lock people out without the owner's explicit approval and a verified working Render configuration.

## Release checklist

1. Ensure both Python versions, existing regression suites, link safety, release audit and tree/map interaction checks pass. Review the PR diff for modifications to historical data (none intended).
2. Confirm new complete "Source access for all" entry in Historical Discoveries, with all indexed people reachable and filters working on narrow screens.
3. Open a family member whose profile bibliography has no direct URL; verify attributed research/event/book evidence still appears when available, without labeling a link as a scanned original.
4. Open all six unresolved-ID cases, inspect references and candidate comparison links, confirm the canonical family tree and separate branch groups are unchanged.
5. Confirm relationship paths cannot navigate through non-indexed relatives. Confirm login remains exactly as before.
6. Deploy the tested merge manually, verify Render commit equals GitHub merge SHA, inspect recent error-level logs and manually open the site authenticated. 
