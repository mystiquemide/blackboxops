from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def isolated_auth_store(monkeypatch, tmp_path):
    store_path = tmp_path / "auth_users.jsonl"
    monkeypatch.setattr("app.auth.AUTH_STORE_PATH", Path(store_path))


def test_signup_creates_user_and_returns_session_token():
    client = TestClient(app)

    response = client.post(
        "/api/auth/signup",
        json={"email": "mide@example.com", "password": "strong-pass-123", "name": "Mide"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == "mide@example.com"
    assert body["user"]["name"] == "Mide"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_signin_accepts_existing_credentials_and_rejects_wrong_password():
    client = TestClient(app)
    client.post(
        "/api/auth/signup",
        json={"email": "ops@example.com", "password": "safe-pass-456", "name": "Ops Lead"},
    )

    ok_response = client.post(
        "/api/auth/signin",
        json={"email": "ops@example.com", "password": "safe-pass-456"},
    )
    bad_response = client.post(
        "/api/auth/signin",
        json={"email": "ops@example.com", "password": "wrong-pass"},
    )

    assert ok_response.status_code == 200
    assert ok_response.json()["token"]
    assert ok_response.json()["user"]["email"] == "ops@example.com"
    assert bad_response.status_code == 401


def test_me_returns_current_user_from_bearer_token():
    client = TestClient(app)
    signup = client.post(
        "/api/auth/signup",
        json={"email": "audit@example.com", "password": "audit-pass-789", "name": "Audit Team"},
    )
    token = signup.json()["token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "audit@example.com"
    assert response.json()["name"] == "Audit Team"


def test_duplicate_signup_is_rejected():
    client = TestClient(app)
    payload = {"email": "dupe@example.com", "password": "strong-pass-123", "name": "Dupe"}

    first = client.post("/api/auth/signup", json=payload)
    second = client.post("/api/auth/signup", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
