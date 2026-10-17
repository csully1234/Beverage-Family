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

## Full-volume scan indexing completed, with appendix-specific findings

**Actual processing:** All **305 image-only PDF pages** of the authorized copy were processed in a **single OCR research pass**. The public navigation JSON `data/colony_ocr_navigation_index.json` contains 35 selected names/topics with candidate source-page numbers, including appendix pages 287–305. This is **not** a fully checked transcription or exhaustive identification of all individuals named in the book. False positives, false negatives and erroneous OCR dates are possible. Visitors must check original page images. The OCR text itself is not rehosted as independent history.

A targeted **visual review of the original scans** at PDF pp. 289, 296–302 has verified that the *printed book* contains these claims, without thereby independently verifying their underlying vital records:

| Printed book passage | Reported name or relationship | Current editorial disposition |
|---|---|---|
| PDF p. 297 | Florence **Merrill** Budlong described as Olive Amelia Beveridge's **lifetime partner**; Newton institutional rolls also associate the two | Published memoir attribution + 1941/1947 address corroboration; typed non-marital association shown on Olive's profile; **no legal spouse edge** |
| PDF pp. 297, 300 | Lyford **Pierson** Beveridge; wife Ruth **Bingham Reynolds**; child Ann **Morrison Beveridge** | Book's compiled Orris/Rose descendants; independently confirm the 1991 obituary's Lyford identity before adding parentage or dates |
| PDF pp. 298, 301 | Arnold Pierson Beveridge's wife **Marion Priscilla Delano** | Sourced name lead; original 1926 marriage record needed |
| PDF pp. 298, 302 | Eliot Pierson Beveridge's wife **Elizabeth Dorothy Gattrell** | Alternate full name noted as book-attributed lead on Dorothy's existing profile; avoid a duplicate person |
| PDF pp. 298, 302 | **Vernon Linwood Beverage**, wife Nellie **Marion Ames**, under Charles H. Beverage/Annie Ursula Leadbetter grouping | Published genealogical family grouping, not independently verified unique vital identity |
| PDF pp. 297, 300 | **Robert William Thomas Barclay** in Helen's branch | Published family-book expansion; compare original marriage and census before attaching |
| PDF pp. 289, 296–297 | **Harriet N. Beverage** / Daniel A. Green, plus Mary E. Beverage / Lamont E. Bemis | Family book names are not original marriage certificates; preserve unverified identity boundary |
| PDF p. 296 | Rose Emma Pierson attributed to Albion Pierson and Olive F. Hart | Original Rose vital/baptism and parents' marriage remain needed |
| PDF p. 301 | Pete and Hortense marriage appears with a specific January 1954 date | Treat as family-book assertion only; no exact-date upgrade without parish marriage register |

**Why the appendix matters:** the existing 82-photo catalog missed systematically printed descendant lists. We have now linked the relevant appendix pages to seven of the 16 unresolved identity inquiries and left all 16 visible until original corroboration. Search-index page hits remain detached from person IDs to prevent accidental conflations.

## Research next-record acquisition (no contact or purchases made)

1. **Massachusetts/New York 1926 marriage original:** Arnold Pierson Beveridge and Marion Priscilla Delano; compare actual registers/filing jurisdiction against family's compiled 1926 wedding assertion.
2. **1934 Eliot–Dorothy original marriage:** claimed Elizabeth Dorothy Gattrell from the book; check exact legal name, place, parents.
3. **Lyford original birth and death records:** identity-specific evidence for Lyford Pierson Beveridge vs 1991 obituary's Lyford brother, and Ruth Bingham Reynolds / Ann Morrison Beveridge original records before father/mother links.
4. **Vernon and Nellie household:** original 1890 birth, 1915 marriage, censuses and Charles/Annie parental proof.
5. **Albion Pierson and Rose:** original baptism/vital or parent's marriage, not repeat memorial/appendix wording.
6. **Nathaniel–Matthew and earlier 1749/Topsham leads:** continue probate, parish and land chain verification; no Scottish migration connection asserted yet.

No emails sent. New archived source-image scans from other institutions were not copied. User's historical residence assertions and Boston Tea Party statement remain untouched.
