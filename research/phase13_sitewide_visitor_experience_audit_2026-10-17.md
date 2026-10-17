# Phase 13: cohesive family archive — site-wide visitor experience improvements

**Design/implementation review: 17 October 2026.** These changes are visitor-facing, additive and independent of speculative ancestry. No historical evidence, source records, modern addresses, protected claims, genealogical edges or server secrets were altered.

## What was audited

The current Streamlit site already includes a nine-section family homepage, surname-sorted directory, focused Graphviz tree, pan/zoom full tree, a full uncapped cross-source timeline, complete 305-page *The Colony* PDF reader, historical maps, story articles, historical images and source/investigation records. Prior PRs #25–#32 already address identity issues and photo links. Duplicating an alternate genealogy app, new timeline or new map would be unnecessary.

**The remaining major friction points found in current code were:**

1. The homepage had only six routes despite many major visitor destinations (especially the illustrated book and original sources).
2. Full-tree users could only scroll a long native dropdown to find an ancestor; clicking a distant node refitted the *entire* diagram, so names became tiny again.
3. The full family tree rendered nodes as visual SVG graphics only; a keyboard-only visitor could not focus/select individual family members.
4. Profiles, trees, photos, timeline and original documents did not provide a consistent “what can I explore next?” action strip, and browsing progress across profiles was lost after leaving a page.
5. Deep-linking from an ancestor's profile to their own timeline was not possible; direct links to a selected person in the focused tree could be overridden by an earlier session selection.
6. The historical source explorer silently stopped after the first **50** matching citations even though hundreds could be present; no further pages existed.
7. On phones, the 3-column grids, tab strips, long button titles and padding did not consistently reflow to a usable width. Technical version/debug information occupied the sidebar instead of a disclosure.

## Implemented

- **Cross-section journeys**: a compact navigation action bar appears below the page breadcrumb, with relevant next routes; on a person-specific view, its action points to the actual selected profile/tree. All actions use existing session-preserving routing. New `visitor_journeys.py` defines one shared link catalog, not a second set of pages.
- **Session-only recently viewed profiles**: the homepage shows the most recently opened profiles, at most three of five stored in ephemeral Streamlit session state, with no tracking, persistent browser storage or new account information.
- **Homepage**: nine prominent destinations, including the entire family map, original sources and the complete illustrated book; no person is accidentally selected before the visitor chooses a profile.
- **Family-tree search**: type a name, surname, year or alias-like ID fragment into the full SVG diagram; matching suggestions update live; Enter or button opens the best match; the complete dropdown remains as an accessible alternative.
- **Full map usability**: choosing a person centers and zooms them to a readable level from the overview; “Fit visible tree” still restores the full extent. Every real person node is keyboard-focusable with Enter/Space selection; unresolved reference-only nodes remain visibly distinct.
- **Selected-person continuity**: focused-tree deep links honor the requested person even after a previous session choice. A person profile can open **that person's filtered complete timeline**, with a shareable `?page=timeline&person=<id>` route; the timeline can jump by historical period while retaining the full year slider, all source levels, and uncapped records.
- **Original-source access**: replaces the arbitrary **50-citation cutoff** with 15-item result pages and a visible total count; all matches can be reached, without hundreds of heavy cards in one Streamlit render.
- **Mobile and information hierarchy**: improved responsive spacing, tabs with horizontal scrolling, minimum touch target sizes, readable hero/profile typography, and technical version information in an optional sidebar expander.
- **Regression safeguards**: Python tests for every cross-page route, source selection, recent-person state, original relationship preservation and map feature presence; JavaScript interaction tests for name search, keyboard selection, no-match behavior, and whole-family continuity. Existing complete CI regression suite remains mandatory.

## Acceptance and release

- Verify authenticated **Home → relative → focused tree → full family map → profile → timeline** loops.
- Verify searching a name and selecting SVG nodes by keyboard on desktop, iPhone and iPad; fit, zoom, pan and branch filter.
- Verify original-source page 4+ is accessible and search filters still work.
- Verify the 305-page book, historical places, archive links, earlier 1786 testimony and photograph permissions remain intact.
- Do not treat any unknown kinship as confirmed. No person record, original location or colonial historical claim was touched.
- **Draft PR only. Do not merge or deploy without explicit user approval.**
