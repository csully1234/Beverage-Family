# Phase 5 — Original evidence can be inspected from the family pages

**Prepared 2026-10-16.** Implementation is a **draft PR**, not yet merged or deployed. No outgoing emails, archive requests, purchases, content copying or outside communications were made.

## Visitor workflow, changed behavior

1. **People:** an `Explore original records and research leads` expander near the top of an individual profile exposes relevant records *before* the page's tabs. The **Historical records** tab now groups claim-level evidence with inherited person sources and archival citations, deduplicates the same URL, and allows filtering to linked items, research leads, or bibliographic-only entries. A profile showing a candidate link does **not** assert that the person is conclusively identified by it.
2. **Timeline:** each event card has `Explore supporting evidence`. Records can be opened at the original publisher from the event itself, rather than displaying only an arbitrary citation count. The 1883 and 1888 bridge/mill discoveries have separately dated events.
3. **Photographs & Documents:** the new **Explore original evidence** tab offers searchable, collection-filtered records including historic film, external PDF scans/transcripts, institutional holdings, early intentions and modern published accounts.
4. **Previews:** PDF records can optionally render through an **external PDF iframe**, opened by the visitor. If the publisher forbids iframe embedding, the direct source link still works. Neither the scanned source nor film is downloaded/rehosted by this feature.
5. **Limits and rights:** each record distinguishes evidence directly documented, the desired primary record not yet obtained, identity assumptions, modern derivative accounts, and rights/permissions. URLs and preview routes are restricted to external HTTP(S) source pages; no remote scripts or HTML from the archive are inserted into the site.

### Why this is a materially better source viewer

Earlier profiles listed bare citation labels and some source URLs in the Historical records tab. A non-clickable bibliography such as `Find A Grave memorial` was sometimes indistinguishable from accessible original page images. The new `evidence_explorer.py` preserves the underlying citations, shows a linked/unlinked count without implying images exist, and exposes each document's **actual claim and limitations** next to its link. The curated catalog `data/evidence_exhibits.json` is **additive**; original October 14 collection snapshots and protected people/residence files remain unchanged.

## New source-specific findings and why they matter

### A. Brunswick 1748/49 James Beveridge–Jean White entry — two derivative transcriptions

- *Bangor Historical Magazine* 4 (1888), reprinted at https://archives.mainegenealogy.net/2008/06/brunswick-marriage-intentions-1740-1764.html, transcribes `James Beveridge and Jean White, of Georgetown` under **6 Feb 1749**.
- *Putnam's Monthly Historical Magazine* 5 (1895), pp.251–252, reprinted at https://archives.mainegenealogy.net/2007/01/brunswick-marriage-intentions-1740-1769.html, transcribes **`James Beviridge and Jean Write`, 6 Feb 1748–9**, illustrating variant name spelling and Old Style date treatment.
- **These transcriptions depend on the same underlying Brunswick marriage-intentions register and are NOT two independent marriages or original marriage-certificate images.** The original entry, solemnized marriage, and exact couple-to-profile identification remain unproven.
- The exhibit links to the existing James/Jean profiles as **candidate identity source associations**, without modifying their marriage or family relationships.

### B. Capt. Matthew / Nathaniel of Rockland — missing original parentage

- Cyrus Eaton, *History of Thomaston, Rockland, and South Thomaston* II (1865), pp.146–147, identifies a Rockland Nathaniel Beverage (b. c.1804), wife Sarah Alexander and three children, and calls him a **nephew** of Capt. Matthew of Hope.
- https://genealogyofnewengland.com/f_86c9.htm instead attributes the 1803 Nathaniel to John White Beverage/Rachel Crosby. **A compiled family tree is not an original parental record.** If Matthew were a brother of Capt. Thomas, this proposed lineage would yield **grandnephew**, a discrepancy requiring original proof.
- A separate original-document request for Matthew's possible Waldo probate has already been sent in a preceding phase; **nothing additional sent by Phase 5**.
- The new viewer puts the Eaton source and compiled alternative next to Nathaniel's profile, with explicit **candidate** labeling. No ancestor edges changed; no 1776 Nathaniel conflated with the 1804 man.
- Next original evidence: Nathaniel's 1838 marriage entry, an original baptism, John White's estate/guardianship records, Rockland civil death/census, and an archival copy of Eaton pp.146–147.

### C. Frank and May Beverage's 1937 photograph

