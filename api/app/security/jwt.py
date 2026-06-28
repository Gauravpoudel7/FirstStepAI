"""JWT access + refresh token encode/decode.

Access tokens are short-lived (15 min) and carry user identity.
Refresh tokens are opaque random strings stored as sha256 in the
refresh_tokens table — JWT format is not used for them.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    *,
    user_id: str,
    email: str,
    role: str,
    ttl_seconds: int | None = None,
) -> tuple[str, int]:
    """Mint an HS256 JWT. Returns (token, ttl_seconds)."""
    ttl = ttl_seconds or settings.JWT_ACCESS_TTL_SECONDS
    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "jti": uuid.uuid4().hex,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=ttl)).timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, settings.AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, ttl


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode + verify a JWT access token. Raises JWTError on failure."""
    return jwt.decode(token, settings.AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM])


def create_refresh_token() -> tuple[str, str]:
    """Mint an opaque refresh token. Returns (raw_token, sha256_hex)."""
    raw = secrets.token_urlsafe(48)
    return raw, _hash_token(raw)


def hash_refresh_token(raw: str) -> str:
    """Compute sha256 of a refresh token (constant-time compare safe)."""
    return _hash_token(raw)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "hash_refresh_token",
    "JWTError",
]