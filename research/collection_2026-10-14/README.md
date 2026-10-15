# Research package integration

This directory preserves the five supplied research files without changing their
bytes. The site reads an extracted collection from
`data/collections/2026-10-14.json`. It displays the original confidence ratings,
source-viewing status and family-review status; inclusion is not verification.

## Coverage and placement

| Material | On-site location |
| --- | --- |
| 57 findings, including 11 conflicts | Research Collection; contextual profile, place and event links; global search |
| 163 source entries | Source Archive → Research source register; individual `SRC` links |
| 33 retrieval targets | Research Collection → Retrieval plan; related findings |
| 29 master-workbook sheets and the candidate review guide | Research Collection → Inventories; searchable tables and filtered CSV downloads |
| Complete narrative dossier, including tables and bibliography | Research Collection → Reports → Read the dossier |
| Five original XLSX / DOCX files | Research Collection → Reports → Download |
| Candidate people and unresolved relationships | Inventories, with their original candidate labels; no inferred tree links |
| Deed fields, photographs, map and object identifiers | Finding detail pages and Properties and Deeds / Images and Maps inventories |

There are 18 strong new discoveries, 5 corroborating source entries, 23 probable
or possible leads, and 11 conflicts in the supplied package. Of 163 registered
sources, 56 were examined as records, transcriptions or catalogs; the register is
not a claim that 163 original documents were read. Every source class remains
partial. The 33 retrieval targets include online material not yet obtained as
well as offline, blocked and restricted records.

## Provenance and safeguards

- Baseline commit: `4e3d4860d3c8d9ae9cbcb19567dafa17e1a93db1`.
- `baseline_hashes.json` records the Git bytes of the nine existing data files.
  All are unchanged by this integration. The research-stage download copies had
  one additional trailing newline; their parsed JSON is identical.
- SHA-256 hashes of the five original reports are embedded in the collection.
- `navigation.json` contains editorial titles and explicit browsing links to
  existing profiles, events and places. These links are not genealogy assertions.
- No candidate people are merged into existing profiles. The two Amelia profiles,
  two Sarah/Kent hypotheses and unidentified James entries stay distinct.
- Registry dates remain registration dates; a diary's activity at a named point
  does not become proof of ownership. No parcel coordinates are invented.
- No newly researched living-person private information is added. The workbook
  inventories retain existing baseline fields, as authorized. The collection
  validator rejects new contextual links to possibly living profiles.
- Photographs and films are cataloged and linked. Rights statements are shown;
  no unlicensed archive images or films are copied into the site.
- Original report statements that no repository changes were made describe the
  completed research phase. This subsequent integration is a draft-PR proposal.

## Updating and checking

Run `python tools/import_research_package.py research/collection_2026-10-14` to
reproduce the extracted collection. The importer reads row 4 as the header in
these specific workbooks and preserves every table cell. It extracts dossier
paragraphs, hyperlinks and tables for the on-site reader. No runtime spreadsheet
or Word dependency is required.

Run `python validate_data.py`, `python -m unittest discover -s tests -v`, and
`npm test`. Validation checks source and subject references, confidence labels,
privacy boundaries, report integrity and baseline preservation. Regression tests
compare the extracted tables and findings against the supplied workbook cells.
The original genealogical and JavaScript map tests continue to apply.

Later, a separately reviewed change to baseline genealogy must explicitly update
the preservation manifest and document the family decision. Do not use the
importer or update hashes to conceal a changed historical assertion. Human review
statuses and unresolved identities remain open in this draft.
