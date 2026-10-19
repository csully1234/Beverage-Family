# Phase 25 — the family archive as a connected visitor experience

**Implementation date:** 19 October 2026  
**Scope:** create a clear, person-first presentation across the existing source-indexed Streamlit archive; preserve all the protected genealogical records and uncertain historical claims.

## Audit: what was already working

The current repository already contains:

- Password-gated family profiles and person directory, with shared person selectors and exact ID-based navigation.
- Focused and full-family trees, accessible through profile links.
- A full historical timeline with person filters and event-source references.
- Historical Places, a Leaflet map, and event/person historical source indexes.
- A 305-page family book reader and cross-referenced photograph-page captions; the viewer already respects missing source binaries.
- Profile life-record summaries in `profile_life_stories.py`, a separate curated document viewer in `evidence_explorer.py`, and a cross-collection `family_research_index.py` with claim limitations.
- Historical Discoveries with dedicated Matthew Hope, probate and Clarissa Cobb investigation pages.
- CI for Python 3.12 and 3.13, source-data validation, Streamlit page smoke checks and family-map interactions.

**The main gap:** a visitor had to navigate separate pages, tabs and the advanced research desk to understand one ancestor from beginning to end. For example, Matthew's profile cited court records while his document case, research history, family map, and source search lived in different menus. A completely new database or a second global evidence archive would increase complexity, not address that gap.

## Visitor-facing work in this PR

### 1. A consistent person exhibit

New `family_exhibits.py` composes **existing** source and media records into a shareable person exhibit at:

`?page=collection&view=person-exhibit&person=<stable-person-id>`

The four sections are accessible within the same authenticated session; selecting a section synchronizes `section=` in the address bar:

- **Life & timeline:** original profile birth/death fields plus **all** dated linked events, including uncertainty and direct links to each full event citation. No arbitrary eight-event presentation cap.
- **Original records:** distinct profile citations with honest "bibliographic only" statuses, plus cross-indexed original case findings tied to the **exact person ID**. Evidence limitations and originating custodial links remain visible. Filtering and pagination make **every record reachable** without loading hundreds of cards on a phone. OCR words never become person identity matches.
- **Photographs & book:** all pages from the previously reviewed author/editor identity crosswalk, each with the caption and link to the exact book page. Only display a preview when the actual book file exists; do not fabricate an image or substitute a web search result.
- **Family connections:** parents, spouses, children, and siblings using the existing genealogy relationship index, linking known relatives to their own exhibits. Unresolved references remain clearly labeled rather than invented profiles.

A single person-focused header provides profile, focused-tree, and full-map links. Summary figures represent catalog entries, **not counts of independent original sources**.

### 2. Simpler home and consistent navigation

The home page now presents **six principal family-friendly journeys** rather than nine equally dominant tiles, with expert/archive destinations retained in a secondary expander. Featured starting exhibits include Matthew of Hope, Clarissa Cobb and the family-book author Lowell P. Beveridge Jr. These use existing stable IDs and are shown only when the person exists in the loaded site data.

Each profile has a prominent **Explore this relative's life, documents and family photographs** link. The standard visitor-journey bar recognizes when an exhibit is open and keeps the correct selected person (not a stale session-relative).

Historical Discoveries gets a visitor-visible entry point and a new subroute, without a duplicate navigation sidebar group.

## Source and rights boundaries

The new page calls the same existing curated evidence, registered research, life-story and photo crosswalk functions. It never creates a child, dates a wedding, adds a location, rewrites a document, or asserts an OCR word is proof of an identity. Unlinked citation labels and rights limits remain legible. **No new scans** are pushed to public GitHub.

The site has separate files for public image publication and already-authorized family book material. The user reported book reproduction permission; **probate-office image redistribution remains unconfirmed**. The new exhibit does not bypass the `waldo_probate.py` image rights gate.

## Engineering checklist and honest limitations

- Site API tests must pass Python 3.12 and 3.13, including smoke-testing home, full exhibit deep links, section switching, a case with many records, book image pages, family navigation and invalid person IDs.
- Source URLs continue through existing safe link handling. Internal navigation uses session-preserving routes with exact IDs; no external archive browsing occurs within the authenticated site on behalf of a family member.
- The original family tree full-map interface is reused rather than duplicated. A full visual mobile usability/accessibility review on the **deployed** site remains necessary; CI validates code and UI interactions, not a full browser-device session.
- **Deployment must be checked separately** against Render's actual running commit; a GitHub merge does not prove the published page updated.
- **Important security preflight:** `app.py` still has a hardcoded legacy password fallback `BEVERAGE`. A correctly configured `APP_PASSWORD` environment variable or secret takes precedence, but before hardening/failing closed, confirm the production Render service has a current dedicated secret, or the site may lock out family visitors. This PR does not silently remove current family access.
- As before, original archive scans that haven't been cleared for redistribution cannot appear inline. The new viewer explains missing assets rather than misleading visitors.

**Suggested manual acceptance test:** From the home page open Matthew's exhibit → Original records → probate context → person profile → focused tree → return to exhibit; repeat with Clarissa and Lowell Jr on a phone and desktop browser. Check date qualifications and original citations remain correct.

No canonical genealogical edges, source files, relative addresses, copyrighted binaries, or protected historical claims are changed.
