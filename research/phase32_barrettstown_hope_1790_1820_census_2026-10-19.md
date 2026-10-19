# Phase 32 — Barrettstown to Hope, 1790–1820: separate the census originals from name-index claims

**Research performed:** 19 October 2026. **Baseline:** Phase 31 main `26d31313fb18bafefd050a44b422807ddc12473b`.

## Evidence-first outcome

The available published *1790 and 1800 Barrettstown Plantation household-head transcriptions* contain **no Beverage/Beveridge surname among recorded household heads**. This is an actual **negative search in those transcribed lists**, not an original-image finding, proof of Matthew's physical absence, or proof that he resided somewhere else. In 1790 Barrettstown included the area later known as Appleton; by 1800 separate Appleton material must also be searched. Household censuses often name only the head, so a resident could be in another household.

The **1810 Hope census** is now independently located to **National Archives microfilm M252, roll 12, beginning at Hope manuscript p. 136**, including a full reel digitized by Internet Archive. **No legible Matthew row or demographic counts from the actual schedule have been inspected in this investigation**.

The **1820 Hope census** is located to **NARA M33, roll 36**, township pages 275–278. A published 2019 household-head transcription lists **Mathew Beveridge on sheet 276**, independently from the Hope town-clerk transcription. The 1820 actual sheet and tally columns were **not read**. The corresponding historical person identity remains an inference pending additional independent records.

These findings make the 1806 Hope clerk transcription a comparatively strong positive **dated municipal** record amid census uncertainty. None connects him to the 1785 Fox Islands petition minor or proves the 1837 Hope decedent was the same person.

## Source examination table

| Year | County and historic jurisdiction | Exact source and link | What was actually verified | Limit |
| --- | --- | --- | --- | --- |
| **1790** | Barrettstown, Hancock, District of Maine / Massachusetts | [Maine Genealogy Archives transcription](https://archives.mainegenealogy.net/2006/10/1790-census-barrettstown-plantation.html) from 1908 federal print, p. 26 | No Beverage/Beveridge household head appears among published named heads | Census does not name most household members. This plantation also included future Appleton |
| **1800** | Barrettstown, Lincoln, District of Maine | [Maine Genealogy Archives, NARA M32 roll 6, pp. 544–548](https://archives.mainegenealogy.net/2008/05/1800-census-barrettstown-plantation.html) | Full published head list searched; no Beverage/Beveridge head. **Charles Whitney** appears p. 544; **Levi Whitney** appears p. 547 | No original manuscript inspected. These Whitneys are **not** evidence for the probate's tentative *Lucy Whitney* seller reading. Check Appleton and neighboring enumerations |
| **1810** | Hope, Lincoln, District of Maine | [Maine Genealogy census guide M252-12, p. 136](https://www.mainegenealogy.net/census_guide.asp?censusyear=1810&county=lincoln); [Internet Archive public complete 1810 census roll](https://archive.org/details/populationschedu0012unix) | Verified the institutional/census reel and starting manuscript page, not any Matthew name in the census | No original Hope household head or age counts read. A named clerk in the municipal ledger is **not** a substitute for an independently viewed census record |
| **1820** | Hope, Lincoln, Maine | [Heirlooms Reunited named-household transcription](https://www.heirloomsreunited.com/2019/09/hope-maine-in-1820-census-then-in.html) sheet 276; [Maine Genealogy M33-36 township index](https://www.mainegenealogy.net/census_guide.asp?censusyear=1820&county=lincoln) | 2019 transcriber identifies head **Mathew Beveridge** on original schedule sheet 276 | NARA M33 roll **36** (NOT roll 37, which covers Washington County). Census row handwriting and age/sex tick marks are not yet inspected |

The 1810 and 1820 reel identifiers have been independently corroborated by the NARA 1810 census microfilm listing and Maine Genealogy's state/county census finding aids. The original 1810 microfilm was digitized and made accessible as a 1,090-page archive.org item, but a full item preview is **not evidence** that the relevant 1810 census page was visually inspected.

### Additional early civic context

A publicly indexed extract from *Hope, Maine Town Clerk Records 1804–1848* (Yale Law archive-hosted literal transcription, p. 35–36) credits town records dated in May and September **1810** to Matthew Beveridge. Those are additional dated passages from the **same Hope municipal ledger** (not census evidence, not independent parentage proof). The verified earlier **June 23, 1806** town-clerk passage remains the current earliest positive dated indexed municipal record in this research. [Hope clerk transcription PDF](https://openyls.law.yale.edu/bitstreams/b01906b3-669f-49a3-8023-099a2cd3ae82/download).

## Original-source reading order and decision rules

1. Open [1810 complete reel M252-12](https://archive.org/details/populationschedu0012unix) and find the **Hope** township from manuscript p. 136. Inspect contiguous census images through the end of Hope (before Plantation of Appleton Ridge, beginning at p. 142), allowing for manuscript page-number and scan-leaf offsets. **Photograph or transcribe the named row only if legible**; capture the exact age/sex tick marks and spelling with a reliable image citation.
2. Open **1820 M33 roll 36**, Hope sheet **276**; verify **Mathew Beveridge**, all age brackets and occupational/household tallies, and adjacent household names from the image. Never treat unlabelled household counts as named spouse/children.
3. Compare the earlier **1790/1800 head-list transcripts** against manuscript images, including **1800 Appleton Plantation** and nearby enumerations. Absence from one list does not establish a move or birth year.
4. The separate Hope tax list (1821), land conveyances (Lincoln pre-1827; Waldo after), and 1837 probate may supply a verifiable **identity chain**, but the census findings alone cannot bridge them.
5. If an original-page census line is obtained, attach its exact repository, roll, page, high-res URL and individual columns, with a clear uncertainty label. Do not invent missing handwriting or retrofit a confirmed person ID.

## Website implementation

- `data/phase32_hope_census_originals.json` stores four year-specific source cards with accurate positive/negative/unknown status, microfilm roll, township page, transcription coverage and explicit limits.
- `hope_census_records.py` shows each year in a readable family-facing comparison with official original-file links, reading checklists and connections to the **1806** clerk, **1785–1786** Fox Islands, and **1837** Waldo probate views.
- Integrated into Historical Discoveries and Hope clerk pages as **Barrettstown to Hope: 1790–1820**.
- All four source cards searchable through the unified research workbench **without a canonical person link** because the linked historical identity remains unproved.
- Structural tests require the absence claims to remain limited to published head lists and enforce no original-age tallies or ancestry edges have been invented.

**No site password, genealogy parent, spouse, child, address, book PDF, probate scan reproduction permission, or the protected Boston Tea Party claim was modified.**

This phase resolves **where to find the original schedules and what the existing transcriptions say**. It does not yet resolve Matthew's unique census identity in 1810, nor his origin or parentage.
