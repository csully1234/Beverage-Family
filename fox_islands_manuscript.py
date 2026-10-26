"""Original 1785–1786 Fox Islands legislative manuscripts: searchable image gallery.

Seven archival copies are accompanied by their source labels, honest partial
readings, archival provenance, and uncertainty about identity/handwritten age.
The optimized JPEGs are displayed directly; original TIFFs remain separate.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

import streamlit as st
from routing_ui import route_link

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "phase47_fox_islands_original_manuscripts.json"
IMAGES_DIR = ROOT / "static" / "approved_media" / "fox_islands_1785"
EXPECTED_LEAVES = ("petition-1", "petition-2", "petition-3", "petition-4",
                   "resolve-1", "resolve-2", "resolve-3")
EXPECTED_PEOPLE = ("James Beveridge", "Thomas Beveridge", "Matthew Beveridge")
IMAGE_STATUS = "optimized_jpegs_hosted_original_tiffs_archived_offline"
SELECTOR_KEY = "fox-1785-manuscript-leaf-selector"


def leaf_image_path(leaf: dict, root: Path = IMAGES_DIR) -> Path:
    """Only declared, relative JPEG basenames are allowed: never user-supplied paths."""
    name = str(leaf.get("image_file") or "")
    if (not name or name != Path(name).name or
            not name.endswith(".jpg") or
            name != str(leaf["id"]).replace("-", "_").replace(
                "petition_", "petition_page_").replace("resolve_", "resolve_page_") + ".jpg"):
        raise ValueError("Unrecognized Fox Islands image basename: " + name)
    return root / name


def load_fox_manuscripts(path: Path = DATA_FILE, image_dir: Path = IMAGES_DIR) -> dict:
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValueError("Expected one versioned manuscript collection")
    record = entries[0]
    if tuple(row["id"] for row in record["leaves"]) != EXPECTED_LEAVES:
        raise ValueError("Seven original leaves required, in manuscript order")
    if record["manuscripts_locally_available"] != len(EXPECTED_LEAVES):
        raise ValueError("Manuscript leaf count inconsistent")
    if record["manuscript_images_status"] != IMAGE_STATUS:
        raise ValueError("Published scans must be honestly described")
    if record["settler_count_in_resolve"] != 72 or record["survey_acres"] != 16527:
        raise ValueError("Original historic figure changed without paleographic review")
    if record["eligibility_date"] != "1784-01-01":
        raise ValueError("Original date cut-off changed")
    if tuple(row["name"] for row in record["key_findings"]) != EXPECTED_PEOPLE:
        raise ValueError("Name index changed without review")
    mentions = record["key_findings"]
    if (len({m["id"] for m in mentions}) != 3 or
            any(m["leaf"] != 3 or m["document"] != "petition" for m in mentions)):
        raise ValueError("Name mentions may not become unsupported identities")
    variants = record.get("primary_secondary_variants", [])
    if len(variants) != 5 or len({row["id"] for row in variants}) != 5:
        raise ValueError("Original/printed textual variants incomplete")
    matthew = mentions[2]
    if (matthew.get("age_status") != "disputed_from_original_handwriting" or
            "major" not in matthew["age_annotation_diplomatic"] or
            "a minor" not in matthew["age_annotation_diplomatic"]):
        raise ValueError("Matthew's age annotation remains disputed")
    for leaf in record["leaves"]:
        if leaf["full_transcription_verified"] or leaf.get("image_status") != "published_optimized_scan":
            raise ValueError("An incomplete transcription cannot be marked complete")
        digest = str(leaf.get("original_tiff_sha256") or "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Missing original TIFF SHA256 source-provenance digest")
        file_path = leaf_image_path(leaf, image_dir)
        if not file_path.is_file() or file_path.stat().st_size < 8_000:
            raise ValueError("Missing published Fox Islands page image: " + str(file_path))
        with file_path.open("rb") as f:
            if f.read(3) != b"\xff\xd8\xff":
                raise ValueError("Invalid JPEG page scan: " + str(file_path))
    return record


def manuscript_publication_ready(record: dict) -> bool:
    """A positive, documented archive publication approval is mandatory."""
    rights = record.get("publication_clearance") or {}
    return bool(rights.get("form_received") is True and
                rights.get("archive_credit_verified") is True and
                rights.get("status") == "confirmed")


def name_mentions(data: dict | None = None) -> list[dict]:
    return list((data or load_fox_manuscripts())["key_findings"])


def manuscript_csv(data: dict | None = None) -> str:
    record = data or load_fox_manuscripts()
    out = io.StringIO()
    fields = ("id", "group", "leaf", "label", "description", "excerpt",
              "confidence", "source_file", "image_file", "original_tiff_sha256")
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for leaf in record["leaves"]:
        writer.writerow({k: leaf.get(k, "") for k in fields})
    return out.getvalue()


def all_scans_zip(record: dict) -> bytes:
    """Create an indexed, provenance-preserving bundle of published derivatives."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=5) as bundle:
        bundle.writestr("MANIFEST.csv", manuscript_csv(record))
        for leaf in record["leaves"]:
            p = leaf_image_path(leaf)
            bundle.write(p, arcname="fox_islands_1785/" + p.name)
    return output.getvalue()


