"""Original record retrieval and manual source review; does not send requests.

Research copies uploaded by a family researcher are session-scoped, not
stored in GitHub or published to the site. Exported JSON is a review packet,
NOT a canonical genealogy edit or archived image.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link, safe_external_url

FILE = Path(__file__).resolve().parent / "data" / "phase42_primary_document_acquisition.json"


def load_acquisition(path: Path = FILE) -> dict:
    content = json.loads(path.read_text(encoding="utf-8"))
    targets = content.get("targets") or []
    custodians = content.get("custodians") or []
    if len(targets) != 9 or len(custodians) < 5:
        raise ValueError("Primary source acquisition register is incomplete")
    ids = set()
    owners = {x["id"] for x in custodians}
    if len(owners) != len(custodians):
        raise ValueError("Repeated original-record custodian")
    for item in targets:
        if item["id"] in ids or not set(item["custodian_ids"]) <= owners:
            raise ValueError("Duplicate target or missing record custodian")
        ids.add(item["id"])
        if item["status"] == "original_inspected":
            raise ValueError("No Phase 42 target's original has been inspected")
        if not safe_external_url(item["url"]):
            raise ValueError("Unsafe public record finding aid")
    for custodian in custodians:
        if not safe_external_url(custodian["url"]):
            raise ValueError("Unsafe archive custody page")
    return content


def acquisition_route(target_id: str = "") -> str:
    prefix = "?page=collection&view=source-expedition&acquire=1"
    return prefix + ("&source_target=" + quote(target_id, safe="")
                     if target_id else "")


def acquisition_for_person(pid: str, data: dict | None = None) -> list[dict]:
    registry = data if data is not None else load_acquisition()
    return [x for x in registry["targets"] if pid in x["person_ids"]]


def request_draft(targets: list[dict], custodian: dict) -> str:
    """A stand-alone draft, never sent, with an explicit custody question."""
    if not targets:
        raise ValueError("Select at least one record target")
    lines = [
        "Subject: Historical Beverage/Beveridge original record location and copy inquiry",
        "",
        "Hello,",
        "",
        "I'm contacting " + custodian["name"] + " because your office or "
        "collection may be able to identify records relevant to the "
        "following family-history questions.",
        "",
        "I'm researching the early Beverage/Beveridge family of the Fox Islands "
        "and surrounding Maine towns for a family-history archive. Could you "
        "help identify whether your office or collection holds original or "
        "contemporary copied records for the following entries, or direct me "
        "to the appropriate custodian?",
        "",
    ]
    for target in targets:
        lines.extend([
            "- " + target["title"] + " — " + target["event"],
            "  Location: " + target["places"],
            "  Record sought: " + target["source_locator"],
            "",
        ])
    lines += [
        "If available, a legible digital photograph or noncertified copy of "
        "the COMPLETE register/deed/court page (including heading, adjoining "
        "entries if needed for context, and volume/page reference) would be "
        "ideal. Please let me know whether there are access or reproduction "
        "fees and whether a family website may display the resulting image "
        "with full institutional attribution.",
        "",
        "I understand that these are leads rather than confirmed entries, "
        "and would appreciate a correction if any date or volume is wrong.",
        "",
        "Thank you for your time and any guidance you can provide.",
    ]
    return "\n".join(lines)


def researcher_packet(*, target: dict, institution: str, shelf: str,
                      record_date: str, transcription: str,
                      observation: str, source_url: str = "",
                      firsthand: bool = False) -> dict:
    """Export claim metadata only; never a scan or fabricated genealogical edge."""
    if target.get("status") == "original_inspected":
        raise ValueError("Acquisition target should not already be closed")
    if source_url and not safe_external_url(source_url):
        raise ValueError("Invalid evidence source URL")
    text = transcription.strip()
    if not text:
        raise ValueError("An exact readable transcription is required")
    return {
        "format": "beverage-family-manuscript-review-v1",
        "target_id": target["id"],
        "source_title": target["title"],
        "original_target_status": target["status"],
        "reported_institution": institution.strip(),
        "actual_volume_page_or_image": shelf.strip(),
        "event_date_as_written": record_date.strip(),
        "transcription_exact_as_seen": text,
        "researcher_observation_not_source_text": observation.strip(),
        "source_url": source_url.strip(),
        "reviewer_reports_read_original": bool(firsthand),
        "verification_status": "researcher-submitted-unreviewed",
        "genealogy_auto_updated": False,
        "source_file_bytes_included": False,
        "next_step": "Check exact document image, handwriting, dates, independent sources and the correct person ID BEFORE proposing any canonical genealogy update.",
    }


def _target_callback() -> None:
    choice = st.session_state.get("acquisition_selected") or ""
    if choice:
        st.query_params["source_target"] = choice
        st.query_params["acquire"] = "1"
    elif "source_target" in st.query_params:
        del st.query_params["source_target"]
    st.session_state["_acquisition_url_target"] = choice


def render_acquisition_center(people: dict, *, selected: str = "") -> None:
    registry = load_acquisition()
    targets = sorted(registry["targets"], key=lambda t: t["priority"])
    by_id = {row["id"]: row for row in targets}
    custodians = {row["id"]: row for row in registry["custodians"]}
    st.subheader("Original record recovery desk")
    st.write("Nine high-value original documents that could verify—or overturn—"
             "early family relationships. Each entry says where to look, which "
             "institution may hold a copy, and what finding would count as proof.")
    st.caption("All nine remain UNINSPECTED here. Source locators are not actual "
               "handwritten findings. No emails have been sent, and no existing "
               "genealogy has been altered.")
    a, b, c = st.columns(3)
    a.metric("Originals to retrieve", len(targets))
    b.metric("Record custodians", len(custodians))
    c.metric("New ancestry links proved", 0)
    requested = selected if selected in by_id else ""
    if st.session_state.get("_acquisition_url_target") != requested:
        st.session_state["acquisition_selected"] = requested
        st.session_state["_acquisition_url_target"] = requested
    options = ["", *(t["id"] for t in targets)]
    chosen = st.selectbox(
        "Jump to a source document",
        options, key="acquisition_selected", on_change=_target_callback,
        format_func=lambda tid: "All original-document targets" if not tid
        else f"{by_id[tid]['priority']}. {by_id[tid]['title']}",
    )
    displayed = [by_id[chosen]] if chosen else targets
    for item in displayed:
        with st.expander(
            f"{item['priority']}. {item['title']} — ORIGINAL NOT YET INSPECTED",
            expanded=bool(chosen),
        ):
            st.caption(item["places"])
            st.write("Reported event: " + item["event"])
            st.markdown("**Where the actual record might be found**")
            st.write(item["source_locator"])
            st.markdown("**Precisely what to look for**")
            st.write(item["initial_query"])
            st.caption("What verification needs: " + item["evidence_needed"])
            st.warning(item["proof_weight"] + ". A name/age match alone "
                       "must never create an unverified family link.")
            route_link("Open existing record-finding aid", item["url"])
            route_link("Bookmark this exact original-record target",
                       acquisition_route(item["id"]), type="tertiary")
            for pid in item["person_ids"]:
                if pid in people:
                    route_link("Inspect relevant profile: " +
                               str(people[pid].get("full_name") or pid),
                               "?page=people&profile=" + quote(pid, safe=""),
                               type="tertiary")
            st.markdown("**Likely archive contacts — check custody first**")
            for owner_id in item["custodian_ids"]:
                owner = custodians[owner_id]
                route_link(owner["name"], owner["url"])
                st.caption(owner["role"] + " · " + owner["contact"])
    st.divider()
    st.markdown("#### Prepare a record request (never sent automatically)")
    st.caption("Choose an archive and record(s). This prepares a draft for "
               "your review; it neither emails anyone nor buys a copy.")
    owner_choice = st.selectbox(
        "Institution", list(custodians), key="acquisition_request_owner",
        format_func=lambda oid: custodians[oid]["name"])
    relevant = [t for t in targets if owner_choice in t["custodian_ids"]]
    selected_targets = st.multiselect(
        "Original records to ask about",
        [t["id"] for t in relevant],
        key="acquisition_request_list",
        format_func=lambda tid: by_id[tid]["title"],
    )
    if selected_targets:
        draft = request_draft([by_id[x] for x in selected_targets],
                              custodians[owner_choice])
        st.text_area("Review and copy the unsent inquiry", value=draft, height=260)
        st.download_button(
            "Download unsent archival inquiry (.txt)", draft,
            file_name="family-original-document-request-draft.txt",
            mime="text/plain",
        )
    else:
        st.info("Select a historical record above to compose an inquiry.")

    st.divider()
    st.markdown("#### Inspect a source copy and preserve your transcription")
    st.caption("A scan uploaded here is previewed in YOUR current browser session. "
               "It is NOT saved to the website, GitHub, or published to family "
               "members. Download the note packet and provide the scan separately "
               "for a reviewed website update.")
    reviewed_id = st.selectbox(
        "Which original document did you obtain?",
        [t["id"] for t in targets], key="acquisition_review_item",
        format_func=lambda tid: by_id[tid]["title"],
    )
    upload = st.file_uploader(
        "Optional image or PDF to inspect right now (session only)",
        type=["pdf", "png", "jpg", "jpeg"], key="acquisition_review_upload",
    )
    if upload is not None:
        if upload.size > 25 * 1024 * 1024:
            st.warning("The file is over 25 MB. Use a smaller image or "
                       "review the scan in a separate local viewer.")
        elif upload.type == "application/pdf":
            st.pdf(upload)
        else:
            st.image(upload, caption="Session-only research reference")
    institution = st.text_input("Repository or original custodian", key="acquisition_review_repository")
    locator = st.text_input("Actual book, page and image ID (not a guessed page)",
                            key="acquisition_review_locator")
    event_date = st.text_input("Date exactly as written, if present",
                               key="acquisition_review_date")
    transcribed = st.text_area(
        "Literal transcription from the original record", height=140,
        key="acquisition_review_transcription",
        placeholder="Enter only what you can read. Mark uncertain letters with [unclear].",
    )
    notes = st.text_area(
        "Interpretation or remaining questions (separate from literal text)",
        height=95, key="acquisition_review_notes",
    )
    source_url = st.text_input("Actual source link (optional)", key="acquisition_review_url")
    firsthand = st.checkbox(
        "I personally read the original or a legible facsimile, not just a database index",
        key="acquisition_review_firsthand",
    )
    if transcribed.strip():
        try:
            packet = researcher_packet(
                target=by_id[reviewed_id], institution=institution, shelf=locator,
                record_date=event_date, transcription=transcribed,
                observation=notes, source_url=source_url, firsthand=firsthand,
            )
        except ValueError as exc:
            st.warning(str(exc))
        else:
            st.download_button(
                "Download evidence-review packet (JSON) — no tree edit",
                json.dumps(packet, indent=2) + "\n",
                file_name="original-record-review-" + reviewed_id + ".json",
                mime="application/json",
            )
            st.caption("This packet requires review and approval before the "
                       "transcription or any proposed genealogy change reaches "
                       "the shared family site.")
    else:
        st.caption("The export becomes available after a literal transcription "
                   "is entered. Uploads alone do not change historical claims.")
