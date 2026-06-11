from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import Header, HTTPException
from pydantic import BaseModel, Field, field_validator


AUTH_STORE_PATH = Path(os.getenv("BLACKBOXOPS_AUTH_STORE", "data/auth_users.jsonl"))
_MIN_PASSWORD_LENGTH = 8
_SESSION_TTL_HOURS = int(os.getenv("BLACKBOXOPS_SESSION_TTL_HOURS", "24"))


class AuthUser(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: str
    picture: str | None = None
    provider: str = "local"


class AuthSession(BaseModel):
    token: str
    user: AuthUser


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=_MIN_PASSWORD_LENGTH)
    name: str = Field(min_length=1, max_length=80)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = _normalize_email(value)
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return normalized


class SigninRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = _normalize_email(value)
        if "@" not in normalized:
            raise ValueError("Enter a valid email address")
        return normalized


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000)
    return salt, digest.hex()


def _verify_password(password: str, salt: str, password_hash: str) -> bool:
    _, candidate_hash = _hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, password_hash)


def _load_records() -> list[dict]:
    if not AUTH_STORE_PATH.exists():
        return []
    return [json.loads(line) for line in AUTH_STORE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_records(records: list[dict]) -> None:
    AUTH_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_STORE_PATH.write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + ("\n" if records else ""), encoding="utf-8")


def _public_user(record: dict) -> AuthUser:
    return AuthUser(
        user_id=record["user_id"],
        email=record["email"],
        name=record["name"],
        created_at=record["created_at"],
        picture=record.get("picture"),
        provider=record.get("provider", "local"),
    )


def _now() -> datetime:
    return datetime.now(UTC)


def _prune_expired(sessions: list) -> list:
    """Drop expired and legacy (non-dict / unparseable) session entries."""
    now = _now()
    live = []
    for entry in sessions:
        if not isinstance(entry, dict):
            continue  # legacy bare-string token: force re-authentication
        expires_at = entry.get("expires_at")
        if not expires_at:
            continue
        try:
            if datetime.fromisoformat(expires_at) > now:
                live.append(entry)
        except ValueError:
            continue
    return live


def _issue_session(record: dict) -> AuthSession:
    records = _load_records()
    token = secrets.token_urlsafe(32)
    expires_at = (_now() + timedelta(hours=_SESSION_TTL_HOURS)).isoformat()
    session_entry = {"token": token, "expires_at": expires_at}
    for stored in records:
        if stored["user_id"] == record["user_id"]:
            kept = _prune_expired(stored.get("sessions", []))
            kept.append(session_entry)
            stored["sessions"] = kept
            record = stored
            break
    _write_records(records)
    return AuthSession(token=token, user=_public_user(record))


def signup_user(request: SignupRequest) -> AuthSession:
    records = _load_records()
    email = _normalize_email(request.email)
    if any(record["email"] == email for record in records):
        raise HTTPException(status_code=409, detail="A BlackBoxOps account already exists for this email")

    salt, password_hash = _hash_password(request.password)
    record = {
        "user_id": f"usr_{secrets.token_hex(8)}",
        "email": email,
        "name": request.name.strip(),
        "created_at": datetime.now(UTC).isoformat(),
        "password_salt": salt,
        "password_hash": password_hash,
        "provider": "local",
        "picture": None,
        "sessions": [],
    }
    records.append(record)
    _write_records(records)
    return _issue_session(record)


def signin_user(request: SigninRequest) -> AuthSession:
    email = _normalize_email(request.email)
    for record in _load_records():
        if record["email"] == email and _verify_password(request.password, record["password_salt"], record["password_hash"]):
            return _issue_session(record)
    raise HTTPException(status_code=401, detail="Invalid email or password")


def upsert_oauth_user(*, email: str, name: str, provider: str, provider_user_id: str, picture: str | None = None) -> AuthSession:
    records = _load_records()
    normalized = _normalize_email(email)
    now = datetime.now(UTC).isoformat()
    for record in records:
        if record["email"] == normalized:
            record["name"] = name.strip() or record.get("name") or normalized
            record["provider"] = provider
            record["provider_user_id"] = provider_user_id
            record["picture"] = picture
            _write_records(records)
            return _issue_session(record)

    record = {
        "user_id": f"usr_{secrets.token_hex(8)}",
        "email": normalized,
        "name": name.strip() or normalized,
        "created_at": now,
        "provider": provider,
        "provider_user_id": provider_user_id,
        "picture": picture,
        "password_salt": "",
        "password_hash": "",
        "sessions": [],
    }
    records.append(record)
    _write_records(records)
    return _issue_session(record)


def update_user_profile(user: AuthUser, *, name: str | None = None, current_password: str | None = None, new_password: str | None = None) -> AuthUser:
    records = _load_records()
    for record in records:
        if record["user_id"] == user.user_id:
            if new_password is not None:
                if record.get("provider", "local") != "local":
                    raise HTTPException(status_code=400, detail="Password change not available for OAuth accounts")
                if not current_password:
                    raise HTTPException(status_code=400, detail="Current password required")
                if not _verify_password(current_password, record.get("password_salt", ""), record.get("password_hash", "")):
                    raise HTTPException(status_code=401, detail="Current password is incorrect")
                salt, password_hash = _hash_password(new_password)
                record["password_salt"] = salt
                record["password_hash"] = password_hash
            if name is not None:
                record["name"] = name.strip() or record.get("name") or user.email
            _write_records(records)
            return _public_user(record)
    raise HTTPException(status_code=404, detail="User not found")


def current_user_from_authorization(authorization: Annotated[str | None, Header()] = None) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    now = _now()
    for record in _load_records():
        for entry in record.get("sessions", []):
            if not isinstance(entry, dict) or entry.get("token") != token:
                continue
            expires_at = entry.get("expires_at")
            if not expires_at:
                continue
            try:
                if datetime.fromisoformat(expires_at) <= now:
                    raise HTTPException(status_code=401, detail="Your session has expired. Please sign in again.")
            except ValueError:
                continue
            return _public_user(record)
    raise HTTPException(status_code=401, detail="Invalid bearer token")
