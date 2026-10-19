# Phase 29 — Complete family graph integrity and documentary-evidence coverage audit

**Research and implementation date:** 19 October 2026  
**Repository baseline:** `csully1234/Beverage-Family`, `main` at `13a712bb41bd4feea28c6a6ece87906b2cec2c2d` (Phase 28, verified live on Render).  
**Objective:** audit every current effective person, relationship and source path; improve family source provenance without asserting unproven genealogical connections.

## 1. Initial measured inventory

The pre-implementation survey combined the imported family and all available reviewed profile overlays, rather than inspecting only an individual historic branch. It found:

| Measure | Preliminary audit |
| --- | ---: |
| Indexed people | 202 |
| Relationship links including sibling inference | 701 |
| Directed parent-child links | 287 |
| Recorded spouse links | 60 |
| Sibling links (including those inferred through shared recorded parents) | 354 |
| Relationships with individual claim-specific source reviews *before* this PR | 12 |
| Separate connected groups among indexed profile IDs | 4 |
| Referenced relationship IDs missing a full profile | 6 |
| Profiles with no bibliography entries | 1 |
| Profiles with no directly linked URL in their own citation field | 109 |
| Profiles with no recorded birth date | 27 |
| Profiles with no recorded death date | 75 |
| Groups with normalized full-name collisions | 3 |

These counts derive from the source archives and versioned overlays in the starting repository; the new dashboard calculates the **current effective site records at runtime**, including review/correction overlays, which are the authoritative displayed numbers. Unreviewed does **not** mean wrong; an unlinked citation is not necessarily an absent original document. Inferred sibling links do **not** represent independent individual source statements.

### Four distinct graph components

1. **Main extended family tree**: 184 profiles in the initial overlay-level inventory. Includes older Beverage family material and recent descendants.
2. **Matthew Beveridge of Hope, Maine**: 12 profiles. Includes his 1837 widow Clarissa, the eight court-named children and Barnabas/Jerusha Cobb, her Carver parents.
3. **Nathaniel Beverage of Rockland**: four profiles, a historically important collateral study.
4. **Mercy Beveridge Henry**: two profiles including her husband.

**No previously unproven branch is joined by a speculative edge.** A surname match, local-history narrative, shared given name, or adjacent court entry does not establish parentage. The dashboard displays all groups and provides source/person routes to help a researcher resolve those links later.

### Six missing-profile references and same-name investigations

Six relationship IDs appear as endpoints in the existing graph but lack full effective profiles. Their original relationship pointers are retained; they are flagged for follow-up, **not auto-created as new people**. The same-name groups include **Sarah Beverage**, **Robert Beverage** and multiple historical **Thomas Beverage** entries. Repeated names across generations must not be merged without independent original records.

### Source coverage interpretation

The initial survey found 109 profile records without a URL *inside their person-source field*. Some have useful bibliographic citations, linked events, curated exhibits, or independently reviewed relationship records elsewhere. The dashboard presents this count as a **direct-link task list**, not as a claim that only 93 people have evidence. Similarly, a person having several listed citations does not imply each family edge has been confirmed.

## 2. Eleven relationship-specific source audits added

This PR preserves the existing 12 Phase 15 reviews and adds **11 specific source reviews** in a **new additive file**, not by changing source profiles.

- **Eight parent-child relations:** all eight persons explicitly called Matthew Beveridge/Beverage's children by the **October 1837 Waldo County probate partition warrant** (received scan 09, duplicate 26), independently mentioned in the September petition (received scan 31). The correct source label is *contemporary original probate evidence*, stronger than an unspecific family-history biography.
- **Matthew and Clarissa:** the 6 March 1837 widow's petition and dower papers document Clarissa as his widow. This does **not** provide a wedding date or demonstrate which children she bore.
- **Barnabas Cobb and Jerusha Cobb to Clarissa:** *Vital Records of Carver, Massachusetts, to the Year 1850* (1911), COBB births, p. 21, states Clarissa's Carver birth and parental names. Philip L. Cobb's *History* (1907) pp. 164–165 supplies the distinct *secondary identity bridge* to Matthew's wife in Hope. The original Carver birth manuscript and marriage return are **still unexamined**.

These reviews become separate, linked evidence cards on the exact parent-child/spouse edges. The old Phase 15 claims and reviews remain intact. The reviewer sees **both** the underlying original-era source locator and a clear statement of what it does not establish.

