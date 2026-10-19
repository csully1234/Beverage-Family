# Phase 20 — Matthew Beveridge in Hope's contemporaneous town records (1811–1827)

*Research date 19 October 2026. This phase is a new, independent **municipal evidence trail**, not another repackaging of Eaton's 1865 family history. The underlying manuscript ledger and original 1820 census schedule remain to be inspected.*

## Documentary breakthrough

Newly located: **Hope, Maine Town Clerk Records, 1804–1848**, a literal transcription of the original municipal ledger by **Cynthia S. DellaPenna**, published under Hope Historical Society auspices. A full text/PDF is independently indexed online at:

**[Hope, Maine Town Clerk Records, 1804–1848 — digitized literal transcription (PDF)](https://openyls.law.yale.edu/bitstreams/b01906b3-669f-49a3-8023-099a2cd3ae82/download)**.

A separately cataloged 2021 edition verifies the transcription's nature and provenance: https://www.lulu.com/shop/cynthia-s-dellapenna/hope-maine-town-clerk-records-1804-1848/hardcover/product-27e7n9.html. The **Hope Historical Society** confirms its 1804–1848 ledger is represented in its Documents archive: https://hopehist.com/HHS2.html.

The transcribed town ledger names **Matthew Beveridge repeatedly as town clerk** over a lengthy period, specifically:

| Date | Transcription pages | What the original-era town entry describes | Not established |
|---|---|---|---|
| 2 Apr 1811 | pp. 39–40 | Matthew listed as one of Hope's highway surveyors in an annual appointment vote, with his name as town clerk in the later official April records | Birth parents, autograph validation |
| 5 Apr 1813 | pp. 54–55 | Town officers sworn and clerk attestations attributed to Matthew | Wife, children, home property |
| 1820 | Separate federal census, sheet 276 | Indexer lists **Mathew Beveridge** as Hope household head | Original page and age tallies not inspected |
| 17 Apr 1821 | p. 119 | Clerk-recorded juror appointment to court of common pleas | Parentage or identity with 1785 minor |
| 7 May 1821 | p. 119 | Two official juror and congressional election entries attributed to Matthew | Two entries in same book are not independent corroboration |
| 25 Aug 1827 | p. 196 | Attestation of a Hope town meeting warrant | Original ink signature and identity with 1865 captain |
| 10 Sep 1827 | p. 196 | Clerk attribution on the constable's town meeting return | Separate household proof |
| 17 Dec 1827 | p. 198 | Official town record of Waldo register-of-deeds voting credited to Matthew | He was **not** elected deeds registrar by this line |

Other early posts are possible; the list is not a complete audit of the 456-page transcript. **No source text reproduced beyond concise editorial paraphrases, and no copyrighted ledger PDF or scan is added to the GitHub repository.**

## Independent census trail

**Hope's 1820 United States federal census**, sheet 276, is separately indexed by an experienced genealogist and includes household head *Mathew Beveridge*. Link: https://www.heirloomsreunited.com/2019/09/hope-maine-in-1820-census-then-in.html

The census schedule is genuinely a distinct contemporary historical source from Hope's town ledger. However this researcher has **not viewed the underlying handwritten 1820 census sheet** to compare the spelling or household age/gender columns. Therefore this is categorized as **separate-source index, original pending**.

Research boundary: the presence of a town clerk in 1811–1827 and a same-name household in 1820 makes local continuity likely, but the *unique identity* of all documents has not been authenticated, nor linked conclusively to the 1785 Fox Islands minor or Eaton's 1865 Captain Matthew and his reported two marriages. This should **not** create a new parent/child edge, legal spouse record, or property pin.

## Jurisdiction trap: why earlier document searches were unsuccessful

Some Hope entries correctly state **Lincoln County** in 1820–1821, while 1827 records explicitly reference **Waldo County**. These reflect jurisdictional changes, **not proof of family migration**. The original ledger uses different court or deed index labels at different dates, which guides where early census, probate and court papers may have been recorded.

Do not search only post-1860 Knox County for an 1820s estate. In addition:

- Waldo County probate books and indexes 1826–1892: https://search.worldcat.org/title/866329316 (index of dockets → probate index → probate record volume/page).
- Original-image county probate collection 1760–1979: https://www.familysearch.org/en/search/collection/2040534 .
- Hope historical society's **1821 taxpayer appendix** and town officers index confirmed in May 2022 meeting minutes: https://hopehist.com/Himages/XMay22.html .
- 1820 census original schedules research guide: https://www.archives.gov/research/census/1820 .
- Hope Historical Society documents and ledger original-image access path: https://hopehist.com/HHS2.html .
- Hope pre-1892 town vital record index: https://ldsgenealogy.com/ME/Hope.htm . Original records/images still to inspect, not the indexed names alone.

**This is a vital geographic bridge between an eighteenth-century islander research hypothesis and documented nineteenth-century civic activity:** at least one Matthew Beveridge was physically active as a town officer in Hope from 1811 through 1827. The earlier Eaton 1865 family group describes Capt. Matthew residing in Hope, but none of the 1811–1827 entries by itself labels the clerk a captain or names Abigail, Clarissa, Thomas or Nathaniel. That's the remaining identity work.

## Implementation

- `data/phase20_hope_matthew_civic_records.json`: **eight individual dated records**, each with transcribed source location and verification level, plus four carefully scoped original-document targets; seven references to **one underlying municipal ledger**, one separate census transcription.
- `hope_matthew_civic.py`: searchable-by-era read-only chronological guide, distinct source-family counts, original archive links, and exactly what the records do **not** prove.
- `family_discoveries.py`: dedicated `?page=collection&view=hope-matthew` route, linked at the top of Historical Discoveries.
- `matthew_reconciliation.py`: links to new town-clerk evidence from existing two-marriages family-account story.
- `family_research_index.py`: full unified archive search now indexes all eight dated original-era civic record references, with **zero automatic canonical family person IDs**.
- `tests/test_phase20_hope_matthew_original_era_records.py`: validates dates, source-family non-independence, 1820 census indexed-vs-original status, 1827 jurisdiction clarification, searchable full-workbench links, and unchanged genealogy.

## Prioritization for next stage

1. Obtain **photographic original pages of Hope's 1804–1848 ledger**, compare the ink/handwriting with modern transcription on pages 39–40, 54–55, 119, 196 and 198, and recover the original ledger volume/folio. Do not assume the printed attributions are original autographs.
2. Inspect **1820 census actual sheet 276**, copy the household age-column counts, and compare them with plausible dates for Captain Matthew and family. If a spouse is only inferred from census household counts, label as inferred, not a named census wife.
3. Search original **Hope pre-1892 vital records**, especially Matthew–Abigail Dyer circa 1801 and Matthew–Clarissa Cobb later, and **1821 taxpayer list**. Both must be identity-matched.
4. Follow **Waldo County probate index → docket → volume/page** and inspect every possible variant-surname estate before asserting Capt. Matthew's death year, widow, heirs or parents.

No new outreach, archival purchase, page-rehosting, 2026 residence claims, uncertain family-tree nodes, or modifications to the Boston Tea Party family tradition.

**Draft PR only. Keep branch unmerged and undeployed pending user approval.**
