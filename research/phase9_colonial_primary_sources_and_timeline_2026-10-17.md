# Phase 9 — Colonial-era identity bridge and honest timeline presentation

*Research review: 17 October 2026. Source-first visitor presentation, no modified original genealogical records, no outgoing requests.*

## What was misleading on the existing website

The old `data/events.json` includes an event with ID `event_marriage_james_jr_jean_white_1749` describing a **completed** James Beveridge–Jean White wedding. The strongest specifically dated source is **only a marriage intention**, February 6, 1748/9 (usually normalized 1749). The old site also describes the 1724 Marblehead child as someone who later emigrated and married Jean. His dated birth is supported by a town-record transcription; that **later identity bridge is not established** merely because both are named James.

The source-backed, browser-visible **presentation overlay** now overrides only the *rendered title, summary and evidence status* of the three entries. It applies in standard timeline cards and in the **complete chronology**, including selected-item detail panels and direct-bookmark messages. The underlying events, claims, relationships, sources, and Boston Tea Party assertion remain present and unchanged. Source review notes are still accessible by link.

## Three defensible evidence statements

| Reported record | What the current source shows | What it does NOT prove |
|---|---|---|
| 16 Dec 1723, Marblehead | Published town marriage record of James Beveridge (variant Beseridge) and Sarah Bennett | James's Scottish birthplace, ancestral parentage, and the specific church where married |
| 27 Aug 1724, Marblehead | Published town birth of James to James and Sarah (Befreadge/Befridge spellings) | That this child is the same James recorded in Georgetown in 1749 |
| 6 Feb 1748/9, Brunswick register | Published **marriage intention** listing James Beviridge/Beveridge and Jean Write/White as of Georgetown | A solemnized wedding, birth identities, children, or a Scottish migration chain |

**Spelling/date nuance:** The published 1740–1769 transcription spells the parties “James Beviridge and Jean Write” and the intention as **1748–9**; the 1740–1764 printed transcription regularizes “Beveridge and Jean White” under **1749**. Those are two editions of the same underlying intention, not two independent 1749 wedding records. The two date styles represent Old Style/New Style year notation, not two separate events. Original register must be examined. [Two transcriptions](https://archives.mainegenealogy.net/2007/01/brunswick-marriage-intentions-1740-1769.html), [other transcription](https://archives.mainegenealogy.net/2008/06/brunswick-marriage-intentions-1740-1764.html).

A modern contributed Ancestry family tree alleges **Sarah Holman** was the 1724 James's mother; the site also has a later 1734 marriage to a Sarah Holman. The **contemporary-derived Marblehead birth record says only “Sarah,”** and the 1723 marriage entry says **Sarah Bennett**. Do not silently combine the different Sarah entries or use the contributed tree as a second independently confirmed birth record. Separate original church/town register comparison is needed.

## Digitized original archives to investigate next

### Maine Historical Society — Pejepscot Proprietors, Coll. 61

- **Finding aid:** https://mainehistoricalsociety.libraryhost.com/repositories/2/resources/2
- **Digitized volume 4:** https://www.mainememory.net/record/112087
- **Independent holding:** Peabody Essex Museum finding aid for the Pejepscot Proprietors papers, https://pem.as.atlas-sys.com/repositories/2/resources/204

The MHS collection is fully digitized, ten volumes of records ranging approximately 1627–1866, and includes original deeds, maps, municipal records, proprietor accounts, lists of settlers and early Topsham incorporation material. This is **direct access to the type of primary evidence needed for the 1752 Samuel and 1758 James Topsham lot clues**; the relevant named entries have **not** yet been isolated or authenticated from the volumes. The user has permission to research, not to infer acreage, title or lineage from finding-aid descriptions.

**Record review plan:** search handwritten ledgers and maps for James/Jas/Jams/Beveridge/Beviridge/Beverage, Samuel/Saml variants; note volume, original folio, digitized page, date, legal context, witnesses and adjoining owners. Map a continuous deed/probate/marriage sequence. Never equate two same-named men merely because dates fit.

### Marblehead Museum — original parish and town sources

- Historical Congregational registers: https://marbleheadmuseum.org/church-records/
- Vital-record volumes and repositories: https://marbleheadmuseum.org/vital-burial-records/
- Birth transcription: https://ldsgenealogy.com/MA/books/Vital-records-of-Marblehead-Massachusetts-to-the-end-of-the-year-1849-part-4.htm

The museum links to original digitized First and Second Congregational church registers overlapping 1723–1734. Find James and Sarah's marriage/children and the later Sarah Holman marriage, checking both parents, township, witnesses and surname variants. The secondary published compilation alone cannot prove church attribution or Scottish origins.

### Original 1749 Georgetown/Brunswick marriages

The February 1749 source is an intention in a Brunswick clerk's list. Locate any **separate** church solemnization entry, family testimony or probate/migration deed tying these people to the specific 1724 James. Until then, keep the marriage and parent-child identification unverified. No requests were sent.

## Engineering/release safeguards

- `data/phase8_event_evidence.json`: additive source-backed display wording with explicit uncertainty and links.
- `historical_claims.reviewed_event_presentation()`: pure, exact-ID, copy-on-read helper; changes no event JSON.
- `app.py`: standard timeline cards and selected-event deep links display accurate descriptions.
- `unified_timeline.py`: full timeline table and selected source records show corrected summaries; original source citations retained and review annotations accessible.
- `data/phase8_identity_evidence.json`: updated early-Georgetown investigation with official archives, manuscript collection links and competing surname/spousal theories clearly labeled as leads.
- Tests verify all timeline items remain present and the three reviewed items do not lose their original event/source identities.

**No family-tree changes, no published addresses altered, no PR merge/deploy or archival correspondence.** This is presentation correction plus independently actionable research leads. The complete site UI still requires human verification behind its family password after review.
