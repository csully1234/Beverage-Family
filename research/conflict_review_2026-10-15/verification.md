# Implementation and verification

## Problems observed in the actual baseline

PR #9 is merged; detached baseline `7ce454f95ed3aed60dda717d5c2e36237bbf1047` was used for comparison. The site already has profiles, focused/full trees, relationship paths, a timeline, geographic map, source archive and research collection. No duplicate versions were built.

| Baseline issue | Implemented behavior |
|---|---|
| Twelve competing top-level navigation choices | Six groups: Home, Search, Family, Places, Archive, Research; original page slugs retained |
| Home emphasizes statistics before useful starting tasks | Six direct starting actions, existing featured stories retained, report counts behind an explanation |
| Global results silently stop at 30 and literal spelling can miss names | Complete pagination; known surname/first-name variants, initials, explicitly labeled approximate name matching; dates/parents/place distinguish people |
| Returning from a profile loses search context | Query, place and result page in return routes, propagated through linked relatives; session memory also restores search |
| Internal link buttons open fresh tabs and login sessions | Shared route controls use Streamlit callbacks, update the same query URLs and preserve authentication; external evidence stays a normal external link |
| Conflicts buried in imported inventories, with old claims easily mistaken for current conclusions | Profile evidence expanders, a dedicated outcome view, latest explanations at existing finding routes, former values and original snapshot one step away |
| Baptism presented as birth and unsupported exact birth retained | Audited shared-data corrections with precision and baptism labels; no edits to immutable data |
| Image inventory is a technical table | Item cards with holding institution, date limitations, rights/resolution notes and original-item links |
| Sidebar heading and logout text have poor contrast | Explicit contrasting heading/button text; 44px minimum navigation/control targets |
| Fixed app header overlaps the start of page content on a phone | Content padding clears the header; shorter search title keeps the form nearer the top |
| Visual trees can be difficult on a phone | Existing readable Family relationship lists and profile selectors made prominent; relationship-path language describes recorded connections, not proof |

## Preservation checks

The original nine baseline JSON files and five supplied reports pass their existing byte-hash guards. Their manifests were not edited. Tea Party wording, all existing residences/property data and every relationship field are identical to the prior effective data. Both Amelia IDs remain addressable. No new relative or relationship is invented. Only the three named profiles have allowlisted factual changes, with before/after values in the ledger.

`load_site_data` applies date precision, then the audited review to a deep copy. All consumers use the resulting effective profiles. Fail-closed tests reject a changed expected baseline, duplicate edits, weakly supported corrections, and attempted residence/relationship/note edits. Every old conflict ID must be present once, with known source references and explicit status. Sarah's documented historical marriage retains the privacy safeguard without fabricating a birth or death date.

The immutable imported collection, original reports and dated snapshots intentionally continue to show the former claims. They are labeled as original evidence rather than silently rewritten. Lowell's older conflicting note is retained under an “Earlier evidence conflicts” heading; the latest review explains the proposed birthplace.

## Automated verification

- `python validate_data.py`: no blocking errors. Existing warnings remain: 1 ID/year mismatch, 6 missing relative profiles, 7 missing event-participant profiles, 53 one-sided relationship links repaired at runtime. No invented records were added to silence them.
- `python -m unittest discover -s tests -v`: **93 tests passed** on Python 3.12, including 7 new evidence/search unit tests and 4 additional Streamlit journey tests. Existing smoke tests were updated to select the actual grouped navigation; integrity expectations were retained.
- `npm test`: **12 tests passed**. These execute the real bundled historical-map document with jsdom, including keyboard-compatible list selection, fallback without map assets, filtering and safe markup.
- Python compile check: all runtime modules, new modules and importer passed.
- `git diff --check`: passed.
- 17 used-source/contact transport checks: 15 HTTP 200, 2 HTTP 403. Columbia and Crimson text were accessible through web retrieval; direct host HEAD checks were blocked. Source access form is recorded separately from transport success.

## Actual browser checks

[Machine-readable results](browser_results.json) record a local Chromium 153 / Playwright run against the real before and after Streamlit applications. A test-only environment password was used; the application's authentication code and production credentials were not changed. No production site was deployed.

The normal browser download failed. A separate temporary Chromium package enabled actual browser testing without adding a runtime or repository dependency.

| Journey | Browser result |
|---|---|
| Spelling variant `Eliot Beveridge` → existing Elliot Pierson Beverage profile | Correct stable ID, no new login |
| Harold → Fremont (parent) → Harold (child) → Petronėlė (spouse) | Connected profiles open in the same authenticated session |
| Diana profile → baptism explanation → CRS001 underlying source link | Correct event label, review and exact Edgartown item URL |
| Pulpit Harbor → James Beverage → Places → Pulpit Harbor | Round trip works at tablet width |
| Archival item → provenance, rights and original repository link | Site caption/rights and external destination verified; remote image rendering was not part of this browser test |
| Focused tree → full profile → readable Family list | Usable phone alternative to the graph |
| Filtered `Bevridge` / North Haven results, page 2 → profile → return | Query, place and page 2 retained without another login |
| Keyboard Tab from search input | Next input receives visible solid focus outline |
| Phone text-size enlargement | Root font at 200%, no main-page horizontal overflow in the captured search state |

Screenshots and width measurements cover 390×844 phone, 768×1024 tablet, and 1440×1000 desktop states. No unintended document/main-container horizontal overflow was measured in those states. This is sampled testing, not a claim of full WCAG certification. Real iOS Safari, VoiceOver and production-host behavior remain untested. Embedded map/graph external HTML links retain their existing behavior; the session-preserving profile selectors, Family lists and normal archive controls provide the verified in-app path.

## Screenshots

These are actual screenshots, not mockups. The `before` files use the latest default-branch baseline, not an older chat description.

| State | Before | After |
|---|---|---|
| Phone home | [Before](screenshots/before-home-phone.png) | [After](screenshots/after-home-phone.png) |
| Desktop home | [Before](screenshots/before-home-desktop.png) | [After](screenshots/after-home-desktop.png) |

Additional actual states: [phone search](screenshots/after-search-phone.png), [Diana profile](screenshots/after-diana-phone.png), [conflict explanation](screenshots/after-conflict-phone.png), [tablet place](screenshots/after-place-tablet.png), [phone family list](screenshots/after-family-list-phone.png), [enlarged search text](screenshots/after-search-text-zoom-phone.png).

## Review limits and remaining decisions

- Original church, vital, deed and stone images remain the decisive gaps. See the eleven prepared retrieval requests; none were sent.
- One classification is resolved, six conflicts narrowed, four await original records. All eleven remain unreviewed by the family. These labels must not be read as family approval.
- Review the three proposed profile changes before merging. Do not merge the two Sarahs, reassign their spouses, reassign James's children, or consolidate Amelia without the additional evidence identified in the ledger.
- The original reports and research package are retained in full. No revised XLSX/DOCX overwrites them; this Markdown/JSON review is their dated successor.
- Draft PR only. No merge, production deployment, visibility change, credential change, archive contact or purchase is authorized by this work.
