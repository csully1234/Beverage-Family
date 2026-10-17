# Phase 11: James Beveridge in Topsham, December 1763

**Evidence-audit date: 17 October 2026.** This phase compares six distinct printed-document sightings. It does not establish a newly identified ancestor or a migration from Scotland to Maine.

## Newly recovered document: Topsham incorporation petition, 21 December 1763

Wheeler & Wheeler, *History of Brunswick, Topsham and Harpswell* (1878), municipal history of Topsham, **printed pages 180–182**, reproduces a provincial petition explicitly dated **21 December 1763**, presented to Governor Francis Bernard and the Massachusetts General Court. Among named petitioners printed in its list is **JAMES BEVERIDGE**, next to William Thorne. Wheeler's attribution points to the **Pejepscot Papers** for the petition.

**Direct readable source:** https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-18.htm

The petition discusses the desire of approximately **35 families** to incorporate as a town after frontier settlement and taxing challenges. The reproduction supports a **named person's presence among the petitioners of Topsham** in 1763 (subject to accuracy of the 1878 transcription). It is more specific than a generic surname in a settler index: it is linked to a named, dated **civil act**. **We have not inspected the original signed manuscript**, so it does not yet prove that a James physically signed an autograph or conclusively link him to another James.

The same Wheeler chapter reports at the **first town meeting on 9 May 1764** the election of **James Beverage as hog constable**, already represented on the website. That is further evidence of a James name in Topsham municipal affairs in the period. It is chronologically consistent with the 1763 petitioner, but a person's identity is not proven merely by a similar name in the same town.

## Identity bridge — six sources kept separate

| Date | What is reported | Present limit |
| --- | --- | --- |
| 16 Dec 1723 | James Beveridge/Sarah Bennett married in Marblehead town record transcript | No Scottish birthplace or Maine identity proven |
| 27 Aug 1724 | James, child of James and Sarah, born in Marblehead | Not automatically the Georgetown James 25 years later |
| 6 Feb 1749 (1748/9) | James Beveridge and Jean White marriage **intention** | Marriage solemnization absent |
| 1758 | James Beveridge, Topsham settler/landowner index, lot 7 | Source is an 1878 compilation, not an original signed title deed |
| 21 Dec 1763 | James Beveridge in incorporation petition name list | Contemporary document reproduced in 1878; original manuscript not inspected |
| 9 May 1764 | James Beverage elected hog constable | Same person as 1763/1758/1749 remains a research proposition |

The website's **James record trail** now shows these six entries with links and explicit limitations. **Only the 1763 petition** is added to the Complete Family Timeline as a *historical document*, not as an unverified family-tree event or as a fabricated biological relationship. The original 1764 office event remains in place, so it is not duplicated.

## Manuscript research next steps, ordered by potential to resolve identity

1. **Locate the original 21 December 1763 petition** in Maine Historical Society Pejepscot Proprietors (Coll. 61) or the Massachusetts General Court petitions series. Record collection, manuscript volume, folio/image, original spelling, whether the marks are actual individual signatures or a clerk's copied list, residence, and any associated testimony or signatory relationships. If a genuine autograph exists, retain an authorized link/image and handwriting sample for comparison to deeds.
2. **Locate 1758 lot 7's original instrument** in Pejepscot deeds and grantor–grantee indexes, then search for subsequent transfer involving the 1763/1764 civic name, witnesses and family relations. Never equate map marker "7" to parcel acreage from a later printed index alone.
3. **Trace 1749 Georgetown intention to an actual marriage return**, plus deeds, baptism records, child records or wills naming the wife. Lack of a marriage record does not prove no marriage occurred; it leaves the claim unconfirmed.
4. **Study 1724 Marblehead child beyond birth**: original parish, probate and migration records. The mother is listed as Sarah in the birth entry, but surname attribution and separate Sarah Bennett/Sarah Holman marriage details must be compared to originals.
5. **Check Samuel (1752) and Robert (1776–77)** via independent probate and town tax lists; neither is yet demonstrably a relative of the 1763 James.

## Engineering and safeguards

- `data/phase10_early_maine_records.json` has one new, exact-dated **petition source card** linked to the already documented 1764 town meeting.
- `data/phase11_james_record_chain.json` makes **six distinct sightings** explorable without sharing a person ID.
- `early_maine_sources.py` adds source navigation and the comparative record cards.
- `unified_timeline.py` displays the petition as **Historical document** with date of the *petition*, not 1878 book publication.
- `visitor_ui.py` adds this comparison to **Stories & Discoveries → Before North Haven**.
- Regression tests protect the source-only nature, timeline uniqueness, no invented genealogical edges, and original event data.

**No original family addresses, Boston Tea Party claim, historical source archive, older event narrative or family relationships were changed. No correspondence, purchases or deployment.**
