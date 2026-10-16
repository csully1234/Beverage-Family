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
- a **Research Collection** with 57 findings, 163 registered sources, 33 retrieval targets, all workbook inventories, a section-by-section dossier reader, and the five original reports;
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

### Matthew's Rockland relatives, documented diaries, and 1749 intention (October 2026)

A follow-up research phase adds **four** distinct public profiles to the existing
historical overlay: Nathaniel Beverage (born about 1804, **not** Nathaniel
Winslow born 1776), his wife Sarah Alexander, their son Henry T. Beverage,
and Henry's later wife Ella Allen. Eaton (1865, vol. II, pp.146–147)
describes the household; the FamilySearch marriage-index trail supports
Henry and Ella's **17 December 1898** marriage. These four profiles have
explicit source provenance; the proposed parentage of 1804 Nathaniel is
**not attached** to the main genealogical line.

A full, accessible 1865 transcription-derived display preserves Capt.
Matthew of Hope's **10 reported children and 11 grandchildren**, plus
Nathaniel's three reported children. Unlike independently verified person
profiles, these additional names are **labeled as a historical family group**,
with no unproved Matthew-to-James relationship grafted onto the family tree.

The **Stories & Discoveries** page now includes two new stories linking the
1865 family group and original material held by the North Haven Historical
Society: Harold Beverage's circa-1930s island film, dated historical society
history, 1907 school graduates, a 1927 auction advertisement, and
**1937/1967 Calderwood diary entries** mentioning Frank/May Beverage and
family-history correspondence with a Samuel Beverage. The original diary
contains a reference to a 1937 photograph; the photograph itself is not
republished. The archive's diary and image permissions are respected.

Seven new historical timeline events include the **1749-02-06 Brunswick
marriage intention** for James Beveridge and Jean White (an *intention*, not
proof of the completed wedding), Henry and Ella's indexed marriage, and
the dated education, auction, archival recovery and diary events. Their
identities and event status are distinguished carefully.

- Source-provenance narrative and original-document to-do:
  `research/matthew_nathaniel_new_sources_2026-10-16.md`
- Capt. Matthew's 1865 family-group transcription and the separate
  1804 Nathaniel identity conflict:
  `research/matthew_nathaniel_family_1865.json`
- Profiles: `data/research_people.json`
- Events: `data/research_events.json`
- Visitor entry point: `?page=stories&story=matthew-rockland-descendants-1865`
- Tests: `tests/test_matthew_nathaniel_2026.py`

No outbound communications, orders, image rehosting, changes to base
people, addresses, or Boston Tea Party history are included in this PR.

### Early-family verification phase 3 — historical records and unanswered identities (October 2026)

The next step is **proving identities and property chains**, not adding inferred
genealogical links. This phase records six prioritized research cases, including:

- Capt. Matthew Beverage's potential 1830s Hope probate: **Waldo County** was
  the relevant county in 1827–1860; Knox County estate files beginning 1861
  do not cover this proposed date.
- The 1786 Putnam report listing original settlers' **declared years of
  settlement**, as cited in *The Maine Genealogist* (November 2025), p. 170
  note 6; its paper archive is not to be confused with the digitized 1785 map.
- Original 1752 Samuel Beveridge and 1758 James Beveridge Topsham land
  entries and the separately numbered Brunswick "Beverage" map label in
  Wheeler's 1878 town history.
- The historically **tentative** Mercy Beveridge–James Henry marriage of
  15 February 1776; original marriage/kinship proof is still needed.
- North Haven's grant/deed chain and the undocumented Scottish origin of
  James Beveridge Sr. (no Scottish parentage silently attached).

The existing map page's research panel now includes four more source-linked
findings, and Stories & Discoveries has a new **Before North Haven: Beveridge
names in Topsham** story. Existing historical profiles remain unchanged.

- Research cases and source register: `research/phase3_research_cases.json`
- Four **unsent** targeted archival request drafts: `research/phase3_archival_requests_not_sent.md`
- Tests: `tests/test_phase3_research.py`

Records offices are identified with publicly documented official contact
information. **No emails have been sent or record orders placed.** Archive
requests and any costs need explicit approval before proceeding.

