# Phase 28 — Connected relatives, clear profiles, and practical evidence access

**Implementation:** 19 October 2026; post-Phase 26 baseline `5f837728ca1603f01474570a128b24081b3aae5c`.

## Scope and existing functionality

The site already had a searchable person dropdown, direct profile links, a focused graph, an SVG whole-family map with pan/zoom and selection synchronization, author-attributed family-book photographs, and a separate source catalog. Duplicating those systems would introduce divergent identity matches and timelines. This release instead connects the existing screens around the exact selected person's stable ID.

## Improvements

### 1. Navigate directly through family

New `family_navigation.py` reads the **existing documented relationship index**, not OCR matches or inferred surnames. It lists parents, spouses, all children and siblings in a stable relationship/name order. A person with an unresolved reference can see the count but cannot jump to a fabricated profile.

The focused tree now offers a **direct relative selector** and a one-click source-evidence exhibit. Choosing a relative updates the focused tree person, the full-map selection, the person profile selector and the shareable `profile=` URL together.

The full-family map now presents a matching **Go to a parent, spouse, child or sibling** selector when a person is selected, plus a link to the exact relative's life-and-evidence exhibit. No relationships or graph layout source data are changed; all already-documented children remain accessible, not just the first few.

### 2. Put a person's story first

The profile's at-a-glance cards show the first three directly linked relatives and add a **Show all** expander for additional relatives. The previous wording simply redirected visitors elsewhere, making larger families such as Matthew's eight court-identified children difficult to browse on phones.

A separate **Read all historical sources for this person** link opens the source section in the existing authenticated exhibit. Longer specialist research modules (identity casework, documented associations and unresolved relationships) remain fully available within a clearly labeled optional research expander, so they no longer interrupt the main story and family tabs.

### 3. A more readable historical-source collection

The person's Original Records section now supports **Show only citations with a record link**. This is an optional display filter, not an archival exclusion: the default shows every historical citation, including sources for which no verified scan or direct URL has been found. The citation list is divided into six-at-a-time pages, with all references reachable. Displaying a cited title still never implies the site holds a court-certified image.

Existing claim-level qualifications, book-page links, official-document citation URLs and source rights labels remain unchanged. PDFs from external archives continue to be offered by link and opt-in preview, not silently copied.

### 4. Mobile full-family map fix

Phase 26 sized the **outer** Streamlit map component to the phone viewport. The inner map still used a fixed 720-pixel height, causing its bottom to be clipped. Phase 28 changes the inner SVG shell to fit its available iframe height and allows the many search/zoom controls to scroll independently on phones, retaining a usable map area and minimum 44-pixel touch targets. The desktop map and its existing custom-component message protocol remain intact.

## Testing and historical integrity

- New pure tests cover all eight of Matthew's court-named children, Clarissa's documented parents, unknown family members, stable selectors, all citation pages, and preserved password behavior.
- New authenticated Streamlit smoke tests navigate directly between relatives from the focused and whole-family maps, inspect Matthew's entire child list, open the evidence section, and toggle the linked-record filter.
- Existing Python 3.12/3.13 validation, map JavaScript tests, data constraints, and book asset/rights audit must all pass before rollout.
- The site's current family password system is **unchanged** as the owner requested. Closed PR #47's alternate authentication behavior is not included.
- No genealogy, uncertainty ratings, related addresses, rights flags, unapproved probate scans, photo IDs or source image binaries have been changed.

## Production acceptance after merge

Render's `Beverage-Family` service is set to **manual deployment**, so GitHub merge and Render rollout are separate steps. After CI:

1. Confirm the new merged SHA passes both Python jobs and the backup workflow.
2. Manually deploy the exact `main` commit in the confirmed Render service, verify `live`.
3. In a family-authenticated desktop and phone browser, visit Matthew's focused tree and jump to Polly Tucker; verify the map centers the same person. Open Matthew's profile and expand all eight children, then open historical sources and show linked-only citations.
4. Test the mobile SVG tree controls and direct book-original links. Source images without reuse clearance must still not be served.
5. Review live logs for immediate runtime exceptions. A passing backend CI suite and Render live status do **not** replace an actual browser visual/accessibility audit.

This is a navigation/reading improvement, not a claim to have resolved Matthew's ancestry or rights to new archive scans.
