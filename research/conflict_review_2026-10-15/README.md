# Conflict review and family usability — 15 October 2026

This versioned successor supplements the five original reports; it does not replace them. Research conclusions are AI-reviewed proposals, not family approval. PR #9 was verified merged, and this work starts from `main` commit `7ce454f95ed3aed60dda717d5c2e36237bbf1047`. The repository contains 180 profiles, 127 events, 57 imported findings, 163 imported sources and 11 imported conflict records.

## Result and scope

One conflict is resolved at the event-classification level (Diana’s baptism); six are narrowed and four await inaccessible original evidence. Diana’s actual birth remains unknown. All eleven are **Not reviewed by family**. Five new source records include one explicit user-tree lead. Ten previously registered historical/baseline sources and one access guide were reexamined; source dependence is recorded rather than counted as independent corroboration. This is a targeted conflict review, not a claim to have exhausted every archive.

Only three profiles receive proposed factual display corrections: Sarah Holman’s birth is unknown; Diana’s December 31, 1780 date is labeled baptism, with birth unknown; Lowell’s birthplace is proposed as Dorchester, Massachusetts, strongly supported by the 1948 institutional register. No relationship, person ID, residence, property, or event record changes. Both Amelia IDs and both Sarahs remain distinct.

- [Machine-readable resolution ledger](../../data/reviews/conflicts_2026-10-15.json) — former fields, reasoning, citations, status, identity checks and retrieval requests.
- [Prepared requests and verified contacts](retrieval_requests.md) — nothing sent, purchased or ordered.
- [Search and access log](search_log.md) and [URL transport checks](link_checks.json).
- [Implementation and verification](verification.md).

## Conflict outcomes

