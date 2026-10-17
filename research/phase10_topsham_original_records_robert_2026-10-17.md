# Phase 10 — Topsham: Samuel (1752), James (1758), Robert (1776–1777)

**Research notes prepared 17 October 2026. Primary original identity links remain unproven.**

## New finding — Robert Beveridge named in 1776 and 1777 company rosters

Wheeler's *History of Brunswick, Topsham, and Harpswell* (1878), Appendix III, printed **pp. 882–883**, lists **Robert Beveridge** among Topsham men in two military rosters:

1. Under **Captain William Lithgow's company (1776)**, a Robert Beveridge entry occurs among recorded service men, with a rank string that OCR suggests private/promoted corporal/sergeant. **Do not publish exact rank dates without examining the original printed page and underlying roll**.
2. Under **Captain George White's company (1777)**, a Robert Beveridge entry appears as **ensign**. It is unproved that the two entries identify the *same* soldier or whether this Robert is related to any James or Samuel.

**Printed source:** https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-83.htm

This is a **new research subject**, not a verified relative. The existing tree's Robert Beverage records born in 1807, 1835, 1872 and 1968 are plainly too late to represent this 1776 roster entry. Creating a dated 1700s Robert profile from these listings would invent missing parentage, birth and death information. A source-only case is the correct status.

**Next originals:**
- Massachusetts Archives / historical *Massachusetts Soldiers and Sailors of the Revolutionary War* and any surviving 1776 Lithgow pay/muster roll with full name, hometown, regiment, rank and age.
- Contemporary 1777 Capt. George White company original return, commission or pay records, ideally with explicit cross-company service information.
- Earliest original Topsham residence, church, tax, probate and deed records identifying a Robert Beveridge. Compare with relatives **only after** finding independent probate or birth family bridges.

## 1752 Samuel and 1758 James — what the lists establish

1. Wheeler 1878 book, printed p. 41, publishes a reproduction of a historic local map key: map reference **3** is labeled **Samuel Beveridge** in Topsham. This is a *map marker*, not a legally proven modern property boundary. Source: https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-5.htm
2. Wheeler, Appendix I, printed pp. 870–872, gives a list of early Topsham **settlers or landowners**. A later transcription based on this list records **Samuel Beveridge (1752, lot/locality 3)** and **James Beveridge (1758, lot/locality 7)**: https://genealogytrails.com/maine/sagadahoc/history_earlysettlerstopsham.html. This is not a scan of an 1752 or 1758 deed. The published history's map key number and the list's lot number should not be automatically equated to surveyed title without inspection of the original key, map, and deed chain.
3. The 1878 town history is a dated historical compilation, not an independent second Pejepscot-era land grant. It is contemporaneous enough to prioritize original records, but cannot prove family kinship or legal title by itself.

### Genuine primary archive locations (now directly reachable from site)

- Maine Historical Society, **Pejepscot Proprietors papers (Coll. 61)** — https://mainehistoricalsociety.libraryhost.com/repositories/2/resources/2 — contains original deeds, correspondence, accounts, meeting minutes, lists of settlers and manuscript maps, ca. 1627–1866.
- Digitized **Pejepscot Volume 1B (1741–1814)** — https://www.mainememory.net/record/112084 — original deed copies, minutes and correspondence, including 1750s title disputes.
- Digitized **Volume 4** — https://www.mainememory.net/record/112087 — deeds, lists of inhabitants, accounts and lots.
- Digitized **Volume 10** — https://www.mainememory.net/record/112092 — Topsham settlement and transfers, disputes and depositions.
- Cataloged **1760 Topsham manuscript map (Coll. 61, Map 33)** — https://mainehistoricalsociety.libraryhost.com/repositories/2/archival_objects/181 — contemporary geographic reference, but no particular Beveridge property has been verified on its image.
- Supporting 1758 legal background — the Maine Historical Society's records also cover Pejepscot/Kennebec proprietor disputes. This must be taken into account when interpreting 1758 lot and title descriptions.

**Document extraction protocol**: identify original volume/image number and folio; manually read whole entry; transcribe exact spelling, date, grantor, grantee, witnesses, boundaries, covenants and relationship words. Photograph or legally available archive URL is preferable to unlicensed rehosting. Trace subsequent conveyance/probate rather than inferring ancestry from proximity. If the source states occupancy but not ownership, record occupancy only.

## 1749 James and Jean remains a separate question

