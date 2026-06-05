from __future__ import annotations

import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.auth import AuthSession, upsert_oauth_user

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
_GOOGLE_STATES: set[str] = set()


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://127.0.0.1:5180").rstrip("/")


def google_redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8001/api/auth/google/callback")


def use_mock_auth() -> bool:
    return _truthy(os.getenv("USE_MOCK_AUTH"))


def callback_url_for_session(session: AuthSession) -> str:
    return f"{frontend_url()}/auth/callback?{urlencode({'token': session.token})}"


def issue_mock_google_session() -> AuthSession:
    return upsert_oauth_user(
        email="operator@blackboxops.local",
        name="BlackBoxOps Operator",
        provider="google",
        provider_user_id="mock-google-operator",
        picture=None,
    )


def build_google_authorization_url() -> str:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")
    state = secrets.token_urlsafe(24)
    _GOOGLE_STATES.add(state)
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": google_redirect_uri(),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return f"{_GOOGLE_AUTH_URL}?{query}"


def consume_google_state(state: str | None) -> None:
    if not state or state not in _GOOGLE_STATES:
        raise HTTPException(status_code=400, detail="Invalid Google OAuth state")
    _GOOGLE_STATES.remove(state)


def exchange_google_code_for_session(code: str | None, state: str | None) -> AuthSession:
    consume_google_state(state)
    if not code:
        raise HTTPException(status_code=400, detail="Missing Google OAuth code")

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials are not configured")

    try:
        token_response = httpx.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": google_redirect_uri(),
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Google did not return an access token")

        userinfo_response = httpx.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        userinfo_response.raise_for_status()
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=401, detail="Google OAuth exchange failed") from exc

    profile = userinfo_response.json()
    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Google profile did not include an email")

    return upsert_oauth_user(
        email=email,
        name=profile.get("name") or email,
        provider="google",
        provider_user_id=profile.get("sub") or email,
        picture=profile.get("picture"),
    )