| Research ID | Subject | Outcome | Confidence |
|---|---|---|---|
| [BF-R005](#bf-r005) | Sarah Holman and Mary White: incompatible dates | Narrowed but unresolved | Strongly supported |
| [BF-R008](#bf-r008) | Diana Daggett: baptism recorded as birth | Resolved with documented evidence | Strongly supported |
| [BF-R011](#bf-r011) | A Thomas Beverage deed cited after his death | Awaiting an inaccessible original | Conflict |
| [BF-R012](#bf-r012) | Two Sarahs linked to Benjamin Kent | Narrowed but unresolved | Probable |
| [BF-R014](#bf-r014) | Benjamin Kent: January or June birth? | Awaiting an inaccessible original | Conflict |
| [BF-R032](#bf-r032) | Eliot / Elliot: birthplace and spelling conflict | Narrowed but unresolved | Probable |
| [BF-R039](#bf-r039) | Lowell’s memorial: age and birthplace cautions | Narrowed but unresolved | Strongly supported |
| [BF-R046](#bf-r046) | Charles Howard’s birth year conflict | Narrowed but unresolved | Possible lead |
| [BF-R047](#bf-r047) | Benjamin Crabtree’s death-day conflict | Awaiting an inaccessible original | Conflict |
| [BF-R048](#bf-r048) | Sarah Sally’s death-day conflict | Awaiting an inaccessible original | Conflict |
| [BF-R049](#bf-r049) | Two Amelia profiles requiring identity review | Narrowed but unresolved | Probable |

## Preservation and correction model

Original JSON records, the imported collection, five reports and baseline hashes are unchanged. A separate ledger applies a small allowlist of fields after the existing overlays and date precision. Each correction must match its expected former value and carry substantial evidence; otherwise loading fails. The effective data is shared by profiles, search, tree, archive and exports. The old value remains in the ledger and each affected profile’s audit metadata. No hash was regenerated to accommodate a correction.

Sarah’s documented 1733/34 marriage establishes historical activity despite her unknown birth. The privacy check accepts only a sourced, substantially supported activity more than 120 years old; an explicit living flag still wins. It does not infer historical status from a surname, relative or address.

The birth-place proposal for Lowell is not a residence/property edit. His original North Haven assertion remains in the immutable data and earlier conflict note, now labeled as earlier evidence. Existing Tea Party wording and every address/property field remain intact. Original imported narratives and reports remain available as dated snapshots and may contain superseded values.

## Detailed evidence reviews

### BF-R005

**Sarah Holman and Mary White: incompatible dates**

Profiles: `sarah_holman_1734`, `mary_white_1728`, `james_beveridge_sr_1700`, `james_beveridge_jr_1724`, `susannah_beveridge_1735`, `jane_beveridge_1737`, `mary_beveridge_1739`

**Existing claims:** Sarah Holman’s stored birth date equals her marriage date. Mary White’s stored 1728 birth would make her about two at the recorded 1730 marriage; daughters born after her stored 1731 death also require review.

**Competing explanations:** These are incompatible repository fields, not grounds to invent replacement dates. Essex notes assign Susannah, Mary and Jane to Sarah, unlike portions of the repository.

**Proposed conclusion:** February 7, 1733/34 is a documented marriage date, not an established birth date for Sarah Holman. Suppress the unsupported exact birth in the effective profile; retain its original value here. Mary White’s dates and the daughters’ maternity remain unresolved.

**Evidence reasoning:** The 1904 marriage transcription explicitly places both James marriages under marriages. The 1905 Essex note assigns Susannah, Mary and Jane to Sarah. These derivative accounts may use the same records; they do not supply Sarah’s birth or prove Mary’s vital dates. Do not substitute the 1706 Sarah Holman found in user trees without identity proof.

**Identity reasoning:** Groom James, bride Sarah, place and day match the stored marriage. James Jr. has a stored 1724 birth and is a separate profile; no reassignment of the marriages or children is made.

**Sources:** [SRC001](#source-src001), [SRC119](#source-src119), [CRS002](#source-crs002)

**Status:** Narrowed but unresolved; **confidence:** Strongly supported; **family review:** Not reviewed by family.

| Profile | Field | Former value | Proposed display value | Reason |
|---|---|---|---|---|
| `sarah_holman_1734` | `birth_date` | 1734-02-07 | None | Stored date matches the documented marriage; no birth evidence located. |
| `sarah_holman_1734` | `birth_date_precision` | None | unknown | No defensible birth date. |

**Next record:** Obtain original Marblehead marriage entries (1729/30 and 1733/34) and identify the 1789 Essex deed naming the three unmarried sisters; establish Mary’s own birth/death and each child’s mother.

### BF-R008

**Diana Daggett: baptism recorded as birth**

Profiles: `diana_daggett_1780`

**Existing claims:** The Doggett-Daggett genealogy identifies Diana’s December 31, 1780 event at Edgartown as baptism, while the repository stores it as birth.

**Competing explanations:** Baptism and birth are different events. Original church entry is required; preserve the repository value pending review.

**Proposed conclusion:** The December 31, 1780 entry is a baptism at Edgartown. Display baptism separately and leave the birth date unknown. The actual birth date and birthplace still need an original record.

**Evidence reasoning:** The scanned 1906 vital-record transcription says bp. and cites Congregational church records. Doggett (1894), p. 113, entry 1033 also calls it baptism and connects Diana to Nathaniel Beverage. Agreement may reflect a shared church source, so independent corroboration is not claimed. Resolution is limited to event type, not exact birth or new parent relationships.

**Identity reasoning:** Diana’s name, date and the genealogy’s Nathaniel Beverage spouse agree with the repository. The printed vital entry names Benjamin Jr. and Elizabeth, matching the genealogy, but no new parent IDs are created.

**Sources:** [SRC001](#source-src001), [SRC121](#source-src121), [CRS001](#source-crs001)

**Status:** Resolved with documented evidence; **confidence:** Strongly supported; **family review:** Not reviewed by family.

| Profile | Field | Former value | Proposed display value | Reason |
|---|---|---|---|---|
| `diana_daggett_1780` | `birth_date` | 1780-12-31 | None | The cited date documents baptism, not birth. |
| `diana_daggett_1780` | `birth_date_precision` | None | unknown | Baptism cannot supply an exact birth date. |
| `diana_daggett_1780` | `baptism_date` | None | 1780-12-31 | Published church-record transcription. |
| `diana_daggett_1780` | `baptism_place` | None | Edgartown, Massachusetts | Place of the baptism, not an inferred birthplace. |

**Next record:** Retrieve the original Church of Christ (Congregational), Edgartown baptism register for December 31, 1780, with heading and adjacent entries; seek any distinct birth entry. Maine birthplace remains a preserved, unverified baseline claim.

### BF-R011

**A Thomas Beverage deed cited after his death**

Profiles: `thomas_beverage_1750`

**Existing claims:** A Woodruff biography cites a Thomas Beverage to James Beverage and others deed under June 28, 1837, after Thomas’s repository death in 1834.

**Competing explanations:** Could be recording date, estate action or another Thomas. Original execution and acknowledgment clauses must be checked; no death-date correction is justified.

**Proposed conclusion:** No death-date or property correction is justified. The 1837 date remains an unresolved deed citation; it has not been shown to be execution, recording or estate action.

**Evidence reasoning:** The Woodruff note provides an exact DGS/page/image target but only a generic FamilySearch link. Direct film/catalog retrieval was inaccessible. Seaview transcription lists Capt. Thomas’s death October 4, 1834 and spouse Mercy, supporting the need to inspect the deed rather than assume a later death.

**Identity reasoning:** The deed parties alone do not distinguish Capt. Thomas from another Thomas or a posthumous transaction.

**Sources:** [SRC001](#source-src001), [SRC123](#source-src123), [SRC091](#source-src091)

**Status:** Awaiting an inaccessible original; **confidence:** Conflict; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Read the complete deed at DGS 8296915, p. 387, image 207/601; capture book/volume, all parties, capacities, execution, acknowledgment and recording dates.

### BF-R012

**Two Sarahs linked to Benjamin Kent**

Profiles: `sarah_beveridge_kent_1758`, `sarah_beverage_1785`, `benjamin_kent_1755`

**Existing claims:** The Kent cemetery transcription calls Sarah Beverage Kent, deceased November 23, 1821 aged 63 years 5 months, a sister of Capt. Thomas. She must not be merged with his daughter Sarah Sally, born 1785.

**Competing explanations:** Repository links both women to Benjamin Kent 1755. A duplicated transcription line says s.o., the fuller line says sis.o.; use original stone and marriages to distinguish them.

**Proposed conclusion:** The older Sarah Kent and Thomas’s daughter Sarah Sally must remain separate. The older Sarah is the more plausible wife in the Kent family evidence, but the spouse links cannot yet be conclusively reassigned.

**Evidence reasoning:** Kent cemetery gives Sarah’s age as 63 years 5 months at her 1821 death, consistent with about 1758, and its fuller duplicate line says sister of Capt. Thomas. The Woodruff junior biography cites that same cemetery entry, so it is dependent rather than independent proof. A separate Seaview Sarah died in 1844 at 59 years 8 months.

**Identity reasoning:** The two deaths, ages, and sister-versus-daughter generations distinguish the women; Benjamin junior’s 1798 birth also makes Sarah born 1785 an implausible mother. Neither age arithmetic nor later narrative proves the marriage.

**Sources:** [SRC001](#source-src001), [SRC092](#source-src092), [SRC091](#source-src091), [SRC125](#source-src125)

**Status:** Narrowed but unresolved; **confidence:** Probable; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Obtain Benjamin senior’s marriage, the original Kent stone and the Vinalhaven Kent family register. Verify senior’s own birth year, too; a user-tree lead gives 1760 rather than stored 1755.

### BF-R014

**Benjamin Kent: January or June birth?**

Profiles: No existing junior profile; keep the research question distinct from Benjamin senior.

**Existing claims:** The edited Benjamin Kent biography gives June 17, 1798 in its narrative and January 17 in a note; Fuller transcription gives June 17.

**Competing explanations:** Internal editorial inconsistency remains unresolved until the cited original vital-record image is checked.

**Proposed conclusion:** June 17 is better represented in the published accounts, but the January/June conflict is not resolved. Do not create a junior profile or attach his dates to the senior Benjamin.

**Evidence reasoning:** The Woodruff narrative and Fuller inscription transcription say June 17, 1798. The Woodruff footnote says January 17 and identifies the original town page. The narrative could depend on the cemetery entry; a vote of two derivative statements is not decisive.

**Identity reasoning:** Junior’s Deborah Thomas marriage and 1882 death distinguish him from the repository’s senior Benjamin. Original family-register context must identify parents.

**Sources:** [SRC125](#source-src125), [SRC090](#source-src090)

**Status:** Awaiting an inaccessible original; **confidence:** Conflict; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Retrieve Vinalhaven town and vital records, DGS 7596929, p. 389, image 215/837, and marriage p. 431, image 236/837.

### BF-R032

**Eliot / Elliot: birthplace and spelling conflict**

Profiles: `elliot_beverage_1908`

**Existing claims:** The repository calls him Elliot Pierson Beverage born North Haven; NHHS calls him Eliot Beveridge born Massachusetts in 1908.

**Competing explanations:** Years and island career suggest the same person, but original birth and Harvard records are needed. Preserve both spellings and locations.

**Proposed conclusion:** A contemporary Harvard newspaper supports the Eliot P. Beveridge spelling and education connection. Massachusetts birthplace remains plausible but unproved; keep the existing profile name and birthplace while exposing the alternative in research and search.

**Evidence reasoning:** The Crimson identifies Eliot P. Beveridge, Harvard A.B. 1930 and A.M. 1931, in 1934; NHHS independently describes Eliot’s Harvard education, island business and 1908–1982 lifespan. Neither the newspaper’s residence nor NHHS narrative substitutes for a birth entry. The online newspaper spells the place Derchester; preserve the transcription caveat.

**Identity reasoning:** Name, middle initial, educational chronology and NHHS life dates support association. Exact birth and parentage still require a certificate or Harvard biographical file. Search expansion is not an identity merge.

**Sources:** [SRC001](#source-src001), [SRC116](#source-src116), [CRS004](#source-crs004)

**Status:** Narrowed but unresolved; **confidence:** Probable; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Seek Massachusetts 1908 birth under Eliot/Elliot P. Beverage/Beveridge, parents Orris Lyford and Rose Emma Pierson; consult Harvard class of 1930 alumni/biographical records. September 15 from a derivative memorial site is a lead, not an adopted date.

### BF-R039

**Lowell’s memorial: age and birthplace cautions**

Profiles: `lowell_beveridge_1905`

**Existing claims:** The diocesan memorial prints 1905-09-19 to 1991-06-18 but calls Lowell 86; those dates yield 85. It calls him a Boston native, while the repository retains North Haven birthplace.

**Competing explanations:** Age is internally inconsistent; native need not be a precise birth-place statement. Do not count this likely obituary reuse as independent corroboration.

**Proposed conclusion:** The printed life dates imply age 85, not 86. A 1948 institutional register directly names Dorchester, Massachusetts as birthplace; propose that birthplace with a citation while retaining North Haven in the audit. Birth-certificate verification remains open.

**Evidence reasoning:** The age calculation uses September 19, 1905 and June 18, 1991. Union’s 1948 catalogue predates the obituary and explicitly says born Dorchester, unlike the ambiguous Boston native wording. Existing obituary and diocesan memorial may share text and count as one evidentiary stream.

**Identity reasoning:** Full name, exact birth date, Harvard degrees, Wellesley employment and Columbia music appointment match the existing Lowell profile. This identifies the register subject strongly without inferring a new relative.

**Sources:** [SRC001](#source-src001), [SRC129](#source-src129), [CRS003](#source-crs003)

**Status:** Narrowed but unresolved; **confidence:** Strongly supported; **family review:** Not reviewed by family.

| Profile | Field | Former value | Proposed display value | Reason |
|---|---|---|---|---|
| `lowell_beveridge_1905` | `birth_place` | North Haven, Maine | Dorchester, Massachusetts | Direct contemporary institutional statement with matching life/career identifiers. |

**Subfinding:** Age from the memorial’s printed life dates — 85 years; arithmetic discrepancy resolved without altering either life date (Confirmed).

**Next record:** Obtain Massachusetts/Boston birth entry for September 19, 1905, Lowell Pierson Beveridge, parents Orris Lyford and Rose Emma Pierson, to close the remaining vital-record question.

### BF-R046

**Charles Howard’s birth year conflict**

Profiles: `charles_beverage_1863`

**Existing claims:** Seaview lists Charles H. as 1862–1938, versus repository birth year 1863.

**Competing explanations:** Surname, initials and death year fit; original stone, birth register and spouse record required.

**Proposed conclusion:** The birth year remains unresolved, and a newly located tree lead uses Charles Hanson rather than Charles Howard. Verify the middle name as well as 1862/1863.

**Evidence reasoning:** Seaview lists Charles H., 1862–1938, husband of Annie A. Leadbetter; another row calls her Annie U. The public family tree calls Benjamin and Amelia’s son Charles Hanson, 1862–1938. Those derivative sources may be related; no original birth or marriage image was accessible.

**Identity reasoning:** Parents, sibling cluster, initial and death year make this a useful candidate, not proof. Do not substitute Hanson or add a spouse merely from these pages.

**Sources:** [SRC001](#source-src001), [SRC091](#source-src091), [CRS005](#source-crs005)

**Status:** Narrowed but unresolved; **confidence:** Possible lead; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Obtain North Haven birth record 1862–1863, 1938 death record and marriage to Annie/Anne Ursula Leadbetter; compare both middle names and parents.

### BF-R047

**Benjamin Crabtree’s death-day conflict**

Profiles: `benjamin_beverage_1822`

**Existing claims:** Seaview gives Benjamin C. death December 17, 1875, versus repository December 7.

**Competing explanations:** Transcription also misplaces death year in birth field. Do not silently replace the baseline day; obtain stone and town death register.

**Proposed conclusion:** December 7 versus December 17, 1875 remains open. Keep the stored day and display the conflict; the cemetery transcription is not safe for an automatic replacement.

**Evidence reasoning:** Seaview repeats death year 1875 in the birth column while giving age 53y 2m 15d. This is an internal transcription defect. The public family tree supplies a household/cemetery retrieval route but no viewed original record resolving the day.

**Identity reasoning:** Initial C., spouse Amelia and approximate age fit Benjamin Crabtree, but that does not validate the day.

**Sources:** [SRC001](#source-src001), [SRC091](#source-src091), [CRS005](#source-crs005)

**Status:** Awaiting an inaccessible original; **confidence:** Conflict; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Retrieve North Haven December 1875 death register and Benjamin C. gravestone photograph; compare December 7 and 17 and the original age inscription.

### BF-R048

**Sarah Sally’s death-day conflict**

Profiles: `sarah_beverage_1785`

**Existing claims:** Seaview gives Sarah death November 23, 1844 aged 59 years 8 months, versus repository November 28.

**Competing explanations:** Matching age supports candidate identity but stone or vital entry is needed to resolve the day.

**Proposed conclusion:** November 23 versus November 28, 1844 remains open. Preserve the stored day and distinguish this woman from the older Sarah Kent.

**Evidence reasoning:** Seaview’s age 59y 8m fits a March 1785 birth but cannot distinguish the two November days. A user-tree search also repeats November 28; its underlying source was inaccessible and it is not independent proof.

**Identity reasoning:** Death year and age support the younger Sarah candidate; the 1821 Kent burial belongs to another generation. No name-based merging is warranted.

**Sources:** [SRC001](#source-src001), [SRC091](#source-src091)

**Status:** Awaiting an inaccessible original; **confidence:** Conflict; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Retrieve Vinalhaven death entry (North Haven was not separately incorporated in 1844) and the Seaview stone; retain both day readings until seen.

### BF-R049

**Two Amelia profiles requiring identity review**

Profiles: `amelia_beverage_1833`, `amelia_beverage_1833_child`, `benjamin_beverage_1822`

**Existing claims:** Two repository IDs appear to describe the same wife of Benjamin Crabtree and daughter of Norwood and Hannah; birth dates differ January 31 versus January 1, 1833.

**Competing explanations:** Duplicate suspected from shared relations, not merged. January 1 is already treated as year-only by the repository precision system.

**Proposed conclusion:** The duplicate hypothesis is strong, but both IDs remain available pending an original record linking Amelia’s parentage and marriage. January 1 is a year placeholder and is not a second exact birth claim.

**Evidence reasoning:** Both profiles share two parents, the same spouse, all nine children, six siblings, and 1833–1908 dates; this is much more than a name match. However both cite a generic Find A Grave memorial, so they are not independent evidence. Seaview names Amelia as Benjamin C.’s wife but also contains a birth-column defect; no exact date is adopted from it.

**Identity reasoning:** The full shared family cluster strongly suggests one intended person. Retaining both IDs prevents an unreviewed identity consolidation; related-profile links make the suspected duplicate explicit.

**Sources:** [SRC001](#source-src001), [SRC091](#source-src091), [CRS005](#source-crs005)

**Status:** Narrowed but unresolved; **confidence:** Probable; **family review:** Not reviewed by family.

No effective field or relationship change.

**Next record:** Obtain Amelia’s 1908 death certificate or marriage record naming parents Norwood and Hannah Grant. If confirmed, consolidate with a canonical ID and compatibility alias in a later reviewed change.

## Source register for this review

Exact access form matters: a published transcription is not an original manuscript, a web transcription is not a newspaper scan, and a catalog or tree entry is not a vital record. Access dates below are in UTC.

### Source CRS001

**Vital records of Edgartown, Massachusetts, to the year 1850 (Boston: NEHGS, 1906)** — NEHGS; Internet Archive, Library of Congress scan. p. 29, Diana Daggett; p. 5, C.R.1 abbreviation; PDF pages 35 and 11.

[Reopen source](https://archive.org/details/vitalrecordsofed00edgar/page/29/mode/1up) · examined 2026-10-15.

**Viewed:** Downloaded published scan; both pages visually examined.

**Quality:** Authoritative published transcription of church records; not original manuscript. **Dependence:** New transcription witness; may share church source with SRC121; independence not assumed.

**Supports:** Diana, daughter of Benjamin Jr. and Elizabeth, baptized December 31, 1780; C.R.1 means Church of Christ, Congregational.

**Rights:** Link and citation only; no scan republished. Reuse permission not assessed.

### Source CRS002

**Vital records of Marblehead, Massachusetts, to the end of the year 1849, vol. II (Salem: Essex Institute, 1904)** — Essex Institute; Internet Archive, Cornell scan. p. 34, BEVERIDGE marriages; PDF p. 38; abbreviations p. 3.

[Reopen source](https://archive.org/details/cu31924092204308/page/n37/mode/1up) · examined 2026-10-15.

**Viewed:** Downloaded published scan; p. 34 visually examined; title and abbreviations read.

**Quality:** Authoritative published transcription; original town/church manuscript not examined. **Dependence:** May share town records with SRC119; not independent proof of every family connection.

**Supports:** James Beveridge married Mary White February 24, 1729/30 (C.R.3, St. Michael’s); James and Sarah Holman February 7, 1733/34. Neither is a birth entry.

**Rights:** Link and citation only; no scan republished. Reuse permission not assessed.

### Source CRS003

**Alumni catalogue 1836–1947 (New York: Union Theological Seminary, 1948)** — Union Theological Seminary; Columbia University Libraries. p. xli, Sacred Music, Lowell Pierson Beveridge entry.

[Reopen source](https://www.columbia.edu/cu/lweb/digital/collections/cul/texts/ldpd_5949068_000/pages/ldpd_5949068_000_00000045.html) · examined 2026-10-15.

**Viewed:** Institutional page OCR read directly; scan-image link opened but not independently inspected at readable resolution; direct scan-image download returned HTTP 403 on 2026-10-15.

**Quality:** Contemporary institutional register. **Dependence:** Predates 1991 obituary/memorial; independent institutional publication, informant unspecified.

**Supports:** Names Dorchester, Massachusetts as birthplace, September 19, 1905; Harvard degrees and Columbia/Union music appointments identify the same Lowell.

**Rights:** Link and citation only; no scan republished. Reuse permission not assessed.

### Source CRS004

**Name Recipients of 31 Fellowships and Scholarships, May 21, 1934** — The Harvard Crimson. Phi Delta Kappa Scholarship, final recipient paragraph.

[Reopen source](https://www.thecrimson.com/article/1934/5/21/name-recipients-of-31-fellowships-and/) · examined 2026-10-15.

**Viewed:** Publisher’s article text read directly; original newspaper image not examined.

**Quality:** Contemporary newspaper, publisher transcription. **Dependence:** Independent of modern NHHS interpretation; identity still requires corroboration.

**Supports:** Eliot P. Beveridge, of [Dorchester; online text reads Derchester], A.B. Harvard 1930, A.M. 1931, Graduate School of Education. Residence is not birthplace.

**Rights:** Link and citation only; no scan republished. Reuse permission not assessed.

### Source CRS005

**Theodore E. Beverage (MF45-BHM), family timeline and source list** — FamilySearch collaborative Family Tree. Parents and siblings; Sources (4); linked tree IDs L3F4-5MG, LC2F-GSH, LHFY-NWK.

[Reopen source](https://ancestors.familysearch.org/en/MF45-BHM/theodore-e.-beverage-1855-1874) · examined 2026-10-15.

**Viewed:** Public tree page read; linked original record images unavailable.

**Quality:** User-created tree: lead only. **Dependence:** Page explicitly attributes a story to Barbara Beverage Reeves/Find A Grave; may share family-tree origins with baseline.

**Supports:** Retrieval leads for Benjamin, Amelia, Charles Hanson (not Howard), 1860 census household and Faylene Hutton cemetery collection; proves no disputed vital date.

**Rights:** Link and citation only; no scan republished. Reuse permission not assessed.

### Source SRC001

**Beverage Family research baseline** — GitHub csully1234/Beverage-Family. Commit 4e3d4860d3c8d9ae9cbcb19567dafa17e1a93db1; 16 research-relevant files.

[Reopen source](https://github.com/csully1234/Beverage-Family/tree/4e3d4860d3c8d9ae9cbcb19567dafa17e1a93db1) · examined 2026-10-15.

**Viewed:** Protected baseline files and original collection read at main 7ce454f; historical snapshot remains indexed by its original commit..

**Quality:** Family-authored repository. **Dependence:** Family-authored starting hypotheses, not independent proof..

**Supports:** Starting hypotheses and existing records; never independent historical proof

**Rights:** Not determined; citation does not grant republication rights

### Source SRC089

**Cemetery Records** — North Haven Historical Society. Cemetery directory and access guidance.

[Reopen source](https://www.northhavenmainehistoricalsociety.org/cemetery-records.html) · examined 2026-10-15.

**Viewed:** Guide and public contact page reopened; not stone images..

**Quality:** Cemetery collection guide. **Dependence:** Institutional access guidance, not evidence of individual dates..

**Supports:** Thirteen cemetery transcriptions; 2013 cemetery map; access guidance

**Rights:** NHHS requests permission before publication of copies or scans and institutional credit; high-resolution availability not confirmed.

### Source SRC090

**Fuller Cemetery** — North Haven Historical Society. PDF pp. 1–5.

[Reopen source](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/fuller_cemetery.pdf) · examined 2026-10-15.

**Viewed:** Saved transcription text reexamined, p. 5 Benjamin Kent entry; original stone not viewed in this review..

**Quality:** Cemetery transcription. **Dependence:** Transcription only; Woodruff narrative may use the same cemetery information..

**Supports:** Beverage inscriptions, spouses, military inscriptions and Kent dates

**Rights:** NHHS requests permission before publication of copies or scans and institutional credit; high-resolution availability not confirmed.

### Source SRC091

**Seaview Cemetery** — North Haven Historical Society. PDF pp. 2–4.

[Reopen source](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/seaview_cemetery.pdf) · examined 2026-10-15.

**Viewed:** Saved PDF/text reexamined, pp. 2–4; original stones not viewed in this review..

**Quality:** Cemetery transcription. **Dependence:** Single transcription with apparent column errors; repeated tree citations are not independent..

**Supports:** Beverage inscriptions, dates, relationships and transcription conflicts

**Rights:** NHHS requests permission before publication of copies or scans and institutional credit; high-resolution availability not confirmed.

### Source SRC092

**Kent Cemetery** — North Haven Historical Society. PDF p. 1.

[Reopen source](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/kent_cemetery.pdf) · examined 2026-10-15.

**Viewed:** Saved transcription text reexamined, p. 1; original stone not viewed in this review..

**Quality:** Cemetery transcription. **Dependence:** Duplicate lines in one transcription are not two independent witnesses..

**Supports:** Sarah Beverage Kent; Joseph W. Kent

**Rights:** NHHS requests permission before publication of copies or scans and institutional credit; high-resolution availability not confirmed.

### Source SRC116

**IsleBuilt Boats** — North Haven Historical Society. Eliot Beveridge biography, models and employees.

[Reopen source](https://www.northhavenmainehistoricalsociety.org/islebuilt-boats.html) · examined 2026-10-15.

**Viewed:** Institutional webpage reopened and full text read..

**Quality:** Historical society interpretation. **Dependence:** Modern interpretation; separate from the 1934 Crimson report but primary birth evidence is missing..

**Supports:** Boat business founded 1955, production circa 1955–1957, wife Dorothy, permanent return 1954

**Rights:** NHHS requests permission before publication of copies or scans and institutional credit; high-resolution availability not confirmed.

### Source SRC119

**The Essex Antiquarian volume IX 1905** — Sidney Perley, editor; Salem Massachusetts; Internet Archive. p. 91, Notes; PDF p. 105.

[Reopen source](https://archive.org/details/essexantiquarian09perluoft) · examined 2026-10-15.

**Viewed:** Saved published text reexamined, p. 91; original deeds not examined..

**Quality:** Published genealogical notes. **Dependence:** May share Marblehead town sources with CRS002; only the original 1789 deed can verify the abstract..

**Supports:** James Beveredge and Sarah Holman marriage; three daughters in 1789

**Rights:** Historical edition; digital reproduction terms not assessed

### Source SRC121

**A History of the Doggett Daggett Family 1894** — Samuel Bradlee Doggett; Boston Press of Rockwell and Churchill; Internet Archive. p. 113, entries 809 and 1033; PDF p. 145.

[Reopen source](https://archive.org/details/historyofdoggett00indogg) · examined 2026-10-15.

**Viewed:** Saved published text reexamined, p. 113 entries 809 and 1033; original church register not examined..

**Quality:** Published genealogy. **Dependence:** May derive from the same church record as CRS001; not independent corroboration of exact birth..

**Supports:** Diana baptism, marriage, reported parents and children

**Rights:** Historical edition; reproduction terms not assessed

### Source SRC123

**Josiah Beverage biographical subject** — Wilford Woodruff Papers Project. Biography and footnotes to vital records, deeds and death notice.

[Reopen source](https://wilfordwoodruffpapers.org/subjects/josiah-beverage) · examined 2026-10-15.

**Viewed:** Institutional biographical text and footnotes reopened and read; FamilySearch deed image inaccessible..

**Quality:** Edited biographical index. **Dependence:** Edited research guide, not examination of the cited deed..

**Supports:** Original-record retrieval pointers; contextual identity of Josiah

**Rights:** Not determined; citation does not grant republication rights

### Source SRC125

**Benjamin Kent biographical subject** — Wilford Woodruff Papers Project. Biography and record citations.

[Reopen source](https://wilfordwoodruffpapers.org/subjects/benjamin-kent) · examined 2026-10-15.

**Viewed:** Institutional biographical text and footnotes reopened and read; cited vital image inaccessible..

**Quality:** Edited biographical index. **Dependence:** Internal narrative/footnote disagreement; narrative and cemetery account may share a source..

**Supports:** Benjamin and Sarah parents; marriage to Deborah Thomas; conflicting January/June birth date

**Rights:** Not determined; citation does not grant republication rights

### Source SRC129

**1991 Journal of the Diocese of Virginia Lowell Beveridge memorial** — Episcopal Diocese of Virginia. p. 73; PDF p. 38.

[Reopen source](https://episcopalvirginia.org/wp-content/uploads/2024/04/1991-Diocese_Journal_searchable.pdf) · examined 2026-10-15.

**Viewed:** Saved institutional memorial text reexamined, printed p. 73; original birth record not examined..

**Quality:** Institutional memorial notice. **Dependence:** May derive from the same obituary as repeated accounts. Not treated as independent birthplace proof..

**Supports:** Life dates, career, brother Lyford and Universal Harmony manuscript; contains age inconsistency

**Rights:** Rights not assessed; text may share obituary origin
