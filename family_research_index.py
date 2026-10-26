"""Unified, provenance-first discovery index across the family research archive.

Search hits are pointers to existing records, NOT transcriptions, proven identities,
a new family tree, or new genealogical assertions. This module is pure Python:
no UI, network, web requests, OCR, generated facts or mutations to source data.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent / "data"

CATEGORIES = (
    "Open identity questions",
    "Relationship evidence",
    "Historical investigations",
    "Historical research findings",
    "Original source register",
    "Historical source exhibits",
    "Scanned book photographs",
    "Scanned book OCR leads",
    "Historical record trails",
    "Existing family profiles",
)
STATUS = {
    "Open identity questions": "Unresolved identity · review original evidence",
    "Relationship evidence": "Reviewed relationship claim · check the stated source limitation",
    "Historical investigations": "Research hypothesis or attributed historical account",
    "Historical research findings": "Preserved archival research finding · interpret its confidence and sources",
    "Original source register": "Registered citation · access and rights vary by record",
    "Historical source exhibits": "Source-backed exhibit · check what the item establishes",
    "Scanned book photographs": "Author-attributed photograph · not independently certified identity",
    "Scanned book OCR leads": "Machine-detected word/page only · NOT identity proof",
    "Historical record trails": "Published report or document lead · may lack originals",
    "Existing family profiles": "Existing genealogy record · individual relationships may be unreviewed",
}
PRIORITY = {category: index for index, category in enumerate(CATEGORIES)}
WORD = re.compile(r"[\w]+", re.UNICODE)


def _read_records(name: str, root: Path) -> list[dict]:
    data = json.loads((root / name).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(name + " must be a JSON array")
    return data


def _safe_url(value: str) -> str:
    """Don't turn untrusted source fields into javascript: or local-file links."""
    value = str(value or "").strip()
    parsed = urlsplit(value)
    return value if parsed.scheme == "https" and parsed.netloc else ""


def _links(sources) -> list[dict]:
    links = []
    for source in sources or []:
        if not isinstance(source, dict):
            continue
        uri = _safe_url(source.get("url"))
        if uri and all(item["url"] != uri for item in links):
            links.append({
                "title": str(source.get("title") or "View historical source"),
                "url": uri,
                "note": str(source.get("finding") or source.get("claim") or
                            source.get("supports") or source.get("type") or "")[:500],
            })
    return links


def _item(*, id, category, title, summary="", limits="", people_ids=(), pages=(),
          route="", sources=(), keywords="", status=None, source_date="") -> dict:
    if category not in CATEGORIES:
        raise ValueError("Unknown archive category: " + category)
    return {
        "id": str(id),
        "category": category,
        "title": str(title),
        "summary": str(summary or ""),
        "limits": str(limits or ""),
        "person_ids": sorted(set(str(p) for p in people_ids if p)),
        "pages": sorted(set(int(p) for p in pages if 1 <= int(p) <= 305)),
        "route": str(route or ""),
        "sources": list(sources),
        "keywords": str(keywords or ""),
        "status": str(status or STATUS[category]),
        "source_date": str(source_date or ""),
    }


