# Phase 15 — relationship-by-relationship evidence review across the family tree

Date: 18 October 2026. Work based on merged main after PR #34.

## Why this is a structural repair

The existing site correctly displays reciprocal parents, children, spouses and siblings. Its genealogy renderer also derives additional siblings from shared parents and reverses one-sided relationship pointers so family navigation works. That is a **graph normalization feature, not proof of genealogy**. A profile can have multiple citations for education, places or death and still no original proof of the parents attached to it.

The critical unanswered visitor question is: **“Why does the tree say these two specific people were related?”**

An undifferentiated green check on a source-bearing person would therefore be misleading. The answer must be claim-by-claim.

## Scope delivered in this phase

1. **Full effective-tree ledger, no historical mutations.** The source-backed runtime enumerates each parent→child pair once (directional), spouse pair once, and sibling pair once, including reciprocal and inherited links. It distinguishes explicit sibling entries from sibling navigation inferred through shared recorded parents.
2. **Transparent coverage accounting.** The Historical Discoveries page contains a searchable and paginated family-connection audit with three honest counters: total current tree links, claims individually reviewed, and links waiting for a relationship-specific source check. Coverage numbers are **not** a truth or correctness percentage.
3. **Source-specific profile panels.** Every person’s Family tab shows evidence statuses for all their recorded direct relationships, including the original provenance and an inspectable source for each curated reviewed pair. Unreviewed links are labeled as awaiting audit, **not rejected**.
4. **Eleven hand-reviewed link cases** in `data/phase15_relationship_reviews.json` (a tiny pilot relative to the whole graph):
   - Lowell Sr. and Ida Louisa Gattrell as reported parents of Lowell Pierson Jr. and Thomas Gattrell (four parent/child links): printed 1960 Harvard family report plus 1991 memorial context.
   - Lowell Sr. and Ida’s reported marriage: 1960 questionnaire and 1991 diocesan memorial.
   - Lowell Jr. and Hortense Sie as spouses: Harvard contemporary self-report, original marriage return not inspected.
   - Lowell Sr. and Lyford’s **sibling** link: 1991 Washington Post obituary names Lyford as brother; neither parent's identity established.
   - Mercy Beveridge and James Henry's **spouse** link: grave transcript plus nineteenth-century family sketch; exact 1776 marriage ceremony **still unverified**.
   - James Sr. to 1724 James Jr., Sarah Bennett to 1724 James Jr., and 1724 James Jr. to Jean White: Marblehead published birth and marriage entries and Brunswick 1748/9 **marriage intention**, with **unique identities and solemnization not established**.
5. **Provenance metadata per claim**, with primary-source acquisition limitations even for those marked corroborated in published reports. Cited two editions of one underlying clerk's record are not described as independent proof.
6. **Tests** ensure every effective edge is included exactly once, no curated link references a non-existent relationship, no unreviewed link is silently called verified, and historic disputed parentage (including Mercy's excluded parents and the James/Jean marriage) is never upgraded based on same-name matches.

## Status explanations for family visitors

- **Supported by corroborating published records:** multiple cited published sources or contemporary self-report and obituary context; original civil certificates may still be missing.
- **Recorded in a contemporary or near-contemporary account:** a meaningful directly named relationship in a report; not always a vital certificate.
- **Reported in a published historical record:** a published cemetery inscription or family sketch; may depend on a single underlying stone or manuscript.
- **Identity or relationship still requires proof:** an existing tree connection remains navigable but the source currently supports only an intention, a namesake or a conditional mother/father identity.
- **Documentary support for this link not yet audited:** inherited link is still included, not declared false. Existing person-level citations may contain relevant proof, but none has yet been systematically matched to this particular edge.

## Limits and what comes next

This phase **does not** certify all relationships. It creates a reliable, testable system for reviewing them. The vast majority will initially be “not individually reviewed,” which is accurate and necessary.

**Next batch of cases, highest genealogical return:**
- Original 1723/1724 Marblehead church/town registers, the 1749 Brunswick intention and **distinct** marriage return, 1758 Topsham lot deed, 1763 original petition, 1764 town roster, and a deed/probate bridge to the earliest Fox Islands generation.
- 1831 James Henry probate naming Mercy or other Beveridge relatives, original Mercy baptism/marriage.
- Probate and parent naming records for Capt. Matthew and Nathaniel Beverage (Rockland), and separation of derivative genealogy from original contemporary family records.
- Explicit original relationship evidence for disputed nineteenth-century Amelia/Hanson and family members in the illustrated 305-page *The Colony*.
- Full review of other high-impact ancestors with many tree descendants before the lower-impact branches.

The entire base genealogy, photos, old disputed claims, residences and Boston Tea Party assertion stay unchanged. Do not use an inferred sibling link or general person citation as a verified birth relationship. No outside messages, record purchases, merge or deployment.

## Review checklist

- Audit dashboard accessible via **Historical Discoveries → How are family relationships documented?** (not an orphaned internal Sources & Method function).
- Every person’s **Family** tab shows the existing same people, parents and children, plus the claim-level research annotations.
- The 1748/9 James/Jean record is a **marriage intention, not a certified ceremony**; Lyford gains no automatic parents; Mercy's unverified parents remain absent.
- The full tree, historical map and relationship finder remain operational without any changed relationship edges.
- GitHub Python 3.12/3.13, full regression, JavaScript map/tree interactions pass before review.
- PR must remain **draft**; authenticated desktop/mobile visual verification is still required before release.
