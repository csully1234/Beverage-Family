# Phase 14 — Every relative deserves an evidence-led life record

**Baseline reviewed 18 October 2026, after PR #33 merged and deployed.**

## Repository reality (not a speculative UX wishlist)

The historical index consists of ~190 effective person profiles merged from the original people register and reviewed overlays. A direct count of the current records finds **only 26 stand-alone `biography` fields**. Almost all profiles have at least one source citation, but many citations are cemetery indexes, published genealogies or old family compilations: a source *count* is not proof that every recorded relationship is correct.

The supplied, authorized 305-page *The Colony* has:
- 82 manually cataloged photograph-bearing pages available for the gallery;
- 23 distinct exact-ID person-photo cross-references, which are still **author-attributed**, not independently certified;
- 16 unresolved name/identity cases;
- OCR navigation across 305 pages, but NOT full manual verification of every name on every original page.

**Opportunity:** A visitor often reaches a profile with dates/relatives but no written life story, cannot understand how it relates to the photos and events, and may take an inherited parent-child link as independently verified. Adding another generic research dashboard would not fix that.

## Phase 14 implementation

New `profile_life_stories.py`, integrated into the existing **People → Story** tab, not a separate parallel genealogy app:

1. **Record-based summary for any profile without a biography.** The words are derived only from birth/death fields with existing date precision, the explicitly listed occupations and education. It does NOT infer parents, marriage dates, religious identity, land ownership, nationality, death place, exact dates or historical context from surnames or approximate ages. It says “the family index records…” rather than making a newly validated claim. Profiles with real authored biographies retain them unchanged.
2. **Whole-life chronology** from birth/death fields and **every** explicitly person-linked historical event. Displays the *source-reviewed public wording*, including the 1749 James/Jean marriage *intention*, without rewriting the original events or their citations. Dates remain distinct from publication dates, evidence status is displayed, and visitors open the individual event with original citations. The Story tab shows an abbreviated preview with a direct link to **all** the relative's complete timeline records; no silent 8-event total cap.
3. **Inline book photographs** in existing person Stories, up to three cropped previews per profile loaded only from the already-authorized scanned *The Colony*. Every preview links back to the original page and full printed caption. Additional indexed photo pages are all accessible by source-page links. Crosswalk matching is by stable person ID ONLY, never by fuzzy name search or surname. Existing book profile panels and full gallery remain intact.
4. **Evidence limits** presented in ordinary family-readable language for missing biographies, uncertain dates and book-photo captions, rather than treating database-generated prose as author-reviewed family testimony.
5. **Full coverage tests** exercising all effective person profiles, uncertain Mercy parentage, 1749 intention source status, *Lowell Sr. vs Lowell Jr.* portrait distinctions, and no invented dates.

No changes to original source records, historic assertions, protected addresses, genealogical relationships, external copyright rights, or previously supplied book pages. No need to create duplicate people or events.

## Remaining BIG projects — recommended order after this release

**Phase 15 — Original-evidence genealogy verification.** Audit relationship links and build *claim-level evidence* for parent-child/spouse assertions (verified vs provisional). Prioritize historic Marblehead–Georgetown–Topsham–Fox Islands chain, the original 1763 petition, 1758 parcel entries, 1831 Mercy/James Henry probate, Lowell/Lyford, and distinct Robert Beveridge Revolutionary War records. A name match is not proof. No descendants added until independent documentary links are found.

**Phase 16 — Complete the full-book cross-reference.** Human-verify all 305 pages beyond noisy OCR, all people and place references, not just the 82 photographic pages. Confirm author-attributed photo subjects, correct misleading Lowell and Amelia/Hanson identity matches, and resolve or explicitly preserve the 16 unplaced names.

**Phase 17 — Authorized family contribution pipeline.** Build a permission-aware process for relatives to propose identifications and upload scans (with documented source, date, consent, and custody). Never automatically publish claims, addresses, or copyrighted historical-society records. Scope and privacy must be agreed before enabling public submissions.

**Phase 18 — Visual/mobile quality and performance pass.** Test the actual Render deployment in authenticated desktop/mobile browsers after merging; review older iPhones, SVG tree selection, full-book rendering, source-card performance, image-crop quality, navigation and dark/light contrast. CI success is necessary but not a visual QA substitute.

## Release

Draft PR #34 only. Merge/deploy only with user direction. Automated regression and graphical browser review should pass before release.