def build_index(people_by_id: dict[str, dict], root: Path = ROOT) -> list[dict]:
    """All category cards cite a page, original record, or explicit archive claim.

    An OCR hit is intentionally NEVER connected to a canonical person ID.
    Author-captions attach only via the existing *exact-ID* editorial crosswalk.
    """
    records: list[dict] = []
    crosswalk = _read_records("colony_people_crosswalk.json", root)[0]
    book_pages = defaultdict(set)
    for entry in crosswalk["linked_people"]:
        for page in entry["pdf_pages"]:
            book_pages[int(page)].add(str(entry["person_id"]))

    photos = _read_records("colony_photo_captions.json", root)[0]["photos"]
    for photo in photos:
        page = int(photo["pdf_page"])
        records.append(_item(
            id="photo:" + str(page), category="Scanned book photographs",
            title=photo["title"], summary=photo["caption_summary"],
            limits="This is the book author's caption or a summary of it, not a separately verified identity. "
                   "Use the full original page to check the printed caption.",
            people_ids=book_pages.get(page, ()), pages=[page],
            route="?page=family-books&book_page=" + str(page),
            keywords=photo.get("section", ""), source_date=photo.get("capture_date") or "",
        ))

    nav = _read_records("colony_ocr_navigation_index.json", root)[0]
    page_terms: dict[int, list[str]] = defaultdict(list)
    for term, pages in nav["hits"].items():
        for page in pages:
            if 1 <= int(page) <= int(nav["scanned_pages"]):
                page_terms[int(page)].append(str(term))
    for page in sorted(page_terms):
        terms = sorted(set(page_terms[page]), key=str.casefold)
        records.append(_item(
            id="ocr:" + str(page), category="Scanned book OCR leads",
            title="The Colony — original PDF page " + str(page),
            summary="Machine-detected words: " + ", ".join(terms),
            limits="One-pass OCR word presence only. A matching word does not establish the identity of a person, "
                   "a relationship, a historical event, or the absence of any other name.",
            pages=[page], route="?page=family-books&book_page=" + str(page),
            keywords=" ".join(terms), status=STATUS["Scanned book OCR leads"],
        ))

    for idx, person in enumerate(crosswalk["unresolved_people"]):
        pages = [int(v) for v in person.get("pages", [])]
        records.append(_item(
            id="unresolved:" + str(idx),
            category="Open identity questions",
            title=str(person["name"]), summary=str(person["issue"]),
            limits="Book-caption candidate; identity and any genealogy connection remain unresolved.",
            pages=pages,
            route=("?page=family-books&book_page=" + str(pages[0])) if pages
                  else "?page=family-books",
            sources=_links(person.get("independent_sources")),
            keywords=person.get("disposition", ""),
        ))

    for row in _read_records("evidence_investigations.json", root):
        records.append(_item(
            id="investigation:" + row["id"], category="Historical investigations",
            title=row["title"], summary=row["summary"],
            limits="; ".join(row.get("unresolved", [])),
            people_ids=row.get("person_ids", ()),
            route="?page=collection&view=workbench&case=" + quote("investigation:" + row["id"]),
            keywords=" ".join(row.get("known", []) + row.get("next_records", [])),
            status=str(row.get("status") or STATUS["Historical investigations"]),
            source_date=row.get("period", ""),
        ))

    hope = _read_records("phase20_hope_matthew_civic_records.json", root)[0]
    early = _read_records("phase31_hope_earliest_clerk_research.json", root)[0]
    for row in sorted([*hope["records"], *early["records"]],
                      key=lambda item: (item["date"], item["id"])):
        records.append(_item(
            id="hope-clerk:" + row["id"],
            category="Historical investigations",
            title=row["date"] + " · " + row["label"],
            summary=row["claim"], limits=row["limit"],
            people_ids=(), pages=(),
            route="?page=collection&view=hope-matthew",
            sources=_links([{"title":row["source_title"],"url":row["source_url"],
                             "claim":row["source_page"]}]),
            keywords="Matthew Beveridge Hope civic record clerk census " + row["town"],
            status="Clerk-ledger transcription" if row["category"]=="town_clerk_transcription"
                   else "Separate census index, original image not inspected",
            source_date=row["date"],
        ))

    census_trail = _read_records("phase32_hope_census_originals.json", root)[0]
    for row in census_trail["cases"]:
        records.append(_item(
            id="hope-census:" + row["id"],
            category="Historical record trails",
            title=str(row["year"]) + " · " + row["place"] + " · Census evidence",
            summary=row["head_claim"], limits=row["limitations"],
            people_ids=(), pages=(),
            route="?page=collection&view=hope-census",
            sources=_links([{"title":row["source_title"],"url":row["source_url"],
                             "claim":row["archive_locator"]}]),
            keywords="Barrettstown Hope census Mathew Matthew Beverage Beveridge "
                     + row["archive_locator"] + " " + row["status"],
            status=row["status"].replace("_", " "),
            source_date=str(row["year"]),
        ))

    original_access = _read_records("phase34_hope_original_reel_and_civic_votes.json", root)[0]
    for record in original_access["cases"]:
        urls = [{"title": record["source_title"], "url": record["source_url"],
                 "finding": record["locator"]}]
        if record.get("companion_url"):
            urls.append({"title": record.get("companion_title") or "Original census transcription",
                         "url": record["companion_url"],
                         "finding": "Separate household-head transcription, not manuscript verification"})
        records.append(_item(
            id="hope-original-access:" + record["id"],
            category="Historical record trails",
            title=record["date_label"] + " · " + record["title"],
            summary=record["finding"], limits=record["limits"],
            people_ids=(), pages=(),
            route="?page=collection&view=hope-census",
            sources=_links(urls),
            keywords="Hope Matthew Mathew Beveridge archival original ledger census clerk "
                     + record["locator"] + " " + record["needs"],
            status=record["status"], source_date=str(record["year"]),
        ))

    # One probate source family, not 31 independent proofs. The source-file
    # index contains text and provenance only; scans await permission to publish.
    probate = _read_records("phase22_matthew_waldo_probate.json", root)[0]
    for claim in probate["claims"]:
        pages = claim["review_pages"]
        records.append(_item(
            id="waldo-probate-claim:" + claim["id"],
            category="Historical investigations",
            title="1837 Waldo probate · " + claim["label"],
            summary=claim["finding"],
            limits=claim["limits"] + " Original supplied images not publicly published.",
            people_ids=(), pages=(),
            route="?page=collection&view=waldo-probate&scan=" + str(pages[0]),
            keywords="Matthew Beverage Beveridge Clarissa widow heir estate probate Hope Waldo "
                     + claim["status"],
            status=claim["status"], source_date=claim["date"],
        ))
    for scan in probate["scans"]:
        number = scan["review_page"]
        records.append(_item(
            id="waldo-probate-scan:" + str(number).zfill(2),
            category="Historical investigations",
            title="Matthew probate · received scan " + str(number).zfill(2)
                  + " · " + scan["label"],
            summary="Source-office scan index and checksum; this label is a "
                    "preliminary editorial classification, not the court's file order.",
            limits=("Exact duplicate of source scan " + str(scan["duplicate_of"])
                    if scan.get("duplicate_of") else
                    "Underlying court image retained offline pending reproduction clearance."),
            people_ids=(), pages=(),
            route="?page=collection&view=waldo-probate&scan=" + str(number),
            keywords="Matthew Beverage Beveridge Waldo Hope probate 1837 "
                     + scan["provisional_type"].replace("_", " ") + " "
                     + (" ".join(h["name"] for h in probate["heirs"])
                        if number in (9, 14, 31) else ""),
            status="Source scan cataloged · not public" if not scan.get("duplicate_of")
                   else "Exact duplicate scan · not new evidence",
            source_date="1837",
        ))

    # Reviewed Phase 23 layer: Court expressly describes these people as
    # "children", unlike a generic inheritance-only designation. Specific
    # legal child links are now anchored to exact stable genealogy IDs.
    phase23 = _read_records("phase23_probate_deed_trail.json", root)[0]
    father = "matthew_beveridge_hope_1837"
    court_children = [p for p in phase23["principal_people"]
                      if p["role"].startswith("named child")]
    for child in court_children:
        records.append(_item(
            id="waldo-court-child:" + child["person_id"],
            category="Relationship evidence",
            title="1837 court child — " + child["label"] + " · Matthew of Hope",
            summary="Probate partition warrant explicitly calls this person a child of Matthew.",
            limits="Court parent-child designation only: this does not establish "
                   "the child's mother, birth date or identity with all later accounts. "
                   + str(child.get("limitation", "")),
            people_ids=[father, child["person_id"]],
            route="?page=collection&view=waldo-probate&scan=9",
            keywords="probate Oct 1837 Matthew Beveridge Beverage children heirs "
                     + child["label"],
            status="Original-era probate warrant · explicit child designation",
            source_date="1837-10-06",
        ))
    for clue in phase23["land_clues"]:
        records.append(_item(
            id="waldo-deed-lead:" + clue["id"],
            category="Historical investigations",
            title="Matthew's Hope property · " + clue["label"],
            summary=clue["reading"],
            limits=clue["certainty"] + ". " + clue["search_strategy"],
            people_ids=[father],
            route="?page=collection&view=waldo-probate&scan=2",
            keywords="1837 Hope Waldo Lincoln grantee grantor deed " + clue["label"],
            status="Unverified deed lead — actual recorded instrument not obtained",
            source_date="1837",
        ))
    for excerpt in phase23["transcriptions"]:
        associated = [father]
        if excerpt["scan"] in {9, 31}:
            associated.extend(p["person_id"] for p in court_children)
        if excerpt["scan"] in {10, 18, 24}:
            associated.append("clarissa_beveridge_widow_1837")
        if excerpt["scan"] == 14:
            associated.append("polly_tucker_matthew_child")
        records.append(_item(
            id="waldo-reading:" + str(excerpt["scan"]).zfill(2),
            category="Historical investigations",
            title="Probate reading · scan " + str(excerpt["scan"]).zfill(2),
            summary=excerpt["text"], limits=excerpt["status"] + ". " + excerpt["note"],
            people_ids=associated,
            route="?page=collection&view=waldo-probate&scan=" + str(excerpt["scan"]),
            keywords="1837 Waldo Hope probate original reading transcription excerpt",
            status=excerpt["type"].replace("_", " "),
            source_date=excerpt["date"],
        ))

    # Phase 24 retains source-by-source distinction: the Carver birth
    # compilation directly names parents; the 1907 genealogy bridges the
    # Clarissa identity to Matthew. 1785 and early deed links remain research
    # leads, not proven Matthew ancestor or land-deed records.
    phase24 = _read_records("phase24_cobb_vital_identity_research.json", root)[0]
    cobb_sources = {row["id"]: row for row in phase24["sources"]}
    for finding in phase24["findings"]:
        cited = [cobb_sources[sid] for sid in finding["source_ids"]]
        records.append(_item(
            id="cobb-origin:" + finding["id"],
            category=("Relationship evidence" if finding["id"] == "clarissa-carver-born"
                      else "Historical investigations"),
            title=finding["title"], summary=finding["claim"],
            limits=finding["limits"],
            people_ids=finding["person_ids"],
            route="?page=collection&view=family-origins",
            sources=_links([{
                "title": source["title"] + " (" + str(source["year"]) + ")",
                "url": source["url"], "claim": source["claim"],
            } for source in cited]),
            keywords="Matthew Beverage Beveridge Hope 1785 1837 "
                     "Clarissa Cobb Barnabas Jerusha Carver Plymouth Fox Islands "
                     + finding["status"].replace("_", " "),
            status=finding["status"].replace("_", " "),
            source_date=finding["date"],
        ))

    for row in _read_records("phase19_matthew_reconciliation_cases.json", root):
        records.append(_item(
            id="matthew:" + row["id"], category="Historical investigations",
            title=row["title"], summary=row["claim"], limits=row["proof"],
            people_ids=row.get("person_ids", ()),
            pages=[row["book_page"]] if row.get("book_page") else [],
            route="?page=collection&view=matthew",
            sources=_links([{
                "title":row["reference"], "url":row.get("url", ""),
                "supports":row["claim"]}]),
            keywords=" ".join(row.get("next_originals", [])),
            status=row["status"],
        ))

    for row in _read_records("phase16_ancestry_bridge_dossiers.json", root):
        records.append(_item(
            id="ancestry:" + row["id"], category="Historical investigations",
            title=row["title"], summary=row["finding"], limits=row["limitations"],
            people_ids=row.get("person_ids", ()),
            route="?page=collection&view=workbench&case=" + quote("ancestry:" + row["id"]),
            sources=_links(row.get("sources")),
            keywords=" ".join(row.get("named_people", []) + row.get("next_originals", [])),
            status=row["status"], source_date=row.get("period", ""),
        ))

    for row in _read_records("phase8_identity_evidence.json", root):
        pages = [int(p) for p in row.get("book_pages", [])]
        records.append(_item(
            id="identity:" + row["id"], category="Open identity questions",
            title=row["name"], summary=row["known"], limits=row["limits"],
            people_ids=[row["tree_profile_id"]] if row.get("tree_profile_id") else [],
            pages=pages,
            sources=_links(row.get("sources")),
            route="?page=collection&view=workbench&case=" + quote("identity:" + row["id"]),
            keywords=" ".join(str(v.get("record", ""))+" "+str(v.get("where", ""))
                              for v in row.get("next_originals", [])),
            status=row.get("status"),
        ))

    # Phase 29 source reviews augment rather than overwrite the original
    # relationship evidence register. Both must appear in the workbench.
    for row in (_read_records("phase15_relationship_reviews.json", root) +
                _read_records("phase29_relationship_reviews.json", root)):
        category = "Relationship evidence"
        a, b = row["from_id"], row["to_id"]
        title_a = people_by_id.get(a, {}).get("full_name", a)
        title_b = people_by_id.get(b, {}).get("full_name", b)
        relation = "parent of" if row["kind"] == "parent_child" else row["kind"].replace("_", " ")
        records.append(_item(
            id="relationship:" + row["kind"] + ":" + a + ":" + b,
            category=category, title=str(title_a) + " — " + relation + " — " + str(title_b),
            summary=row["finding"], limits=row["limitations"],
            people_ids=[a, b], sources=_links(row["sources"]),
            route="?page=people&profile=" + quote(a),
            status=row["status"],
        ))

    # The large, preserved historical collection is the core documentary archive.
    # Its confidence statuses must be copied, not recast as confirmed facts.
    source_register = json.loads(
        (root / "collections" / "2026-10-14.json").read_text(encoding="utf-8")
    )
    source_by_id = {record["Source ID"]: record for record in source_register["sources"]}
    for row in source_register["findings"]:
        nav = row["Navigation"]
        rids = sorted(set(re.findall(r"\\bSRC\\d{3}\\b",
                                  str(row.get("Supporting sources") or ""))))
        cited = [source_by_id[sid] for sid in rids if sid in source_by_id]
        links = _links([{"title": str(record.get("Title") or record["Source ID"]),
                         "url": record.get("URL", ""),
                         "claim": record.get("What it supports", "")}
                        for record in cited])
        records.append(_item(
            id="finding:" + row["Research ID"],
            category="Historical research findings",
            title=nav.get("title") or row["Research ID"],
            summary=row.get("Proposed fact or narrative", ""),
            limits=row.get("Notes about uncertainty", ""),
            people_ids=nav.get("people_ids", ()),
            route="?page=collection&finding=" + quote(row["Research ID"]),
            sources=links,
            keywords=" ".join(str(t) for t in nav.get("topics", [])) + " " +
                     str(row.get("Location") or "") + " " +
                     str(row.get("Exact citation") or ""),
            status=str(row.get("Confidence") or "Unrated") +
                   " · " + str(row.get("Human-review status") or "Review status unknown"),
            source_date=row.get("Date or date range", ""),
        ))
    for row in source_register["sources"]:
        sid = row["Source ID"]
        records.append(_item(
            id="register:" + sid, category="Original source register",
            title=row.get("Title") or sid,
            summary=row.get("What it supports") or "Registered historical citation",
            limits="Viewed status: " + str(row.get("Viewed status") or "Unknown") +
                   ". Source access: " + str(row.get("URL status") or "Unverified") +
                   ". Rights: " + str(row.get("Rights") or "Check source host before reusing."),
            route="?page=archive&source=" + quote(sid),
            sources=_links([{"title": row.get("Title"), "url": row.get("URL"),
                             "supports": row.get("What it supports", "")}]),
            keywords=str(row.get("Repository", "")) + " " +
                     str(row.get("Source type", "")) + " " +
                     str(row.get("Locator", "")),
            status=str(row.get("Viewed status") or "Not directly inspected"),
            source_date=row.get("Access date", ""),
        ))

    for row in _read_records("evidence_exhibits.json", root):
        records.append(_item(
            id="exhibit:" + row["id"], category="Historical source exhibits",
            title=row["title"], summary=row["claim"], limits=row["limits"],
            people_ids=row.get("people_ids", ()),
            sources=_links([row]),
            route="?page=collection&view=workbench&case=" + quote("exhibit:" + row["id"]),
            keywords=str(row.get("collection", "")) + " " + str(row.get("type", "")),
            source_date=row.get("date", ""),
        ))

    for filename, category in (
        ("phase10_early_maine_records.json", "Historical record trails"),
        ("phase12_mercy_henry_sources.json", "Historical record trails"),
        ("phase11_james_record_chain.json", "Historical record trails"),
    ):
        for row in _read_records(filename, root):
            ident = filename.replace(".json", "").replace("phase", "p")
            summary = row.get("summary") or row.get("proof") or ""
            limits = row.get("limits") or row.get("link_status") or row.get("person_status") or ""
            route = row.get("route") or "?page=stories&story=topsham-beveridge-before-fox-islands"
            records.append(_item(
                id=ident + ":" + str(row["id"]), category=category,
                title=row.get("title") or row.get("record") or row["id"],
                summary=summary, limits=limits,
                sources=_links([{"title": row.get("source_title") or "Published historical record",
                                 "url": row.get("source_url")}]),
                route=route, source_date=row.get("date") or row.get("year") or "",
            ))

    # Source-access casework has no safe Matthew-specific person attribution.
    # Even the 1889 name Matthew Beveridge (minor) is not linked by identity
    # to the Hope 1837 decedent, so none of these cards have a person_id.
    fox_cases = _read_records("phase30_fox_islands_original_source_access.json", root)
    for case in fox_cases:
        for record in case["sources"]:
            records.append(_item(
                id="fox-original:" + record["id"], category="Historical record trails",
                title=record["title"], summary=record["establishes"],
                limits=record["does_not_establish"],
                people_ids=[],
                sources=_links([record]),
                route="?page=collection&view=fox-originals",
                keywords=record["identifier"] + " " + record["repository"] + " " +
                         record["request"] + " " + record["category"],
                source_date=record["date"],
                status=record["access"].replace("_", " "),
            ))

    # Phase 50: a newly supplied original Putnam settlers list now provides
    # a direct Thomas Beverage name and reported fifteen years' settlement.
    # This is a name/document observation, not a verified canonical ancestor ID.
    putnam = _read_records("phase50_putnam_original_settlement_statement.json", root)[0]
    observed = putnam["observation"]
    records.append(_item(
        id="putnam-original:" + observed["id"],
        category="Historical record trails",
        title="1786 original Putnam list · Thomas Beverage, 15 years settled",
        summary=observed["establishes"] + " Approximate settlement c. 1771.",
        limits=observed["cannot_prove"],
        people_ids=[],
        sources=[],
        route="?page=collection&view=fox-originals",
        keywords="Rufus Putnam Fox Island division Thomas Beverage Beveridge "
                 "1786 March 18 1785 December 16 1771 fifteen years manuscript "
                 "settlement original " + putnam["original_uploaded_file"],
        source_date="1786-03-18",
        status="Original manuscript reviewed · canonical identity not established",
    ))

    # Phase 39: editor-graded original image retrieval targets and unresolved
    # branch hypotheses. Exact-person search matching describes a RESEARCH
    # QUESTION, never verified parentage. Individual deed mentions with a
    # conflicting chronology have NO canonical person attribution.
    expedition = _read_records("phase39_primary_record_expedition.json", root)[0]
    _source_person_ids = {
        "vinalhaven-josiah-1793": ["josiah_winslow_beverage_1793"],
        "trinity-1774-thomas-mercy": ["thomas_beverage_1750", "mercy_kent_1754"],
        "woodruff-1838-josiah": ["josiah_winslow_beverage_1793"],
        "lewiston-josiah-1858": ["josiah_winslow_beverage_1793"],
        "nathaniel-compiled-1803": ["nathaniel_beverage_1804_rockland"],
        "nathaniel-eaton-1865": ["nathaniel_beverage_1804_rockland"],
        "hope-1837-probate": ["matthew_beveridge_hope_1837",
                              "clarissa_beveridge_widow_1837"],
    }
    for case in expedition["cases"]:
        records.append(_item(
            id="expedition-case:" + case["id"],
            category="Open identity questions",
            title=case["title"], summary=case["question"],
            limits=case["not_proved"],
            people_ids=[pid for pid in case["people_ids"] if pid in people_by_id],
            route="?page=collection&view=source-expedition&case=" + quote(case["id"]),
            sources=_links([source for source in expedition["sources"]
                            if source["id"] in case["source_ids"]]),
            keywords=" ".join([case["place"], case["working_theory"],
                               " ".join(case["next_checks"])]),
            status=case["status"], source_date=case["period"].split("–")[0],
        ))
    for source in expedition["sources"]:
        records.append(_item(
            id="expedition-source:" + source["id"],
            category="Historical record trails",
            title=source["title"],
            summary=source["establishes"] + " · " + source["locator"],
            limits=source["limits"],
            people_ids=[pid for pid in _source_person_ids.get(source["id"], [])
                        if pid in people_by_id],
            route="?page=collection&view=source-expedition",
            sources=_links([
                {"title": source["repository"], "url": source.get("url")},
                {"title": "Find original record in institutional catalog",
                 "url": source.get("original_access")},
            ]),
            keywords=(source["class"] + " " + source["repository"] + " " +
                      source["locator"]),
            status=("Original-era scan previously reviewed"
                    if source["original_inspected"] else
                    "Original image NOT independently inspected"),
            source_date=source["year"],
        ))

    # Phase 41: competing online-parentage identities are searchable as
    # questions, never imported as confirmed person-edge source records.
    from identity_claim_review import load_claims, claim_review_route
    for conflict in load_claims(root / "phase41_competing_identity_claims.json"):
        records.append(_item(
            id="identity-dispute:" + conflict["id"],
            category="Open identity questions",
            title=conflict["title"], summary=conflict["question"],
            limits=conflict["limits"],
            people_ids=[pid for pid in conflict["person_ids"] if pid in people_by_id],
            route=claim_review_route(conflict["id"]),
            sources=_links([{"title": claim["value"], "url": claim.get("url")}
                            for claim in conflict["claims"]] +
                           [{"title": row["title"], "url": row["url"]}
                            for row in conflict.get("corroborating_context", [])]),
            keywords=" ".join([conflict["source_target"],
                               *conflict["research_tasks"]]),
            status=conflict["status"], source_date=conflict["period"].split("–")[0],
        ))

    # Phase 42: finding aids and open document requests; never describe an
    # uninspected original as a confirmed parentage citation.
    from original_record_intake import load_acquisition, acquisition_route
    retrieval = load_acquisition(root / "phase42_primary_document_acquisition.json")
    owners = {x["id"]: x for x in retrieval["custodians"]}
    for target in retrieval["targets"]:
        records.append(_item(
            id="original-retrieval:" + target["id"],
            category="Open identity questions",
            title=target["title"],
            summary=target["event"] + ". " + target["source_locator"],
            limits="NOT INSPECTED: " + target["evidence_needed"],
            people_ids=[pid for pid in target["person_ids"] if pid in people_by_id],
            route=acquisition_route(target["id"]),
            sources=_links([{"title": "Original research finding aid",
                             "url": target["url"]}] + [
                             {"title": owners[oid]["name"], "url": owners[oid]["url"]}
                             for oid in target["custodian_ids"]
                        ]),
            keywords=target["initial_query"] + " " + target["places"],
            status="Original source NOT inspected · request/inspect original",
            source_date=target["event"].split(" ")[0],
        ))
    # Phase 43: every published annual office entry is a source-search item,
    # but there is NO proven stable person ID in the 1889 printed name list.
    # This must never become a dated family-timeline event by surname inference.
    from vinalhaven_civic_history import load_civic_roster, civic_route
    civic = load_civic_roster(root / "phase43_vinalhaven_civic_officers.json")
    for row in civic["records"]:
        records.append(_item(
            id="vinalhaven-civic:" + row["id"],
            category="Historical record trails",
            title=f"{row['year']} Vinalhaven {row['office']}: {row['printed_name']}",
            summary=f"{row['printed_name']} appears in the {row['year']} "
                    f"municipal {row['office'].lower()} roster; 1889 edition p. "
                    f"{row['printed_page']}.",
            limits="1889 retrospective printed list only; original town "
                   "minutes not read and exact indexed genealogy person NOT verified.",
            people_ids=[],
            route=civic_route(row["printed_name"], row["year"]),
            sources=_links([{"title":"1889 Vinalhaven centennial, p. " +
                             str(row["printed_page"]), "url":row["source_url"]}]),
            keywords="town clerk treasurer selectman Fox Islands 1889 Vinalhaven",
            status="Retrospective civic source · individual identity unverified",
            source_date=row["year"],
        ))
    # Phase 44: corroborating publication families with zero verified person
    # identifications. Distinct name appearances never become ancestry edges.
    from fox_islands_government_trail import load_government_trail,trail_route
    island_trail=load_government_trail(root/"phase44_fox_islands_government_census_crosswalk.json")
    island_sources={s["id"]:s for s in island_trail["sources"]}
    for record in island_trail["records"]:
        source=island_sources[record["source_id"]]
        records.append(_item(
            id="island-document:" + record["id"],
            category="Historical record trails",
            title=record["date_label"] + " · " + record["printed_name"] +
                  " — " + record["event_type"],
            summary=record["details"] + " · " + record["page"],
            limits=source["limits"] + " Exact genealogy identity UNVERIFIED.",
            people_ids=[],
            route=trail_route(record["id"]),
            sources=_links([{"title":source["title"],"url":source["url"]}]),
            keywords=record["next_original"]+" "+record["identity_status"],
            status="Historical publication name · ancestry identity not proved",
            source_date=record["date_label"],
        ))
    # Phase 45: a counted 1790 household, original 1820 reel, and
    # new scholarly migration context. Do not duplicate Phase 30's existing
    # 1785 petition / 1786 Putnam box references in the discovery index.
    from early_fox_island_atlas import load_early_islands, early_islands_route
    earliest=load_early_islands(root/"phase45_early_island_census_settlement_context.json")
    earliest_sources={s["id"]:s for s in earliest["sources"]}
    already_indexed={"1785-settlement-petition-context","1786-putnam-context"}
    for item in earliest["findings"]:
        if item["id"] in already_indexed:
            continue
        source=earliest_sources[item["source_id"]]
        records.append(_item(
            id="early-islands:" + item["id"],
            category="Historical record trails",
            title=f"{item['year']} · {item['title']}",
            summary=item["detail"],
            limits=item["limits"]+" "+source["limitations"],
            people_ids=[],
            route=early_islands_route(item["id"]),
            sources=_links([{"title":source["title"],"url":source["url"]}]),
            keywords=item["manuscript_target"]+" "+item["name_as_printed"],
            status="Published source or finding aid · original genealogical identity unverified",
            source_date=item["year"],
        ))
    for pid, person in people_by_id.items():
        from family_data import life_span
        records.append(_item(
            id="person:" + pid, category="Existing family profiles",
            title=person.get("full_name") or pid,
            summary="Recorded lifetime: " + life_span(person) + ". Open this person to examine specific citations and relationships.",
            limits="An existing tree profile is not itself proof of every listed parent, spouse or child.",
            people_ids=[pid], route="?page=people&profile=" + quote(pid),
            keywords=" ".join(map(str, person.get("alternate_names", []) or [])),
        ))

    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate discovery result IDs")
    return records


