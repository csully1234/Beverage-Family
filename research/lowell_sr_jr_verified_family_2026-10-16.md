# The two Lowell Pierson Beveridges — verified direct descendants and the 1954 marriage

Prepared October 16, 2026, for PR #25. **No emails were sent, no releases were deployed, and the existing historical genealogical files were not rewritten.**

## The actual distinction

The website previously included a family-tree profile for **Lowell Pierson Beveridge Sr., born September 19, 1905, died June 18, 1991**, one of Orris Lyford Beverage and Rose Emma Pierson's children. It credited **Lowell P. Beveridge Jr.** as the author of the 2016 family memoir *The Colony*, but had not given that son a separate profile. The two were consequently easy to conflate.

These are **separate father and son**, supported by two highly relevant independent contemporary sources:

1. [Harvard College, Class of 1925, *Thirty-Fifth Anniversary Report* (1960), printed p.20](https://ldsgenealogy.com/MA/books/Harvard-class-of-1925-thirty-fifth-anniversary-report-part-2.htm). The **father** reported marriage to Ida Louisa Gattrell in Newburyport **25 December 1926**, and sons **Lowell Pierson Jr., born April 7, 1930**, Harvard '52, and **Thomas Gattrell, born April 6, 1938**, Harvard '59. The report lists a historical spouse **Hortense Sie** for the elder son. A digitized version of the original 1960 printed volume is at https://archive.org/details/harvardclassof1900unse ; the catalog name is unusual but its digitized text does contain the relevant 1925 class report. Compare the same p.20 at https://ldsgenealogy.com/books2/harvardclassof1900unse_1.pdf . The two URLs are different representations of the **same 1960 book**, not independent eyewitness reports.
2. [Episcopal Diocese of Virginia, 1991 annual journal memorial for the Rev. Lowell P. Beveridge](https://episcopalvirginia.org/wp-content/uploads/2024/04/1991-Diocese_Journal_searchable.pdf). Independent contemporary institutional memorial reports surviving wife **Ida** and sons **Thomas and Lowell Jr.**, confirming the generational distinction.
3. [Lowell 'Pete' Beveridge's own May 23, 2012 oral history](https://s3.amazonaws.com/bhs.assets/bhs_2011.019.032_beveridge-pete_20120523_a.pdf), Brooklyn Historical Society, collection 2011.019.032. The narrator gives his **full name, April 7 1930 birth, Newton MA birthplace** on PDF page 3, independently corresponding to his father's 1960 report. The 2016 book's author byline is **Lowell P. Beveridge Jr.**, not the father (died 1991).

## Four new full-tree profiles

- `ida_louisa_gattrell_beveridge_1901`: spouse of Lowell Sr., mother of Lowell Jr. and Thomas; historical name and relationship in 1960 report and 1991 memorial. Death 1993 comes from a secondary cemetery listing, so original death return remains desirable.
- `lowell_pierson_beveridge_jr_1930`: Lowell's son, author of *The Colony*, interview narrator 'Pete', born 7 Apr 1930.
- `thomas_gattrell_beveridge_1938`: second son, born 6 Apr 1938 per 1960 father-authored biography; corroborated by 1991 memorial.
- `hortense_tee_sie_beveridge_1923`: documented 1954 historical spouse of Pete; public documentary film editor 'Tee' (1923–1993), corroborated by [Smithsonian's original film collection](https://www.si.edu/object/south-africa-uncensored%3Anmaahc_2012.79.1.5.1a) and academic publication on African American film editors.

**Graph linkage:** The four new profiles are **additive** in `data/phase7_people.json`. Pete and Thomas list both Lowell Sr. and Ida as parents; the family graph's reciprocal links then show Lowell Sr.'s wife and children automatically, without editing the checksum-protected original `data/people.json`. Existing 180 original people, earlier four phase4 people, addresses and parentage links remain untouched. New living-status information and private addresses are not inferred.

**Book and portrait disambiguation:** The 2016 book metadata now holds `author_person_id=lowell_pierson_beveridge_jr_1930`; its book reader links directly to the author profile. The Harvard 1923 class portrait at PDF p.246 is linked to the **father** by exact ID, not by a fuzzy string check that also incorrectly attaches it to the son.

## The Google excerpt about banishment: partly true, important errors

The quoted Google excerpt's subject **IS the real Pete Beveridge who wrote the book**, but it compresses a nuanced first-person interview into exaggerated conclusions.

**Directly supported, in Pete's own words (2012 transcript):**
- PDF pp.3–4: summers on the island with his father, seven paternal aunts and uncles, and 16 cousins on jointly held family land; he reported membership in the Harvard Young Progressives and Communist Party as a young adult.
- PDF pp.12–13: he wished to introduce Tee to the North Haven family before the wedding, but his parents **discouraged the visit**; his father's seven siblings wrote critical letters and strongly opposed the interracial relationship. He suggested that shared ownership of the family property complicated these family tensions. His relatives' opposition is his firsthand *recollection of the correspondence*, not a finding that every living descendant would agree with his interpretation.
- PDF pp.14–16: **wedding in January 1954**, NOT 1953, at **St. Philip's Church in Harlem** during Pete's Army leave. Pete directly states his **parents gave the marriage their blessing**; both parents and younger brother Thomas **attended**. His father introduced the officiant Shelton Hale Bishop, who counseled the parents to accept the marriage.
- His parents' initial caution or fear of the older relatives' response **must not** be described as a categorical permanent parental repudiation of Pete. The literal “banished for 20 years” period, or an exact start/end of an exile, is **not established** by the cited 2012 transcript and Harvard report.

**Harvard father-authored report in 1960** says the family sold its North Haven farm in the preceding five years. This is a valuable direct land-history lead, but **does not prove why it was sold or identify the deed or parcel**. It cannot be described as a punishment or as evidence Pete was barred.

## Original documents, photo leads and rights

- The [2012 oral history 34-page transcript](https://s3.amazonaws.com/bhs.assets/bhs_2011.019.032_beveridge-pete_20120523_a.pdf) is **expressly for research purposes only**. Link it to people, events and stories; no verbatim transcript or embedded copied audio is stored on the site.
- Pete's oral history refers to letters from his father's seven siblings objecting to the wedding, which Pete reported **keeping**. These may be unique firsthand family documents, but have not been located, digitized, permissioned or individually authenticated. Do **not** name any particular aunt or uncle as letter author without seeing the letter.
- The oral history is richer than a simple ancestry link: it relates North Haven summers and communal property to 20th-century family cultural change and to the real filmmaker Tee Beveridge. An archive source viewer links the Smithsonian record and transcript without violating reuse rights.
- The 1960 Harvard source's claimed sold farm needs historical deeds (circa 1955–1960) before a family-property polygon, acreage or exact parcel is created.

## Still unresolved

1. The 1954 original wedding certificate and exact January day have not been located. The year and month are supported by the groom's firsthand recorded recollection.
2. The precise estate/deed of the sold North Haven farm 1955–1960; this matters for the family map.
3. The alleged exactly “20-year banishment,” and actual details of any return or reconciliation. The firsthand interview confirms family opposition but not an exile period.
4. A biographical distinction between Tee's career, Pete's political activities, and unsupported attributed views of others.
5. Additional historical family relatives from the 2016 book are not added solely on a mention: a traceable named source and relationship is required. Original identity cases for Frank and Nathaniel remain separate within the existing draft PR.

**Changes:** `data/phase7_people.json`, `data/phase7_events.json`, `family_data.py`, `family_books.py`, `data/book_sources.json`, `data/evidence_exhibits.json`, a sourced visitor story, and regression tests. No outbound correspondence or repository merge.
