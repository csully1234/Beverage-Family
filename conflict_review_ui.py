"""Family-readable explanations, with full evidence and previous values one step away."""
import json
import streamlit as st
from routing_ui import route_markdown, route_link
from archive import archive_url
from conflict_review import load_review, STATUSES


@st.cache_data(show_spinner=False)
def review_data():
    return load_review()


def resolution_for(rid):
    return next((r for r in review_data()["resolutions"] if r["research_id"] == rid), None)


def review_link(rid):
    return archive_url("collection", view="Conflict review", finding=rid)


def render_resolution(r, collection, people, *, detail=False):
    route_markdown("**Latest evidence review · " + r["checked_on"] + "**")
    st.write(r["conclusion"])
    st.caption(f"{r['resolution_status']} · {r['confidence']} · {r['family_review_status']}")
    if not detail:
        route_markdown(f"[Read evidence and previous values]({review_link(r['research_id'])})")
        return
    route_markdown("**Why this conclusion**")
    st.write(r["reasoning"])
    st.write("Identity check: " + r["identity_reasoning"])
    if r["changes"]:
        route_markdown("**Proposed corrections in this version**")
        st.dataframe([{"Person": people[c["person_id"]]["full_name"], "Field": c["field"],
                       "Before": str(c["before"]), "After": str(c["after"]), "Reason": c["reason"]}
                      for c in r["changes"]], hide_index=True, width="stretch")
        st.caption("These are evidence-reviewed draft corrections, not family approval. Original files are unchanged.")
    for sub in r.get("subfindings", []):
        st.write(f"{sub['claim']}: {sub['outcome']} ({sub['confidence']})")
    with st.expander("Original claims and competing explanations"):
        st.write(r["baseline_conflict"])
        st.write(r["competing_claims"])
        st.json(r["existing_claims"], expanded=False)
    route_markdown("**Evidence and exact citations**")
    new = {s["id"]: s for s in review_data()["sources"] + review_data().get("existing_source_checks", [])}
    for sid in r["source_ids"]:
        if sid in new:
            s = new[sid]
            route_markdown(f"- [{sid} · {s['title']}]({s['url']})")
            st.caption(f"{s['repository']} · {s['locator']} · accessed {s['accessed']}")
            st.write(s["supports"])
            st.caption(f"Examined: {s['viewed']} · {s['quality']}")
            st.caption("Source dependence: " + s["dependency"])
        else:
            s = collection.sources[sid]
            route_markdown(f"- [{sid} · {s['Title']}]({archive_url('archive', source=sid)})")
            st.caption(f"{s['Locator']} · {s['Viewed status']}")
    route_markdown("**What remains to establish**")
    st.write(r["remaining_question"])
    with st.expander("Prepared retrieval request — not sent"):
        st.write(r["retrieval_request"])
        st.caption("No fees incurred or archive contacted. Confirm availability and fees before ordering.")
    if r["people_ids"]:
        route_markdown("**Related profiles:** " + " · ".join(
            f"[{people[pid]['full_name']}]({archive_url('people', profile=pid)})" for pid in r["people_ids"]))


def render_profile_review(person_id, collection, people):
    records = [r for r in review_data()["resolutions"] if person_id in r["people_ids"]]
    if records:
        with st.expander(f"Dates, identity and evidence notes ({len(records)})"):
            for r in records:
                render_resolution(r, collection, people)


def render_review_page(collection, people):
    review = review_data()
    st.subheader("Questions we are working through")
    st.write("Read the latest conclusion, the evidence behind it, and the record still needed. An evidence review is separate from family approval.")
    status = st.selectbox("Review outcome", ["All", *STATUSES], key="review_outcome")
    records = [r for r in review["resolutions"] if status == "All" or r["resolution_status"] == status]
    st.caption(f"{len(records)} of {len(review['resolutions'])} questions · reviewed {review['checked_on']}")
    for r in records:
        with st.container(border=True):
            route_markdown(f"### [{r['title']}]({review_link(r['research_id'])})")
            render_resolution(r, collection, people)
    with st.expander("Download the complete evidence review"):
        st.download_button("Download resolution ledger (JSON)", json.dumps(review, indent=2, ensure_ascii=False),
                           file_name="Beverage_Family_Conflict_Review_2026-10-15.json", mime="application/json")


def render_review_source(source_id, collection, people):
    source = next((s for s in review_data()["sources"] if s["id"] == source_id), None)
    if not source:
        return False
    st.subheader(source["title"])
    for field in ("repository", "locator", "accessed", "viewed", "quality", "dependency", "supports", "rights"):
        route_markdown(f"**{field.title()}:** {source[field]}")
    route_link("Open source", source["url"])
    for r in review_data()["resolutions"]:
        if source_id in r["source_ids"]:
            route_markdown(f"[{r['title']}]({review_link(r['research_id'])})")
    return True
