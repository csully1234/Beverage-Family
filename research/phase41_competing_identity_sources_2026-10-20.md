# Phase 41 — Competing ancestry claims: new Rachel and Josiah discrepancies

**Research date:** 20 October 2026. Builds on Phase 39 primary-source targets and Phase 40 hypothetical connections. Canonical ancestry and family login remain unchanged.

## New findings with significant implications for family-tree correctness

### The Rachel surname problem

The site's Rachel `rachel_crosby_1778` is listed as **Rachel Lucy Crosby**, spouse of John White Beverage. The derivative genealogy [Genealogy of New England family page 344? / John White household](https://genealogyofnewengland.com/f_86c8.htm) likewise names Rachel Lucy Crosby, marriage 2 February 1800, and children including Norwood, Josiah and Nathaniel.

Meanwhile the contributed [Ancestry Josiah B. "Si" Beverage profile](https://www.ancestry.com.au/genealogy/records/josiah-b-si-beverage-24-tsnws0) explicitly names the purported mother as **Rachel Luce Tarr**. The [contributed Jane McKenny Beverage page](https://www.ancestry.com.au/genealogy/records/jane-mckenny-beverage-24-y5g9s) repeats Rachel Luce Tarr as the purported mother with John White as father. **Both Ancestry pages are one contributed-platform source family**, potentially copied from another tree, NOT two independent contemporary parentage witnesses.

No actual Rachel marriage entry, birth or death register was opened. The labels may be variants, conflations, names from different women, or incorrect user submissions. **Do not replace Rachel Crosby, add Tarr parents, or invent a second wife.**

### Josiah B. "Si" Beverage parentage contradiction

The canonical website profile `josiah_b_beverage_1821` currently lists **Josiah Winslow Beverage (b. 1793) and Mary Dyer (b. 1795)** as parents. Ancestry's contributed profile for an apparent 1821 Josiah B. "Si" instead names **John White Beverage and Rachel Luce Tarr** with a **5 April 1821** birth. The derivative [Genealogy of New England household list](https://genealogyofnewengland.com/f_86c8.htm) independently names John White and Rachel Lucy Crosby with a Josiah **born June 1821**. The historical birth-month mismatch raises further identification doubts.

These are competing claims about an apparently corresponding person, not a proof that the existing genealogy is wrong or that the contributed tree is right. A contemporaneous 1821 birth register, Josiah–Jane Young 1844 marriage return and 1918 Maine death certificate naming parents could resolve the competing identities.

### Nathaniel Rockland and 1837 deed remain unresolved

[Derivative Nathaniel household profile](https://genealogyofnewengland.com/f_86c9.htm) reports 20 October 1803 birth, son of John White and Rachel Crosby, while canonical `nathaniel_beverage_1804_rockland` is an **approximately** 1804-born disconnected person without proved parents. Phase 40 only *simulates* connection; an original town register and 1838 marriage record are required to establish it.

The editorial [Wilford Woodruff Papers Josiah profile](https://wilfordwoodruffpapers.org/subjects/josiah-beverage) cites a June 1837 Hancock deed attributed to Thomas Beverage, with precise DGS 8296915 image 207/601, **after** the main Capt. Thomas's recorded October 1834 death. The manuscript deed remains uninspected and the named Thomas cannot be assumed to be that captain.

## Work completed

- `data/phase41_competing_identity_claims.json`: four independently delineated conflict cases, eight explicit alternative claims, editorial source-family identifiers, known date/identity anomalies, exact original documents needed, person IDs affected and openly limited evidence.
- `identity_claim_review.py`: all-case or individual-case comparison reader, source-family de-duplication (not confidence voting), selected original-document tasks, profile links and complete CSV export. No new images or third-party copyrighted scans reproduced.
- Integrated into **Historical Discoveries → Family Origins Expedition**, the exact linked-person historical-exhibit pages, and the full searchable Research Workbench. All cases are accessible; not first-25 limited.
- Tests assert the actual 202-person genealogy, four branches, existing `Josiah B.` parent IDs, separate Nathaniel branch and original-source flags are unchanged, enforce safe links and prevent attribution of unviewed manuscripts as inspected.

## Direct first-hand record objectives

1. Find the 1800 original marriage register entry for John White and Rachel, and inspect the actual bride surname, filing date, witnesses and town context.
2. Locate the 1821 original birth entry for Josiah B. in Vinalhaven/North Haven; determine whether two contemporary Josiahs with similar names existed.
3. Open the 1918 Maine death certificate for Josiah B. "Si", preserving the original parental informant attribution and date, and compare against his 1844 marriage.
4. Read 1803 birth records and 1838 marriage return for Nathaniel of Rockland; examine John White 1839 probate.
5. Read DGS 8296915 image 207/601 before assigning the 1837 deed to any Thomas Beverage profile.

**Access limitation:** Attempts to open FamilySearch DGS 7596929, 8296915, and 8130800 from this research environment returned inaccessible pages. No claim of direct inspection or read transcript was made. Archive site and derivative records were reviewed as separate **online publications**, not multiple witnesses just because several public pages link to the same ancestry data.

## Next truly substantive archival breakthrough

A named-parent original birth/estate document for Nathaniel would justify a cautious, clearly sourced tree update after validation. A contemporaneous Josiah B. parental record would be at least as important: the site's existing *parentage* may be wrong and should not be rubber-stamped as proved. Until then, none of these claims is promoted to a new parent-child edge.

**Unchanged:** all genealogy JSON overlays, relatives' addresses, Boston Tea Party claim, photos, 305-page book, family password, historic document permissions and no outbound messages.