Two printed transcriptions of the **same** Brunswick town intention spell James's surname and Jean's surname differently. Even if the 1749 intent precedes James's 1758 Topsham listing, no original record currently identifies the James of 1749 with the James of 1758, or either with the 1724 Marblehead-born James. A wedding ceremony is still not proven.

## Visitor implementation in this PR

- Adds `data/phase10_early_maine_records.json` (six dated leads; **source records**, not people/events/places).
- Adds `early_maine_sources.py` — compact original-source exploration cards with date, names, evidence status, what the source means, what it does not prove, and exact next archival task.
- Integrates this section into **Stories & Discoveries → Before North Haven: Beveridge names in Topsham**.
- Adds regression coverage protecting the existing verified family tree, legacy research and provenance.

**No new ancestors, genealogical edges, land ownership pins, modern addresses, outbound messages, original-family historical claims or existing source records have been changed.** No original 1752/1758 title instrument or 1776/1777 muster roll was claimed examined.


## Major independent corroboration — Massachusetts archival service compilation

After the Wheeler 1878 roster discovery, a substantially stronger source was located: *Massachusetts Soldiers and Sailors of the Revolutionary War: A Compilation from the Archives*, issued by the Secretary of the Commonwealth (1896 onward), B-surname entries. The public scanned edition is at:

https://upload.wikimedia.org/wikipedia/commons/8/8e/Massachusetts_soldiers_and_sailors_of_the_revoluntionary_war._A_compilation_from_the_archives_%28IA_cu31924092739980%29.pdf

Unlike Wheeler's two separate 1776/1777 roster tables, the Massachusetts state-archive compilation **joins the 1776 Lithgow and 1777 George White assignments into a single published Robert Beveridge of Topsham service entry**. Details recorded:

- **11 March 1776** — enlisted private, Capt. William Lithgow's company, of **Topsham**. Reported service at Falmouth.
- **22 March 1776** — promoted corporal.
- **9 August 1776** — promoted sergeant.
- **3 December 1776** — date referenced as start of subsistence in Capt. George White's company, Col. Ebenezer Francis's regiment.
- **3 February 1777** — reported commissioned ensign.

**Evidence classification:** Strong independent *archival compilation* documenting a coherent military service career for Robert of Topsham, more trustworthy than independently guessing two same-name rosters describe one man. It is **still not an inspection of each contemporaneous original roll** and does **not** prove his father, age, spouse, or kinship with James and Samuel.

### Same-name military entries must remain separate

Nearby B-surname entries in the **same** Massachusetts compilation also report:

- **Robert Beveredge/Bevekedge** — fifer, Capt. James Lemont's sea-coast company, enlisted **22 July 1775**, service at Georgetown to December 1775. The spelling is inconsistent in the OCR source. Could this be the same future Topsham Robert? No unique identifier yet.
- **Robert Beverage** — seaman in the brigantine **Tyrannicide**, Capt. Jonathan Haraden, **13 March–31 August 1777**. Possible overlap with the Topsham ensign's term makes automatic conflation especially unwarranted.
- A separately worded **Robert Beverage**, second sergeant in Lithgow's company, with a later 1776 pay period; **could be another rendition of the named Topsham Robert**, but match requires pay-roll crosscheck. Its presence must not be counted as an independent second person without proof.

The public story displays these as source leads, but none is added as a genealogy node. No Revolutionary War pension, postwar residence, family heirloom or probate record has yet been identified to connect Robert with James or Samuel.

### Additional underlying material, not itself proof of Robert's presence

A 1901–1904 handwritten descendant's transcript of **Capt. George White's January 1778 company roster**, copied from Massachusetts State Archives, survives in a digitized manuscript discussion: https://www.heirloomsreunited.com/2020/06/1778-muster-roll-of-capt-george-white.html . Its surviving list and company context may help locate original MA Revolutionary Rolls (the copied manuscript cites Vol. 43, p. 75 for **certain other soldiers**). This is **not** a located 1777 Ensign Robert entry; never cite that reference as his individual roster without locating him.

**Original retrieval priority:** Massachusetts Archives Lithgow March–November 1776 payroll sheets and Feb 1777 officer appointment; militia/bounty rolls with residence and age; the distinct Georgetown Lemont and Tyrannicide entries; then probate, town vital, land and tax material to establish Robert's parentage and the possible Topsham family network.

**Editorial update:** The initial assertion above that the 1776/1777 listings were only a plausibly similar pair has been superseded by this verified published Massachusetts archival compilation. Original individual records are still needed.