### Expanded Fox Islands map atlas and founding-era evidence (October 2026)

The **Historical Map** page now has a **Historic maps & early records** tab with ten
source-hosted map images (1776, three 1859 views, 1867, 1868, 1873–74, 1890, 1901,
1941) available in a zoom/pan viewer. Files and survey/publication dates are
verified against the user's `All_NH_Maps.zip` and
[Holmgren's map descriptions](https://holmgren.org/NorthHavenHistoricalMaps/).
No unreviewed image binaries have been committed.

The same page features linked original-era 1785/1786 Fox Islands survey plans from
the Maine State Archives and research notes on the 1785 land petition (James,
Thomas, Matthew Beveridge), Capt. Matthew Beverage in Cyrus Eaton's 1865 local
genealogy, and the Carver connection. These are curated as **research leads,
not automatic changes to the family tree**. A story in **Stories & Discoveries**
provides family-friendly navigation to the cited plans and historical accounts.

- Evidence catalogue: `research/early_fox_islands_evidence.json`
- Full provenance and unresolved questions: `research/fox_islands_land_matthew_carver_2026-10-16.md`
- Atlas UI: `historical_atlas.py` and `static/historical_atlas.html`
- Validation: `tests/test_historical_atlas.py` and the existing JavaScript map tests.

The 1786 legislative **16,527 acres** is an entire-island-group figure; a
historic name or mapped wall does **not** determine Beverage acreage. The
proposed identity of a Matthew born around 1766, his possible father James,
and his identification with Capt. Matthew of Hope remain unresolved. Existing
family relationships, private addresses and the Boston Tea Party claim are unchanged.

### 1859 Fox Islands map gallery

The existing `?page=map` Historical Map page has two tabs. The first retains
the sourced modern place-pin map with its existing deep links; the second shows
three original 1859 map extracts, all from J. Chace Jr. & Co.'s *Map of Waldo
County, Maine*: the North Haven/Vinalhaven island sheet, North Haven village
inset, and Carver's Harbor/Vinalhaven inset.

`historical_atlas.py` supplies descriptions, provenance and exact externally
hosted scan URLs; `static/historical_atlas.html` supplies an independent,
mouse/touch/keyboard-operable zoom and pan viewer. The source imagery remains
served by the [Historical Maps of North Haven Island and Environs](https://holmgren.org/NorthHavenHistoricalMaps/)
collection; this repository has not copied or altered the original scans.
The original image and three-file ZIP are always linked for full-resolution
access or if external hosting becomes temporarily unavailable.

**Research boundaries:** The map's surname/house labels are location leads,
not surveyed parcel outlines, title evidence, or acreage figures. The possible
"B. C. Beverage" identification is provisional, not a confirmed property
assignment. No people, coordinates, historical relationships, or property
records were modified to add this viewer.

### Research collection — 14 October 2026

Open `?page=collection`. Findings link from relevant profiles, places and timeline
records, and participate in global search. The collection has views for findings,
chronology, sources, the retrieval plan, inventories, and reports. Subject filters
include land/property, businesses, images/objects, institutions, and maritime history.
The existing Source Archive also exposes the complete research source register.

Examples:

- `?page=collection&finding=BF-R033` — island registry entries and their limits;
- `?page=collection&person=elliot_beverage_1908` — related Eliot / Elliot research;
- `?page=collection&status=Conflict` — conflicts awaiting family review;
- `?page=archive&source=SRC118` — source details and the findings citing them;
- `?page=collection&target=BF-G001` — a specific retrieval request;
- `?page=collection&view=Reports` — all five original reports and the dossier reader.

`data/collections/2026-10-14.json` is an independent evidence collection, not a
genealogy overlay. No candidate people, disputed dates, inferred relationships,
deed ownership or unlocated properties are inserted into the family tree or map.
Confidence labels, viewed status, exact citations and uncertainty notes are
preserved from the supplied workbooks. The original baseline files, including
the Boston Tea Party claim and residence/property records, remain unchanged.

The reports, navigation cross-references and integrity manifest are in
[`research/collection_2026-10-14`](research/collection_2026-10-14/README.md).
The reproducible importer uses only the Python standard library:

```bash
python tools/import_research_package.py research/collection_2026-10-14
python validate_data.py
```

The workbook's original review statuses are retained. Adding a finding to this
research collection does not mark it as family-reviewed or resolve its identity
questions. All seven source categories still have documented research gaps.

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

### Evidence review and easier family navigation — 15 October 2026

The existing destinations are grouped under **Home, Search, Family, Places,
Archive, and Research**. Their old URL slugs still work. Global search recognizes
Beverage/Beveridge variants and initials, labels approximate name matches,
paginates all results, and keeps the query/place/page in a profile's return link.
Internal controls preserve the same authenticated session instead of opening
a new login tab; external evidence remains a normal link.

- `?page=collection&view=Conflict%20review` — latest outcomes for all 11 conflicts;
- `?page=collection&finding=BF-R008` — baptism evidence, former values and original snapshot;
- `?page=archive&source=CRS003` — Lowell's additional institutional citation;
- `?page=collection&view=Images` — item descriptions, provenance and rights links;
- `?page=search&q=Bevridge&where=North+Haven&results_page=2` — shareable search context.

The separate `data/reviews/conflicts_2026-10-15.json` ledger retains the earlier
claims and proposes changes to three profiles. `conflict_review.py` applies only
allowlisted fields whose former values match, and `validate_data.py` checks every
original conflict is covered with citations and review status. Original data,
reports, integrity hashes, addresses and property claims remain unchanged.
These are evidence-reviewed proposals, **not family approval**.

Read the [evidence review and source register](research/conflict_review_2026-10-15/README.md),
[unsent retrieval requests](research/conflict_review_2026-10-15/retrieval_requests.md),
and [verification report](research/conflict_review_2026-10-15/verification.md).

### Museum-style family exploration (draft PR #11, 15 October 2026)

Six navigation groups are retained. The **Stories & Discoveries** page contains
six grounded, linked narratives. The **People** directory defaults to surname
A–Z, with first-name and chronological sort choices also available in the
individual profile selector. Profile pages display core family relationships
above the existing detailed tabs.

The **Full Family Map** opens around a selected person, with an adjustable
one- to four-step relative neighborhood, a separate whole-family overview,
and a synchronized selected-person dropdown when clicking tree nodes.
The focused tree initializes with the maximum documented depth for the chosen
relative/direction and permits reducing that depth.

The **Complete Family Timeline** combines:
- Existing events and profile birth, baptism, and death records.
- All 57 research findings, including probable, disputed and possible leads.
- Additional research notes, historical place connections, source records,
  archival photo/scan/object descriptions, family stories and documents.
- An undated category for leads without a defensible historical year.

Each chronology entry identifies the *type of date*: event, archival record,
research-associated date, historical connection, publication or story period.
A source's publication year does not establish when its contents happened;
research confidence affects a label and interpretation, never inclusion.

**Photographs & Documents** allows local original scans only with documented
rights and matching item identifiers (see `static/approved_media/README.md`).
External holdings are linked and can appear in in-page previews where the
archive permits them. The 1786 Thomas Beverage dossier has a linked document
reader with an annotated summary, scanned-page source links and a brief
transcribed excerpt; it does not falsely claim to hold a complete original
handwritten affidavit or original photographs without obtaining scans.

**Security before deployment:** The repository remains public and presently
contains the legacy family-password fallback in `app.py`. Do not publish
sensitive living-family information in public source files. Configure a
deployment-managed secret, rotate previously exposed credentials and verify
production access before disabling the fallback; removing it first might
lock out the live website. No visibility, credentials or production settings
are changed in this draft. Automated CI and a production-browser check should
both pass before the PR is merged.

### Person selection and book-catalog update (15 October 2026)
- The full-family explorer now uses a bidirectional Streamlit component, rather
  than an unconnected iframe. A map click sends the selected person ID to Python
  and updates the parent page's selected relative; this selection also follows
  you back to the focused tree. Each click is given a one-time event ID, so
  stale component values cannot override subsequent dropdown selections.
- Whole family overview is the default. The smaller "Explore nearby relatives"
  mode remains available; Fit and Center Selected controls make recentering
  explicit rather than surprising.
- The People directory is again one continuous, scrollable list, with a
  searchable jump dropdown and surname A-Z/Z-A, given-name A-Z/Z-A and
  birth-year sorting. All entries remain available without pagination.
- A privately supplied illustrated family history, *The Colony: Stories from a
  Down East Island* (Lowell P. Beveridge, Jr., 2016), is indexed under Archive
  and the timeline. Chapter topics and selected photo references are recorded
  as research leads, with links from pertinent historical profiles.
- **Book image and page reproduction for this family website is now authorized**,
  as confirmed by the user. The author and copyright notices remain credited;
  no broader sublicensing rights are claimed. A complete 305-page PDF reader
  and 103-page visual index are implemented. The original watermark is retained.
  Upload the supplied 22-MB optimized PDF under `static/books/` on the feature
  branch before merging; see `static/books/README.md`.

### Full illustrated-book reader and tree controls (15 October 2026)
- The user confirms permission to reproduce the entire 2016 book *The Colony*
  on the family website, including its photographs and original page images.
- A 305-page web-optimized PDF (22 MB) has been produced separately from the
  122-MB supplied edition, preserving captions and existing DEMO watermark.
- The book reader offers page jumps, prior/next navigation, browser-native PDF
  controls, full-size individual page previews, chapter browsing and 103
  illustrated source-page entries. The timeline indexes those entries as
  undated photographic/illustrated records where capture dates are unknown.
- The PDF binary is **not part of these source-code-only commits**. Upload the
  supplied optimized file to `static/books/` before merging; otherwise the
  reader truthfully displays a missing-asset notice.
- In the full-family tree, the former ambiguous Steps selector is renamed
  to plain-language relative ranges (Immediate, Close, Extended and Wider).
  It is hidden in Whole Family mode and shown only in Nearby Relatives mode.


### Family-first browsing (15 October 2026)

The visitor site is for relatives, not for reviewing the work done to assemble
the archive. The six sidebar groups now lead to **Home, Search, Family, History,
Places and Archive**. These destinations offer profiles, both family trees,
the complete historical timeline, stories, historical discoveries, locations,
the illustrated family book, photographs, testimony and original historical
sources.

**Visitor pages do not show raw Search Log spreadsheets, workflow inventories,
research work queues, automated data audits, bulk research reports or technical
source-register dashboards.** Historical records are still shown, including
probable and disputed genealogical leads. A source's review status and
genealogical uncertainty remain accessible beside the relevant discovery.

Research work products and the original 436-row search log are retained in the
repository's existing data collection for provenance and later research. They
are not deleted or recast as family events, and the family timeline no longer
counts internal source-register entries, retrieval targets, inventory rows or
research administration as historical moments.

Old bookmarked routes (`?page=collection&view=Inventories&inventory=Search+Log`
and `?page=research`) open the curated Historical Discoveries screen rather
than an internal spreadsheet. Deep links to specific historical findings and
archival sources remain functional. The original scanned-book work is unchanged.

### Book photography and evidence links (15 October 2026)
- The family's **Photographs & Documents** page now opens on a dedicated
  **Family photographs** tab featuring 82 individually captioned photographic
  pages from Lowell P. Beveridge Jr.'s *The Colony* (2016). Search by name,
  location or subject, filter by photograph subject, and browse in book order.
  Load more photographs in batches as needed; every caption links to its
  original full-size book page, where the complete printed caption remains.
- The original photographs and printed text come directly from the authorized,
  watermarked-free 305-page PDF in `static/books`. Images are rendered on demand;
  they are not separately invented/restored or duplicated in GitHub.
- All 103 image-bearing book pages remain available in the complete book. The
  82 photograph pages exclude text-only, tables, maps, and decorative headings.
  Capture dates and person identifications are attributed to the book and are
  not upgraded into independently confirmed genealogical facts.
- **Event and birth-date source access**: the complete timeline and smaller
  event cards now open individual citations under each event. Where the
  original record URL or a specific Find a Grave memorial ID exists, users
  can follow it. When the repository only stores a title like "Riposta
  Funeral Home obituary", the visitor sees "bibliographic reference only"
  until a verified original link/scan is acquired; the count never implies
  that digitized clips are hosted.
- Original internal research notebooks remain outside visitor navigation.
