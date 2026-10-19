# Phase 34 — Find the original 1820 Hope census reel; distinguish the 1813 bond and 1821 clerk vote

**Research performed:** October 19, 2026.  
**Repository baseline:** Phase 33 merged main, Render confirmed live.  
**Publication decision:** Show only links and textual research summaries; **do not rehost archival scans** or assert family relationships.

## Finding A — Exact original 1820 reel now linked

The original microfilm reproduction of the **1820 Lincoln County, Maine census** is available as Internet Archive item [populationsc18200036unit](https://archive.org/details/populationsc18200036unit), *Population schedules ... 1820, Maine*, 1959 preservation copy digitized by Allen County Public Library Genealogy Center. Its own metadata identifies **Reel 0036**, National Archives M33 series, covering Lincoln County, and **209 scanned IA pages**. The source is therefore more direct than linking only a federal guide or the 2019 name transcription.

- **Manuscript locator:** Hope township, pages **275–278**, from [Maine Genealogy's 1820 Lincoln County census guide](https://www.mainegenealogy.net/census_guide.asp?censusyear=1820&county=lincoln).
- **Independent modern transcription:** [Heirlooms Reunited's 2019 Hope household-head index](https://www.heirloomsreunited.com/2019/09/hope-maine-in-1820-census-then-in.html) reports **“Mathew Beveridge” on sheet 276**; the site also attributes the return to enumerator Thurston Whiting.
- **What has *not* been read:** the Mathew handwritten name and every household age/sex or occupation tally on the original image. The IA item listing and landing-page metadata were accessible, but its JavaScript-driven manuscript viewer did not yield a legible subject row in the research environment. Do not claim scan number, household composition, birth year, spouse/child names, or manuscript spelling from the uninspected original.
- **Next operation:** navigate page by page within the digitized original until manuscript sheet 276, capture the exact visual image source and date, then transcribe columns on both sides of the double-page if necessary. Do not confuse **IA scanned-page index** with historic **manuscript folio**.

## Finding B — Town collector's accepted bondsmen in 1813 context

The indexed public text of [*Hope, Maine Town Clerk Records 1804–1848*](https://openyls.law.yale.edu/bitstreams/b01906b3-669f-49a3-8023-099a2cd3ae82/download), 2021 literal transcription, p. **54**, vote **17**, identifies **Matthew Beveridge**, **Almond Gushe** and **Micah Hobbs** as bondsmen accepted for the town collector for the current year. The passage occurs immediately before the **April 5, 1813** town clerk note on the following page, already indexed by Phase 20. It is a **different function** from Matthew's ordinary role signing as town clerk, though from the **same underlying municipal ledger**.

**Limits:** The precise date of numbered vote 17 is not independently fixed by the isolated indexed snippet. Being named a bondsman does not establish property ownership, parentage, place of birth, or linkage to 1785 petition minor or 1837 decedent.

## Finding C — Town voters expressly choose Matthew as clerk in April 1821

The **same transcript**, p. **116**, has an April town meeting vote naming **Matthew Beveridge** as town clerk for the present year. This is an **explicit recorded selection**, rather than simply an officer's name appearing at the end of an attestation. It is an additional passage of a previously known 1821 clerk ledger; not a separate independently collected original.

**Date discrepancy requiring manuscript inspection:** The indexed transcription gives a header **“Hope April 2nd 1821”**, but meeting text says **“third day of April it being the first monday”**. Gregorian April **2, 1821 was Monday**, and April **3 was Tuesday**. The isolated transcription does **not** decide whether one date was mistyped, whether the header refers to something different, or what the historic manuscript actually says. The new display reads **“April 1821 — exact date unresolved”**, not an invented April 2 or April 3 event date.

## Comparison with prior evidence

| Date or period | Underlying source family | What we can currently say | Remaining evidence gap |
| --- | --- | --- | --- |
| 1785–1786 | Fox Islands petition/survey | “Matthew Beveridge (a minor)” appears in published Fox Islands historical excerpts | Whether this minor became Matthew of Hope |
| 1806 and 1807 | Hope municipal ledger, *one underlying record family* | Matthew credited as clerk in dated later transcription | Original manuscript and signature |
| 1810 | Federal census M252 roll 12 | Hope original reel located, name and tallies not verified | Inspect Hope manuscript pp. 136–141 |
| 1813 | Same Hope ledger | Matthew accepted with two named bondsmen for town collector; separately signed a clerk record | Exact meeting date and manuscript |
| 1820 | Federal census M33 roll 36 | Original full county reel accessible; index separately names Mathew household head, sheet 276 | Read original handwriting and anonymous age tallies |
| April 1821 | Same Hope ledger | Voted Matthew clerk for year, from modern transcript | Contradictory transcript day numbers; check manuscript |
| 1837 | Waldo probate | Eight court-described children and widow Clarissa already reviewed elsewhere | Prove census/clerical identity match and original Hope origin |

The 1813/1821 entries share a source **with** the earlier 1806/1807/1811/1827 entries; they are **not** multiple independent attesters of his biological family. The 1820 census is independent as a historic record **type**, but its observed name currently derives from a separate *modern transcription*, not a first-hand view of the manuscript. Nearby same-sheet names cannot themselves prove land dealings or family connection.

## Website and testing

Added additive versioned **`data/phase34_hope_original_reel_and_civic_votes.json`** and read-only **`hope_primary_access.py`**. Visitors see all three full attributed source cards in existing **Historical Discoveries → Barrettstown to Hope, 1790–1820**, with original reel and publication links, explicit uncertainty labels, and tasks to verify pages. Three index entries are also searchable in **Research Workbench**; **none is attributed to a canonical person ID**.

Regression tests validate exact archive ID/roll, historic vs scan-page caution, bond co-signers, the 1821 conflicting calendar labels, original-manuscript-read flags, existing previous census status, unaltered family profiles, and password compatibility. CI must pass Python 3.12/3.13, family-tree data validation, repository release audit, and JS map interactions before merge.

**No changes** to imported/verified person or event datasets, Boston Tea Party assertion, relative addresses, site password, private Waldo probate scans, historic photo licensing, or existing deployment configuration. Render's automatic deployment remains disabled; only deploy after release checks pass.

## Priority next research

1. **Personally inspect the 1820 original manuscript, Hope sheet 276** through the already identified exact reel. Record the image citation and all columns with confidence, not estimates.
2. Inspect **1810 Hope M252 roll 12 pp. 136–141** for Matthew and relevant variants; do not assume a household exists.
3. Check **original Hope ledger manuscripts**, especially the vote context for the 1813 bond and the contradictory 1821 dates.
4. Retrieve **Lincoln/Waldo deeds** and compare named parties with 1837 estate to bridge identity. Do not infer birth parents solely from place and surname.
