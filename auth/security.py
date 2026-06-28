"""Password hashing and signed token helpers."""
from __future__ import annotations

from typing import Any, Optional

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config.settings import get_settings
from core.exceptions import TokenExpiredError, TokenInvalidError


# ---------- passwords ----------

def hash_password(plain: str) -> str:
    """Hash a password with bcrypt."""
    rounds = get_settings().BCRYPT_ROUNDS
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt comparison."""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------- signed tokens ----------

_serializer: Optional[URLSafeTimedSerializer] = None


def _get_serializer() -> URLSafeTimedSerializer:
    global _serializer
    if _serializer is None:
        _serializer = URLSafeTimedSerializer(get_settings().AUTH_SECRET, salt="firststepai")
    return _serializer


def sign_token(payload: dict[str, Any], max_age: int) -> str:
    """Return a signed, max-age-limited token. `max_age` is in seconds."""
    ser = _get_serializer()
    return ser.dumps(payload)


def verify_token(token: str, max_age: int) -> Optional[dict[str, Any]]:
    """Verify a token. Returns the payload dict or None if invalid/expired."""
    ser = _get_serializer()
    try:
        return ser.loads(token, max_age=max_age)
    except SignatureExpired as e:
        raise TokenExpiredError(str(e)) from e
    except BadSignature as e:
        raise TokenInvalidError(str(e)) from e


def safe_verify_token(token: str, max_age: int) -> Optional[dict[str, Any]]:
    """Like verify_token but swallows expired/invalid errors and returns None."""
    try:
        return verify_token(token, max_age=max_age)
    except (TokenExpiredError, TokenInvalidError):
        return None