"""Visitor-facing stories, people directory, media catalog and historical documents.

Only researched claims and repository-backed assets appear here. An image description
is not treated as a hosted photograph, and unresolved genealogical identities remain
explicitly uncertain.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st

from routing_ui import route_link, route_markdown
from research_collection_ui import load_collection, render_finding
from family_data import life_span, year_from_date
from evidence_explorer import render_exhibit_library, render_investigations, investigation_catalog

ROOT = Path(__file__).resolve().parent
MEDIA_ROOT = (ROOT / "static" / "approved_media").resolve()
MEDIA_MANIFEST = ROOT / "data" / "media_manifest.json"

STORIES = (
    {
        "id": "matthew-rockland-descendants-1865",
        "title": "Matthew's reported children and Nathaniel's separate family",
        "period": "Early 1800s to 1865",
        "summary": "Explore Matthew's ten reported children and the Rockland relatives listed in a near-contemporary published history.",
        "body": "Cyrus Eaton's 1865 history names Capt. Matthew Beverage of Hope, two wives, ten children and several grandchildren. It separately describes Nathaniel Beverage (born about 1804), his wife Sarah Alexander and their three children. These are published family groups, not ten independently certified relationships. Nathaniel's father and the exact degree of his connection to Matthew remain unproved. Nathaniel born about 1804 must not be confused with Nathaniel Winslow Beverage born 1776.",
        "terms": ("Matthew", "Nathaniel", "Beverage"),
        "family_group": True,
        "source_links": (
            ("Read the 1865 family history, vol. II, pp.146–147", "https://www.scribd.com/document/845728319/History-of-Thomaston-Rockland-and-South"),
            ("Compare the compiled Nathaniel parentage hypothesis", "https://genealogyofnewengland.com/f_86c9.htm"),
            ("Indexed marriage evidence for Henry T. and Ella Allen", "https://ancestors.familysearch.org/en/GM6N-6CV"),
        ),
    },
    {
        "id": "north-haven-preserving-family-history",
        "title": "When North Haven saved its history",
        "period": "1907–2009",
        "summary": "Early school graduates, a 1927 auction notice, 1930s film and town documents rescued in 1975.",
        "body": "The North Haven Historical Society reports that old deeds, maps, bridge-construction bills and historical papers recovered from the town dump inspired its organizing meeting on November 13, 1975. Its account credits Sam Beverage, Lewis Haskell and others with finding these records. The society also hosts 1930s film taken by Harold Beverage and describes the first North Haven high-school class of 1907, including Elsie and Jennie Beverage. A July 30, 1927 Courier Gazette notice announces an August 24 auction of the Sands H. Witherspoon homestead at Pulpit Harbor with 'Frank Beverage, Auctioneer'; this shows a proposed sale, not proof of a completed transaction or of which Frank acted. The film and images remain on their rights holders' websites. The historical society also publishes Tonny Calderwood's diaries. In an October 15, 1937 entry, Tonny describes Frank and May Beverage's golden wedding anniversary and records a caption for a photograph of the couple. His 1967 entries describe writing to a Samuel Beverage about Calderwood family information. These entries illustrate the family's daily life and historical research, but do not independently establish which existing Frank or Samuel profile they describe. The diaries and images are owned by others; the site links the original archive without copying the content. The society also offers a corrected 2009 edition of a history of Pulpit Harbor by Seward E. Beacom.",
        "terms": ("North Haven", "Pulpit Harbor", "Beverage"),
        "source_links": (
            ("Historical Society: recovered records in 1975", "https://www.northhavenmainehistoricalsociety.org/history.html"),
            ("Harold Beverage's historical film", "https://www.northhavenmainehistoricalsociety.org/videos.html"),
            ("First high-school graduating class, 1907", "https://www.northhavenmainehistoricalsociety.org/a-free-high-school.html"),
            ("Courier Gazette July 30, 1927 original", "https://upload.wikimedia.org/wikipedia/commons/2/2a/Courier_Gazette_July_30_1927.pdf"),
            ("Tonny Calderwood's 1937 diary: Frank and May's 50th anniversary", "https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/1937.pdf#page=29"),
            ("Tonny Calderwood's 1967 diary: Samuel Beverage genealogy correspondence", "https://www.northhavenmainehistoricalsociety.org/uploads/5/2/8/7/5287313/1967.pdf#page=54"),
            ("Original Calderwood diary archive and rights information", "https://www.northhavenmainehistoricalsociety.org/calderwood-diaries.html"),
            ("Pulpit Harbor Two Hundred Years and 2009 corrected edition", "https://www.northhavenmainehistoricalsociety.org/shop.html"),
        ),
    },
    {
        "id": "topsham-beveridge-before-fox-islands",
        "title": "Before North Haven: Beveridge names in Topsham",
        "period": "1749–1776, with nineteenth-century records",
        "summary": "A 1749 recorded intention for James and Jean plus 1750s Topsham lots may help identify the family's mainland origins.",
        "body": "An 1888 publication of Brunswick marriage intentions records James Beveridge and Jean White, both of Georgetown, on February 6, 1749. This proves a published intention, not that a wedding occurred or that the couple is uniquely identified with the family tree. In an 1878 history of Brunswick, Topsham and Harpswell, Samuel Beveridge appears in a numbered historical map key for Topsham. A derivative early-settler listing based on the history associates Samuel with lot 3 in 1752 and James Beveridge with lot 7 in 1758. A separate family sketch tentatively reports Mercy Beveridge marrying James Henry on February 15, 1776. These names may provide clues to the mainland kinship network that preceded North Haven, but the source does not prove whether James or Samuel are the men in this website's current early family tree, establish an acreage, or positively identify Mercy. Original deeds, probate records and a contemporary marriage entry are still needed.",
        "terms": ("Topsham", "Beveridge", "Mercy"),
        "source_links": (
            ("1749 Brunswick marriage-intention transcription", "https://archives.mainegenealogy.net/2008/06/brunswick-marriage-intentions-1740-1764.html"),
            ("Read Wheeler's complete 1878 town history", "https://www.loc.gov/resource/gdcmassbookdig.historyofbrunswi01whee/"),
            ("Locate the numbered historical map references", "https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-5.htm"),
            ("Compare the early-settlers index", "https://genealogytrails.com/maine/sagadahoc/history_earlysettlerstopsham.html"),
            ("Read the tentative Henry–Beveridge marriage passage", "https://ldsgenealogy.com/ME/books/History-of-Brunswick-Topsham-and-Harpswell-Maine-including-the-ancient-territory-known-as-Pejepscot-part-79.htm"),
        ),
    },
    {
        "id": "fox-islands-land-matthew",
        "title": "The Fox Islands land petition and Matthew Beveridge",
        "period": "1785–1786, with later family histories",
        "summary": "An early land petition names James, Thomas and a minor Matthew Beveridge; a potential missing family branch needs verification.",
        "body": "The Fox Islands settlers sought secure title following wartime displacement. A 1785 petition, preserved in later transcriptions, names James Beveridge, Thomas Beveridge and Matthew Beveridge (a minor) among the claimants; George White and John Calderwood represented the inhabitants as attorneys. The March 1786 resolution conditionally granted the island group to qualifying settlers, not a defined number of acres to the Beveridges. A 2025 genealogical study dates the land petition to June 1, 1785 and cites a separate 1786 original survey report recording settlers’ declared years of residence. An 1865 local history separately describes a Capt. Matthew Beverage of Hope, his two wives and ten children, but original records are still required to prove he was the same Matthew or Capt. Thomas Beverage's brother. The Maine State Archives retains the 1785 survey and 1786 island plans, so this history can be explored alongside period maps without drawing imaginary property boundaries.",
        "terms": ("Fox Islands", "Matthew", "land"),
        "source_links": (
            ("2025 professional research citing original 1786 settlement declarations", "https://maineroots.org/images/Nov25TMG2.pdf"),
            ("1785 Maine State Archives survey", "https://digitalmaine.com/planbook_knox_county/8/"),
            ("1786 Fox Islands plan (Pulpit Harbor)", "https://digitalmaine.com/planbook_8/17/"),
            ("1889 transcribed petition and grant", "https://tile.loc.gov/storage-services/public/gdcmassbookdig/briefhistoricals00vinl/briefhistoricals00vinl.pdf"),
            ("1935 Carver genealogy", "https://archive.org/details/carverfamilyofne00carv_0"),
            ("1865 Capt. Matthew genealogical account", "https://www.scribd.com/document/845728319/History-of-Thomaston-Rockland-and-South"),
        ),
    },
    {
        "id": "thomas-revolution",
        "title": "Thomas Beverage and the American Revolution",
        "period": "1781–1786",
        "summary": "A sworn statement about a British fishing pass, a schooner named Ann and disputed wartime ownership.",
        "body": "In 1786, Thomas Beverage provided a sworn declaration at Fox Island at Paul Reed's request. Thomas said he personally witnessed Robert Duglass obtain a fishing pass from British Captain Henry Mowat. The remainder of his statement reports what Duglass told him about a schooner, an alleged bill of sale and a possible trading arrangement behind British lines. The papers also include Reed's failed petition to reopen a civil judgment. They do not establish Thomas's politics or conclusively connect this witness to every Thomas in a compiled family tree.",
        "terms": ("Thomas Beverage", "Fox Island", "Paul Reed"),
        "document": "thomas-1786",
    },
    {
        "id": "harold-radio",
        "title": "Harold Beverage and long-distance radio",
        "period": "Twentieth century",
        "summary": "The engineering work of Harold H. Beverage, including the antenna that bears his name.",
        "body": "The site's existing engineering and family sources record Harold Beverage's work in radio communications. Explore his biography, family connections and original engineering references rather than relying on a short invention anecdote.",
        "terms": ("Harold", "antenna", "radio"),
    },
    {
        "id": "beveridge-point",
        "title": "The history of Beveridge Point",
        "period": "North Haven, Maine",
        "summary": "Family memories, historical island life and records that may explain the Point's story.",
        "body": "A 1958 diary transcription references hauling wood from Beveridge's Point for Eliot Beveridge. This is evidence of the place name and activity, not by itself a deed or proof of exact property boundaries. Related island-registry and land records remain separate leads that require original documents.",
        "terms": ("Beveridge Point", "Point", "land"),
    },
    {
        "id": "islebuilt",
        "title": "IsleBuilt: boats made on North Haven",
        "period": "From 1955",
        "summary": "Eliot Beveridge's boatbuilding operation and the search for surviving boats.",
        "body": "Historical Society research associates Eliot Beveridge with IsleBuilt, a North Haven boat operation that reportedly produced more than 350 boats. Original advertisements, photographs, construction records and surviving vessels remain promising research targets.",
        "terms": ("IsleBuilt", "Eliot", "boats"),
    },
    {
        "id": "lowell-music",
        "title": "Lowell Beveridge: a life in music",
        "period": "Twentieth century",
        "summary": "Church music at Columbia and the reported Universal Harmony manuscript.",
        "body": "Lowell Pierson Beveridge served as an organist and music leader at Columbia. A memorial describes a large manuscript called Universal Harmony; its current archival location still needs verification. Recent review of a contemporary institutional record also affects the reported birthplace and remains explicitly labeled as a proposed correction.",
        "terms": ("Lowell", "music", "Universal Harmony"),
    },
    {
        "id": "island-life",
        "title": "Everyday life on North Haven",
        "period": "Nineteenth and twentieth centuries",
        "summary": "Farming, schools, island shipping, trades and families at work.",
        "body": "Historic photographs, diaries and accounts tell the story of island farms, freight, schoolrooms and waterfront labor. Item dates and person identifications should be checked against their original captions, rather than assumed from a surrounding historical narrative.",
        "terms": ("North Haven", "farms", "schools"),
    },
)

DOCUMENTS = {
    "thomas-1786": {
        "title": "Thomas Beverage's sworn testimony and the Paul Reed petition",
        "research_ids": ("BF-R001", "BF-R002"),
        "date": "June 1, 1786 (testimony); June 14–15, 1786 (legislative action)",
        "citation": "Documentary History of the State of Maine, vol. XXI (1916), printed pp. 214–222; Thomas Beverage's statement on pp. 221–222.",
        "url": "https://archive.org/details/documentaryhisto21mainuoft/page/220/mode/2up",
        "pdf_url": "https://sites.rootsweb.com/~mealhn/books/mehist_v21.pdf#page=241",
        "summary": "Paul Reed asked the Massachusetts General Court to set aside a £120 judgment arising from the schooner Ann. His petition was referred to a committee. Thomas testified at Reed's request; the committee recommended allowing Reed to withdraw his petition, rather than granting a new trial.",
        "excerpt": "I Thomas Beverage of Lawful Age do Testify and say ... Robert Duglass Then an Inhabitant of Fox Island, Procured a Pass of Capt Henry Mowit in my Presents, for Fishing ...",
        "limits": "The source is a 1916 printed transcription of historical papers, not the original handwritten affidavit or a verbatim trial transcript. Thomas personally observed the permit but repeated Duglass's account of the bill of sale and proposed trade. The identification of this witness with a particular Thomas in the family tree still requires corroboration.",
    },
}


def _year(value: object) -> int | None:
    """Extract an approximate year only for ordering, never display it as exact."""
    match = re.search(r"(?<!\d)(1[6-9]\d{2}|20\d{2})(?!\d)", str(value or ""))
    return int(match.group(1)) if match else None


def approved_assets() -> dict[str, dict]:
    """Read only local, explicitly licensed and reviewed image assets."""
    if not MEDIA_MANIFEST.is_file():
        return {}
    try:
        payload = json.loads(MEDIA_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    result: dict[str, dict] = {}
    for entry in payload if isinstance(payload, list) else []:
        if not isinstance(entry, dict) or entry.get("rights_status") not in {"permission", "public_domain"}:
            continue
        identifier = str(entry.get("item_identifier") or "")
        relative = str(entry.get("local_path") or "")
        if not identifier or not relative.startswith("static/approved_media/"):
            continue
        path = (ROOT / relative).resolve()
        if path != MEDIA_ROOT and MEDIA_ROOT not in path.parents:
            continue
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"} or not path.is_file():
            continue
        result[identifier] = {**entry, "path": str(path)}
    return result


SORT_OPTIONS = ("Surname A–Z", "Surname Z–A", "First name A–Z", "First name Z–A", "Birth year (oldest first)", "Birth year (newest first)")


_DISAMBIGUATION = re.compile(r"\s*\([^()]*\)\s*$")
_GENERATION_SUFFIX = re.compile(r"^(?:jr\.?|sr\.?|ii|iii|iv|v)$", re.I)


def _name_parts(person: dict) -> tuple[str, str]:
    """Find the primary family name, ignoring year/alias and Jr/III suffixes.

    A displayed name such as 'John White (1748)' must sort under W, not
    under '(1748)'. The original display name is never changed.
    """
    full_name = str(person.get("full_name") or "").strip()
    base = full_name
    while True:
        trimmed = _DISAMBIGUATION.sub("", base).strip()
        if trimmed == base:
            break
        base = trimmed
    words = base.split()
    while words and _GENERATION_SUFFIX.fullmatch(words[-1]):
        words.pop()
    if not words:
        return "", full_name
    return words[-1].casefold(), " ".join(words[:-1]).casefold()


def surname_first_label(person: dict) -> str:
    """Make a surname-sorted dropdown visually obvious to people browsing it."""
    name = str(person.get("full_name") or "")
    surname, _ = _name_parts(person)
    if not surname:
        return name
    original = name
    # Remove trailing annotations from the name but keep them in the label.
    annotations = []
    while True:
        m = _DISAMBIGUATION.search(original)
        if m is None:
            break
        annotations.insert(0, m.group().strip())
        original = original[:m.start()].strip()
    words = original.split()
    suffixes = []
    while words and _GENERATION_SUFFIX.fullmatch(words[-1]):
        suffixes.insert(0, words.pop())
    if not words:
        return name
    family = words.pop()
    rest = " ".join(words)
    extra = " ".join([*suffixes, *annotations])
    return f"{family}, {rest}" + (f" {extra}" if extra else "")


def _surname_first_key(person: dict) -> tuple:
    surname, given = _name_parts(person)
    return (surname, given, str(person.get("full_name") or "").casefold(), str(person.get("id") or ""))


def order_people(people, order="Surname A–Z") -> list[dict]:
    if order == "Surname Z–A":
        return sorted(people, key=_surname_first_key, reverse=True)
    if order in {"First name A–Z", "First name Z–A"}:
        return sorted(people, key=lambda person: (str(person.get("full_name") or "").casefold(), str(person.get("id") or "")), reverse=order == "First name Z–A")
    if order == "Birth year (oldest first)":
        return sorted(people, key=lambda person: (year_from_date(person.get("birth_date")) or 9999, _surname_first_key(person)))
    if order == "Birth year (newest first)":
        return sorted(people, key=lambda person: (-(year_from_date(person.get("birth_date")) or 0), _surname_first_key(person)))
    return sorted(people, key=_surname_first_key)


def render_people_directory(people: list[dict], people_by_id: dict) -> None:
    """An index by name and birth period; it does not infer new relationships."""
    st.write("Browse a relative, or search a name without needing to know the exact spelling.")
    query = st.text_input("Find a person", placeholder="Name or alternate spelling…", key="directory_query").casefold().strip()
    period = st.selectbox("Birth period", ["Any period", "Before 1800", "1800s", "1900s", "2000s", "Unknown"], key="directory_period")
    from family_search import person_match
    order = st.selectbox("Sort people", SORT_OPTIONS, key="directory_sort")
    people = order_people(people, order)
    matches = []
    for person in people:
        if query and not person_match(query, person):
            continue
        birth = _year(person.get("birth_date"))
        if period == "Before 1800" and (birth is None or birth >= 1800):
            continue
        if period == "1800s" and (birth is None or not 1800 <= birth < 1900):
            continue
        if period == "1900s" and (birth is None or not 1900 <= birth < 2000):
            continue
        if period == "2000s" and (birth is None or birth < 2000):
            continue
        if period == "Unknown" and birth is not None:
            continue
        matches.append(person)
    st.caption(f"{len(matches)} of {len(people)} people")
    if not matches:
        st.info("No matching profiles. Try fewer letters, a different spelling or another period.")
        return
    st.caption("Every matching person is listed below in the selected order. No pages and no hidden results.")
    if st.session_state.get("directory_jump") not in {"", *[p["id"] for p in matches]}:
        st.session_state["directory_jump"] = ""
    st.selectbox(
        "Jump to a person",
        options=["", *[person["id"] for person in matches]],
        format_func=lambda pid: (
            f"{surname_first_label(people_by_id[pid]) if order.startswith('Surname') else people_by_id[pid]['full_name']} · {life_span(people_by_id[pid])}"
            if pid else "Choose any person from the complete list…"
        ),
        key="directory_jump",
    )
    if st.session_state.get("directory_jump") in people_by_id:
        target = st.session_state["directory_jump"]
        route_link("Open selected person's profile",
                   "?" + urlencode({"page": "people", "profile": target}),
                   type="primary")
    st.markdown("**All matching relatives**")
    for person in matches:
        label = surname_first_label(person) if order.startswith("Surname") else str(person.get("full_name", "Unknown"))
        route_link(f"{label} · {life_span(person)}",
                   "?" + urlencode({"page": "people", "profile": person["id"]}),
                   type="tertiary", width="stretch")


def render_stories_page() -> None:
    collection = load_collection()
    st.title("Stories & Discoveries")
    st.write("Explore the lives and events behind the family tree. Each story leads back to the research and source records.")
    story_id = st.query_params.get("story", "")
    story = next((s for s in STORIES if s["id"] == story_id), None)
    if story_id and not story:
        st.warning("Story not found; choose one below.")
    if story:
        route_link("← Browse all stories", "?page=stories")
        st.title(story["title"])
        st.caption(story["period"])
        st.write(story["body"])
        if story.get("family_group"):
            group_path = ROOT / "research" / "matthew_nathaniel_family_1865.json"
            if group_path.exists():
                families = json.loads(group_path.read_text(encoding="utf-8"))
                st.subheader("Capt. Matthew's children, as listed in 1865")
                st.caption("Source-attributed family history; original relationships and Matthew's 1785 identity remain unproved.")
                for wife in families["matthew"]["wives"]:
                    with st.expander("Children attributed to " + wife["name"]):
                        for child in families["matthew"]["children"]:
                            if child["by_wife"] != wife["name"]:
                                continue
                            st.markdown("**" + child["name"] + "**")
                            details = [child.get("information", "")]
                            if child.get("birth_approx"):
                                details.append("Born about " + str(child["birth_approx"]))
                            if child.get("death"):
                                details.append("Died " + child["death"])
                            st.write(" · ".join(part for part in details if part))
                            for grandchild in child.get("children", []):
                                st.caption("Reported next generation: " + grandchild["name"] +
                                           (", born about " + str(grandchild["birth_approx"])
                                            if grandchild.get("birth_approx") else ""))
                st.subheader("Nathaniel's separate Rockland household")
                nathaniel = families["nathaniel"]
                st.write(nathaniel["name"] + ", born about 1804, and " +
                         nathaniel["spouse"] + " are listed with " +
                         ", ".join(child["name"] for child in nathaniel["children"]) + ".")
                st.caption(nathaniel["candidate_parentage"]["status"])
                st.warning(nathaniel["candidate_parentage"]["generational_issue"])
                for person_id, label in (
                    ("nathaniel_beverage_1804_rockland", "Nathaniel's research profile"),
                    ("sarah_alexander_beverage_1808", "Sarah's research profile"),
                    ("henry_t_beverage_1841_rockland", "Henry T.'s research profile"),
                    ("ella_allen_beverage_1854", "Ella Allen's research profile"),
                ):
                    route_link(label, "?page=people&profile=" + person_id)
        if story.get("document"):
            route_link("Read the historical document", "?page=documents&doc=" + story["document"])
        if story.get("source_links"):
            st.subheader("Original sources and later transcriptions")
            for label, url in story["source_links"]:
                route_link(label, url)
            route_link("Explore the historical map atlas", "?page=map")
        st.subheader("Follow the evidence")
        seen = set()
        for term in story["terms"]:
            for finding in collection.select(query=term):
                rid = finding["Research ID"]
                if rid in seen:
                    continue
                seen.add(rid)
                with st.container(border=True):
                    st.markdown("**" + finding["Navigation"]["title"] + "**")
                    st.write(finding["Proposed fact or narrative"])
                    st.caption("Evidence: " + finding["Confidence"] + " · " + finding["Notes about uncertainty"])
                    route_link("Review evidence and original sources", "?page=collection&finding=" + rid)
                if len(seen) >= 5:
                    break
            if len(seen) >= 5:
                break
        if not seen and not story.get("source_links"):
            st.info("This story does not yet have a dedicated imported finding. Search the existing archive for supporting records.")
        route_link("Search this history", "?page=search&q=" + urlencode({"q": story["terms"][0]})[2:])
        return
    for index in range(0, len(STORIES), 2):
        cols = st.columns(2)
        for col, item in zip(cols, STORIES[index:index + 2]):
            with col.container(border=True):
                st.subheader(item["title"])
                st.caption(item["period"])
                st.write(item["summary"])
                route_link("Explore story", "?page=stories&story=" + item["id"], width="stretch")


def render_media_page() -> None:
    collection = load_collection()
    st.title("Photographs & Documents")
    st.write("Explore archival items and read historical records. We display original image files only when reuse rights and source identification are established.")
    with st.container(border=True):
        st.markdown("**The Colony — Complete Illustrated Family Book (2016)**")
        st.write("Explore all 305 original pages, including 82 cataloged historic-photo pages and 103 photographic, map and illustration pages altogether, with author credits and their printed captions.")
        route_link("Open the complete book and its visual collection", "?page=family-books")
    requested_case = str(st.query_params.get("case", "") or "")
    if requested_case in {case["id"] for case in investigation_catalog()}:
        # Deep links from a relative profile lead straight to the case file.
        render_investigations()
        st.divider()
    from colony_photos import render_colony_photographs
    photos_tab, images_tab, documents_tab, evidence_tab = st.tabs(
        ["Family photographs", "Other historical images", "Historical documents",
         "Explore original evidence"]
    )
    with photos_tab:
        render_colony_photographs()
    with images_tab:
        search = st.text_input("Search images, captions, people or places", key="media_search").strip()
        order = st.selectbox("Order", ["Oldest associated year", "Newest associated year", "Holding institution"], key="media_order")
        rows = [r for r in collection.inventory_rows("Images and Maps")
                if not search or search.casefold() in json.dumps(r, ensure_ascii=False, default=str).casefold()]
        if order == "Holding institution":
            rows.sort(key=lambda r: str(r.get("Holding institution", "")).casefold())
        else:
            rows.sort(key=lambda r: _year(r.get("Date")) or 9999, reverse=order == "Newest associated year")
        st.caption(f"{len(rows)} archival item descriptions. An associated research year is not necessarily the photograph's capture date.")
        approved = approved_assets()
        if not approved:
            st.info("Original thumbnails will appear here after approved scans and rights information are added. Until then, use each item's holding-institution link.")
        page_count = max(1, (len(rows) + 7) // 8)
        page = st.selectbox("Catalog page", range(1, page_count + 1), format_func=lambda n: f"{n} of {page_count}", key="media_page")
        for index in range((page - 1) * 8, min(page * 8, len(rows)), 2):
            for col, record in zip(st.columns(2), rows[index:index+2]):
                key = str(record.get("Collection or item identifier") or record.get("Item ID") or "")
                asset = approved.get(key)
                with col.container(border=True):
                    if asset:
                        st.image(asset["path"], caption=asset.get("credit") or record.get("Holding institution"))
                    else:
                        st.caption("Original scan not hosted")
                    st.markdown("**" + str(record.get("Subject", "Untitled archival item")) + "**")
                    st.caption(str(record.get("Date", "Undated")) + " · " + str(record.get("Holding institution", "")))
                    st.write(str(record.get("Item or caption", "")))
                    link = record.get("Direct item page")
                    if isinstance(link, str) and link.startswith(("https://", "http://")):
                        route_link("View original at archive", link)
                        with st.expander("Show original archive page here"):
                            st.caption("The holding institution controls whether previews are permitted. If blocked, use the original link above.")
                            st.components.v1.iframe(link, height=520, scrolling=True)
                    with st.expander("Identification, rights & citation"):
                        st.write("Identifier: " + key)
                        st.write("Rights: " + str(record.get("Rights", "Unknown")))
                        st.write("Review: " + str(record.get("Viewed status", "Not reviewed")))
                        st.write("Resolution: " + str(record.get("High resolution", "Unknown")))
    with documents_tab:
        for id_, document in DOCUMENTS.items():
            with st.container(border=True):
                st.markdown("**" + document["title"] + "**")
                st.caption(document["date"])
                st.write(document["summary"])
                route_link("Read document and original pages", "?page=documents&doc=" + id_)
    with evidence_tab:
        if not requested_case:
            cases_tab, sources_tab = st.tabs(
                ["Family history investigations", "All linked source records"]
            )
            with cases_tab:
                render_investigations()
            with sources_tab:
                render_exhibit_library()
        else:
            render_exhibit_library()


def render_document_page() -> None:
    doc_id = st.query_params.get("doc", "thomas-1786")
    item = DOCUMENTS.get(doc_id)
    if not item:
        st.warning("Unknown document.")
        route_link("Browse documents", "?page=media")
        return
    route_link("← Back to photographs and documents", "?page=media")
    st.title(item["title"])
    st.caption(item["date"])
    st.write(item["summary"])
    st.subheader("Original source")
    st.write(item["citation"])
    route_link("Open original scanned pages at Internet Archive", item["url"])
    route_link("Alternate PDF scan, page 241", item["pdf_url"])
    with st.expander("Preview external source within this page"):
        st.caption("The outside archive may prevent embedding. Use the direct links above if the preview is blank.")
        st.components.v1.iframe(item["pdf_url"], height=650, scrolling=True)
    st.subheader("Transcribed excerpt")
    st.write(item["excerpt"])
    st.caption("Excerpt only; consult the printed pages for exact wording and the complete deposition.")
    st.subheader("What this record does—and does not—prove")
    st.write(item["limits"])
    route_link("See the related family story", "?page=stories&story=thomas-revolution")
    route_link("Consult source-register entry SRC118", "?page=archive&source=SRC118")
