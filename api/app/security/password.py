"""Password hashing using bcrypt directly (rounds=12, parity with existing app).

We bypass passlib because passlib's bcrypt backend detects a wrap-bug on
initialization that fails on newer bcrypt (>=4.x) releases. The on-disk hash
format ($2b$…) is identical, so existing data/users.json hashes still verify.
"""
from __future__ import annotations

import bcrypt

from app.config import get_settings

settings = get_settings()


def _to_bytes(value: str) -> bytes:
    # bcrypt has a 72-byte limit on the secret — truncate defensively
    raw = value.encode("utf-8")
    return raw[:72]


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(_to_bytes(plain), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def needs_rehash(hashed: str) -> bool:
    """True if the hash should be re-hashed (e.g., rounds were bumped)."""
    if not hashed:
        return True
    try:
        rounds = int(hashed.split("$")[2])
        return rounds < settings.BCRYPT_ROUNDS
    except (IndexError, ValueError):
        return True