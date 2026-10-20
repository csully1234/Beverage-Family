# Phase 42 — From historical research leads to original document recovery

**Date researched:** 20 October 2026.  
**Baseline:** Phase 41 merged, tested and confirmed live on Render at `c9d0441646d38eedc76e8e5dd65b6a311b470297`; no open PRs at start.  
**Goal:** Replace repeated speculative internet pedigree searches with a precise, usable, original-source acquisition and review workflow available directly on the family website.

## Evidence: why this is achievable

1. [Maine State Archives genealogy guidance](https://www.maine.gov/sos/archives/archives-services/genealogy-research) says most pre-1892 vital records were kept at the *town level*, only a minority of historical town copies were submitted to the State, and staff generally cannot do individual searches of incomplete unindexed early records.
2. [Maine Title 22 §2706](https://legis.maine.gov/statutes/22/title22sec2706.html) expressly provides that certificates and records before 1892 are open to the public and that noncertified copies are obtainable. This is an access path, **not** evidence that any one handwritten entry survives or proves ancestry.
3. The [North Haven Municipal Clerk](https://www.maine.gov/sos/elections-voting/find-a-municipal-clerk-or-registrar?title=North+Haven), [Vinalhaven Town Clerk](https://www.townofvinalhaven.org/1256/Administration---Town-Office) and [North Haven Historical Society](https://www.northhavenmainehistoricalsociety.org/visit.html) offer realistic custodian contacts. **No contact has confirmed possession of the requested original or quoted a fee.** The Historical Society's own archive description covers the early North Fox Island years.
4. [Vinalhaven Historical Society](https://www.vinalhavenhistoricalsociety.org/summerexhibit/2013exhibitearlydays.html) reports that its museum houses a **copy of the 1785 Fox Islands settler petition**. This is a concrete original-document visit opportunity, but the copy's accuracy and the Massachusetts original must still be compared.
5. Vinalhaven and North Haven were one town before the North Island's 1847 separation. A modern "North Haven 1803 birth" may occur in a Vinalhaven town register, not a book originally headed North Haven.
6. The scholarly [Wilford Woodruff Papers' early Fox Islands source footnotes](https://wilfordwoodruffpapers.org/subjects/josiah-beverage) specifically cite Vinalhaven Town Clerk digital image set **DGS 7596929**, with an exact source location for Josiah Winslow Beverage (1793), and [other contextual Vinalhaven register entries](https://wilfordwoodruffpapers.org/subjects/benjamin-kent) around original 1800–1821 marriages. **Those neighbor pages do not prove the 1800 John/Rachel marriage or 1803 Nathaniel / 1821 Josiah births**; the actual handwritten pages for the latter are not yet located.
7. The state's [Maine Vital Records 1670–1921 collection](https://www.familysearch.org/en/search/collection/1803978) is a plausible source for Josiah's 1918 death certificate. The death informant's knowledge matters: a reported parent on a 1918 certificate is not automatically first-hand 1821 evidence.

## The nine top-priority original records

| Priority | Original record | Potential historical resolution | Current source state |
| --- | --- | --- | --- |
| 1 | John White Beverage–Rachel circa 2 February 1800 marriage | Actual recorded bride surname; evaluate Crosby vs Luce Tarr claim | Manuscript entry not located |
| 2 | Nathaniel Beverage circa 20 October 1803 birth | Parents for separate Rockland family branch | Not located/read |
| 3 | Josiah B. "Si" Beverage 1821 birth | Decide competing parent pairs; April vs June date | Not located/read |
| 4 | Nathaniel–Sarah Alexander circa 26 April 1838 marriage | Bridge 1803 birth man to Rockland marriage identity | Not located/read |
| 5 | John White Beverage circa 1839 probate | Check for expressly named son(s) Nathaniel/Josiah | Estate file and court jurisdiction not identified |
| 6 | Josiah B. 16 November 1918 death certificate | Independent informant's parental report, spouse and birth clues | Certificate not read |
| 7 | Thomas Beverage–James & others 1837 deed | Check death-before-execution chronology | Exact image locator DGS 8296915 image 207/601; image uninspected |
| 8 | Original 1785 Fox Islands petition | Check named James, Thomas and minor Matthew and any kin words | Society reports onsite copy; original packet uninspected |
| 9 | Original 1820 Hope census Mathew head | Household age totals without naming unnamed household members | NARA M33-36 located; handwritten sheet uninspected |

The first three have the highest immediate genealogical impact. Both disputed Josiah parent pairs remain open, including current site parents and external user-contributed alternatives. Nathaniel of Rockland remains in a separate recorded branch.

## What the new website does

### Original record recovery desk

`data/phase42_primary_document_acquisition.json` models nine original document targets and seven independently grounded institutional locations. Each carries person IDs, historical place/administrative context, known and unknown source volume/image references, a precise reading request, access notes, next evidence requirements, and a status that cannot claim original inspection.

The existing **Historical Discoveries → Family Origins Expedition** now includes the **Original record recovery desk** prominently for visitors arriving via original-record deep links. Filters and bookmarked individual source targets use routes like:

`?page=collection&view=source-expedition&acquire=1&source_target=josiah-1821`

Any person affected by an open retrieval target gets a direct link from the **person's historical evidence exhibit**. All nine are in the searchable Research Workbench as *uninspected retrieval leads*, not proof citations.

### Copyable, unsent historical record inquiry

Select an institution and one or more records it may reasonably hold. The site generates a complete, respectful record-location/copy request asking for original folio context, fees, and image reuse terms. **The site does not send an email, pay, book, or submit anything**; the family researcher can inspect, edit, copy or download the draft before choosing whether to contact the archive.

### Original evidence inspection and handoff

A family researcher may upload a JPEG, PNG or PDF **to a temporary in-browser session preview** and manually enter literal handwriting transcription, reported archival custodian, actual scanned folio/image, original date and *separate* notes. No OCR confidence or face/name matching is invented. The resulting downloadable JSON evidence packet is explicitly **unreviewed** and contains no uploaded image bytes or automatic genealogical parent-child edits. To make a newly acquired scan available to all family members on the website, it still needs a reviewed source/licensing check and code/repository integration; **uploads do not persist between sessions**.

## What was NOT obtained or modified

No original 1800/1803/1821 handwritten record was fully read during Phase 42. FamilySearch access to the precise image is incomplete from the research environment, and original custodians have not confirmed the entries exist. No named-parent connection, living relative data, historical addresses, existing password, original book reproduction, or other recorded relationship was changed.

The site must not confuse a family tree on Ancestry or Genealogy of New England with original contemporaneous testimony. One compilation reporting two parents is one source family. Original documents obtained in future should receive original image review, date/spelling transcription, source context, consistency comparison, and separate approval before any tree changes.

## Follow-up actions for an actual original-record breakthrough

1. Use the prepared, unsent **Vinalhaven Town Clerk** inquiry for the 1800 marriage and 1803/1821 births; verify whether pre-1847 North Island originals are there or North Haven.
2. Ask **North Haven Historical Society** if they can locate early North Island family registers or original-record indexes, particularly Nathaniel's 1838 marriage and later probate clues.
3. Use a free FamilySearch account or an affiliate-access location to inspect DGS 7596929, recording exact actual folio and image number for every specific original. Do not infer nearby page numbers from unrelated subjects.
4. Request the 1918 state death return for Josiah from the Maine vital collection and assess whether the informant personally knew the parents.
5. After a legible original is obtained, enter the literal transcription in the site's research workbench, export the packet, and submit the actual facsimile with permission information for a separate evidenced family-tree improvement PR.

**Release gate:** Python 3.12/3.13 complete tests, existing JS map/tree interactions, data and link safety, full verified backup, manual Render deployment with exact merged commit confirmed `live`, immediate error logs. Browser acceptance should test the scanner upload preview and export in a logged-in Streamlit session on desktop/mobile.
