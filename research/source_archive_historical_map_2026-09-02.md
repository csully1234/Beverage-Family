# Source Archive + Historical Map MVP

Implementation date: September 2, 2026. Base: current merged `main`, commit `73ba56a` (PR #7). Branch: `research/source-archive-historical-map`.

## Scope and result

The archive now has normalized bibliographic records, public places, and cited place assertions. The Streamlit site exposes a historical map, place records, source records, and links from existing profiles and timeline cards. All prior data files are retained byte for byte.

| Measure | Before | After |
| --- | ---: | ---: |
| Effective profiles | 180 | 180 |
| Effective timeline events | 127 | 127 |
| Research notes | 16 | 16 |
| Normalized places | 0 | 21 |
| Normalized source records | 0 | 28 |
| Person/place assertions | 0 | 36 |
| Distinct person/place pairs | 0 | 31 |
| Historical people with map assertions | 0 | 20 |
| Event/place assertions | 0 | 24 |
| Distinct timeline events with map assertions | 0 | 19 |

The source count includes 21 historical evidence items and 7 geographic/context references. Multiple assertions for one person/place preserve distinct roles and dates rather than collapsing them into an ambiguous single connection.

## Data structures

`data/archive_sources.json` contains the requested ID, title, short title, document date/precision, source type, repository, collection, URL, citation, excerpt, summary, people/place/event IDs, evidence level, notes, conflicts and access date. `provenance` distinguishes citations imported from merged research from geographic/context references reviewed in this phase. Excerpts are null where no checked transcription is supplied; summaries are not passed off as quotations. Existing inline citations and legacy strings remain unchanged and usable.

`data/places.json` contains stable IDs, alternate names, place type, latitude/longitude, parent place, historical notes, optional validity dates, confidence and normalized source IDs. Additional fields explicitly record public-place status, coordinate precision, coordinate source, and derivation notes. Coordinates may be paired nulls for a future unlocated record. Modern representative points do not define historical jurisdictions. Current records leave place validity dates null rather than inventing establishment/closure dates.

`data/place_links.json` contains one assertion per subject/place/role/date interval. Fields: `id`, `subject_type` (`person` or `event`), `subject_id`, `place_id`, `relation`, `category`, `date_from`, `date_to`, `date_precision`, `source_ids`, `summary`, `evidence_level`, `notes`. Person and event IDs resolve against the effective overlay-loaded archive. A source must identify the linked subject and place in its backlink fields; a place must list that supporting source.

`schemas/archive.schema.json` is JSON Schema draft 2020-12. All three arrays have required fields, types, vocabularies and unique reference arrays. `archive_validation.py` additionally checks IDs, referential integrity, dates, place hierarchy cycles, URL schemes, evidence strength, coordinate provenance, and historical-person privacy. Missing optional archive arrays still permit the pre-existing site to run. Malformed arrays fail visibly rather than silently dropping records.

`archive.py` provides `ArchiveIndex`, inverse source/place/subject lookups, time-overlap semantics, stable application URLs, and the map's explicit public projection. This stays independent of Streamlit and Leaflet, allowing future place pages, map layers, exports or another frontend to use the same model.

## Linking and evidence rules

- A direct person/place assertion requires its own documentary basis. It is never manufactured from surname, residence text, modern geocoding, or every place mentioned in a participant's event.
- The 1808 memorial links the event to Vinalhaven, Castine and historic Buckstown (modern Bucksport). John Beverage has a direct connection to the petitioning community, Vinalhaven; no personal visit to either court town is asserted.
- The 1819 manuscript link identifies Vinalhaven as its subject. The catalog does not establish an exact writing room or property.
- The 1848 bridge is an authorization. The law's approval date, August 8, is recorded on the source; the existing timeline's year-only date is retained. Its marker represents Pulpit Harbor, not a surveyed bridge site. Neither completion nor modern parcel ownership is asserted.
- Early Maine legislative service links to the represented Vinalhaven community. Separate event-context assertions place the seat of government at Portland, backed by the legislature's State House history. There is no modern Augusta pin substituted for the early capital.
- Colby/Hallowell are city-level education and career links. A present-day Colby campus pin would misleadingly imply that Orris attended there, so no campus building is mapped.
- Guatemala is a country-level mission connection, 1953–1972. No Guatemala City or mission-station location is invented.
- New York is Samuel's documented departure city. No embarkation pier, military unit position, or reconstructed route is supplied.
- Fuller Cemetery associations are explicitly **corroboration**, drawn from the already merged compiled index. They do not establish relationships, burial dates, causes of death, or exact graves.
- `evidence_level` describes the limited assertion/summary being used, not a blanket certification of everything in an obituary or historical publication. The original citations retain their tier labels.

## Map architecture and user experience

New routes follow the existing Streamlit query convention: `?page=map`, `?page=places`, `?page=archive`. Deep links select `person`, `event`, `place`, or `source`; the family-password gate remains in front of all routes.

`historical_map.py` renders a self-contained HTML document from `ArchiveIndex.map_payload()`. `static/historical_map.js`, `.css` and `.html` provide the reusable UI, with locally vendored Leaflet 1.9.4. Upstream JS/CSS bytes were checked against the official published SHA-256 hashes, and the license is included. Node/jsdom are development-test dependencies only; production remains Python/Streamlit.

The first map opens on Penobscot Bay. It offers clickable, keyboard-focusable markers and an equivalent place list, a detail panel with cited assertions, person selection, event jumps, category filtering, inclusive year ranges, and an explicit undated toggle. Selecting an event resets conflicting filters and fits all of its locations. Selecting a person shows only supported personal places and associated events at those places. Broad country/town points have conservative focus zooms. Reset, fit-results, and Penobscot Bay controls keep navigation recoverable. Layouts adapt to a narrow viewport; the enclosing Streamlit iframe scrolls for longer mobile content.

The map detail follows the active filters; the linked place record exposes the complete reviewed connection set. Source/profile/place links open in a new tab. Existing person Places/Sources tabs and timeline cards now link to the normalized records. The legacy Sources & Method page is preserved.

OpenStreetMap supplies only the live background. Browser-default caching applies; there is no prefetch, tile export, geocoder, user-location request, or API key. Tile requests use an origin-only referrer, so profile query parameters are not sent. Visible attribution remains on the map. On missing tiles, the markers, list, filters, and historical records remain available with an explanatory notice; a library failure also leaves list/detail navigation usable. Live basemaps are best effort, not a promised offline map.

## Seeded places

| ID | Place | Geographic precision | Person assertions | Event assertions |
| --- | --- | --- | ---: | ---: |
| `north_haven_me` | North Haven, Maine | municipality | 4 | 4 |
| `vinalhaven_me` | Vinalhaven, Maine | municipality | 7 | 7 |
| `pulpit_harbor_me` | Pulpit Harbor | harbor | 3 | 2 |
| `fuller_cemetery_me` | Fuller Cemetery | approximate_site | 3 | 0 |
| `topsham_me` | Topsham, Maine | municipality | 1 | 1 |
| `waterville_me` | Waterville / Colby, Maine | municipality | 1 | 1 |
| `hallowell_me` | Hallowell, Maine | municipality | 1 | 1 |
| `orono_me` | Orono / University of Maine | municipality | 1 | 1 |
| `rockland_me` | Rockland, Maine | municipality | 1 | 0 |
| `camden_me` | Camden, Maine | municipality | 2 | 0 |
| `hope_me` | Hope, Maine | municipality | 2 | 0 |
| `union_me` | Union, Maine | municipality | 2 | 0 |
| `waldoboro_me` | Waldoboro, Maine | municipality | 1 | 0 |
| `castine_me` | Castine, Maine | municipality | 0 | 1 |
| `bucksport_me` | Bucksport / historic Buckstown, Maine | municipality | 0 | 1 |
| `portland_me` | Portland, Maine | municipality | 0 | 2 |
| `marblehead_ma` | Marblehead, Massachusetts | municipality | 2 | 1 |
| `new_york_ny` | New York City, New York | municipality | 1 | 1 |
| `dallas_tx` | Dallas, Texas | municipality | 2 | 0 |
| `shenandoah_pa` | Shenandoah, Pennsylvania | municipality | 1 | 0 |
| `guatemala` | Guatemala | country | 1 | 1 |

Municipality coordinates were read from the 2025 Census national county-subdivision/place Gazetteer files, matched by state and exact municipality name, rounded, and accompanied by the Census GEOID. The file URLs are retained in the geographic source record. Pulpit Harbor uses NOAA station 8414888's harbor reference, not the proposed bridge endpoints. Fuller uses a rounded compiled cemetery point with medium confidence. Guatemala uses a published country-level reference. Town confidence is confidence in the place identification/modern reference, not survey accuracy for any historical event.

## Seeded sources

| ID | Source | Type | Evidence use |
| --- | --- | --- | --- |
| `src_vinalhaven_officers` | [Vinalhaven Town Officers, 1790–1889](https://archives.mainegenealogy.net/2007/01/vinalhaven-town-officers-1790-1889.html) | town_history | strongly_supported |
| `src_court_memorial_1808` | [Journal of the House of Representatives of the Commonwealth of Massachusetts, 1808](https://upload.wikimedia.org/wikipedia/commons/6/69/Journal_of_the_House_of_Representatives_of_the_Commonwealth_of_Massachusetts._%28IA_journalofhouseof1808mass%29.pdf) | legislative_journal | verified |
| `src_vinalhaven_manuscript_1819` | [History of Vinalhaven, 1819](https://www.mainememory.net/record/20801) | manuscript | verified |
| `src_constitution_1819` | [Constitution of Maine with 1819 Convention delegate list](https://legislature.maine.gov/uploads/originals/const1820.pdf) | government_record | verified |
| `src_maine_house_1823` | [Civil Government of Maine, 1823](https://lldc.mainelegislature.org/Open/Laws/1823/Laws1823res_s0189-0195_CivGov.pdf) | legislative_journal | verified |
| `src_maine_payroll_1828` | [Pay Roll — House, 1828](https://lldc.mainelegislature.org/Open/Laws/1828/1828_RES_c064.pdf) | government_record | verified |
| `src_bridge_act_1848` | [An act to establish the North Haven Bridge Company, Chapter 154](https://lldc.mainelegislature.org/Open/Laws/1848/1848_PS_c154.pdf) | government_record | verified |
| `src_ieee_harold` | [Harold H. Beverage](https://ethw.org/Harold_H._Beverage) | institutional_biography | strongly_supported |
| `src_topsham_history` | [History of Brunswick, Topsham, and Harpswell, Maine](https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-18.htm) | town_history | strongly_supported |
| `src_colby_catalogue_1887` | [Second General Catalogue of the Officers and Graduates of Colby University, 1820–1887](https://upload.wikimedia.org/wikipedia/commons/5/5a/Second_general_catalogue_of_the_officers_and_graduates_of_Colby_University%2C_Waterville%2C_Maine%2C_1820-1887_%28IA_secondgeneralcat01colb%29.pdf) | catalog | strongly_supported |
| `src_congress_petition_1912` | [Congressional Record — House, 1912](https://www.govinfo.gov/content/pkg/GPO-CRECB-1912-pt3-v48/pdf/GPO-CRECB-1912-pt3-v48-11.pdf) | legislative_journal | verified |
| `src_pulpit_auction_1927` | [Public Auction — Sands H. Witherspoon homestead, Pulpit Harbor](https://upload.wikimedia.org/wikipedia/commons/2/2a/Courier_Gazette_July_30_1927.pdf) | newspaper | verified |
| `src_water_bonds_1926` | [North Haven Water Loan Bonds notice](https://files01.core.ac.uk/download/pdf/270234656.pdf) | newspaper | verified |
| `src_samuel_obituary` | [Samuel Hiram Beverage obituary](https://www.tributearchive.com/obituaries/990096/Samuel-Hiram-Beverage) | obituary | strongly_supported |
| `src_john_miller_obituary` | [John Miller Beverage obituary](https://obituaries.tahlequahdailypress.com/obituary/john-beverage-744038102) | obituary | strongly_supported |
| `src_hartley_obituary` | [Hartley George Beverage, Sr. obituary](https://www.penbaypilot.com/article/hartley-george-beverage-sr-obituary/102205) | obituary | strongly_supported |
| `src_florence_obituary` | [Florence Pearse Beverage obituary](https://www.penbaypilot.com/article/florence-pearse-beverage-obituary/138141) | obituary | strongly_supported |
| `src_estelle_obituary` | [Estelle Beverage Libby obituary](https://www.penbaypilot.com/article/estelle-beverage-libby-obituary/271766) | obituary | strongly_supported |
| `src_petronele_notice_1979` | [Mirė Petronėlė Jurgeliūtė-Beverage](https://www.spauda2.org/vienybe/archive/1979/1979-04-27-VIENYBE.pdf) | newspaper | strongly_supported |
| `src_marblehead_vitals` | [Vital Records of Marblehead, Massachusetts, to the End of the Year 1849](https://ldsgenealogy.com/MA/books/Vital-records-of-Marblehead-Massachusetts-to-the-end-of-the-year-1849-part-4.htm) | vital_record | verified |
| `src_fuller_index` | [Fuller Cemetery, North Haven](https://www.familysearch.org/en/cemeteries/sites/46772/fuller-cemetery?showMap=false) | cemetery_index | corroboration |
| `src_census_coordinates` | [2025 U.S. Census Gazetteer Files](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html) | geographic_reference | verified |
| `src_noaa_pulpit` | [NOAA tide station 8414888 — Pulpit Harbor](https://tidesandcurrents.noaa.gov/benchmarks/8414888.html) | geographic_reference | verified |
| `src_fuller_location` | [Fuller Cemetery location](https://www.findagrave.com/cemetery/89947/fuller-cemetery) | geographic_reference | corroboration |
| `src_guatemala_coordinates` | [Guatemala geographic overview](https://iri.columbia.edu/~idb_enso/luisbrito/Geography.html) | geographic_reference | strongly_supported |
| `src_north_haven_history` | [About North Haven](https://www.northhavenmaine.org/about_north_haven.php) | institutional_history | strongly_supported |
| `src_maine_capital_history` | [History of the Maine State House](https://legislature.maine.gov/general/history-of-the-state-house/9137) | institutional_history | strongly_supported |
| `src_bucksport_name_history` | [Bucksport public library history](https://www.bucksportmaine.gov/community/public_library/index.php) | institutional_history | strongly_supported |

## Research and normalization performed

This is a source-archive implementation phase built primarily from the already merged research, not a claim to have completed another exhaustive genealogy investigation. Existing sources were normalized selectively. The manuscript catalog, bridge statute, IEEE biography, selected occupational/missionary/military obituaries, Census files, NOAA reference and municipal geographic context were rechecked where needed. Original access dates are retained for imported citations that were not reverified in full.

The 1819 manuscript's catalog supplies its exact date and William D. Williamson collection (Coll. 62). The bridge PDF gives its August 8 approval on PDF page 5. The 1927 auction source distinguishes the July 30 newspaper issue from the August 24 advertised auction. Samuel's source leaves publication date unknown rather than reusing his death date. The 1926 bond notice likewise does not turn the notice date into an unverified newspaper issue date. Petronėlė's newspaper PDF returned HTTP 403 on re-fetch; the existing merged research and prior access date are identified explicitly. No new claim was derived from that failed fetch.

Conflicts remain visible: bridge completion/location, the auction's advertised-versus-completed distinction, Petronėlė's overnight death date, and Leroy/Elroy in Estelle's obituary. No parentage or protected historical claim was changed.

## Validation and review evidence

- `python validate_data.py`: **PASS**, 180 people, 127 events, 16 research notes; 21 places, 28 sources, 60 place assertions; zero blocking errors.
- `python -m unittest discover -s tests -q`: **70 tests pass**, including the complete prior regression suite, archive schema/reference/privacy mutation tests, loading compatibility, safe map serialization, source search, place navigation, family-login gating, and direct map/source/place routes.
- `npm test`: **12 tests pass**, executing the real HTML/JavaScript and bundled Leaflet in jsdom. Covers markers, place details, correct links, person/event/category/date interactions, empty/invalid ranges, injection handling, missing-library fallback and tile-error notices. Network resources are disabled in these tests.
- Python compilation and `git diff --check`: **PASS**.
- `git diff --exit-code origin/main -- data/people.json data/events.json data/research_people.json data/research_events.json data/research.json data/date_precision.json`: **PASS**. All six existing data files are byte-identical to the starting main, including protected historical content and all residence data. Existing hash-based protected-record tests pass.
- All new IDs and references validate; all 20 personally mapped subjects are historical/deceased. The map projection contains no raw profile notes, residences, private contact fields or living-person profiles. No private modern information was added to the new JSON records. Geographic/context links do not geocode addresses.
- Existing nonblocking research warnings remain unchanged: 1 ID/year mismatch, 6 unresolved relationship profiles, 7 unresolved participants in old timeline events, 53 nonreciprocal relationship links. None of those unresolved IDs is used by the new map assertions.
- CI now runs Python checks plus the Node DOM tests on both existing Python 3.12 and 3.13 jobs.

**Visual testing limit:** The supervised browser-preview environment supports Node/Vite projects and could not start this Streamlit repository. No framework migration or authentication bypass was made for preview. Streamlit pages render in AppTest, and Leaflet initializes with all 21 markers in DOM tests, but a live browser screenshot, narrow-screen visual review, and actual remote tile loading have not been verified. Review these on the normal Streamlit deployment before promoting this draft. No live deployment is performed by this PR.

## Unresolved design questions

1. Should future administrative history be modeled as dated boundaries/aliases, or as separate historical jurisdiction entities? The MVP intentionally stores modern places with historical notes.
2. Should claim/source relationships be extracted into a more general assertion table when non-geographic claims grow? The current typed place assertions already preserve individual evidence and roles.
3. When adding scans, what permission, transcription review, file-size, and preservation policy should govern local copies? Current source records link to repositories without mirroring images or full publications.
4. Which long-term tile provider is appropriate if usage grows? The map renderer is isolated so provider changes do not change the genealogy data.
5. How should formal historical uncertainty be represented spatially—areas, polygons, or approximate point radii? Current confidence and precision labels do not imply survey accuracy.

## Recommended Phase 2

1. Complete a live desktop/mobile browser review on the existing Streamlit host; check tile availability, scrolling, new-tab links, and keyboard navigation.
2. Obtain town/deed/bridge records to resolve the 1848 bridge's completion and actual public historic alignment. Only then add a geometry or a narrowly located public-site record.
3. Add reviewed cemetery transcriptions or grave photographs to corroborate Fuller entries. Do not upgrade compiled indexes automatically.
4. Identify precise, historically correct locations for Colby, Hallowell schools, public civic buildings, Calderwood Neck, North Haven Village and other institutions only when the source establishes the link. Add additional cemeteries with coordinate provenance.
5. Extend source coverage to probate, deeds, original military files, and historical newspapers; retain exact page/issue identifiers and short checked transcriptions.
6. Add date-aware jurisdiction boundaries, historical-map overlays, and migration narratives only when evidence establishes the dates and routes. The current data do not justify drawing travel lines between pins.

## High-value unresolved historical leads

- The tannery/mercury story remains a research lead; no industrial site, cause-of-death pin, or new public factual claim was created.
- Civil War Navy identities and the possible USS Passaic connection remain unresolved; no service geography was attached to a guessed person.
- Harold's exact early wireless-station site, Samuel's embarkation pier, Guatemala mission settlements, and the proposed bridge endpoints remain unlocated.
- Hiram's Mill Stream dam, Providence career links, Calderwood Neck, village institutions, and further burial places are candidates for a later explicitly sourced mapping pass; this phase does not infer location from broad family or occupational associations.
