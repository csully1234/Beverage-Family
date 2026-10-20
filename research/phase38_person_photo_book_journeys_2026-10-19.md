# Phase 38 — Person-first photographs, book pages and original-source journeys

**Date:** October 19, 2026 US Eastern (some GitHub commits dated October 20 UTC)  
**Baseline verified:** Phase 37 is merged/live on Render at `86cda414822d02221ea2b7c23ab58b6ff436455e`. GitHub had no open pull requests.  
**Scope:** Major visitor-facing improvements using the existing 202-profile family tree, 305-page permitted book, 82 photo-bearing book-page gallery, exact-ID caption crosswalk, person exhibits and full/focused family trees. This phase **does not add unsupported relationships or republish new materials**.

## Identified visitor problems

1. The photo gallery had a free-text search, a subject picker and book-order sorting, but no exact-person filter and no stable person-specific gallery URL. A visitor coming from an individual life profile had to re-search that name and could receive OCR/textually similar but historically unrelated images.
2. Per-person exhibits already had correctly indexed photos and original source scans; however, they did not connect visitors directly to a full person-filtered gallery with a visible source trail and one-tap profile navigation.
3. The book reader's individual `book_page` deep links were technically honored by a numeric page input, but the 720-pixel full-book PDF viewer appeared **before** the selected original scan and printed caption. On a phone, the target family evidence could be buried below a large embedded PDF; the full PDF was also loaded on every book visit.
4. The journey bar preserved a person when using the People/tree pages but ignored exact-person `person=` links on the photo gallery, making the contextual buttons point back to a different previously visited relative.
5. A book image page showed exact indexed people and historical questions but did not lead to the corresponding gallery filtered to those actual people.
6. The focused tree and full tree offered strong profile/evidence links, but no direct route to the selected relative's full set of attributed photographs.

## Phase 38 implementation

### Exact-profile photo navigation, all 82 photo pages retained

`family_photo_navigation.py` is a **pure, read-only data and routing layer**. It cross-references `data/colony_photo_captions.json` with `data/colony_people_crosswalk.json` by **exact stable person ID and original numbered PDF page only**. OCR-only mentions, display-name resemblance, or family relationships do not create a visual identity match.

`?page=media&person=<indexed-id>` is a shareable, pre-filtered family gallery, and `?page=media&photo_page=<PDF-page>` highlights one complete photograph and its source first, even if it is far below the first 12 cards. An optional combined bookmark provides both. All 82 photo pages remain browsable through the existing small, lazy "load 12 more" batching, without a false 25-item cap.

The gallery gives an explicit "Everyone" option, a simple actual-relative dropdown, free-text search, subjects, and sorting. Switching relative resets stale caption searches and pinned pages. The selected relative's original profile and entire evidence exhibit remain one click away.

**Source fidelity:** Each card links to the actual printed page, gives the book attribution and known/unknown photo date, and offers a direct gallery share route. Possible identity crosswalks are explicitly labeled as needing verification. A person without indexed attributed photos receives a clear empty state rather than a fabricated portrait. All unrelated historical media tabs still display all their original content.

### Selected original book page first; full edition remains on demand

`family_books.py` now displays the requested high-resolution original source page and printed caption **immediately beneath the page number and previous/next controls**; it no longer makes visitors scroll through a full 305-page embedded PDF to reach the requested source image. A clearly labeled **Open complete 305-page PDF viewer** toggle loads the original entire edition when the visitor wants continuous reading. That avoids rendering a 22 MB full PDF for visitors browsing individual pages/photos on phones.

Book-page connections retain the existing attributed person names, unresolved historic names, case studies and research links, and add **exactly filtered gallery routes** and original person-exhibit links. A newly added "View this page in the family photograph gallery" route gracefully handles source pages not cataloged as standalone photographs.

### Connected visitor journeys in both trees and profiles

Person profiles, "Photographs & book" exhibit tabs, source-linked life stories, focused tree and complete family map all lead directly to the selected relative's full attributed photograph collection. The top cross-section visitor journey bar now follows a valid `person=` route in the gallery/timeline/book without overriding a new explicit tree selection.

### Regression protections

`tests/test_phase38_family_photo_journeys.py` covers all 82 catalogued pages, source-page sorting, exact-ID filters, fabricated-name exclusion, shareable URLs/escaping, pinned page correctness, invalid crosswalk entries, backward links, stale filter reset, the selected scanned book page appearing before the full PDF, stable person selection, no genealogy mutations and preservation of the family password. Existing broad Python 3.12/3.13 suite, map/tree JS tests and release/backup validators remain the release gate.

## Honest limits and genealogy next steps

- A book photograph's printed caption is not independent proof that every person with that name is the same relative. No image recognition, automatic parentage or merging was performed.
- Gallery "photo pages" are based on 82 human-cataloged pages, while 103 pages contain some type of photograph, map, decorative illustration or scanned item. The complete 305 pages remain available through the book reader. A missing attributed photograph is not evidence the person was never photographed.
- The four separately indexed family branches and six unresolved relative IDs are maintained. Parents for Matthew Beveridge of Hope remain unverified. An 1820 Hope census manuscript page and 1837 probate original still need full source reading before any historical identity bridge.
- Since the user explicitly prefers easy access over hardening, this release **does not change the shared password, GitHub visibility, documents, private hosting, or family permissions**. It improves navigation and performance, not privacy policy.

## Release checklist

1. Run both Python versions and all existing regression tests; verify all 82 photos, 305 book pages, crosswalks and source links remain intact.
2. From a profile and both trees, follow "photographs" and verify the chosen relative stays selected.
3. Select a named relative in the gallery, switch to another, clear filter, switch subjects, check direct `photo_page` bookmarks and original printed captions; confirm no candidate portrait is labeled proven.
4. Open book PDF pages 49, 159 and 246 from direct URLs on a phone; see each chosen original page immediately without opening the large full-book document. Toggle full original edition on demand and verify it is 305 pages.
5. Check older relatives with no person-linked portraits still have accessible profiles and complete original sources.
6. Confirm the old shared family password and Streamlit login flow work, no duplicate widgets or missing Streamlit runtime media, both tree selection controls work and no other media tabs were filtered.
7. Merge only when CI is green; then trigger Render manually (`autoDeploy=no`), confirm the exact commit reports `live`, check error logs and verify the post-merge source backup succeeds.

**No user emails or external archival requests are sent during this phase.**