def sync_leaf_url() -> None:
    """Maintain shareable source citations for each of the seven actual scans."""
    current = st.session_state.get(SELECTOR_KEY)
    if current in EXPECTED_LEAVES:
        st.query_params["leaf"] = current
        st.session_state["_fox_last_url_leaf"] = current


def move_leaf(direction: int) -> None:
    """Streamlit on_click runs before the leaf selector is recreated."""
    old = st.session_state.get(SELECTOR_KEY, EXPECTED_LEAVES[0])
    idx = EXPECTED_LEAVES.index(old) if old in EXPECTED_LEAVES else 0
    st.session_state[SELECTOR_KEY] = EXPECTED_LEAVES[(idx + direction) % len(EXPECTED_LEAVES)]
    sync_leaf_url()


def render_original_manuscripts() -> None:
    record = load_fox_manuscripts()
    st.subheader("1785–1786 · Original Fox Islands legislative papers")
    st.write(
        "Read the actual archival page images, not just later printed versions. "
        "The Massachusetts legislative file includes **four petition leaves** "
        "and **three resolve leaves**. The scans below are optimized JPEG "
        "copies; original full-resolution TIFFs are preserved separately."
    )
    st.caption("Original provenance: " + record["archival_identifier"])
    if not manuscript_publication_ready(record):
        st.warning(
            "The seven image files have been prepared in a development branch, "
            "but Massachusetts Archives requires a Permission to Publish form "
            "and approved credit before manuscript images are published. "
            "The full-page public viewer and downloads remain disabled until "
            "those requirements are documented."
        )
        st.write(
            "The petition names James, Thomas and Matthew Beveridge. Matthew "
            "is annotated 'a minor' with another lower word possibly reading "
            "'major'; its meaning is unresolved. The handwritten 1786 resolve "
            "reads 72 settlers before January 1, 1784, while the 1889 "
            "printed edition reads 75 in the same sentence. Neither fact "
            "establishes genealogical relationships."
        )
        route_link("Read the Maine State Archives 1785 island survey",
                   "https://digitalmaine.com/planbook_knox_county/8/")
        st.caption("Manuscript citation: Massachusetts Archives, SC1 / "
                   "Series 228, February 1785 session, Chapter 97.")
        return
    left, middle, right = st.columns(3)
    left.metric("Original manuscript leaves", 7)
    middle.metric("Beveridge name occurrences", 3)
    right.metric("Proven genealogical links from petition", 0)

    st.markdown("**Find the original handwriting — Petition leaf 3**")
    cols = st.columns(3)
    detail_files = ("james_beveridge.jpg", "thomas_beveridge.jpg",
                    "matthew_beveridge.jpg")
    for col, mention, name in zip(cols, name_mentions(record), detail_files):
        with col.container(border=True):
            st.markdown("**" + mention["name"] + "**")
            st.image(str(IMAGES_DIR / "details" / name),
                     caption="Close reading, original petition leaf 3",
                     width="stretch")
            st.caption(mention["column"].capitalize() + " column")
            st.write(mention["evidence"])
            if mention.get("age_status"):
                st.warning("Age status disputed: " + mention["age_annotation_diplomatic"])
            st.caption("No verified person-ID or family relationship assigned.")
    with st.expander("Enlarge Matthew's disputed lower annotation"):
        st.image(str(IMAGES_DIR / "details" / "matthew_age_annotation.jpg"),
                 caption="Enlarged excerpt: 'a minor' above apparent 'major' note",
                 width="stretch")
        st.caption("The lower word's transcription, author, date and purpose "
                   "remain unverified. Read it in context on petition leaf 3.")

    requested_leaf = st.query_params.get("leaf")
    if isinstance(requested_leaf, list):
        requested_leaf = requested_leaf[0] if requested_leaf else ""
    if (requested_leaf in EXPECTED_LEAVES and
            st.session_state.get("_fox_last_url_leaf") != requested_leaf):
        st.session_state[SELECTOR_KEY] = requested_leaf
        st.session_state["_fox_last_url_leaf"] = requested_leaf
    elif st.session_state.get(SELECTOR_KEY) not in EXPECTED_LEAVES:
        st.session_state[SELECTOR_KEY] = EXPECTED_LEAVES[0]

    by_id = {row["id"]: row for row in record["leaves"]}
    st.markdown("### Original-page image viewer")
    p, q, n = st.columns([1, 4, 1], gap="small")
    with p:
        st.button("Previous", on_click=move_leaf, args=(-1,),
                  key="fox-1785-previous", width="stretch")
    with q:
        st.selectbox("Manuscript leaf", EXPECTED_LEAVES,
                     format_func=lambda key: by_id[key]["label"],
                     key=SELECTOR_KEY, label_visibility="collapsed",
                     on_change=sync_leaf_url)
    with n:
        st.button("Next", on_click=move_leaf, args=(1,),
                  key="fox-1785-next", width="stretch")
    selected = by_id[st.session_state[SELECTOR_KEY]]
    st.caption(selected["description"])

    with st.container(border=True):
        st.image(str(leaf_image_path(selected)), width="stretch",
                 caption=(selected["label"] + " · Massachusetts Archives SC1/Series 228 "
                          "· Digitally optimized manuscript copy"))
        st.caption("Image scanned from the original TIFF copy; some handwriting "
                   "remains unsettled. Download for detailed local zoom or review.")
        st.download_button(
            "Download this manuscript page (JPEG)",
            data=leaf_image_path(selected).read_bytes(),
            file_name=selected["image_file"], mime="image/jpeg",
            key="fox-1785-download-current-page",
        )
    with st.expander("Selected reading, source details, and caveats", expanded=True):
        st.code(selected["excerpt"], language=None)
        st.caption("Reading status: " + selected["confidence"])
        st.caption("Original TIFF: " + selected["source_file"])
        st.caption("Original SHA-256: " + selected["original_tiff_sha256"])
        st.caption("Complete verified diplomatic transcription: no")

    with st.expander("Compare the original 1786 resolution to the 1889 printing"):
        st.warning(
            "The original resolve reads **seventy two settlers before January 1, 1784**; "
            "the 1889 printed transcription renders the SAME sentence as "
            "**seventy-five settlers**. The reason for this difference is unknown."
        )
        for entry in record["primary_secondary_variants"]:
            st.markdown("**" + entry["source"] + "**")
            st.write(entry["reading"])
            st.caption(entry["notes"])
        st.caption("Matthew's apparent second annotation (possibly 'major') is "
                   "not a verified correction. Neither note establishes his age or kinship.")

    with st.expander("What the conditional grant does and does not establish"):
        st.write(
            "The original March 1786 resolution recites **16,527 surveyed acres**, "
            "a **January 1, 1784** settlement eligibility condition, and public "
            "reservations. It does not identify exact individual Beveridge "
            "allotments or who the other ten people in the 1790 Thomas "
            "Beverege household were."
        )
        st.warning(record["limits"])
        route_link("View the 1785 archived survey map",
                   "https://digitalmaine.com/planbook_knox_county/8/")
        route_link("Compare 1790 and 1820 original-census research",
                   "?page=collection&view=source-expedition&early-islands=1")
        route_link("Compare 1837 Hope probate evidence",
                   "?page=collection&view=waldo-probate")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download all seven scan images + provenance",
            data=all_scans_zip(record),
            file_name="fox_islands_1785_1786_original_scans_and_manifest.zip",
            mime="application/zip",
            key="fox-1785-download-bundle",
            width="stretch",
        )
    with c2:
        st.download_button(
            "Download manuscript page index (CSV)",
            manuscript_csv(record),
            file_name="fox_islands_1785_1786_page_index.csv",
            mime="text/csv", width="stretch",
            key="fox-1785-download-index",
        )

    with st.expander("Archival and supporting citations"):
        for source in record["sources"]:
            st.markdown("**" + source["title"] + "**")
            st.caption(source["type"])
            if source.get("url"):
                route_link("Open source with custodian", source["url"], type="tertiary")
    with st.expander("What must still be located"):
        for item in record["outstanding"]:
            st.write("• " + item)
        st.caption(record["published_image_policy"])
