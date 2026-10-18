# Phase 17 — A unified, source-first family research workbench

*Research / engineering audit: 18 October 2026. Built from currently preserved records on the site. Draft only.*

## Why this is larger than another casework PR

The family website now has excellent individual sections but still makes a researcher repeat a search across separate systems. The critical problem is **fragmentation of original evidence**:

- The preserved historical research collection contains its own extensive **findings, source register, confidence ratings, access and reuse limitations** (2026-10-14 research snapshot). It must not be dropped or overwritten by recent research.
- The book is a complete authorized **305-page, image-only PDF**, with a limited 35-term automatically detected OCR navigation index. It has not been fully transcribed, spellchecked and manually verified, and the full book does NOT magically become full-text searchable because its page navigation has terms.
- **82 curated photo-bearing pages** are captioned, with 23 exact-ID profile cross-references and **16 unresolved caption/identity questions**. It is misleading to label a machine-detected surname on a different page as an independently verified person photo.
- Individual historical exhibits, the 2026-10-14 research collection, reviewed family-tree relationships, the eight Phase 8 identity cases, phase 16 original-document casework and older early Maine source trails are in different modules.
- Existing Historical Discoveries provided access to research findings and individual cases, but no **one interface** connecting the person, original scanned page, historical claim, research source and uncertainty.

## Complete read-only archival search now implemented

`family_research_index.py` constructs a deterministic, source-preserving indexed set of **ten categories**:

1. **Open identity questions** — all sixteen unplaced book-caption people plus eight individual identity investigations, with original pages and sources.
2. **Relationship evidence** — the exact person-ID-reviewed parent/child and spouse/sibling source notes from Phase 15 and 16; does not call an unreviewed edge proven.
3. **Historical investigations** — original exhibit casework and the new Matthew, Nathaniel and Topsham source dossiers.
4. **Historical research findings** — *all* existing entries from the **preserved 2026-10-14 research collection**, retaining confidence categories (including *Possible lead*, *Conflict* and *Rejected*), associated people and exact uncertainties. These are NOT silently raised to “confirmed.”
5. **Original source register** — *all* registered collection citations, including source-viewed/access status, holding repository and rights warnings. An entry in a source register is not proof that its image was visually examined.
6. **Historical source exhibits** — previously reviewed original source exhibits and their precise historical claims and limitations.
7. **Scanned book photographs** — exactly the 82 authorized, author-captioned photograph-bearing pages, canonical people only by the preexisting exact-ID crosswalk.
8. **Scanned book OCR leads** — one navigational card for each PDF page containing one or more of the **35 indexed OCR words**, never a canonical person ID. Automatically detected words cannot prove identification or kinship.
9. **Historical record trails** — dated Topsham settlement/military lists, James civic records and Mercy/James Henry grave and marriage source leads.
10. **Existing family profiles** — every effective family profile with a link to its original page, not a new automatically verified genealogy.

Every entry has a stable source ID, category, display title, evidence status and limitations, exact person IDs where editorially reviewed, scanned PDF page references when appropriate, direct context links and safe external original-document links. **No migration or modification of old data files was necessary.**

## Visitor interactions (not just another static information page)

`family_research_workbench.py` provides four connected views under **Historical Discoveries → Family Research Workbench**:

- **Explore the archive:** Search across all ten categories using multiple search tokens. Filter by collection and exact relative. All matches are reachable through lightweight pagination, with an option to exclude tentative OCR word hits. Every result has status/limits, original-document links and an exportable source-attributed Markdown research note.
- **Case files:** Direct, shareable links to open a particular disputed person, historical question or relationship; displays the actual case immediately, not hidden behind a tab. Source packet exports include what the evidence does NOT establish, original URL locators and source-page links, rather than fabricated narratives.
- **Cross-search book pages:** Intersect **two** indexed words (or show either) across the same 305-page PDF; navigate direct to the original scan. An intersection does NOT assert both words refer to one person or event. Empty results never imply historical absence because the OCR is deliberately a limited vocabulary.
- **Unresolved research priorities:** Exposes the 16 book-caption identities, the four ancestry bridge dossiers, and additional identity cases in a research task queue. The list is grouped rather than assigned fictitious statistical probabilities.

**Every scanned page** gains a link to the workbench scoped to **that exact PDF page**, so actual photo annotations, still-unidentified people and tentative OCR navigation are kept separate. Every ancestor profile gains a direct exact-ID workbench link. The book's search tab and the Historical Discoveries visitor journey both lead to this interface.

## Security, privacy, rights and historical accuracy

- The workbench runs **behind the existing site password**, not in the public static directory. There is no public family upload/registration endpoint, no new storage, no email access, and no network mutation.
- `case_packet()` produces plain UTF-8 Markdown of *curated reference descriptions and URLs*. It does NOT embed, rehost or copy external historical-society scans.
- All external links are restricted to absolute HTTPS destinations by a separate URL normalizer. Sources with no safe link remain navigable by their internal source-register record.
- The old Boston Tea Party family claim, all protected historic and contemporary addresses, relationships, source scans and approved book rights remain untouched. No new parent/child link is inferred from surname, shared location, OCR coincidence, compiled tree, duplicated printing of the same gravestone or a photo caption.
- An inferred claim is not made “more likely” merely because the same original record was printed by two later compilers.
- Book photo profiles remain **author-attributed**. The Lowell Sr. Harvard 1923 portrait and the Lowell Jr. baby portrait remain distinct.

## Engineering acceptance checks

New `tests/test_phase17_research_workbench.py` verifies:
- Total index has hundreds of cards, unique stable IDs and direct valid routes.
- Complete preserved **2026-10-14 findings and source register** are indexed **one-for-one**, with confidence, research uncertainty, links and access status unchanged.
- All 82 photographs and all 16 unresolved-book cases are reachable, with no fuzzy person-ID matches.
- OCR page cards never include person IDs; all 35 terms remain limited page-navigation leads, not a transcription.
- Book term intersection/union computes exact PDF page sets, and scoped page deep links can access photos, unresolved cases and OCR separately.
- Specific 1749 intention links and archival case packet language retain their source limitations.
- Selecting an exact person filters only editorially linked records, never all surname OCR matches.
- Search and source-packet creation never mutate the effective genealogy, Lyford parentage, or Mercy's corrected unknown parents.

**After merge:** confirm performance and usage on authenticated desktop/iPhone, especially clicking from person → archive → original *The Colony* page → its scoped source records. CI success does not prove pixel-perfect mobile experience.

## Subsequent substantial projects (not included in this PR)

1. **Source transcription and 305-page book audit:** build *verified* page-level transcription carefully, with human-reviewed proof and exact text/source separation. Image-only PDF requires quality-controlled OCR or manual transcription, not blind assumptions. Copyright permission applies to the family website only.
2. **Relationship evidence expansion:** review all remaining hundreds of inherited parent/child/spouse/sibling claims one at a time; prioritize original vital, deed, and probate links along the Marblehead/Topsham/Fox Islands line.
3. **Original archival item acquisition:** inspect original Topsham 1758 lots and 1763 signed petition, Hope/Warren Cobb marriage and 1831 James Henry probate, and source photographs, rather than relying on historical indexes.
4. **Consent-gated family submissions:** relatives can suggest identifications with proof/custody/rights and an approval process. Must be designed against modern personal address exposure and copyrighted source redistribution.

**PR #37 remains draft. No merge, production deployment, unsanctioned email, archive purchase or change to the genealogy graph.**
