"""Keep internal navigation in the authenticated Streamlit session.

External evidence stays a normal link. Internal URLs remain shareable in the
address bar, but their controls use callbacks rather than opening new sessions.
"""
from hashlib import sha256
import re
from urllib.parse import parse_qsl, urlsplit
import streamlit as st

INTERNAL_LINK = re.compile(r"\[((?:\\.|[^\]])+)\]\((\?[^)\s]+)\)")


def begin_routes():
    st.session_state["_route_button_counts"] = {}


def open_route(url):
    target = urlsplit(url)
    if target.scheme or target.netloc or target.path or not target.query:
        raise ValueError("Expected an internal query route")
    st.query_params.clear()
    st.query_params.update(dict(parse_qsl(target.query, keep_blank_values=True)))
    st.session_state.pop("_last_query_slug", None)


def safe_external_url(value: str) -> bool:
    """Prevent untrusted catalog entries from becoming script/data links."""
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        return False
    if any(char in value for char in "<>\\\\"):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme in {"http", "https"} and bool(parsed.hostname)
                and not parsed.username and not parsed.password
                and parsed.port in (None, 80, 443))
    except ValueError:
        return False


def route_link(label, url, **kwargs):
    if not isinstance(url, str):
        st.caption("Source link unavailable: no verified web address.")
        return None
    if not url.startswith("?"):
        if not safe_external_url(url):
            st.caption("Source link unavailable: the address is not a verified HTTP(S) URL.")
            return None
        return st.link_button(label, url, **kwargs)
    digest = sha256((str(label) + url).encode()).hexdigest()[:16]
    counts = st.session_state.setdefault("_route_button_counts", {})
    occurrence = counts.get(digest, 0)
    counts[digest] = occurrence + 1
    return st.button(label, key=f"route_{digest}_{occurrence}", on_click=open_route,
                     args=(url,), **kwargs)


def route_markdown(body, **kwargs):
    """Render curated internal Markdown links as session-preserving controls.

    Keep text, headings and all external links as Markdown. This small adapter
    allows existing citation/relative formatters to retain their stable URLs.
    """
    body = str(body)
    links = list(INTERNAL_LINK.finditer(body))
    if not links or kwargs.get("unsafe_allow_html"):
        return st.markdown(body, **kwargs)
    cursor = 0
    for match in links:
        before = body[cursor:match.start()].strip()
        if before.strip("#*-· \n"):
            st.markdown(before.strip(" ·\n"), **kwargs)
        label = match.group(1)
        route_link(label, match.group(2), type="tertiary")
        cursor = match.end()
    after = body[cursor:].strip()
    if after.strip("#*-· \n"):
        st.markdown(after.strip(" ·\n"), **kwargs)
