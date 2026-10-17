# Phase 7 — The Colony identity evidence and navigation audit (17 October 2026)

## Baseline verified from the live repository
- PR #26 is merged into `main`. The canonical author is `lowell_pierson_beveridge_jr_1930`, **not** his father `lowell_beveridge_1905`. Both belong to the same documented lineage; retaining their distinct IDs prevents wrong photograph attributions.
- The 305-page website edition of *The Colony: Stories from a Down East Island* (2016) is present at `static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf`.
- The existing **82 photo-bearing pages** have caption summaries. The 23 canonical profile associations and 16 unresolved-name/identity cases in `data/colony_people_crosswalk.json` are *not* an exhaustive list of everyone named in the 305-page text.
- The linked scanned PDF was inspected outside GitHub. It is entirely **image-only**: the PDF has 305 pages, but no embedded searchable text. OCR is therefore a lower-confidence *research aid*, not a primary transcription, and any resulting names/dates require visual comparison with the actual page.

## Newly corroborated source leads, not identity resolutions

### Olive Amelia Beveridge and Florence N. Budlong
1. R. L. Polk and Co.'s *Newton City Directory, 1941*, indexed in the digitized book edition, lists **Florence N. Budlong** as a teacher at **21 Elm**, Newton. [1941 directory](https://ldsgenealogy.com/MA/books/Newton-Middlesex-County-Mass-city-directory-1941-part-15.htm).
2. The *City of Newton Assessed Polls 1947*, Elm Street entry 21, independently lists both **Olive A. Beveridge** (teacher, b. 1890) and **Florence N. Budlong** (teacher, b. 1900). [1947 municipal roll](https://ldsgenealogy.com/MA/books/Assessed-polls-City-of-Newton-1947-part-34.htm).
3. The authorized *Colony* memoir calls Florence Olive's life partner (PDF p. 235).

**Interpretation:** multiple published records corroborate shared address and long-term association. They do *not* establish a legal marriage or justify a `spouses` graph edge. A non-marital partner/companion relation would need its own evidence semantics and UI, distinct from genealogical parentage and legal spouses. The public site currently keeps her in the **unresolved-name/relationship** index with links to the original sources; it does not erase the partnership.

### Hanson Beverage (Amelia's brother in the caption)
A published **1887** genealogy of the Barrett family names **Hanson Beverage (born 1847)** and Mary Barrett in a family grouping, consistent with a historical Hanson surname record. [Potter, *Genealogies of some old families of Concord*](https://ldsgenealogy.com/MA/books/Genealogies-of-some-old-families-of-Concord-Mass-and-their-descendants-in-part-to-the-present-generation-1887-part-5.htm).

**Limit:** this cannot establish the person shown in the 2016 book's photograph, especially given the two Amelias and several generations of similar names in the archive. Hold the candidate; retrieve the original 1887 page and the underlying family record before assigning a person ID to the caption.

### Albion Pierson and Rose Emma Pierson
A memorial compilation for Rose attributes her parentage to Albion Pierson and Olive F. Hart. [Rose memorial](https://www.findagrave.com/memorial/157486335/rose-emma-beverage). **Derivative evidence only**. It is a concrete lead for a Tenants Harbor-era birth or marriage register, not independent proof of a father-child relationship. No parents were added.

## Case-by-case work plan for the remaining 16 unresolved entries
| Topic | Current decision | Original evidence needed |
|---|---|---|
| Hanson / Amelia | Candidate; no silent photo-to-ID match | 1887 genealogy scanned page, 1850–1880 original census households, full p. 49 image |
| Vernon Beverage | Keep unmatched | Birth/marriage/census matching book's p. 45/177 context |
| Albion Pierson | Parentage candidate | Rose's original Maine birth/baptism or parents' marriage |
| Jesse Hart | Ancestor candidate | Documented sequence of descent to Rose and contemporary register |
| Florence Budlong | Documented close association; non-marital relationship type unresolved | 1941/1947 city pages, shared household across dates, carefully phrased first-person memoir |
| Priscilla, Arnold's wife | First name in memoir only | Original 1926 marriage entry and complete full names |
| Ruth and Ann, Lyford family | Unresolved familial positions | Detailed caption plus contemporary marriage/birth records |
| Robert “Bob” Barclay | Named uncle; exact identity unresolved | Marriage/census and the original p. 239 caption |
| Daniel and Hattie Green | Name/household ambiguous | Vital and land records, p. 181 caption |
| Herman and Sarah Bengell | Historical context, not genealogical profile | Kinship evidence if any; otherwise context only |
| William W. Howe | Historical context only | School records and original source if relevant |
| Leonard and Helen Patton | Historical context only | Establish any actual kinship before genealogy |
| Charles and Mary Gates | Historical context only | Same guardrail |
| Helen Metcalf | Historical context only | Same guardrail |
| Captain Eleazer Crabtree | Candidate historic building attribution | Match source on p. 21 against unique historic person record |
| People in 1918/1936 group photos | Caption rows unresolved | Manually inspect p. 174, 194, 198, 223, 229, 253 with names/positions |

## Earlier ancestral expansion remains source-gated
- Nathaniel Beverage c.1804 vs Capt. Matthew's kinship: 1865 Eaton's family-history wording and compiled 1803 parents conflict. Obtain original 1838 marriage, probate/baptism, not a fuzzy name match.
- Topsham Samuel (1752 lot 3) / James (1758 lot 7): original land deeds and original indexed survey/map, no automatically inferred Maine → Scotland line.
- 1749 Georgetown James Beveridge / Jean White: *intention to marry*, not a confirmed solemnized wedding or an established branch connection.
- 1785 petition, 1786 report and 1781 testimony must remain distinguished. Do not modify the pre-existing Boston Tea Party claim, original residential assertions or property boundaries.

## Visitor-facing improvements in this draft
- Book reader offers context-aware profile links and unresolved questions **on the same original PDF page**.
- Original PDF scans can be displayed **inline on an ancestor profile** after an explicit visitor toggle.
- A dedicated **People & identity questions** tab searches unresolved cases, shows institutional/published source links and jumps to relevant original pages.
- Whole-family map can isolate recorded ancestors and descendants by *directional parent-child edges*, with all documented generations. No invented connections or collapsed historical siblings.

## Permission and publication boundary
No external correspondence sent; no paid scans or new copyright grant assumed. The user has permitted reproduction of *The Colony* on this family website, but external historical society photographs and archival oral histories remain linked rather than rehosted. Names from imperfect image OCR will not be treated as independently verified identities. Preserve existing archive source data and original research snapshots byte-for-byte. Merge/deployment requires the user's explicit approval.
