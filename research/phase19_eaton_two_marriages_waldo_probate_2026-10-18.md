# Phase 19 — correction: Eaton's two wives, one published Capt. Matthew household

*18 October 2026. The 1865 printed register has been checked against a searchable digitization of the original published book; the two marriage certificates, birth records and probate remain to be examined.*

## Major correction to Phase 18

Phase 18 described a possible disagreement between the *The Colony* (2016) account naming Matthew's wife **Abigail Dyer** and the 1851 Warren history naming **Clarissa Cobb** as the wife of a Captain Matthew. That framing was **incomplete**.

**Cyrus Eaton's *History of Thomaston, Rockland, and South Thomaston* (1865), vol. II, printed p. 146**, explicitly identifies Capt. Matthew Beverage of Hope as husband of **Abigail Dyer, first**, and **Clarissa Cobb, second**, then divides **ten named children** into **five attributed to each wife**. The scan-derived original-edition text is visible at https://www.scribd.com/document/845728319/History-of-Thomaston-Rockland-and-South (search for 'BEVERAGE, Capt. Matthew'), and a digitized original edition is at https://archive.org/details/historyofthomast02eato.

This proves that the **one 1865 printed family account** intentionally describes one Matthew with two successive wives. It does **not** establish either official marriage date, that the original historic register is correct about each child's maternity, or that this Matthew must be the **1785 minor claimant** or **Thomas's younger brother** as described in a later book.

Eaton's **1851** *Annals of Warren* says **Clarissa Cobb**, daughter of Capt. Barnabas Cobb, married Capt. Matthew of Hope; his **1865** local history lists her as **second wife**. These books are by the **same author** and need not represent independent family testimony. The *Colony* p. 17 reports a Matthew who married Abigail Dyer **in 1801** and calls him a younger brother of Thomas Beverage. The 1865 book gives no marriage year for Abigail and no direct identification of the book's Thomas–Matthew sibling pair; consistency of names alone is not a unique identification.

**We are correcting a former research interpretation, not announcing that new original vital records have been found.** We no longer present Abigail and Clarissa as contradictory wife accounts. All original imported genealogy, page scans, modern addresses, and protected Boston Tea Party tradition remain unchanged.

## Published children: use the existing exact family register, no new tree nodes

The preexisting, carefully sourced file `research/matthew_nathaniel_family_1865.json` already lists all ten names from Eaton, including by which wife each child was reported:

| Wife named by Eaton | Children in the printed 1865 register |
|---|---|
| First, Abigail Dyer of Fox Islands | Harrison, Achsa, Louisa, Mary Miles, James Madison |
| Second, Clarissa Cobb | Ezekiel G. D., Sarah Abby, Thomas Jefferson, George W., Martha W. |

The new case interface shows these as two **source-attributed groups**, with links to the underlying 1865 book; it does not represent ten new verified civil birth entries or silently add ten descendants to the canonical tree. A separate 1865 entry at printed **p. 147** calls **Nathaniel Beverage (born around 1804)** a nephew of Captain Matthew, and wife Sarah Alexander a niece, but names **neither set of parents**. The candidate online John White/Rachel Crosby parents remain unconfirmed. Nathaniel of Rockland and Nathaniel Winslow Beverage born 1776 remain distinct.

## Priority original-record route found

### The Hope estate and the county boundary trap

Early public county archive record collections can cause false negatives. The separately titled [Knox County Probate Estate Files collection](https://www.familysearch.org/en/search/collection/1931808) begins **1861**, after the period suggested by Capt. Matthew's family reports. Searching it alone for an estimated 1830s estate would be misdirected.

More suitable early holdings:

- [FamilySearch: Maine County Probate Records, 1760–1979](https://www.familysearch.org/en/search/collection/2040534) — original bound court-book image collection; exact locality and date vary.
- [Waldo County Probate Court *Probate Records and Indexes 1826–1892*](https://search.worldcat.org/title/866329316) — a cataloged original probate-book/index microfilm. Description provides the workflow: **index to dockets → index to probate records → volume and page**.
- [Waldo County official Register of Deeds](https://www.waldocountyme.gov/178/Registry-of-Deeds) — documents from the 1700s onward; deeds must be used to corroborate any Hope residence/heirs.
- [FamilySearch Maine Marriages, 1771–1907](https://www.familysearch.org/en/search/collection/1674915) and [Maine Vital Records, 1670–1921](https://www.familysearch.org/en/search/collection/1803978) are indexes/image collections to investigate for original first and second marriage returns. Before statewide 1892 registration, original town/church archives are critical and coverage varies.

**Unperformed step:** an image of Capt. Matthew's actual probate, guardianship, marriage or original baptism has **not yet been opened and authenticated**. The location, death year, exact spouse dates and genealogy must not be inferred from a catalog description. Search Waldo/earlier county jurisdiction according to actual estate filing date, and compare the physical/digitized court docket reference. The 1837 death year is tentative.

### The next three documents to obtain, in priority order

1. **Original estate of Capt. Matthew Beverage of Hope**, if one exists: identify named widow, adult or minor children, witnesses, probate venue/filing date, associated bonds and deeds. Compare all name variants (*Beverage, Beveridge, Beviridge, Bevridge*).
2. **Original Matthew–Abigail Dyer marriage**, reportedly **1801** in the later book, and **Matthew–Clarissa Cobb** original marriage return, period/date unknown; check town and parish records for Fox Islands, Warren, Hope and their historical jurisdictions.
3. **1785 Fox Islands minor Matthew** land-claim or guardianship register, and a **separate parent-naming original** confirming whether Thomas (born around 1750) and Matthew were siblings. This link is unresolved even though Eaton's account explicitly lists both wives.

## Changes to the website

- `data/phase19_matthew_reconciliation_cases.json`: six claim-level original-source and index notes separating *recorded 1865 marriages*, *published 2016 account*, *1785 minor*, *1865 Nathaniel nephew*, and *pre-1860 Waldo probate pathway*.
- `matthew_reconciliation.py`: a new user-facing **two-wife, ten-child published family evidence comparison** with accessible sources and original retrieval tasks, built from the **existing** 1865 household data. No parallel genealogy database was invented.
- `data/phase18_colony_page_source_review.json` and `data/phase16_ancestry_bridge_dossiers.json`: correct the earlier ambiguous framing so users do not see contradictory research explanations.
- `family_discoveries.py` and `colony_source_review.py`: source comparison accessible in **Historical Discoveries** and from **book p.17**.
- `family_research_index.py`: all six cases indexed in the site's whole-archive workbench with exact person links only where supported.
- Regression coverage checks the two five-child groups, published evidentiary limits, reviewed legacy source wording, no invented Matthew genealogy profile or parentage, and completeness of the probate route.

## Unchanged historical integrity

No raw birth/death/marriage records, relationships, privacy-sensitive addresses, family book pages/photos, copyright permissions or Boston Tea Party claims changed. Source reporting is explicitly qualified; an 1865 family report is not automatically an original 1801 marriage certificate.

**Draft PR only; do not merge/deploy unless the user explicitly directs it. No archive contact or record purchase initiated.**