def search_index(records: list[dict], *, query: str = "", category: str = "",
                 person_id: str = "", show_ocr: bool = True, book_page: int = 0) -> list[dict]:
    """Token-AND matching; exact-ID person filter never uses fuzzy name inference."""
    tokens = [v.casefold() for v in WORD.findall(query or "")]
    results = []
    for row in records:
        if category and row["category"] != category:
            continue
        if person_id and person_id not in row["person_ids"]:
            continue
        if book_page and book_page not in row["pages"]:
            continue
        if not show_ocr and row["category"] == "Scanned book OCR leads":
            continue
        haystack = " ".join(str(row.get(k, "")) for k in
                            ("title", "summary", "limits", "keywords", "source_date")).casefold()
        if tokens and not all(token in haystack for token in tokens):
            continue
        results.append(row)
    return sorted(results, key=lambda row: (PRIORITY[row["category"]],
                                         str(row["title"]).casefold(), row["id"]))


def overview(records: list[dict]) -> dict:
    counts = Counter(row["category"] for row in records)
    return {"total": len(records), "by_category": dict(counts),
            "unique_book_pages": len({page for row in records
                if row["category"] == "Scanned book OCR leads" for page in row["pages"]}),
            "profile_ids_with_photo": len({pid for row in records
                if row["category"] == "Scanned book photographs" for pid in row["person_ids"]}),
            "unresolved_book_names": len([r for r in records if r["id"].startswith("unresolved:")])}


def case_packet(row: dict) -> str:
    """Safe, reproducible plain Markdown case notes with links, not copied media."""
    content = [
        "# Family history evidence packet: " + row["title"],
        "",
        "**Research status:** " + row["status"],
        "**Catalog category:** " + row["category"],
        "",
        "## What the source or research currently says",
        row["summary"] or "No summary transcribed.",
        "",
        "## What is not established",
        row["limits"] or "Individual original-source verification is still required.",
        "",
        "## Original records and links",
    ]
    if row["route"]:
        content.append("- Family archive: " + row["route"])
    for source in row["sources"]:
        content.append("- " + source["title"] + ": " + source["url"])
        if source.get("note"):
            content.append("  - " + source["note"])
    for page in row["pages"]:
        content.append("- *The Colony* PDF page " + str(page) +
                       ": ?page=family-books&book_page=" + str(page))
    content.extend([
        "", "## Research standard",
        "This is a navigation packet, not an independent verification of parentage, "
        "marriage, ownership or identity. Inspect original scans before updating "
        "the family tree. External copyrighted material is linked, not reproduced.",
    ])
    return "\n".join(content) + "\n"
