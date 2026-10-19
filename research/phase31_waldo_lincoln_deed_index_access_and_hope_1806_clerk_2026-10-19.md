# Phase 31 — Hope land-record index investigation and newly indexed 1806–1807 clerk entries

**Investigation date:** 19 October 2026. **Baseline:** Phase 30 main commit `86d13ecbf741fb5e2776bdb7acf34f0f834931e2`.

## Purpose

Research the 1837 estate of Matthew Beveridge/Beverage of Hope backward through Waldo and Lincoln deed registries, looking for a recorded volume/page and the title history of the homestead and parcel names tentatively read in the estate inventory. Protect evidence integrity: never present a registry's available searchable indexes as proof that an actual Matthew deed was found.

## Deed access result — no verified instrument

- **Waldo County Registry SearchIQS** guest landing page https://searchiqs.com/mewal/ is accessible; its scanned index books cover **1827–1980**, and scanned record books volumes 1–694 begin **19 January 1828**. See the platform's official holdings guide: https://help.searchiqs.com/article/95-mewal.
- **Lincoln County Registry SearchIQS** guest landing page https://searchiqs.com/MELIN/ is accessible; historic alphabetical index books cover **1761–1847**, with scanned early deed books going back to **1761**. See https://help.searchiqs.com/article/93-melin.
- The guest **index-book viewer is an interactive JavaScript/search workflow**, and it did not expose a readable name-result page to the available public text-based research tools. We **did not** read an actual B-surname index image, click a handwritten Matthew row, or obtain deed book/page numbers. Independent web-indexed searches for variants Matthew Beverage/Beveridge, Clarissa Beverage, Ezekiel G. Beverage, Nathaniel Alford, and Lucy Whitney returned no reliably attributable recorded instrument.
- **FamilySearch** has other deed-image access routes, including the separate `Maine, Wills and Deeds, ca. 1700s–2017` search collection (https://www.familysearch.org/en/search/collection/3158868). The county-specific Waldo deeds/indexes 1827–1900 are cataloged as image browse records. No FamilySearch deed image identifying the specific Hope Matthew was obtained.
- Maine Genealogical Society's **Lincoln County Master Index to Deeds, vols. 1–100 (1760–1818)** is a modern alphabetic index of about **88,000 original deed index entries**, but is a printed publication sold by MGS and was **not inspected or purchased**. Source: https://maineroots.org/shop/special-publications/product/94-lincoln-county-maine-master-index-to-deeds-in-volumes-1-100-90. This is a potential efficient alternative to individually reading many B-surname index pages.
- The 1837 probate's tentative seller names **Nathaniel Alford** and **Lucy Whitney** remain *unverified handwriting readings*, not confirmed deeds or kin. No new property bounds, owner chain, land locations, or deed book/page are asserted.

**Next access step:** interactive guest-browser navigation (e.g., in ChatGPT Work's cloud browser or a normal logged-in guest-browser session) to the *Waldo Grantor and Grantee Index Books*, letter **B** and A–Z surname variants around 1827–1845; extract book/page for Matthew's estate, widow Clarissa, Ezekiel G., Achsa Heald, James M., Polly Tucker, Thomas J., Sarah A., George W., Martha, and other children. Only after inspection, cross-check with Lincoln's A–Z B-surname index through 1827 for possible earlier homestead acquisition. Reverse-name searches for Alford and Whitney must be crosschecked against a particular matching grantee before identification.

## Positive historical result: Matthew in Hope by June 1806

The digital text of the **Hope Town Clerk Records 1804–1848**, modern literal transcription (https://openyls.law.yale.edu/bitstreams/b01906b3-669f-49a3-8023-099a2cd3ae82/download), includes the following earlier dated entries, previously absent from individually indexed site research:

1. **June 23, 1806, transcription p. 12** — town meeting mentions **Matthew Beveridge** as clerk in the closing attribution. This is a direct textual reference in a *modern transcription of a historical municipal ledger*; the manuscript signature is **not inspected**.
2. **April 9, 1807, transcription p. 15** — Matthew Beveridge credited with recording the April 6 meeting.
3. **June 19, 1807, transcription p. 18** — Matthew Beveridge named as clerk recording road votes; a discussion of a deed **between other people** is **not** a deed conveying property to Matthew.

This brings the earliest independently indexed town-clerk passage from **1811** back to **1806**, with two additional 1807 records. There is still **one underlying Hope town clerk ledger**; the new lines are **not** three independent attestations of ancestry, a land deed, or a link to the 1785 Fox Islands minor. Historic Hope municipal ledger originals and any autograph remain a priority for manuscript inspection.

## Website implementation

- New additive `data/phase31_hope_earliest_clerk_research.json` holds three page-cited supplemental clerk records and transparent deed-search limitations; Phase 20's original researched snapshot is preserved unchanged.
- `hope_matthew_civic.py` merges them in date order into the existing historical town timeline, changes the date range to **1806–1827**, adds an **1806–1807** filter, and reminds visitors all town entries come from a single transcript.
- `family_research_index.py` includes all three new records (bringing indexed dated Hope clerk/census observations from eight to eleven), without assigning a canonical person ID to an unproved historical same-name identity.
- Tests verify exact transcript years/pages, single-source-family classification, no verified deed claims, and all eleven archive search cards.
- No fabricated parent or ancestry link, no unlicensed historical document republished, no address or family password modifications.

**Release boundary:** This is a new *documentary chronology lead and archived research*, not confirmation that a specific land instrument exists or that the 1806 clerk was the 1837 decedent.
