> **October 17 integration notice:** PR #25 was merged before PR #26. Its four phase7 Lowell-family IDs are authoritative; this PR retains only two unique new collateral profiles (Lyford and Dorothy) and remaps book-photo profile links to the existing phase7 IDs. Earlier six-profile descriptions below document the pre-reconciliation draft, not final installed identities.

# Phase 6 — Lowell family, Pete's testimony and book-name audit

Prepared October 16, 2026. This is a **draft PR**. No email, purchase, merge, deployment, or republication of restricted interview pages.

## Core genealogy correction (verified)
- Lowell Pierson Beveridge Sr. (1905–1991) already exists as `lowell_beveridge_1905`, descended from Orris Lyford Beverage and Rose Emma Pierson.
- His **1991 Washington Post obituary** names Ida Gattrell Beveridge as his wife, Lowell P. Beveridge Jr. and Thomas Beveridge as two sons, and Lyford Beveridge of Rockland as his brother. This is contemporary independent supporting evidence for the central relationships. https://www.washingtonpost.com/archive/local/1991/06/20/the-rev-lowell-beveridge-professor-of-music-dies/b9e898f1-334c-44d7-bbdd-66354b1bbe83/
- Pete himself confirms `My real name is Lowell Pierson Beveridge, Jr.` at p. 3 of a **May 23, 2012** 34-page Brooklyn Historical Society interview (catalog 2011.019.032), describes his father, his younger brother and his marriage. https://s3.amazonaws.com/bhs.assets/bhs_2011.019.032_beveridge-pete_20120523_a.pdf
- **Five new sourced profiles plus an additional documented named wife**: Ida, Lowell Jr. (Pete), Thomas, Hortense, Lyford, and Dorothy 'Jimmy' Gattrell Beverage. Existing Lowell Sr. and Eliot have spouse/child/sibling links updated *only in the additive Phase 6 overlay*. The original protected `data/people.json` and `data/research_people.json` are untouched.
- The obituary calls Lyford Lowell Sr.'s brother but does not explicitly prove which parents the siblings shared. Lyford is included as a sibling node, **without assigning Orris or Rose as parents**. This intentionally leaves an isolated/partially connected branch pending proof.
- The book page 257 and Calderwood diary identify Eliot's spouse Dorothy. Her childhood, birth, death and marriage-register specifics are not established. She has no invented dates/parents or private address.

## First-person 2012 interview; quotation/interpretation precautions
- Pete reports that he and Hortense 'Tee' Sie married in **January 1954 at St Philip's Church in Harlem**, not 1953; an original church entry could fix the exact day.
- He recalls some extended relatives objecting to the interracial marriage and says he stayed away from North Haven for approximately **20 years**, but he also describes his own parents ultimately supporting the marriage and later family reconciliation. Treat the duration and family dynamics as **attributed participant testimony**, not a legal banishment, collective opinion of all relatives or proven objective motive of every person.
- His political involvement is also explicitly described **by Pete** in the May 2012 interview; do not ascribe the entire estrangement solely to politics or label people with politics based on a Google/AI excerpt.
- Research-only archive terms at pp. 1–2 of the transcript expressly restrict republication without rights clearance. The website **links to the institution's PDF**, not a copied transcript or image.
- Hortense's professional film-editing work and birth/death years are independently documented by the Smithsonian, including **Ages of Time** (1959, NMAAHC collection). https://nmaahc.si.edu/object/nmaahc_2012.79.1.3.1a
- Two newly attributed timeline events record January 1954 marriage and May 23, 2012 interview. No unverified criminal, defamatory or blanket family-wide allegations.

## 2016 book audit — important scope warning

