"""One family login gives identical access to every archival section.

No user tiers, guest accounts, or document-specific permissions are created.
The password must come from deployment configuration, NEVER public source.
This gate covers Streamlit navigation, NOT arbitrary public static-file URLs.
"""
from __future__ import annotations

import hashlib
import hmac


def valid_deployment_password(password: str | None) -> bool:
    """Avoid accepting empty, obsolete, or clearly unusable deployment secrets."""
    if not isinstance(password, str):
        return False
    return len(password) >= 12 and password != password.strip()[:0] and password.casefold() != "beverage"


def matches_family_password(candidate: str, configured: str | None) -> bool:
    """Constant-time equality check with no special role or section grants."""
    if not valid_deployment_password(configured) or not isinstance(candidate, str):
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), configured.encode("utf-8"))


def session_password_fingerprint(configured: str | None) -> str | None:
    """Detect a rotated password without retaining its plaintext in session state.

    A fingerprint is not an authorization cookie and does NOT protect public URLs.
    """
    if not valid_deployment_password(configured):
        return None
    return hashlib.sha256(b"beverage-family-login-revision-v1\0" +
                          configured.encode("utf-8")).hexdigest()


def session_authorized(session: dict, configured: str | None) -> bool:
    expected = session_password_fingerprint(configured)
    return bool(expected and session.get("password_correct") is True
                and hmac.compare_digest(
                    str(session.get("_family_access_revision") or ""),
                    expected,
                ))
