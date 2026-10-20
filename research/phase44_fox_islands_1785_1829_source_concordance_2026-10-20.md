# Phase 44 — Fox Islands civic, census and customs documentary trail, 1785–1829

**Research date:** October 20, 2026.  
**Current site base:** Phase 43 merged and live at `fa20a978a748bdace30a32770191a28229b99667`.

## What additional published historic records establish

### 1. Plantation clerk at the North Island's earliest recorded public meeting

The **1889 Vinalhaven Centennial Committee** *A Brief Historical Sketch of the Town of Vinalhaven* gives positive dates beyond its officer summary on pages 35–39. Its narrative [printed pp. 11–12](https://tile.loc.gov/storage-services/public/gdcmassbookdig/briefhistoricals00vinl/briefhistoricals00vinl.pdf) describes:

- **March 11, 1785:** earliest plantation meeting known to the author, held at **Benjamin Kent's house on North Island**, where **Thomas Beverage** was chosen clerk. Evidence is the **retrospective published meeting account**, not the original minutes or a signature read in this work.
- **October 28, 1788:** Thomas Beverage elected plantation clerk, with Joseph Waterman, William Vinal and George White named as assessors.
- **March 1789:** Thomas Beverage chosen clerk again at the annual meeting. Specific election day in March not stated in the extracted account.

The 1939 *Descendants of Robert Waterman* p.303 [repeats](https://www.cga.ct.gov/hco/books/Descendants_of_Robert_Waterman_1939.pdf) this same narrative. This repetition MUST NOT be counted as another independent contemporary town-minute witness. It is unlikely to establish parentage of Capt. Thomas or resolve the 1837 Thomas-after-1834 deed without additional proof.

The date 1785 is especially interesting because this meeting was **before** the March 1786 Massachusetts legislative land grant; do not conflate planting, petitions, plantation officer election and town incorporation into one date.

### 2. The 1820 Vinalhaven census named four Beverage household heads

An independent **2019 modern alphabetical name transcription** of [Vinalhaven's 1820 U.S. Census](https://www.heirloomsreunited.com/2019/09/vinalhaven-maine-in-1820-census-then-in.html) lists **John Beverage, Nathaniel Beverage, Thomas Beverage and Benjamin Beverage** as household heads. It describes the census as handwritten **sheets 657–664**. Those FOUR names are new source pointers, **not an original row-by-row manuscript transcription performed here**. The source has no ages for named or unnamed household members and gives no stable household sheet/row locator for each Beverage. A head named Nathaniel in 1820 does not establish the parents of Rockland Nathaniel and does not identify which Nathaniel headed that household.

### 3. John Beverage appears in a federal Customs officers listing

An OCR/text-extracted scan of the **U.S. Official Register**, Treasury Department **Customs / Penobscot**, includes the text **John Beverage** with the duty **Inspector** (the printed line uses a ditto mark after an earlier inspector) and duty location **Vinalhaven**. Two scans are available at:

- [Library of Congress archived copy](https://tile.loc.gov/storage-services/public/gdcmassbookdig/officialregister37unit/officialregister37unit.pdf)
- [Wikimedia Commons copy from Internet Archive](https://commons.wikimedia.org/wiki/File:Official_register_of_the_United_States_.._(IA_officialregister22unit).pdf)

An independent portal for United States official registers indexes both Internet Archive identifiers `officialregister37unit` and `officialregister22unit` as **September 30, 1827**; however, the full searchable scan text carries commissioner/collector footnotes referring to **March 1829**. Therefore **the edition and entry date are NOT resolved**. It would be misleading to assert "John White Beverage was appointed customs inspector in 1827." The title leaf, exact column and true register year need original-page visual review. The two copies derive from a **single printed source family**.

This provides another original-era publication **type** beyond local histories and census, and may be helpful to identify a John living/working at Vinalhaven in the late 1820s. It is **not** direct documentary proof that the town clerk John of 1799–1812, the 1820 head John, and the federal Inspector John are the same person. It says nothing about Rachel's birth surname, Nathaniel's parents or Josiah's disputed parentage.

## Integrations completed

`data/phase44_fox_islands_government_census_crosswalk.json` records eight source observations and **three** editorial/publication source families with explicit access and identity uncertainty. `fox_islands_government_trail.py` adds an attractive chronological research exhibit accessible from the **Family Origins Expedition**. Each item provides exact printed date or caveat, named person as in the source, place, work/office, positive finding, exact original-record verification target and source URL, plus optional compatible family profiles as **comparison, not proof**.

Visitors can deep-link any historical observation via `?page=collection&view=source-expedition&community=1&community_record=...` and download all eight in a CSV. A homepage shortcut and person historical-exhibit research comparisons make it discoverable. All eight appear in the searchable Research Workbench **without person IDs**, and nothing is auto-added to the canonical individual family timeline.

### What the three sources are *not*

1. Three episodes of Thomas Beverage in one 1889 narrative are not three independent first-hand witnesses. The 1889 Vinalhaven annual roster and narrative are the same publication family; the 1939 derivative family history repeats some details.
2. A modern indexed 1820 census name is a research trail to the original age-count manuscript, not a warrant to name unnamed family members or assign a birth year.
3. A federal Official Register OCR string from an edition with internally conflicting metadata is **not** confirmation of a precisely dated U.S. appointment or the identity of John White Beverage.
4. A familiar surname in a different state (e.g., John Beverage in West Virginia) cannot be linked to this Maine family without substantial independent proof. These records are explicitly scoped to **Vinalhaven / North Fox Island, Maine**.

## Highest-priority next original records

- Find North Haven/Vinalhaven **original 1785, October 28 1788 and March 1789 plantation minute pages**, including clerk's signature and the municipality's legal status.
- Check **the original 1820 Vinalhaven manuscript sheets 657–664** for rows named John, Nathaniel, Benjamin, Thomas. Capture original spelling, column headers and tallies; never assert invented occupant identities.
- Inspect **the actual title page and Customs table** of each candidate 1827/1829 federal register edition, and locate Customs Penobscot appointment / customs-collectors correspondence. Identify John by an address, middle name, legal signature or matching original deed before adding an occupation to a canonical profile.
- Continue retrieving the **original 1800 John–Rachel marriage**, **1803 Nathaniel birth**, **1821 Josiah birth**, and **1839 John White estate** from Phase 42. These, not the name-only civic register, are most likely to prove parentage.

## Release gate

Python 3.12 and 3.13 full regression suites, genealogy integrity, map/tree JS tests, complete archive backup/restore, manual Render deployment and live-commit check. No new genealogical edges, family password, rights, family addresses, Boston Tea Party claim, book or historic person IDs have been modified. No archive emails sent.

**Image-access limitation:** The LOC 1889 and federal-register PDF files are too large for the research browser's PDF page viewer. The historical wording was accessible via indexed PDF text/OCR; **actual page images and handwritten originals have not been independently visually inspected**. Do not assert otherwise.
