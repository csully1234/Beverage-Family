# Phase 33 — Person-first evidence access and honest family branch navigation

**Date:** 19 October 2026  
**Starting point:** Phase 32 merged into `main`, Render live at that merge, automatic deploy disabled.  
**Goal:** Make existing historical evidence easier to find *from the relative it concerns*, while preserving exact-ID attribution, provisional notes and the real gaps between separately recorded family groups.

## Starting audit and issues addressed

- The complete audited family graph includes four connected components in the Phase 29 baseline: the main extended group, Matthew Beveridge of Hope, Nathaniel of Rockland, and Mercy Beveridge Henry. Six referenced family IDs lacked indexed profiles. These were not necessarily six missing relatives with established identities.
- A person exhibit already displayed profile bibliography, curated exhibits, indexed research, illustrations and timeline links, but sources recorded **only on individual timeline events** could require leaving the person's Original records tab. Event evidence was not integrated into that exhibit's local source reading sequence.
- The integrity dashboard already counted events with no direct URL but showed a queue for *no citation* without an equivalent targeted visitor-facing queue for **cited events without a direct source link**.
- The numeric direct-link audit accepted syntactically plausible HTTP(S) URLs that the actual site refused to open (e.g. credential-bearing or unusual-port URLs). This could overstate access.

## Changes

### Person's Original records tab

- Show every citation-bearing dated event linked via its **exact `people_involved` ID**, in date order. Include existing curated source exhibits attached via exact **event ID** and existing event citations, deduplicated through the existing source normalizer.
- Source cards retain citation titles, limits, published vs original distinctions, and safe external links; missing digitized originals remain **visible as bibliography**, rather than being hidden.
- Provide direct, session-preserving links back to each timeline event. Lazy expandable event cards and five-event pagination keep the mobile page manageable while retaining all entries.
- **Never** associate an event with a person because an OCR match or description happens to contain their name. No new genealogy relation is asserted and no unpublished scan is uploaded.

### Family Connections tab

- Identify the selected person's numbered connected component and its indexed size with the deterministic read-only graph auditor.
- Explain that another component is **not** confirmed related to the selected component; offer a direct link to the complete disconnected-branches explorer.
- Make unresolved missing-profile references more readable without creating selectable phantom ancestors. All recorded relationship links remain unchanged.

### Archive integrity and evidence access

- Show a paginated, clickable queue of **events that do have citations but do not have a visitor-openable direct URL** in the event field. Distinguish this from uncited events and from separately curated links.
- Add a CSV of **all** event records lacking a direct citation URL (ID, date, title only), for future archival retrieval and careful link completion.
- Count direct source URLs using the same safe-URL policy as visitor-facing links. Counts are still *link access*, not document authenticity or rights to republish.

## Tests and acceptance criteria

New `tests/test_phase33_source_navigation.py` covers:
1. Exact-person attribution, date ordering, deduplication, direct and bibliographic references; rejects unsafe source links.
2. Real historical event attribution and empty-source handling.
3. Original-record summary counts (without treating citations as scans).
4. Every indexed person mapped to exactly one existing connected group; no link between Matthew and Nathaniel created.
5. Unknown relationship ID remains non-selectable with no phantom profile.
6. Safe URL count matches what visitors can actually open.
7. Historical data validation and the unchanged legacy authentication route.

Run the existing `python -m unittest discover -s tests`, Python 3.12/3.13 CI, JS tree/map interaction tests and release audit. Check the new event evidence UI on phone and desktop, especially event pagination, source expanders, timeline back-navigation and four branch-group labels.

## Protected boundaries and what remains to do

- No edits to `data/people.json`, the versioned person or event overlays, Boston Tea Party claims, relative residences, copyright flags, historical images, credentials or password-gate behavior.
- Six unresolved referenced IDs **remain unresolved** until evidence supports actual profiles. Four graph components remain separate until contemporary records justify an edge.
- Original 1810 Hope census and 1820 Hope sheet 276 still require legible high-resolution inspection and possible identity-chain comparison against Hope clerk/deed and 1837 probate evidence.
- Externally linked websites can move or block embeds; this release checks stored URL safety and navigation, **not** live remote content availability or original authenticity.
- Received Waldo probate scans are not republished by this work pending the existing reproduction-rights decision.
- GitHub passing tests do **not** substitute for authenticated manual UI checks. Render has `autoDeploy = no`; a PR merge alone will not publish this release. Deploy separately only after checks and a successful recovery point.

## Deployment smoke checklist

1. Confirm the merged GitHub head and Render commit IDs match after an authorized deploy.
2. Log in using the existing family credential; confirm all existing sections remain gated and available.
3. Open James Beveridge Sr.'s person exhibit → Original records → dated event source cards. Verify bibliography-only entries and external source buttons, then timeline round-trip.
4. Open Matthew of Hope → Family connections: verify branch number, eight individually named children, widow Clarissa, and no asserted parents.
5. From the integrity dashboard, open all four connected groups and the separate cited-events-without-direct-URL queue and download the complete CSV.
6. Repeat the central person, event and tree actions on a narrow mobile screen; back up or roll back if authentication, navigation or media fails.
