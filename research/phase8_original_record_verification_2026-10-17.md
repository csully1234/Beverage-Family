# Phase 8 — original records, identity controls and family evidence trails

**17 October 2026. Draft research and website integration. No outreach, purchases, merges or deployment.**

## 1. Verified baseline and what did not need duplicating

- Production deployment of PR #27 was confirmed **live** on Render at commit `d7c16ab7e76126814d9aae071010347d9294c6ab`. Render's deployment completion is *not* a substitute for hands-on testing behind the site's password gate.
- The current tree already contains distinct Lowell Sr. and Lowell Jr. profiles, existing documented Lyford sibling-only relation, the Eliot/Dorothy spouse relation, and the existing original-book photo crosswalk. All remain unchanged.
- The 2013 contemporary obituary for **Arthur Woodrow Beveridge** identifying father Norwood Pierson Beveridge, mother Winifred Dorothy Woodrow Beveridge and grandparents Orris/Rose was *already* in `data/research_people.json`; no duplicate or new edge is needed.
- The user-authorized *The Colony* 305-page PDF and 35-term OCR-based **navigation** index remain available; index matches are not original transcriptions or confirmed people.

## 2. Independent research: what has and has not been established

### Arnold P. Beveridge and Marion Priscilla Delano

**New useful corroboration:** the searchable 1940 federal-census name index for Sharon, Norfolk County, Massachusetts independently lists **Arnold P. Beveridge** (born approximately 1904) and **Priscilla D. Beveridge** (approximately 1901), plus other Beveridge entries. It does **not** show household relationships on the town-wide summary; obtain the actual enumeration image before declaring them married in 1940. The separate Tri Delta museum **name index** contains `Beveridge, Marion Priscilla Delano`. A FamilySearch compilation offers a lead to obituaries and cemetery records, but none constitutes an original marriage return.
- 1940 index: https://ldsgenealogy.com/MA/1940-Census-Sharon-MA.htm
- Tri Delta name-index lead: https://tridelta-test.historyit.com/tag.php?id=4070&q=Mencken%2C+Sara+Haardt
- FamilySearch compilation: https://ancestors.familysearch.org/en/K83Y-C4N/marion-priscilla-delano-1900-1996

**Decision:** Do not add a legal spouse edge or children until the original 1940 household and 1926 marriage registration establish the precise connection. The published book gives the claim, and there is genuinely independent *name co-occurrence*, not a fully verified civil union.

### Lyford P. Beveridge, Ruth Bingham Reynolds and Ann Morrison

The 1991 obituary identifies **a brother named Lyford**. The authorized family book describes a Lyford Pierson with Ruth and Ann, and a later compiled genealogy mirrors a 1925 Massachusetts wedding and age ranges. Repeated compiled data cannot be counted as two independent vital attestations, and a modern Lyford Pierson may be a namesake rather than the 1900-born person. Do not attach inferred parents or living relatives solely by recurrence of the name.

- 1991 obituary: https://www.washingtonpost.com/archive/local/1991/06/20/the-rev-lowell-beveridge-professor-of-music-dies/b9e898f1-334c-44d7-bbdd-66354b1bbe83/
- Secondary lead: https://www.mytrees.com/names/Married/1925/1/BINGHAM%2BREYNOLDS

**Records to obtain:** 1925 Massachusetts marriage register, 1900 birth and 1999 death certificates/obituary, then original documentation for Ruth and Ann. No unauthorized request or purchase made.

### Vernon Linwood Beverage and Nellie Marion Ames

The memoir's appendix claims these names; a separate FamilySearch **compiled** Milton Ames Beverage family page names them as Milton's parents. This is a promising target for an original 1918 Maine birth return and a 1915 reported marriage, but no scanned returns were authenticated.
- Compilation: https://ancestors.familysearch.org/en/9C27-C6S/milton-ames-beverage-1918-1993
- Original records search collection: https://www.familysearch.org/en/search/collection/1803978

**Decision:** Keep Vernon out of the family tree pending the original household chain; do not infer Charles and Annie from online cemetery prose alone.

### Early Maine ancestors: Matthew, Clarissa, Nathaniel and Georgetown/Topsham

A **separate 1851 published *Annals of Warren*** lists Clarissa, child of Capt. Barnabas Cobb, as wife of Capt. Matthew Beverage of Hope. This supports the Matthew–Clarissa *reported marriage* independent of the 1865 narrative, but neither source independently places Nathaniel born c.1804 among Matthew's children. Nor does an intention to marry establish the Georgetown James/Jean wedding or prove Scottish parentage.
- Historic published genealogy: https://ldsgenealogy.com/ME/books/Annals-of-the-town-of-Warren-with-the-Early-History-of-St-Georges-Broad-Bay-and-the-Neighboring-Settlements-on-the-Waldo-patent-part-39.htm
- Maine Archives digitized **originals**: https://www3.maine.gov/sos/archives/digital-archives
- Maine Archives pre-1892 custody/background: https://www3.maine.gov/sos/archives/archives-services/genealogy-research

**Next documentary chain:** original 1838 Nathaniel/Sarah marriage and baptism/parent names; Matthew's probate, deeds, inventory and any town registers; Clarissa's original marriage; 1749 Georgetown marriage intention **and separate solemnization**; 1752/1758 Topsham lot deeds and original survey. Candidate names should be attached only when the parent-child and name/disambiguation chain is documented.

### Already known pairs and people

Eliot and Dorothy have contemporaneous historical diary context plus the family memoir; the more specific Elizabeth Dorothy Gattrell name requires her original marriage. The 1887 Concord genealogy establishes a historic Hanson name, but not which Hanson is in the Amelia portrait. Olive/Florence appear at the same address in Newton published directories and are described as partners in the memoir; the site correctly preserves this as a **historical association**, not a presumed legal wedding. Do not erase ambiguities or upgrade source status without reviewing original images.

## 3. Implemented visitor-facing source navigation

- `identity_casework.py`: a family-friendly original-evidence explorer, using exact person ID and original book-page associations instead of fuzzy name matches.
- `data/phase8_identity_evidence.json`: eight family cases, each with separate **what we know**, **what it does not prove**, **clickable sources**, and **the exact original records that would settle the question**.
- Family Books has the accessible evidence section next to the existing 16 unresolved source/photo identities.
- Opening a scanned book page displays related evidence cases **without promoting an uncertain identity to a confirmed relative**.
- Existing ancestor profiles with a reviewed relevant record get an original-evidence disclosure linking to the source; no genealogy or original source-record archive edits.

## 4. Review and release gates

1. GitHub CI on Python 3.12 and 3.13: all archive, genealogy and JS interaction tests should pass.
2. Verify live PR #27 Streamlit password gate and direct links manually in a real browser; Render deployed successfully but automated GitHub checks do not prove the on-screen UX behind login.
3. PR #28 remains **draft**, with no merge, deployment or outbound messages.
4. New original certificates or more complete archived item access can justify a later **separate, evidence-reviewed** relationship merge.

No historical Boston Tea Party claims or existing family addresses were touched. No modern residence information was collected or added.
