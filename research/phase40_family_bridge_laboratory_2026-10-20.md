# Phase 40 — Family Connection Laboratory: tested ancestry hypotheses, not invented links

**Date:** October 20, 2026. Builds on the merged Phase 39 archival expedition.

## The genuinely important unresolved discovery

Nathaniel Beverage of Rockland (born around 1803/1804), husband of Sarah Alexander, remains in a separate four-person family branch. A contributed New England genealogy explicitly lists his parents as **John White Beverage** and **Rachel Lucy Crosby**. They already appear together in the main tree, but are not linked to this Nathaniel.

The 1865 Cyrus Eaton *History of Thomaston* calls Nathaniel the **nephew of Capt. Matthew**, while calling his wife Sarah his **niece**, without naming either's parents. <https://genealogyofnewengland.com/f_86c9.htm>

**Evidence boundary:** These are corroborative research leads only. The contributed family tree contains both claimed parents and is **one derivative source**, not two original proofs. The 1865 kinship statement is different but can be consistent with either several blood or marital arrangements. The birth-date discrepancy (1803 in the compilation versus the indexed 1804 approximate birth) remains unresolved. **Do not insert Nathaniel as child of John White or Rachel until a named original register or estate record is inspected.**

## Interactive work created

- New `family_bridge_lab.py`: explicit proposals for two potential parents, each with documentary basis, required independent original record, and an unproved label. These are plain research tickets, not editable tree data.
- Pure read-only `bridge_preview()` overlays hypothetical parent-child links into copied graph maps, then calculates how many disconnected groups would remain **IF** the claim were proven. It never saves edges, changes JSON, or asserts a newly proved ancestor. The real component count is displayed beside the hypothetical result.
- New dedicated **Family connection laboratory** section integrated directly into existing `Family Origins Expedition`, with selectable hypotheses, live comparison, original-record research obligations, and links to the disconnected branch and original archives.
- `tests/test_phase40_bridge_laboratory.py` checks canonical relationship mappings stay unchanged, original-source proof requirements, strict exact-profile endpoints and all four disconnected family groups.

## Primary original records to acquire in evidence priority order

1. **1803 birth, Vinalhaven/North Haven**: Find the actual image of Nathaniel's alleged 20 October 1803 birth in a contemporary municipal town register with the names of both parents. Inspect the handwriting, register folio, date and place. FamilySearch [Maine Births and Christenings, 1739–1900](https://www.familysearch.org/en/search/collection/1674856) provides a searchable index but an index match alone will not identify the handwritten entry.
2. **1838 Sarah Alexander marriage**: Locate an April 26, 1838 contemporaneous marriage return naming place, bride, groom and, if recorded, parents/witnesses. Compare with the descendant's later records to ensure the correct Nathaniel.
3. **1839 John White Beverage estate**: Search contemporaneous probate distribution for Nathaniel as an explicitly named son or legatee. A same-name witness to a different estate is not proof.
4. **1837 Thomas Beverage deed contradiction**: Before attaching the deed to Capt. Thomas (currently dated dead in 1834), read FamilySearch DGS 8296915 image 207/601, Hancock Deeds p.387 for actual grantor, acknowledgement and recording dates. The Hancock County Registry's [official deed search](https://hancockcountydeeds.com/search) advertises searchable deeds and public watermarked copies. This is a practical retrieval option, not a claim the image was examined.
5. **1820 Hope census**: Read NARA M33 roll 36 Hope manuscript sheet 276 to capture Matthew's household tally, without inventing household members' names.

The original images listed above are not presently inspected. The Woodruff editorial source apparatus has exact DGS pointers (see Phase 39), but image locators are not original evidence until the images are actually read. No user emails, courthouse requests or access changes were performed.

## Next large expansion once originals are inspected

If two independent contemporaneous records agree on exact persons and parentage, update the effective people overlay with cited parent links, verify component and relationship consistency, update person profiles, focused/full trees, timeline, provenance and historical notes together in a dedicated evidence-reviewed PR. If the originals disagree, retain both competing theories in this laboratory instead of changing the tree.

This phase intentionally makes research easier for the entire family and keeps the same password, all photos, 305 book pages and original sources accessible.
