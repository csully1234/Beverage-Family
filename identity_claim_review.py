"""Side-by-side historically sourced identity review for the family archive.

Evidence is documented as independent source *families*, not counted as votes.
No proposed parent or alternate Rachel surname alters canonical genealogy.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from routing_ui import route_link, safe_external_url

REGISTRY = Path(__file__).resolve().parent / "data" / "phase41_competing_identity_claims.json"


def load_claims(path: Path = REGISTRY) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) != 4:
        raise ValueError("Expected four reviewed Phase 41 conflicting genealogy cases")
    ids = set()
    for case in cases:
        identifier = str(case.get("id") or "")
        if not identifier or identifier in ids:
            raise ValueError("Missing or duplicate historical conflict case")
        ids.add(identifier)
        if len(case.get("claims", [])) < 2 or not case.get("research_tasks"):
            raise ValueError("Each case requires alternative claims and tasks")
        claim_ids = set()
        for claim in case["claims"]:
            if claim["id"] in claim_ids:
                raise ValueError("Repeated source-claim identifier")
            claim_ids.add(claim["id"])
            if claim["original_inspected"]:
                raise ValueError("Do not mark uninspected original witnesses as reviewed")
            url = claim.get("url")
            if url and not safe_external_url(url):
                raise ValueError("Unsafe historical claim source link")
        for source in case.get("corroborating_context", []):
            if not safe_external_url(source.get("url")):
                raise ValueError("Unsafe historic source comparison link")
    return sorted(cases, key=lambda row: row["priority"])


def cases_for_person(person_id: str, cases: list[dict] | None = None) -> list[dict]:
    return [case for case in (cases if cases is not None else load_claims())
            if person_id in case["person_ids"]]


def witness_families(case: dict) -> dict[str, list[str]]:
    """Deduplicate shared editorial provenance, NOT a score or proof counter."""
    grouped: dict[str, list[str]] = {}
    for claim in case["claims"]:
        grouped.setdefault(claim["source_family"], []).append(claim["id"])
    for row in case.get("corroborating_context", []):
        grouped.setdefault(row["source_family"], []).append("context:" + row["title"])
    return grouped


def claim_review_route(case_id: str = "") -> str:
    base = "?page=collection&view=source-expedition&conflict=1"
    return base + ("&conflict_case=" + quote(case_id, safe="") if case_id else "")


def conflict_report_csv(cases: list[dict]) -> str:
    buffer = io.StringIO()
    cols = ["case", "priority", "person_ids", "claim", "source_family",
            "claim_text", "source_url", "original_inspected",
            "research_requirements", "limitations"]
    writer = csv.DictWriter(buffer, fieldnames=cols)
    writer.writeheader()
    for case in cases:
        for claim in case["claims"]:
            writer.writerow({
                "case": case["id"], "priority": case["priority"],
                "person_ids": "; ".join(case["person_ids"]),
                "claim": claim["id"], "source_family": claim["source_family"],
                "claim_text": claim["value"], "source_url": claim.get("url") or "",
                "original_inspected": "no",
                "research_requirements": " | ".join(case["research_tasks"]),
                "limitations": case["limits"],
            })
    return buffer.getvalue()


def render_conflict_review(people: dict, *, selected: str = "") -> None:
    cases = load_claims()
    st.subheader("Competing evidence — review before changing the tree")
    st.write("A different website is not a reason to rewrite someone's parents. "
             "Compare the existing family record with published alternatives "
             "and examine exactly which first-hand documents would decide the question.")
    st.caption("All four cases are OPEN. No original register/deed image in these "
               "new competing claims has been directly inspected. Multiple "
               "contributed pages can depend on the same copied family tree.")
    requested = selected if selected in {row["id"] for row in cases} else ""
    valid = ["", *(row["id"] for row in cases)]
    # Stable case-specific widget avoids wiping a visitor's selection whenever
    # they switch other sections of this historically large Streamlit page.
    chosen = st.selectbox(
        "Compare a historical identity question",
        valid, index=valid.index(requested),
        format_func=lambda cid: (
            "All family history conflicts" if not cid else
            next(row["title"] for row in cases if row["id"] == cid)),
        key="phase41_identity_case",
    )
    for case in ([next(row for row in cases if row["id"] == chosen)]
                 if chosen else cases):
        with st.container(border=True):
            st.markdown("**" + case["title"] + "**")
            st.caption(case["status"] + " · " + case["period"])
            st.write(case["question"])
            st.markdown("**Competing claims — not a vote between websites**")
            for claim in case["claims"]:
                with st.expander(claim["value"], expanded=bool(chosen)):
                    st.write(claim["basis"])
                    st.caption(claim["status"].replace("_", " ") +
                               " · source family: " + claim["source_family"])
                    st.caption("Contemporary original personally inspected: NO")
                    if claim.get("url"):
                        route_link("Open this claim's cited publication", claim["url"])
            if case.get("corroborating_context"):
                st.markdown("**Additional context (may share provenance)**")
                for item in case["corroborating_context"]:
                    route_link(item["title"], item["url"])
                    st.caption(item["limits"])
            st.caption(str(len(witness_families(case))) +
                       " different editorial/source-family labels represented. "
                       "That is NOT the number of independent original records "
                       "or a confidence calculation.")
            st.warning(case["limits"])
            st.markdown("**Which original documents can resolve this?**")
            st.write(case["source_target"])
            for i, task in enumerate(case["research_tasks"], 1):
                st.write(str(i) + ". " + task)
            for pid in case["person_ids"]:
                if pid in people:
                    route_link("Inspect current tree profile: " +
                               str(people[pid].get("full_name") or pid),
                               "?page=people&profile=" + quote(pid, safe=""),
                               type="tertiary")
            route_link("Bookmark this exact evidence conflict",
                       claim_review_route(case["id"]), type="tertiary")
    st.download_button(
        "Download all conflicting claims and original-record tasks",
        conflict_report_csv(cases),
        file_name="beverage-family-competing-identity-research.csv",
        mime="text/csv",
    )
