from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def isolated_auth_store(monkeypatch, tmp_path):
    store_path = tmp_path / "auth_users.jsonl"
    monkeypatch.setattr("app.auth.AUTH_STORE_PATH", Path(store_path))
    monkeypatch.setenv("FRONTEND_URL", "http://127.0.0.1:5180")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8001/api/auth/google/callback")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-google-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-google-client-secret")


def _token_from_redirect(location: str) -> str:
    parsed = urlparse(location)
    return parse_qs(parsed.query)["token"][0]


def test_mock_google_login_redirects_to_frontend_callback_with_session(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AUTH", "true")
    client = TestClient(app)

    response = client.get("/api/auth/google/login", follow_redirects=False)

    assert response.status_code == 307
    location = response.headers["location"]
    assert location.startswith("http://127.0.0.1:5180/auth/callback?")
    token = _token_from_redirect(location)

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "operator@blackboxops.local"
    assert me.json()["name"] == "BlackBoxOps Operator"


def test_google_login_redirects_to_google_when_mock_disabled(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AUTH", "false")
    client = TestClient(app)

    response = client.get("/api/auth/google/login", follow_redirects=False)

    assert response.status_code == 307
    location = response.headers["location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    assert parsed.netloc == "accounts.google.com"
    assert query["client_id"] == ["test-google-client-id"]
    assert query["redirect_uri"] == ["http://127.0.0.1:8001/api/auth/google/callback"]
    assert query["scope"] == ["openid email profile"]
    assert query["response_type"] == ["code"]
    assert query["state"][0]


def test_google_callback_rejects_invalid_state(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AUTH", "false")
    client = TestClient(app)

    response = client.get("/api/auth/google/callback?code=fake-code&state=not-issued", follow_redirects=False)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Google OAuth state"
