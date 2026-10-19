# Phase 30 — Original Fox Islands settlement record retrieval, 1785–1786

**Date:** 19 October 2026. **Baseline:** Phase 29 `main` commit `48b144275f74fbbb84a98f8c0744372a782da431`.

## Purpose and outcome

A newly retrieved original-source *locator chain* makes the Fox Islands settlement problem substantially more actionable. Previously the site cited the 1785 petition's printed list and the 1786 Rufus Putnam settlers' report largely as uninspected leads. This phase found **three individually cataloged digital source records** in the Maine State Archives map collection and a **precise original Massachusetts petition/resolve archival series and chapter**. The 1786 paper settler report's full bibliographic/physical box number is independently traceable via the 2025 scholarly article.

**No new Matthew parent, sibling, birth year, marriage, real-estate conveyance, or identity correspondence has been proved by these source locators.** No new person is added to the family graph.

## Verified archival holdings — separate the record types

| Record and date | Holding institution / catalog locator | Direct access | What has actually been inspected |
| --- | --- | --- | --- |
| Fox Island Division of Islands land survey, Oct–Nov 1785; conditional grant 13 March 1786 | Maine State Archives, Knox County Plan Book p. 7, digital ID **302962**, a copy from Massachusetts Maps and Plans **#1343** | [Institutional item](https://digitalmaine.com/planbook_knox_county/8/) | Archive catalog transcription describes coastline survey by Jonathan Stone and John Mathews, attested Rufus Putnam; accessible hosted image/preview exists. No person-level original map labels transcribed. |
| Nov 1785 Fox Islands geographic list | Maine State Archives, Plan Book 9 p. 01.5, digital ID **210870** | [Institutional item](https://digitalmaine.com/planbook_9/2/) | Archive catalog describes a geographic listing of islands by Rufus Putnam, **not a known settler/household list**. No Matthew record verified. |
| Fox Island Division outline map, 1785 title / 1786 catalog date | Maine State Archives, Plan Book 8 p. 16, digital ID **209714** | [Institutional item](https://digitalmaine.com/planbook_8/17/) | Archive catalog describes island names including Pulpit Harbor and Crabtree Point and grant to John Calderwood and others. Catalog title/date discrepancy and copy relationship unresolved. |
| Massachusetts Fox Islands settlers' petition and grant | Massachusetts Archives, **SC1 / Series 228, Passed Resolves; Resolves 1785, February Session, Chapter 97; dated 13 March 1786** | [Scholarly footnotes 2–3](https://rsc.byu.edu/banner-gospel-wilford-woodruff/lord-told-me-go-i-went) | A historical scholar cites an actual received copy of the state original at this precise series/chapter. **The original petition sheets/signatures were not obtained** by this project. |
| March 18, 1786 Putnam settler's-declaration report | Maine State Archives, Augusta, **paper Box 001**, source title beginning “General Putnam's Report and Description in the County of Lincoln ...”, dated **1786-03-18** | [The Maine Genealogist 47(4), Nov 2025, p. 170–171, note 6](https://maineroots.org/images/Nov25TMG2.pdf) | Flanagan & Barbara Beverage Reeves cite an original report in the physical archive and say island claimants reported years of residence. **No original Matthew-specific survey declaration has been seen**. |
| 1785 petition settler list in a later historical book | *A Brief Historical Sketch of the Town of Vinalhaven* (1889), printed p. 10 | [Library of Congress digitized book](https://tile.loc.gov/storage-services/public/gdcmassbookdig/briefhistoricals00vinl/briefhistoricals00vinl.pdf) | This is a **digitized 1889 printed transcription**. It names James Beveridge, Thomas Beveridge, and “Matthew Beveridge (a minor)” on the island petition list, but does not define familial relations. |
| Museum's reproduction of the old petition | Vinalhaven Historical Society, *Early Days* exhibition | [Historical society exhibit information](https://www.vinalhavenhistoricalsociety.org/summerexhibit/2013exhibitearlydays.html) | Historical society reports that a copy of the petition can be viewed at its museum; whether it reproduces original signatures or merely a published transcript remains unverified. |

**Important distinction:** a digitized 1785 map is **not** the March 1786 paper settlers' report, and neither is necessarily the manuscript petition signed by original inhabitants. Even if two plan-book images reflect the same original plan, two different catalog records are not two independent attestations of any person's identity.

## What could actually connect the Matthew records?

Current documentary identity chain remains separated:

1. **1785 published petition transcription** — Matthew Beveridge named as a *minor*, without parents identified.
2. **1811–1827 Hope civic ledger** — Matthew Beveridge named as town clerk, without a unique birth/family link to the earlier island petitioner.
3. **1837 Waldo County probate** — Matthew Beverage/Beveridge of Hope, widow Clarissa Cobb (Cobb identification through later sources), eight children explicitly described in an original-era court warrant. It contains no proof of his own parents.

The 1889 historical publication lists other Beveridge names on the petition, but **same-list co-occurrence does not establish brotherhood**. The hypothesis that Capt. Thomas or James was Matthew's father/brother remains unresolved. A contemporary named guardian, individual claimed lot, later sale linking the lot and person, parentage-mentioning deed/probate, or marriage record is needed.

In particular, the 1786 Putnam report has a meaningful potential feature: in a peer-reviewed/edited genealogical reconstruction of the Eames family, authors report the settlers' claimed number of prior years on their land. If a distinct Matthew row exists, it could constrain his presence and the specific holding, but its **existence and contents are not currently verified**.

## Specific proposed archival retrievals — **not sent**

The website now generates copyable *unsent* specifications:

**Massachusetts Archives:** SC1/Series 228 Passed Resolves, February 1785 session, Ch. 97, dated 13 March 1786. Request the **complete original petition including signer pages, not just the resolve summary**, source folio numbers, reverses/endorsements, and image reuse guidance. Compare the minor notation, any guardian/lot context and spellings to the 1889 book.

**Maine State Archives:** March 18, 1786 General Putnam report, *paper Box 001*, especially all Fox Islands settlers' declarations, land holders, original page and lot designations. Request a complete original scan and reproduction terms. Compare any Matthew, Thomas and James separately; link them only if manuscript identifiers support it.

**Map image inspection:** compare the Knox County Plan Book p. 7, Plan Book 8 p. 16, Plan Book 9 p. 01.5 and Massachusetts Maps and Plans #1343. Determine whether digital images are copies of one field survey, not independent record witnesses. Check whether any lot-name labels can be confidently read.

**Hope probate-deed chain (still awaiting exact instrument):** seek Matthew's earliest confirmed deeds and 1837 homestead grantor chain in Lincoln/Waldo registries. No particular Matthew deed book/page/parcel is claimed verified in this phase.

## Website implementation

- `data/phase30_fox_islands_original_source_access.json`: seven distinct provenance cards with precise item numbers, host links, what was actually viewed, limitations, proposed actions and preserved three-record identity comparison. No added tree edges.
- `fox_islands_originals.py`: friendly **Fox Islands, 1785–1786: original-document trail** reader splitting *digitized plans*, *not-yet-obtained manuscripts*, *published contextual accounts*, and *the three-Matthews identity test*. Adds copyable retrieval notes, with explicit **not sent** language.
- `family_discoveries.py` and `family_origins_casework.py`: navigate to this page from the general Historical Discoveries and Clarissa–Matthew origins investigation.
- `family_research_index.py`: seven searchable source records as **Historical record trails**, with **no person IDs** (because the 1785 Matthew is not proved to be the Hope 1837 Matthew); also repairs workbench indexing so the eleven Phase 29 source-reviewed relationships appear alongside the original twelve.
- Tests check unique archival IDs, manuscript-not-inspected status, source URL/identity boundaries, workbench index 23 audited links, and authenticated Streamlit route rendering.

**Rights and operational boundary:** the official Maine maps remain hosted by Maine State Archives; no maps, archival manuscript facsimiles or probate images are downloaded into the site. The 2025 journal is linked, not republished. No external archivist contact, purchases or permission requests were sent. The existing login, relative residential addresses, protected Boston Tea Party claim and entire genealogy remain unchanged.

## Next evidentiary decision

Once the **original petition** or **1786 individual Putnam paper report** is actually in hand, separately transcribe every relevant Matthew/James/Thomas entry and test land-claim/identity crosswalks. Only then could a graph connection be responsibly proposed. Until then, the established four family groups remain separate.

This release creates an **actionable source trail**, not a claimed ancestry breakthrough.
