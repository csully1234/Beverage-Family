# Phase 22 — Waldo County probate of Matthew Beverage/Beveridge (1837)

**Reviewed:** 19 October 2026. **Source:** one ZIP containing 31 PNG scans reportedly supplied by the probate office to the site owner. The scans were supplied with opaque filenames and without the original docket number or a verified folio sequence. The user's separately retained source ZIP is authoritative for the image bytes; the public repository includes the checksum-indexed descriptions **but not the copies themselves**. Nothing here is represented as an official certified transcript.

## What the court records actually add

| Review scan(s) | Original-era proposition | Evidence character and limit |
| --- | --- | --- |
| 10 | Clarissa Beveridge of Hope requests estate administration, reporting Matthew's death on **14 February 1837**; petition dated **6 March 1837** | A contemporary petitioner's report of death and a probate proceeding; not a civil death certificate |
| 7, 18, 24 | Clarissa identified as Matthew's **widow** in dower documents | Court records independently support widowhood, **not** the birth surname **Cobb** given by Eaton's historical family narrative |
| 31 and 9 | A September 1837 proceeding describes **eight heirs**: Ezekiel G. Beverage, Achsa Heald, James M. Beverage, Polly Tucker, Thomas J. Beverage, Sarah A. Beverage, George W. Beverage and Martha Beverage | Strong contemporary legal-heir evidence; partial initials/surnames may require clearer images; it is not a complete civil-birth register nor proof of which wife was each person's biological mother |
| 14 | **Polly Tucker of Lowell, Massachusetts** identified as an heir, with **Nathan Allen of Hope** acting for her | Distinct court instrument cross-checks an heir's contemporary location and interest, but does not independently establish that she was Eaton's Mary Miles Beverage Tucker |
| 1, 2, 4, 9, 11, 17, 18, 20, 23, 24, 28 | Warrants, inventory/accounting, land partition, widow's allowance and dower proceedings | Primary evidence of probate actions; this review does not authenticate a modern parcel, value calculation, or extent of the original probate packet |

These are *multiple documents from the same estate*, not 31 independent family witnesses. Review scans **9 and 26 are bit-identical**, leaving **30 unique images** among the 31 supplied copies. Review pages are **researcher-assigned**, and the sequence **must not** be cited as an archival docket order.

## Comparing contemporaneous estate papers to published family history

Cyrus Eaton's *History of Thomaston, Rockland and South Thomaston*, vol. II (1865), pp. 146–147, reports a Capt. Matthew Beverage of Hope married first to Abigail Dyer and then to Clarissa Cobb and identifies ten children split by those wives. The probate papers independently mention Clarissa as widow and eight heirs whose names substantially correspond with Eaton's reported household. Those overlaps are strong corroboration, but still require exact identity, maiden-name and parentage review. **No new ancestor, spouse, parent-child edge, or 1785 Fox Islands minor identity was inserted into the canonical family graph.**

A formerly open research target — “locate original-era probate for Matthew in Waldo County” — is therefore now **partly met**. The original Phase 19 and Phase 20 research records remain unchanged as dated research snapshots; the website now provides a clearly labeled newer court-evidence view rather than silently editing past reports.

## Public image rights and integrity

The owner reports the original copies came from a probate office. That is **not confirmation of redistribution permission** for those particular digital copies. The repository is public even though the Streamlit family website has a password. Consequently the 31 binary scans were **not pushed to GitHub** and no placeholder download link pretends otherwise. Public citation metadata are safe to browse in **Historical Discoveries → Waldo probate** and the global Research Workbench.

The image viewer is deliberately fail-closed: even a filename present on disk is not displayed until both the approved local file and explicit publication-authorized status are set. Once the user verifies that these scans can be reproduced publicly, originals can be copied into `static/approved_media/waldo_probate_1837/` with exact manifest filenames and the rights indicators carefully updated, without changing the probate interpretation. Never place the unreviewed ZIP itself in a public Git tree.

## How to finish source authentication

1. Ask the probate office for the estate case/docket number, court book/folio references, chronological order of the supplied images and whether these are complete filings.
2. Request written confirmation about website redistribution of the digital copies, including any desired credit wording.
3. Re-read ambiguous surname and middle-initial letters from the highest-resolution image for the court's eight named heirs, especially Ezekiel and Martha.
4. Compare the original heir petition to independently documented marriages and children; record every inference separately.
5. Search for original Matthew–Abigail and Matthew–Clarissa marriage returns and an identity bridge to the 1785 Fox Islands land claimant before adding older-generation tree edges.

## Technical implementation

- `data/phase22_matthew_waldo_probate.json`: one source-family manifest, 31 scan crosswalks, original filename and SHA-256 checksum for each, six evidence claims, eight heir names, rights flag and unresolved targets.
- `waldo_probate.py`: searchable, shareable court-document browser with selected-scan permalinks; source-integrity metadata and image-rights gating.
- `family_research_index.py`: 31 metadata entries plus six claim entries in the complete source-search workbench.
- `family_discoveries.py`, `matthew_reconciliation.py`, `hope_matthew_civic.py`, `visitor_ui.py`: family-facing ways to discover the new packet and interpret older research notes in their appropriate chronology.
- `tests/test_phase22_waldo_probate.py` and source-route smoke tests guard key claims, one-source-family counting, exact duplicate, missing permissions, and no new genealogy edges.

The original `Archive.zip` and individually oriented review scans remain in the user's supplied working files; this public commit makes no claim to have uploaded their bytes.