**Publication boundary:** the 1837 probate-office scan originals are still local/unpublished. The case page may show reviewed abstracts and context, **not** a reproduction of the unlicensed images. Court-source reviews point to the internal 1837 evidence notebook; offsite published references link to their existing archival hosts.

## 3. Visitor-facing whole-family dashboard

New `genealogy_integrity.py` implements pure deterministic calculations and source checks over `load_site_data` plus the complete `relationship_index`:

- Connected components computed using **real indexed person IDs**, including inherited relationship edges but excluding unknown/fabricated profiles.
- Distinct parent-child, spouse and sibling edge coverage as tracked by the existing `audited_edges` ledger; reviewed vs unreviewed **documentation** counted independently.
- Complete person-by-person citation/link counts, date availability, linked-event counts and reviewed relationship counts.
- Display-only name-collision candidates and dated-event or parent-child chronology screenings. These are **prompts to inspect original evidence**, not automatic data edits.
- Event records with no cited source and no direct linked source URL.
- Complete CSV review queues, with family names and source-status details available to signed-in family members through the existing password-gated site.

The new `research_integrity_dashboard.py` adds one integrated interface under **Historical Discoveries → Family history evidence dashboard**. It has an overall summary with prioritized archival tasks, a branch browser for **every disconnected group**, a source-audit list containing **all** inherited and reviewed edges, date/source coverage checklists and exports.

**Visibility:** family members still use the existing single family-site password. No authentication code or Render environment settings changed.

### Cross-navigation

Each family exhibit now provides a direct route from **Family connections** to the source reviews involving that exact person. Original archival readers, source rights/status labels, family books and trees remain accessible through the existing site.

## 4. Research priorities from original evidence

1. **Matthew's Hope deed chain, 1761–1837.** Locate a specific grantor/grantee index item, instrument book and page, actual parties, prior residence and bounds in historic Lincoln and Waldo registries. Tentative probate parcel sellers (Alford, Whitney, etc.) are *not* verified deeds.
2. **1785 petition vs 1786 Rufus Putnam Fox Islands survey.** Obtain original named-minor entry, evidence of origin and household context, and compare with the later Hope town clerk. A 2025 scholarly article provides Maine State Archives Box 001 for Putnam's report but no inspected original Matthew-specific survey entry.
3. **Clarissa original birth/marriage chain.** Inspect the town's underlying 1786 Carver birth entry and a contemporary marriage intentions/return for Capt. Matthew and Clarissa Cobb. Do not assign Clarissa maternity to Matthew's eight children without independent evidence.
4. **Nathaniel of Rockland and Mercy Henry branches.** Original vital, probate and deed relationships should be sought before drawing a graph edge to the larger extended family.
5. **Civil vital-record and source-link completion.** Prioritize true source-specific reviews for each parent-child relation before assuming inferred siblings are separately supported.

The first four are **specific original-document retrieval targets**, not accomplished ancestry breakthroughs. No new original deeds, marriage returns or unpublished images were retrieved during this code-and-record audit.

## 5. Implementation and release acceptance

The existing structural validator and protected baseline data are unchanged. New pure tests verify full tree coverage; four historically disconnected branches; eight original court-named children; two Carver birth-parent links; the widow marriage statement; no invented birth parent for Matthew; no inferred maternity for Clarissa; all missing referenced IDs; same-name groups; chronological screening; and downloadable every-edge audit rows.

New Streamlit smoke tests open the full audit, branch browser, person-specific relationship evidence, original-record gaps and CSV exports. Python 3.12/3.13 GitHub validation and existing JavaScript map tests must pass before merge.

**Protect:** do not change the Boston Tea Party claim or relative residential addresses, and do not publish uncertain archival image material. Source records and family genealogy remain exactly as they were at the Phase 28 baseline; only new **review metadata** and dashboard code are added.

## 6. Limits of this release

This release accomplishes a **comprehensive structural and evidence-coverage audit**, plus eleven previously missing primary-/published-source relationship reviews. It does **not** finish original-document verification for all ~700 graph edges, prove previously disconnected branches relate, or establish every unrecorded date. The completed dashboard makes these gaps explicit, complete, searchable, and actionable.

A successful GitHub merge must still be separately deployed to Render, which has automatic deployment disabled. An authenticated human mobile/desktop visual check remains the definitive end-to-end acceptance step.
