# Phase 43 — Vinalhaven Beverage civic history, 1790–1846

**Research date:** 20 October 2026.  
**Baseline:** Phase 42 merged as `49052ad80e2c2671b6981cb37572e9c07ee576e4`. The existing shared family login and family-tree record set are intentionally unchanged.

## Newly usable historical source

**Vinalhaven Centennial Committee**, *A Brief Historical Sketch of the Town of Vinalhaven, From Its Earliest Settlement* (Rockland, Maine: Free Press Office, **1889**), printed **pp. 35–39**, publishes year-by-year names of the **town clerk; treasurer; selectmen** from 1790 onward. See [Maine Genealogy's source-attributed transcription](https://archives.mainegenealogy.net/2007/01/vinalhaven-town-officers-1790-1889.html); complete 1889 edition [Google Play Books (free)](https://play.google.com/store/books/details/Vinalhaven_Me_Centennial_Committee_A_Brief_Histori?id=gJ9CIFiSOY0C).

This provides an authentic 19th-century **published civic history**, close in time to the latest years, that is independent of modern contributed family trees. It is NOT original signed town election minutes. The original 1889 printed-page photographs and 1790–1846 original municipal minutes have not been read; the published name list is visible in the attributed transcription. The genealogy site does not claim that each year is an independent witness or a contemporaneous register.

### Extracted full published Beverage surname roster

The resulting `data/phase43_vinalhaven_civic_officers.json` includes **55 office entries across 41 years** from 1790–1846, with the exact 1889 printed page, original year, name *as printed*, role, source URL and cautious potential-profile **comparisons** only.

| Printed name | Recorded office(s) | Annual entries, grouped by year |
| --- | --- | --- |
| Thomas Beverage | Town clerk, selectman | clerk **1790–1798** (9 annual records); selectman **1797** and **1810** |
| John Beverage | Town clerk | **1799–1812**, 14 consecutive annual roster records |
| Benjamin Beverage | Selectman | **1806–1810, 1812, 1815–1817, 1819–1822, 1836–1837, 1839** (16 entries) |
| Nathaniel Beverage | Town treasurer, selectman | treasurer **1813–1819** (7); selectman **1812, 1818 and 1828** |
| James Beverage | Selectman | **1833, 1834 and 1842** |
| Josiah Beverage | Selectman | **1846** |

Distinct people named in print: **6 name strings**, not six identity-certified individuals; a "Benjamin" or "Thomas" might represent different men over the span. Role counts: **23 clerks, 7 treasurers, 25 selectmen** (55 annual office-role rows), not unique terms of office. The 1889 compilation does not necessarily prove exact election dates or uninterrupted service.

### Significant identity constraints

1. **Nathaniel 1812:** The surname-only listing of an adult selectman in 1812 cannot reasonably identify Rockland Nathaniel whose approximate birth is 1804 in the actual tree (age ~8), nor the online derivative's alternative precise 1803 date (age ~9). **Nathaniel Winslow Beverage (born 1776)** is chronologically plausible, but the 1889 source does NOT name a middle name, birth date or parents, so it does **not** confirm he held that office. Distinguish his other 1813–1819 treasurer records and 1818, 1828 selectman entries in the same way.
2. **John 1799–1812:** John White Beverage (born 1774) is chronologically plausible, but *John Beverage* in the roster could be another John. A 14-year sequence strongly supports civic historical presence of a printed John, but **does not prove Nathaniel's or Josiah's ancestry**. The original contemporary oath or town book might establish more.
3. **Benjamin 1806–1812 vs 1830s:** Benjamin Kent Beverage born 1779 is old enough for the first appearance; Benjamin Crabtree Beverage born 1822 was not. Their shared surname and forename across later 1836/1837/1839 rows are **not enough to assign all entries to one person**.
4. **Josiah 1846:** Both Josiah Winslow Beverage (born 1793) and Josiah B. "Si" Beverage (born 1821) could be adults in 1846. The single printed name does not resolve the Phase 41 parentage conflict or prove they are the same person.
5. **Thomas 1790–1798:** Capt. Thomas Beverage (born 1750) is a possible identification. The printed list does not provide a parentage bridge, and it cannot resolve the distinct 1837 Thomas-deed-after-recorded-1834-death contradiction.

The source is a *new 19th-century civic evidence family*, not a source of genealogical birth, death, parent or marriage statements. No existing person is assigned a confirmed municipal office.

### Improvements implemented

- Source-faithful JSON inventory with all 55 entries, unedited period-specific page locators and an explicit "printed-name only" status for **every row**.
- `vinalhaven_civic_history.py` builds the visitor exhibit in the existing Family Origins Expedition, with per-person-string and office filters, complete uncapped interactive table, original printed page/year inspection, shareable deep links and CSV download.
- It compares already indexed **name candidates** to published office dates. Chronologically impossible cases are flagged rather than linked as supported identities; plausible-aged comparisons remain labeled **not proven**.
- From affected individual historical life exhibits, visitors can open a same-name **comparison** without creating an unreviewed person/event source attribution.
- **All 55 entries are searchable** in the Research Workbench as "Historical record trails," with the source URL, original year, office, precise 1889 printed page and zero canonical person IDs.
- Homepage "More ways to explore" links directly to the exhibit.
- New regression tests validate complete source coverage, exact five-page ranges, year-role counts, Nathaniel 1812 chronological exclusion, both possible Josiahs in 1846, absence of invented person links, unchanged 202 people/four branches, and preserved shared family password.

### Highest-value next original documents

Seek 1799–1812 **Vinalhaven original annual election/appointment and town-clerk signature entries** that distinguish which John is named; seek **1812 and 1818** municipal officer/minute manuscripts for the adult Nathaniel. Check Vinalhaven's historical 1846 oath/selection entry for whether its Josiah bears a distinguishing initial, age, property description or spouse. Original Vinalhaven town records are cataloged as FamilySearch **DGS 7596929**, but these particular civic appointment pages are **not yet located or read**. The 1800 John–Rachel marriage and the Nathaniel 1803 / Josiah 1821 birth records remain separate high-priority targets from Phase 42.

**Restrictions preserved:** No genealogical edge, person birth/death, historical address, Boston Tea Party wording, book/license, family password or archive ownership changed. No emails or external requests sent.

## Release tests

Run full Python 3.12+3.13, JS family-tree/map interactions, the historical validator, archive path checks and post-merge verified backup. Merge a single tested PR; manually deploy Render, confirm exact merge commit `live`, and check startup errors. Authenticated phone/browser user testing remains separate from CI.