- [Tonny Calderwood's 1937 diary transcription](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/1937.pdf#page=29) names **Frank and May Beverage** at their October 15, 1937 golden wedding and refers to a contemporary **photograph and caption**.
- The 50th anniversary suggests a wedding **around 1887**, but does not prove the day or which Frank Beverage in the tree was photographed.
- **The photograph itself has not been obtained**, much less licensed; no image has been copied. The diary transcript is externally hosted and previewable in a read-on-page iframe, and the link on the Frank born 1861 profile is explicitly flagged **candidate**.
- Next source: 1887 marriage return or town church notice, original photograph location, and permission from the historical society/owners before adding the actual picture.

### D. Direct access to original family bridge and mill documents

- [The Pulpit Harbor Bridges, NHHS PDF](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/bridges.pdf) is **9 pages**, with historic images, descriptions of First Bridge and Beach Bridge, an **1883 town contract involving Alvin Beverage on PDF p.8**, and additional historical town payment records on p.9. Pages 1–2 describe bridge chronology and the town's $250 authorization for Alvin. A bridge location does **not** by itself establish legal land title. A new **1883** timeline event points to the contract at the original PDF.
- [The Mill Stream, NHHS PDF](https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/the_mill_stream.pdf) describes Thomas Beverage's grist mill, son James's tannery, **Harrison Beverage's 1888 dam purchase**, Hiram's 1909 sawmill labor and 1932 dam construction, and a sketch rescued by Sam Beverage. New **1888** event is marked a **later claim requiring an original deed**, with no presumed Harrison profile attached as a verified event participant.
- [Original 1848 Maine legislative act](https://lldc.mainelegislature.org/Open/Laws/1848/1848_PS_c154.pdf) relates to the bridge at James and Josiah Beverage land near Pulpit Harbor. It is linked as an original *legislation scan* from the existing people's pages and timeline; no acreage inference.
- [NHHS 1975 rescue account](https://www.northhavenmainehistoricalsociety.org/history.html) recounts bridge construction bills, school-lot deeds and early Pulpit Harbor road map recovered by Sam Beverage and neighbors.
- The 2017 society exhibits and [North Haven Conservation Partners' Pulpit Harbor history](https://northhavenconservation.org/pulpit-harbor-history/) hold external image-rich context; the viewer links the originals rather than copying protected photos.

### Next archival step (NOT SENT)

The [North Haven Historical Society archives policy](https://www.northhavenmainehistoricalsociety.org/archives.html) allows staff-provided copies/scans depending on item condition and rights. Their site states research/copy services are provided without fixed fees and donations welcome; seek separate publication rights. If the user later approves contacting them, ask for the **1883 original bridge contract**, 1906 bill reference, **1888 Harrison dam deed and land survey**, the 1975 salvaged Pulpit Harbor road map and bridge bills (collection/box numbers), and the **1937 Frank and May photograph** and permission to publish.

## Evidence grades and permissions

| Source | What is actually online | Cannot automatically infer |
|---|---|---|
| Maine Legislature 1848 act | Contemporary official PDF | Family acreage/deed boundary |
| NHHS Pulpit Bridges PDF | Historical photographs and original-document reproductions | Marriage/parentage of Alvin, survey lot title |
| NHHS Mill Stream PDF | Illustrated published local history | Original 1888 deed or identity of Harrison |
| Brunswick intentions 1888, 1895 | Two typeset transcriptions of same original register | Ceremony, couple's identity |
| Calderwood 1937/1967 PDFs | Transcribed diary entries, caption references | Original photo file, living family identity |
| FamilySearch 1898 marriage leads | Indexed item referenced by a profile | Original marriage image inspected |
| NHHS 1975 founding account | Near-firsthand retrospective | Contents of each surviving original archive item |

**Image rights:** No copyrighted historical photo, diary scan, film, or library document has been rehosted. Access links and user-initiated iframe embedding point to holding institutions. A rights/attribution statement is rendered alongside each exhibit.

## Test and development details

- `evidence_explorer.py`: curated evidence load/index, safe HTTP(S) links, deduplication, citation normalization, grouped visitor UI and opt-in external PDF reading.
- `data/evidence_exhibits.json`: source-by-source claims, evidence limitations, association confidence, rights, person/event IDs and institution links.
- `data/phase5_events.json`: two additive time-marked observations, not revisions to baseline records.
- `family_data.py`: composes events from original protected JSONs and the additive phase5 overlay.
- `tests/test_evidence_explorer.py`: source integrity, no false lineage, URL security, original page targets, rights, baseline validation.
- Counts in `tests/test_archive.py` and `tests/test_research_collection.py` incorporate the added event layer while retaining the exact 180-person baseline and original snapshot checks.
