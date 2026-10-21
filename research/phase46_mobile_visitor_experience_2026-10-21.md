# Phase 46 — Mobile-first family archive visitor experience

**Date:** October 21, 2026. **Base:** Phase 45 merged/live on `main`, commit `b58cee186b4bb298826ba6a174ad68f508b7b489`.

## Primary objective

Family members should be able to open the password-protected archive on a phone and complete these four journeys without wading through research dashboards, large embedded documents, dozens of source cards, or paginated directories:

1. **Find a relative** by their first name, surname, initial, or an accepted historical spelling variant.
2. **Open that relative's tree** while keeping the selected real profile ID.
3. **Browse their attributed family photographs** and click back to printed source pages.
4. **Read their original evidence** before the speculative research or unresolved-identity queues.

### Audited friction found in the Phase 45 code

- `render_home()` put its only free-form / quick profile lookup **below** a six-card menu, featured family cards and a long additional-link menu. The second lower-page picker was a 202-option dropdown, duplicated by the sidebar.
- `render_journey_bar()` provided three generic destinations above *every* section, even when one exact relative was already selected. It made the visitor look for special controls to get directly to that person's photos or original sources.
- `render_person_exhibit()` put dated-count metrics, three navigation cards and potentially dozens of speculative research, archival target, name-match and source-list buttons **ahead** of the chosen life, records, photograph or family exhibit. On a phone, deep-linked records could require substantial scrolling.
- `render_media_page()` constructed **four entire heavy Streamlit tabs simultaneously**: large scanned family book photos, museum image catalog and embedded third-party archive frames, entire document index, research case catalog and original records. Streamlit tabs did not defer rendering of their hidden bodies. Visiting the gallery or a research case unnecessarily computed the others.
- Historical image cards embedded third-party archive pages in expandable iframes. Such external site embeds can load even when folded and are not needed when archive-provided links are already present.
- The family archive already uses mobile wrapping CSS and accessible 44-pixel controls, and offers a continuous 202-person list. Those are preserved rather than replaced with a new overlapping visitor site.

## Changes implemented

**Fast find on the home landing:** `visitor_fast_paths.py` ranks exact indexed relative names first, then name prefixes, name tokens, alternate spellings and visibly labeled fuzzy surname suggestions. The preview is capped to seven UI suggestions, but the database is **never capped**; links to the complete full-text search and complete continuous people directory are always available. No fuzzy match alters an identity, parent or sibling relation. The redundant bottom-of-home name dropdown is replaced with obvious full-list navigation.

**One-tap selected-relative paths across the site:** When a visitor has selected a verified person ID, the compact cross-section compass provides four direct, shareable URLs to **Life profile**, **Family tree**, **Family photos** and **Original records**, all scoped to that exact ID. Older generic "more places" routes remain available under a small optional section. Someone without a selected relative still sees the existing three general ways to continue exploring.

**Person-exhibit content first:** An exact profile's requested life / records / book-photo / family section now renders immediately after four direct action buttons. A compact selectbox replaces the four-wide horizontal radio on phones, preserves `section=` permalinks and existing sync callbacks, and only executes the chosen section. Dated metrics, full-map shortcuts, competing parentage, uninspected archival requests, and early-island name comparisons remain complete behind an **opt-in, lazily evaluated** research toggle below the visitor's requested content. Those research links are never removed.

**Media collection conditional rendering:** A compact bookmarked `media_view=photos|images|documents|evidence` selector ensures only the chosen collection executes. A link with `person=` or `photo_page=` defaults to the photo gallery; an investigation `case=` link defaults to evidence; manual selections update the URL for sharing. All 82 photograph-bearing book pages, linked 305-page source book, other historical images, documents, original evidence and investigations remain available in their corresponding views. External holding-institution links replace eager third-party archive iframes, which improves stability and avoids needless network renders. The original 8-per-page historical image browsing and 12-at-a-time family gallery remain unchanged.

**Continuity and research correctness:** 202 indexed profiles, 4 recorded components, all family relationships, 305 scanned book pages, 82 cataloged photo pages, all source records, the shared password gate, family history statements, copyrights, and source permissions are **unchanged**. These are presentation, routing and lazy-render improvements.

## Concrete visitor acceptance checks

- On a phone or narrow browser, open Home, type `Orris`, select the exact indexed relative; verify life profile loads. Try `Beveridge`, including the Beverage/Beveridge equivalent index, and use full search to reach results past the seven suggested cards.
- On a selected profile, use **Family tree**, then **Family photos**, then **Original records**. Verify each route references the same person ID. A person with no cataloged photo must show an honest empty state rather than a fabricated portrait.
- From the older historical evidence URL `?page=collection&view=person-exhibit&person=matthew_beveridge_hope_1837&section=Original%20records`, see the original-record section before long original-document request and unresolved parentage queues. Switch between sections, then opt into the long research controls.
- Open `?page=media&person=orris_beverage_1860`, verify the named-person photo filter. Select Historical images, then Historical documents, then Original evidence; only the chosen collection should be rendered on each rerun, not all four.
- A direct `?page=media&photo_page=49` should show the original page first. A known `?page=media&case=<existing-case-id>` should open an investigation rather than making the user find the research tab. Old deep links to the complete original book must still work.
- Test a **continuous** alphabetical directory including all 202 indexed relatives; no hidden 25-person limit or forced paging.
- Run both supported Python versions, source validator, JS tree and map interactions, the Streamlit AppTest login/route/evidence smoke suite and verified source backup, then merge a single PR and deploy manually on Render. Confirm exact live SHA and immediate error logs.

### Limits

The changes are validated in automated Streamlit tests but not yet manually exercised with the real family password in an authenticated mobile browser. Rendering fewer hidden media sections is a concrete code-level improvement; exact real-world mobile load-time measurements have not been taken. No outbound archival emails or messages have been sent.
