# Phase 18 — full 305-page source extraction and evidence review

*18 October 2026. This phase is a page-by-page OCR sweep and an initial **selective** original-page research review. It is NOT a manually verified transcription of every page.*

## Real source inspected

- Original: *The Colony: Stories from a Down East Island*, Lowell P. Beveridge Jr. (2016), original clean 305-page scan already in the repository and explicitly authorized by the copyright holder/user for the family website.
- Verified source PDF size: **22,944,649 bytes**, **305 landscape page images**, no embedded searchable text.
- SHA-256 of the identical user-supplied file: `2eaefbb79aaa7039aab1fb7d493ec5c44792f7a88d32f005b1e67cff2db576ac`.
- An offline research extraction processed **all 305 pages** using Tesseract 5 in English at 144dpi, `--psm 3`, grayscale, with process concurrency limited to 4.
- Raw OCR produced **429,987 characters and 77,839 OCR-detected words**, with **25 pages under 50 OCR characters** (mostly illustrations/facsimiles/headings; this does not imply the original pages were empty).
- All 305 OCR operations completed without error in the local research run. **No generated word is independently certified by the tool**, no inferred kinship is created from detected terms, and low-text pages should be inspected visually.
- Research-only artifacts: `full_page_ocr_unverified.json.gz` (compressed page-separated OCR) and `full_page_ocr_unverified.txt`. These are delivered as conversation files rather than published as unrestricted verbatim text in the GitHub repository.

## New original-book browsing experience

**The existing site reader** now includes a **Source review & expanded OCR** tab and a **source-review panel next to selected original pages**. The existing full PDF download and inline preview, previous 82-captioned photo pages, 23 canonical photo-person crosswalks and 16 unresolved photo identities are preserved.

A reproducible offline script `scripts/build_colony_ocr_index.py` takes the 305-page PDF and produces a controlled **navigation vocabulary**, listing the pages where a named historical topic possibly appears. The generated public site index does not copy full OCR text, does **not** expose automatically inferred person IDs, and cannot certify birth dates, marriages or identity. The existing 35-term OCR page index is the fallback if the expanded index has not been generated.

**The workbench** also opens the notebook, alongside the original case files and scanned book page cross-search, so a visitor investigating Matthew or James can open a precise book page, see its recorded interpretation and then follow the missing original-record tasks.

The new `data/phase18_colony_page_source_review.json` contains **13 carefully qualified research notes on 12 original PDF pages** covering the eighteenth-century account and the published genealogy appendix. These are *not* 13 new verified family relationships. Source-verification method is explicitly described on each note; some were visually checked against the original image while others remain machine-assisted page leads requiring line-by-line verification.

## Highest-value newly surfaced identity conflict: two Matthews

**Book p. 17:** The original book scan clearly reports that a younger brother of Thomas Beverage named **Matthew** returned to the Fox Islands, and reports Matthew married **Abigail Dyer in 1801**. The printed passage describes Abigail as a niece of Mercy Kent (daughter of Mercy's sister Susana).

**Independent published source, already documented in Phase 16:** Cyrus Eaton's 1851/1865 Warren/Thomaston narratives identify a **Capt. Matthew Beverage of Hope** who married **Clarissa Cobb**, daughter of Capt. Barnabas Cobb.

These facts are **not proof of one Matthew with two wives**. Neither text alone proves the Matthew's parental identity, the marriage order, widowhood or the same person's location. Also possible are **two distinct namesakes**. Priority evidence: find original 1801 Matthew/Abigail marriage entry, original Capt. Matthew/Clarissa entry (date and location), Matthew probate naming a spouse and relations, plus deeds/tax rolls to confirm identity, and documentary proof of Capt. Matthew's parent(s) and Nathaniel's.

**Do not collapse the two Matthew labels into a single person or add new parental lines** until the original documents establish identity. This conflict is now visible in the source notebook and cross-index, rather than lost as a footnote.

## Other source-specific historical limits made visible

- **Page 13:** Family-history narrative states an elder James came from Scotland and suggests indentured servitude; a proposed occupation is not a contemporary arrival record or a proven Scottish parent.
- **Page 15:** Jean McKinney White's widowhood, children George/John and James's reported move to Minot's stockade are memoir claims requiring separately keyed original records. The 1748/9 original Brunswick **intention** does not itself certify marriage.
- **Page 16, visually checked:** Printed book gives a 13 April 1774 Thomas–Mercy Boston wedding account and preserves Thomas's **Boston Tea Party participation as family tradition**, explicitly without surviving participant proof. The existing site claim remains unchanged.
- **Page 17, visually checked:** Printed account gives James's reported 1787 death on the islands and links Thomas, James and Matthew in narrative; an 1787 grave or probate naming heirs remains a critical missing link.
- **Pages 18–19:** The 1785 Fox Islands land-claim story and reproduced petition facsimile must be separated from **Topsham's 21 December 1763 incorporation petition**. OCR of p19 is unreliable; only an authenticated original archive folio could settle signatures/dates.
- **Page 22:** The Peter Grant/Dunbar–Lynn Iron Works family tradition concerns the **Grant collateral line**, not proof of Scottish origins for an earlier Beveridge namesake.
- **Pages 288, 291, 296–298:** Published 2016 family-group compilations supply valuable name, spouse and date leads; they are not original civil returns. Lowell Sr./Jr. IDs remain distinct, and Olive's life partner Florence Budlong is **not** silently presented as a civil marriage.

## What remains genuinely unverified

1. **Manual text comparison for all 305 pages** is not complete. This phase covers the image sweep and controlled index, plus a specific sample of pages reviewed in context. We must not market the machine extraction as fully corrected transcription.
2. **Full biographical person/entity tagging** is not complete. The OCR page-to-word index uses controlled vocabulary and **has no page-to-person identity assertions**. Same-name collisions (especially James, Thomas, Matthew, Lowell) must be resolved separately.
3. **Original contemporary documents** for the emigrant James's identification, the 1749 marriage ceremony, 1774 Thomas–Mercy marriage return, 1785/1786 land/testimony, 1801 Matthew–Abigail marriage, Capt. Matthew–Clarissa marriage, and 1831 Henry probate remain priority acquisitions. No outreach or purchases were initiated.
4. The **source PDF includes living or recently living descendants** in its later appendix. The expanded public repo index deliberately includes no unrestricted full-text reproduction or address-sensitive source excerpts. The original website remains password protected and the scan unchanged.

## Implementation and release checklist

- `scripts/build_colony_ocr_index.py`: exact PDF hash/305-page guard, bounded concurrency OCR, controlled vocabulary, reproducible generated index metadata and no full raw-text release.
- `data/phase18_colony_page_source_review.json`: 13 transparent page notes on 12 source pages, each with evidence limit and next original record.
- `colony_source_review.py`: read-only notebook and full scanned-page indexed topic matching, original page links, no guessed canonical person matches.
- `family_books.py`, `family_research_workbench.py`: new tab and per-original-page source context with exact source link.
- `tests/test_phase18_complete_book_review.py`: preserve Tea Party tradition, record the Matthew ambiguity, validate original person IDs, no changed parent links, all generated OCR pages in range and no transcript implied.
- OCR build workflow is limited to a named research branch and commits **navigation metadata only**, not private research text. GitHub CI must remain green on both Python versions and JavaScript map/tree tests.

**Draft PR only. Do not merge/deploy until the user explicitly requests it.**