**The complete 305-page PDF could not be acquired for a fresh full-text page-by-page audit during this run.** Its existing *82 individually cataloged historical-photograph page* index (`data/colony_photo_captions.json`) and `data/book_sources.json` were inspected and cross-matched with the effective tree. That produces:
- **23** explicit person-ID associations to captioned photo pages, including Lowell Sr., Pete, Ida, Norwood, Lyford, Eliot, Rose, Orris, Olive, Mary, Jemima, Harriet, etc.
- **16** documented missing/ambiguous identity questions, including Hanson vs Dana Hanson, Albion Pierson (Rose's father), Jesse Hart, Vernon, Florence Budlong, Priscilla, Ruth and Ann, Helen's Uncle Bob Barclay, and figures in the 1918 and 1936 large group captions.
- **A two-way viewer link:** each matched person now has original book page links on their profile, and captioned gallery photographs display links back to their matching tree profiles. The Family Books page includes a browsable unresolved-name audit. These page references only establish the *book's* attribution; they are not independent civil proof.
- Book-only married surnames were added as carefully labeled aliases for Mary 'Mae' Beverage Bemis, Jemima 'Mima' Beverage Carver and Harriet Beverage Green. No unknown husband was created.
- Dorothy was added as spouse to Eliot; independently accessible diary plus caption support the relationship, but source and surname uncertainties remain identified. No automatic `Hanson = Dana Hanson` or `Hattie = Harriet` merge.
- Florence Budlong is described by the memoir as Olive's life partner. The relationship has **not** been turned into the site's `spouses` edge, which currently displays as a legal-marriage relationship and would inaccurately imply a marriage. This needs a richer partner relationship type rather than deleting or misconstruing the important history.
- Names found only as historical cottage owners are kept as context pending demonstrable kinship.
- **Do not describe this as all people in the entire 305-page book being reviewed**: the indexed 82 pages do not include every named chapter person or the full row-by-row names in captions on pages 174, 194, 198, 223, 229, 253. The remaining full-book review can resume when the complete PDF is made accessible to programmatic or paginated reading.

## Parallel historical cases (not manufactured outcomes)
- Frank and May: two dated anniversary references support an **October 15, 1887** marriage hypothesis, but original civil/church return and identity-specific proof for the existing Frank born 1861 remain outstanding. Historical society correspondence is drafted but **not sent**.
- Nathaniel/Matthew: compiled parentage vs Eaton's nephew wording is still unresolved, awaiting 1838 marriage, probate and baptism originals. Neither father-child edge is fabricated.
- North Haven deeds: 1883 Beach Bridge contract and 1888 dam acquisition are linked in PR #24 evidence explorer. Exact lot/acreage still requires deed originals; no fabricated property polygons.
- James/Jean: two transcriptions of one 1749 intention are not independent proofs of an actual wedding.

## Code, tests and safety

- `data/phase6_people.json` contains the six newly identified profiles and historical patches; `data/phase6_events.json` contains two firsthand-sourced dated events.
- `data/colony_people_crosswalk.json` is explicitly *caption-index-only*, including unresolved names with book page references.
- `family_books.py` indexes individuals by **stable person ID**, removing the old fuzzy first-name logic that could confuse Lowell Sr. and Jr. on the book page 246; book page links are on person profiles and the Family Books index.
- `colony_photos.py` adds return links from book-photo cards to individual people where identifications are documented, labeling candidate identities.
- `tests/test_phase6_book_tree_audit.py` tests separate father/son IDs, parent/spouse/sibling edges, page provenance, unresolved identity boundaries, and compatibility with existing tree model.
- The October 2026 imported research snapshot's hashes and the historical residence/privacy protections remain unchanged. Users must approve any external email, merge, and deployment.

## Next phase of the exhaustive book audit

To achieve the user's goal of **every verifiable named family member in the 305-page book**: obtain a processable copy of the authorized original PDF (it is in the repository but the GitHub connector does not support large binary download); enumerate all printed proper-name passages including the 1918/1936 photograph captions, check each against the effective profile index and original corroborating sources, mark exact/uncertain identities, review modern or living people's privacy, and add only defensible tree edges in further versioned overlays.
