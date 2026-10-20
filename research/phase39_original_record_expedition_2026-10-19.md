# Phase 39 — Family Origins Expedition: first-hand register targets and the missing family-branch bridges

**Date researched:** October 19, 2026 US Eastern.  
**Baseline:** Phase 38 merged, tested in Python 3.12/3.13, and confirmed live in Render at commit `5fd8af10af03569c5b840fce02e293fa780ac043`. No open pull requests before this phase.  
**Release principle:** **A source locator is not an inspected document, and a published family-tree pedigree is not a new kinship proof.** Never link people simply because of a compatible name or year.

## Biggest new historical opportunity: original image locators in an edited nineteenth-century diary project

The [Wilford Woodruff Papers' scholarly subject profile of Josiah Beverage](https://wilfordwoodruffpapers.org/subjects/josiah-beverage) supplies precise manuscript/image references. Its citations are significantly more actionable than the generic online ancestry records that have dominated older searches:

| What to verify | Exact cited original location | Current research status |
| --- | --- | --- |
| Josiah Beverage birth, reported July 10, 1793, Vinalhaven | Vinalhaven Town Clerk, vital/town register printed/manuscript p. **380**, FamilySearch **DGS 7596929 image 209 of 837** | Scholarly editorial image locator identified, ORIGINAL IMAGE NOT INSPECTED |
| Thomas Beverage / Mercy Kent marriage, reported Apr. 13, 1774, Trinity Church Boston | FamilySearch church register **DGS 8130800 image 459 of 798** | Editorial image locator identified, ORIGINAL IMAGE NOT INSPECTED |
| Wilford Woodruff with Josiah Beverage on North Fox Island, April 3, 1838 | Wilford Woodruff Papers subject index and the [1838–1839 journal transcription](https://www.documents.wilfordwoodruffpapers.org/documents/22e14db2-30f8-4a6d-af51-132c66e05d8b/transcript), section April 3 | Scholarly subject profile identifies the historical encounter; the publicly extracted diary day **omits the personal name in tag slots**. Check manuscript/entity tags before claiming an independently observed diary mention |
| Thomas Beverage-to-James Beverage & others deed, dated June 28, 1837 | Hancock County Maine deed book p. **387**, FamilySearch **DGS 8296915 image 207 of 601** | Editorial image locator identified, ORIGINAL IMAGE NOT INSPECTED. **Chronology conflict:** the site's Capt. Thomas (b. 1750) is recorded dead **Oct. 4, 1834**; cannot automatically assign him as executing grantor in 1837 |
| Josiah Beverage death notice, published January 8, 1858 | Lewiston Falls Journal notice index, FamilySearch **DGS 8203644 image 392 of 814** | Editorial image locator identified, ORIGINAL IMAGE NOT INSPECTED; might contextualize the site's reported 1857 death |

**Source accounting:** The Woodruff editorial profile is a **single scholarly source for these original-image citations**. Its footnotes refer to *different prospective original record families*. Until we read those images, we have NOT gained five independent original proofs by collecting one editorial page.

**Caution about the 1837 Thomas deed:** An original-era deed may have a named seller, a representative or estate, a later recording date, or an identification error. The source must be read before assigning it to the captain or any particular Thomas/James pairing. This is precisely the kind of chronological contradiction the site should help reveal rather than silently "fix."

## The most promising path to reconnect a disconnected family branch

The 1865 *History of Thomaston, Rockland and South Thomaston* by Cyrus Eaton (vol. II, pp. 146–147) reports that **Nathaniel Beverage**, husband of **Sarah Alexander**, was a *nephew* of Capt. Matthew, while Sarah was his *niece*. This was already recognized as a historical published-kinship claim in the project's Phase 16 source review; it does not identify Nathaniel's parents.

A [compiled New England genealogical entry](https://genealogyofnewengland.com/f_86c9.htm) supplies a much more specific, unproved parentage proposal: **Nathaniel Beverage b. October 20, 1803, North Haven**, with parents **John White Beverage and Rachel Lucy Crosby**, married to Sarah Alexander April 26, 1838, and died 1886 Rockland. John White and Rachel already exist in the principal tree as a married pair. Nathaniel of Rockland already has his own separate family group in the tree.

**This is potentially important, not yet safe to connect:** The proposed parents come from a derivative, contributed genealogy, not a read original town birth return. Parentage can also be copied between online trees. The existing tree does NOT presently name Nathaniel as John White's son. His relationship to Capt. Matthew, and whether "nephew" referred to blood or marriage kinship, remain unresolved.

**Highest-information next document:** Read an original 1803 Vinalhaven/North Haven birth/baptism register **with Nathaniel's parents**, or obtain an original 1838 marriage return and supporting family/probate evidence. The [North Haven vital record catalog](https://ldsgenealogy.com/ME/North-Haven.htm) and [Maine State Archives guidance](https://www1.maine.gov/sos/archives/archives-services/genealogy-research) identify custody and possible original-access paths. The original image has not yet been retrieved in the research environment. Do not create John White → Nathaniel or Rachel → Nathaniel tree edges.

## Other original-evidence gaps deliberately still open

**Matthew of Hope:** The original 1820 census microfilm reel is linked by [Internet Archive identifier populationsc18200036unit](https://archive.org/details/populationsc18200036unit), NARA M33 roll 36. A separate later transcription reports "Mathew Beveridge" on Hope manuscript sheet 276, but the handwritten row and household tally remain uninspected. The user-supplied 1837 Waldo probate original-era scans have been reviewed and the court names widow Clarissa and eight children, but those papers do not supply Matthew's birth parents, Clarissa's maternity for every heir, or an identity bridge to the 1785 petition minor. Court scans remain withheld from the public website pending reproduction clearance.

**1785 Fox Islands Matthew (minor):** An [1889 Vinalhaven history](https://tile.loc.gov/storage-services/public/gdcmassbookdig/briefhistoricals00vinl/briefhistoricals00vinl.pdf) reproduces the settlers' petition with James, Thomas and a minor Matthew separately named. That does NOT prove siblings, parents, ages or the later Hope identity. Compare the Massachusetts Archives original petition and 1786 Rufus Putnam Maine Archives manuscript; neither has been fully inspected.

**Separate people sharing names:** The main tree's Nathaniel Winslow Beverage (b. 1776) is not Nathaniel of Rockland (b. ~1804). A Thomas mentioned in an 1837 deed must not automatically be a Thomas recorded dead in 1834. The number of distinct records indexed by a modern editor is not the number of independently inspected original witnesses.

## Major website changes

New `data/phase39_primary_record_expedition.json` contains **four prioritized research case files and eleven evidence-graded source access cards**, each with repository, period, exact reel/DGS/folio/scan location where known, original-inspection flag, what it does and does not establish, copyright/access limitation, and numbered document-check tasks. No raw unpublished scan images are added.

New `primary_source_expedition.py` renders **Historical Discoveries → Family Origins Expedition**, providing:

- Four clear family mysteries: Nathaniel's Rockland parentage bridge, the Thomas/Mercy/Josiah original record chain, Matthew's Hope records/probate identity, and the 1785 Fox Islands minor hypothesis.
- An original-record-by-original-record view with the exact digital manuscript locator, independent review flag and publication/rights caution.
- Links to existing people and historical source pages. A runtime audit indicates when a case names members of **different currently separate graph components**, *without claiming the case connects them*.
- A complete download of cases, archival targets and source limitations as a no-private-image CSV.
- Site-wide discovery, home and disconnected-branch navigation; new Research Workbench entries for all cases/sources. The 1837 Thomas deed is **not** attributed to Capt. Thomas as an exact-person source; the 1820 Hope head transcription does **not** automatically become a verified Matthew (1837) person source.

New `tests/test_phase39_primary_source_expedition.py` exercises exact image locators, original-versus-editorial flags, blocked automatic Nathaniel parentage, preservation of four connected components and 202 people, posthumous 1837 deed conflict, entire-case export and accurate research indexing.

**Unchanged:** Password/access method, full family tree data, historical persons, parent/spouse/child edges, addresses, Boston Tea Party claim, 305-page authorized book, historic scans, and any email/request sending.

## Concrete follow-through after this phase

1. Get the image for **Nathaniel's 1803 birth**, ideally with both parents, and compare with original 1838 marriage return to Sarah Alexander. This is the single best near-term target for a *real* cross-branch proof.
2. Read Vinalhaven DGS **7596929** image **209/837** for Josiah's original 1793 birth; read Boston Trinity Church DGS **8130800** image **459/798** for Thomas/Mercy's marriage.
3. Read 1837 Hancock deed DGS **8296915** image **207/601**, explicitly resolve the Thomas-after-death identification problem rather than adding a citation to a deceased person.
4. Open 1820 census Hope manuscript sheet 276 in M33-36; transcribe tally columns faithfully, without naming unnamed household members.
5. Follow original Fox Islands 1785 petition and 1786 Putnam material to identify Matthew's parents or conclude it stays unresolved.

**Release:** Merge only if Python 3.12/3.13 complete automated tests, data validation, original-source link safety and JS maps/tree interaction checks pass. After merge confirm the 90-day verified backup/restore workflow and manually deploy to Render, exact SHA live and error-level logs. Authenticated manual browsing remains a final human UX check.
