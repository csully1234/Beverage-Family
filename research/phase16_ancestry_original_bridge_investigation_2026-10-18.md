# Phase 16 — ancestry bridges: Matthew, Clarissa Cobb, Nathaniel and the original Topsham surveys

*Research and implementation: 18 October 2026. Draft investigation only; no correspondence, merges, purchases or source-image republication.*

## Research result 1: Clarissa Cobb and Captain Matthew Beverage of Hope

A significant complementary named-family source was located for a Matthew Beverage whom the site does not currently place in the proven family tree.

**Cyrus Eaton, *Annals of the Town of Warren* (1851), printed p. 383, Cobb family section** reports a Clarissa, daughter of Captain Barnabas Cobb, as wife of **Captain Matthew Beverage of Hope**.

- Transcribed and searchable page: https://ldsgenealogy.com/ME/books/Annals-of-the-town-of-Warren-with-the-Early-History-of-St-Georges-Broad-Bay-and-the-Neighboring-Settlements-on-the-Waldo-patent-part-39.htm

**Cyrus Eaton, *History of Thomaston, Rockland and South Thomaston*, vol. II (1865), printed p. 178–179, Cobb family section** also identifies Captain Barnabas Cobb (born 1760), wife Jerusha Cobb, their daughter Clarissa (reported born 27 March 1786) and Clarissa’s marriage to Captain Matthew Beverage. The caption supplies a potentially testable 1786 date, but **we have not inspected her original birth register**.

- Digitized source book: https://archive.org/details/historyofthomast02eato

**Dependency warning:** Eaton is the author of **both** the 1851 and 1865 texts. They may be a revision of the same field notes or informant. Treat them as **one linked printed evidence family**, not two independent marriage records. No original church solemnization, probate inheritance or 1786 birth record has been located. We intentionally do **not** add a Capt. Matthew or Clarissa genealogy person profile here.

This lead is valuable because **Cobb family marriage/probate records** may independently name Captain Matthew and his kin, revealing a route around surname-only ancestry inference.

## Research result 2: The explicit 1865 uncle/nephew and niece report

The same Eaton *Thomaston–Rockland* volume, printed pp. 146–147, reports **Nathaniel Beverage**, roughly born 1804, formerly of Fox Islands, as *a nephew of Captain Matthew*; Nathaniel’s wife **Sarah Alexander** is separately called a *niece* of the captain. Children Henry T., Mercy and Frederic are listed.

It does NOT identify Nathaniel's father, mother, or Sarah's birth parents. The two reported nephews/nieces could reflect different kinship paths; in older usage these words may also denote relatives by marriage. One sentence is not a probate conclusion.

The site's already existing `nathaniel_beverage_1804_rockland` and `sarah_alexander_beverage_1808` profiles remain unaltered. The specific spouse edge now has a `published_record` claim note in `data/phase15_relationship_reviews.json`, with the 1865 cited edition and its exact limitations.

A modern contributed New England genealogy proposes **John White Beverage** and **Rachel Crosby** as Nathaniel’s parents (https://genealogyofnewengland.com/f_86c9.htm). That can guide original register searching but is **not** itself enough to insert a parent-child link or decide which Nathaniel is intended. Be careful not to conflate Nathaniel of Rockland (c.1804) with Nathaniel Winslow Beverage (1776).

## Research result 3: Primary eighteenth-century manuscript maps exist—but do not prove family-owned land

Maine Historical Society / Maine Memory Network original Pejepscot Proprietors maps:

- **Coll. 61 Map 33**, Topsham, circa 1760 (MMN 11732): https://www.mainememory.net/record/11732
- **Coll. 61 Map 77**, original survey dated **28 June 1763** (MMN 109025): https://www.mainememory.net/record/109025 . A large 121 × 146 cm manuscript on paper shows numbered lots and many named owners across 25,190 acres, attributed to surveyor Stephen Gatchell.
- **Coll. 61 Map 40**, Topsham lots **7 April 1764** (MMN 11737): https://www.mainememory.net/record/11737
- **Wheeler**, published 1878, copies Topsham petition dated **21 December 1763**, naming James Beveridge: https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-18.htm

The public **Map 77 catalog names other owners but does not name a Beveridge** in its abbreviated list. That does not establish he is absent from the image. We have NOT read every minute manuscript label, identified James's supposed 1758 lot 7, inspected an original dated 1758 deed, or proved the 1724 Marblehead child was the 1763 Topsham petitioner. Never plot these maps as a verified modern Beverage home address.

The Maine Memory website limits image reproduction despite limited educational allowances. Provide **hyperlinks and call numbers** rather than uploading full-resolution source images without permission.

**Priority original-document retrieval:** inspect high-resolution Map 77; transcribe exactly visible labels and lot numbers (including negative findings); inspect Map 33/40; locate Pejepscot deed ledger for James's lot and Samuel's 1752 entry; obtain the provincial **21 Dec 1763 petition manuscript** and determine if names are autograph signatures or one copied clerk's list.

## Which unknown relationships would new records resolve?

| Proposed identity/kinship | Current evidence | Exact missing evidence |
|---|---|---|
| Capt. Matthew Beverage married Clarissa Cobb | Eaton 1851/1865 linked published histories | Original Hope/Warren marriage return or named Cobb probate |
| Capt. Matthew was Nathaniel's uncle | Eaton 1865 explicitly reports it | Parent-naming Nathaniel record + documented sibling of Matthew |
| Sarah Alexander was Matthew's niece | Eaton 1865 explicitly reports it | Sarah Alexander parent record plus mapped relationship to Matthew or his spouse |
| John White Beverage and Rachel Crosby were Nathaniel's parents | Later compiled genealogy; not an independently checked register | Fox Islands/North Haven baptism or birth, plus unique matching 1804 Nathaniel |
| 1758 Topsham lot-7 James is 1763 petitioner | 1878 published settler list and published copy of 1763 petition | Original lot deed and original petitioner evidence with identifying features |
| 1724 Marblehead James is 1749 Georgetown James | Town birth transcription and another town marriage-intention transcript | Baptism, marriage solemnization plus migration/property/probate identity chain |

**Zero new parent-child or sibling edges.** The crosslinked cases are presented as open research only. The independently necessary historical evidence has not been obtained; this is a real documentary route, not a claim of having solved the entire early Maine ancestry.

## Code and review

- `data/phase16_ancestry_bridge_dossiers.json`: four strict-ID case files, each with provenance, claim, exact limitations and original-record priorities.
- `ancestry_bridge_casework.py`: visitor-facing searchable cases in Historical Discoveries and linked from applicable existing profiles, but not a second family tree.
- `data/phase15_relationship_reviews.json`: adds a specifically qualified 1865 published spouse report for the existing Nathaniel/Sarah edge.
- `tests/test_phase16_ancestry_bridges.py`: six regression tests checking source URLs, linked exact-person IDs, no new parents, correct relative referent, map provenance and spouse-review limits.
- `tests/test_phase15_relationship_evidence.py`: expected reviewed edge coverage updated from 11 to 12.

**Publication safeguards:** Entire original source register, source files, locations, Boston Tea Party claim, family addresses, original kinship graph, photo reproduction permissions and historical testimony remain unchanged. Draft PR only. No archival letters or correspondence sent, no purchases, no Render deploy.
