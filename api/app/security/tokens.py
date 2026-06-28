"""Itsdangerous-signed tokens for password reset (parity with existing app)."""
from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import get_settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError

settings = get_settings()

_serializer = URLSafeTimedSerializer(settings.AUTH_SECRET, salt="firststepai-reset")


def sign_reset_token(payload: dict) -> str:
    """Sign a payload (typically ``{"email": ...}``) for a password-reset link.

    The TTL is enforced on decode via ``settings.RESET_TOKEN_MAX_AGE`` —
    ``itsdangerous`` doesn't accept a max-age at sign time, so a parameter
    here would silently do nothing.
    """
    return _serializer.dumps(payload)


def verify_reset_token(token: str, max_age: int | None = None) -> dict:
    """Verify a signed reset token and return the payload.

    Raises TokenExpiredError if past max age; TokenInvalidError otherwise.
    """
    age = max_age or settings.RESET_TOKEN_MAX_AGE
    try:
        return _serializer.loads(token, max_age=age)
    except SignatureExpired as exc:
        raise TokenExpiredError("Reset token has expired") from exc
    except BadSignature as exc:
        raise TokenInvalidError("Invalid reset token") from exc