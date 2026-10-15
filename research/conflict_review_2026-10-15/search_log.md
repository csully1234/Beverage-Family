# Search and access log

Review date: 15 October 2026 (UTC). This is a targeted conflict review. The table records the investigation scope, source examinations and access outcomes; it is not a verbatim export of every search-engine request. No negative search result establishes that a historical record does not exist.

| Research IDs | Name / record routes examined | Result and limitation |
|---|---|---|
| BF-R005 | James Beveridge/Beveredge, Sarah Holman, Mary White, Marblehead marriages; Susannah/Mary/Jane sisters and Essex Antiquarian references | Downloaded and inspected 1904 Marblehead marriage page 34. Reexamined Essex Antiquarian IX p. 91. Birth dates and maternity not established; 1789 deed lacks verified book/page. User-tree Sarah born 1706 not adopted. |
| BF-R008 | Diana/Daggett/Doggett, Edgartown, Benjamin Jr. and Elizabeth, Nathaniel Beverage | Downloaded Edgartown 1906 vital-record edition and inspected p. 29 and abbreviation p. 5. Reexamined Doggett p. 113. Both describe baptism; original church register and birth entry not seen. |
| BF-R011 | Thomas Beverage, James and associates, 1837 deed, Woodruff Josiah biography footnotes | Edited footnote supplies DGS 8296915 p. 387 image 207/601. Film/catalog routes did not yield an accessible original. Date and legal capacity remain unverified. Related Trinity Boston marriage target: DGS 8130800 image 459/798. |
| BF-R012, BF-R014 | Sarah Beverage/Kent/Sally; Benjamin Kent senior/junior; Kent and Fuller cemeteries; Vinalhaven vital pages | Reexamined cemetery transcriptions and Woodruff Benjamin narrative/notes. DGS 7596929 p. 389 image 215/837 and marriage p. 431 image 236/837 remain retrieval targets. Duplicate cemetery lines are not independent evidence. |
| BF-R032 | Eliot/Elliot P. Beverage/Beveridge; Harvard education; North Haven/Dorchester; IsleBuilt | Read NHHS interpretation and 1934 Crimson article. Educational identity strengthened; locality in newspaper is residence, not birth. Derivative September 15, 1908 claim not adopted. |
| BF-R039 | Lowell Pierson/P. Beveridge; Union, Columbia, Harvard; Dorchester/Boston/North Haven | Read 1948 institutional register OCR p. xli; compared 1991 diocesan memorial. Age arithmetic separately resolved. Item page accessible through web retrieval; direct host HEAD and image GET returned 403. No assertion that the original birth entry or readable register image was examined. |
| BF-R046 | Charles H./Howard/Hanson Beverage; Annie/Anne Leadbetter; Benjamin and Amelia household | Reexamined Seaview pp. 2–4; public FamilySearch Theodore page exposes Hanson and household/cemetery leads. Linked Charles LHFY-NWK page requires JavaScript; original vital and census images not examined. No name/year replacement. |
| BF-R047 | Benjamin C./Crabtree Beverage, Amelia, December 1875 | Seaview transcription contains apparent birth-column duplication and December 17, competing with stored December 7. FamilySearch L3F4-5MG is only a tree target. Original stone/death entry unavailable. |
| BF-R048 | Sarah/Sally Beverage, November 1844, Vinalhaven/Seaview | Reexamined Seaview age/date. Genealogy of New England search lead repeats November 28, but page returned 502; snippet not proof. Stone and death entry needed. |
| BF-R049 | Amelia Beverage, Norwood, Hannah Grant, Benjamin Crabtree, nine-child household | Compared both exact baseline profiles and date-precision metadata; FamilySearch LC2F-GSH and Theodore MF45-BHM are leads. No original naming parents plus spouse obtained; no merge. January 1 is already a year-only placeholder. |

## Second pass: access routes and overlooked source dependence

- Separated shared church/town origins from independent witnesses; the two marriage/baptism publications cannot be counted as independent proof of every assertion.
- Separated the Lowell memorial's incorrect age from birthplace. Located a pre-obituary institutional register; did not treat “Boston native” as a birth record.
- Rechecked original versus interpreted date fields, senior/junior identity, the two Sarah generations, the Amelia placeholder, and Seaview column defects.
- Pursued an alternative readable image for the Columbia register; direct image GET returned 403. Logged the limitation rather than upgrading OCR to visual inspection.
- Rechecked the NHHS cemetery/access guide and institutional contact page.
- Searched official archive routes using these exact continued-pass queries:
  - `site.mass.gov archives vital records 1841 1930 birth research copies fee`
  - `site.library.harvard.edu alumni records biographical files Harvard University Archives research`
  - `site.vinalhaven.org town clerk genealogy vital records`
  - `site.northhavenmaine.org town clerk vital records genealogy`
  - `site.sec.state.ma.us archives "digital images" "five" "1935"`
  - `site.library.harvard.edu "Quinquennial" "Biographical"`
- Opened Massachusetts Archives vital-record and reference-services guidance, Harvard University Archives, Vinalhaven's official office page, and Maine's North Haven clerk directory. Harvard's detailed biographical guide returned HTTP 429; its file-description search result remains a retrieval lead, not an examined file.

## Access barriers and next action

1. **FamilySearch DGS 8296915:** deed image not accessible. Use the exact cited image through authorized access or ask the relevant registry after checking the film title/volume. Do not assign a county book number from guesswork.
2. **FamilySearch DGS 7596929:** vital image not accessible. Use authorized access or Vinalhaven clerk with exact pages/images.
3. **FamilySearch tree-linked records:** public tree information read, original images not obtained. Request the census/vital source itself; tree IDs are not record citations.
4. **Original cemetery images:** only NHHS transcriptions examined in this pass. Request stone photographs or worksheets; retain apparent transcription defects visibly.
5. **Columbia scan:** OCR item page read, scan download blocked. Seek the page image from Columbia to inspect it, plus the birth record independently.
6. **Crimson / Columbia host HEAD:** HTTP 403 in final transport checks despite readable web-tool pages. These are client access differences, not proof that the source no longer exists.
7. **Harvard guide:** 429 on opening; use the verified archive contact/copy-request route. Do not repeatedly retry the blocked guide.

See [link_checks.json](link_checks.json) for 17 direct transport checks (15 HTTP 200, 2 HTTP 403). The check uses HEAD and does not claim to validate the content of an original record. Verified institutional request guidance and public contacts are linked in [retrieval_requests.md](retrieval_requests.md). No log or screenshot contains newly discovered private information about a living relative.
