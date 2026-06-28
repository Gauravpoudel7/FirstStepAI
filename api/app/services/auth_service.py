"""AuthService facade — high-level operations over an AuthProvider.

Mirrors the existing auth/services.py::AuthService: thin wrapper that takes
a provider, exposes the same operations, and handles token issuance for
the /auth/* endpoints.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.exceptions import InvalidCredentialsError, UserNotFoundError
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_refresh_token,
)
from app.security.tokens import sign_reset_token, verify_reset_token
from app.services.auth_providers.base import AuthProvider
from app.services.auth_providers.db_provider import SQLAuthProvider

settings = get_settings()


def _build_provider(db: Session) -> AuthProvider:
    """Currently only SQL provider is implemented; left as a switch for AzureAD/Google/LDAP."""
    return SQLAuthProvider(db)


class AuthService:
    """High-level auth operations."""

    def __init__(self, db: Session):
        self.db = db
        self.provider = _build_provider(db)

    # ---- login ----

    def login(self, email: str, password: str, remember_me: bool = False) -> tuple[User, str, int, str, datetime]:
        """Returns (user, access_token, access_ttl, refresh_raw, refresh_expires_at)."""
        user = self.provider.authenticate(email, password)

        access_token, access_ttl = create_access_token(
            user_id=user.id, email=user.email, role=user.role
        )
        refresh_raw, refresh_hash = create_refresh_token()
        refresh_ttl = (
            settings.REMEMBER_ME_MAX_AGE if remember_me else settings.JWT_REFRESH_TTL_SECONDS
        )
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=refresh_ttl)
        row = RefreshToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
        self.db.add(row)
        self.db.commit()
        return user, access_token, access_ttl, refresh_raw, expires_at

    def refresh(self, refresh_raw: str) -> tuple[User, str, int, str, datetime]:
        """Rotate a refresh token. Reuse of a revoked token revokes the chain."""
        if not refresh_raw:
            raise InvalidCredentialsError("Missing refresh token")
        token_hash = hash_refresh_token(refresh_raw)
        row = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            raise InvalidCredentialsError("Unknown refresh token")

        now = datetime.now(timezone.utc)
        if row.revoked_at is not None:
            # Reuse — revoke the entire chain.
            self._revoke_chain(row.user_id)
            raise InvalidCredentialsError("Refresh token reuse detected; please log in again")
        row_expires = row.expires_at
        if row_expires.tzinfo is None:
            row_expires = row_expires.replace(tzinfo=timezone.utc)
        if row_expires < now:
            raise InvalidCredentialsError("Refresh token expired")

        user = self.provider.get_user_by_id(row.user_id)
        if user is None:
            raise UserNotFoundError("User no longer exists")

        new_raw, new_hash = create_refresh_token()
        new_row = RefreshToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=new_hash,
            expires_at=row.expires_at,
        )
        row.revoked_at = now
        row.replaced_by = new_row.id
        self.db.add(new_row)
        self.db.commit()

        access_token, access_ttl = create_access_token(
            user_id=user.id, email=user.email, role=user.role
        )
        return user, access_token, access_ttl, new_raw, new_row.expires_at

    def logout(self, refresh_raw: str | None) -> None:
        if not refresh_raw:
            return
        token_hash = hash_refresh_token(refresh_raw)
        row = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .one_or_none()
        )
        if row is not None and row.revoked_at is None:
            row.revoked_at = datetime.now(timezone.utc)
            self.db.commit()

    def _revoke_chain(self, user_id: str) -> None:
        """Revoke every active refresh token for a user (used on reuse detection)."""
        now = datetime.now(timezone.utc)
        rows = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .all()
        )
        for row in rows:
            row.revoked_at = now
        self.db.commit()

    # ---- users ----

    def get_user(self, user_id: str) -> User | None:
        return self.provider.get_user_by_id(user_id)

    def list_users(self) -> list[User]:
        return self.provider.list_users()

    # ---- password management ----

    def change_password(self, user_id: str, current: str, new: str) -> None:
        self.provider.change_password(user_id, current, new)

    def request_password_reset(self, email: str) -> str | None:
        """Returns a dev token so the user can complete the reset; None if email unknown.

        Always succeeds from the caller's perspective (no email enumeration).
        """
        user = self.provider.get_user_by_email(email)
        if user is None:
            return None
        return sign_reset_token({"email": user.email, "uid": user.id})

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        payload = verify_reset_token(token)
        email = payload.get("email")
        if not email:
            raise InvalidCredentialsError("Reset payload missing email")
        user = self.provider.get_user_by_email(email)
        if user is None:
            raise UserNotFoundError("User no longer exists")
        self.provider.reset_password(user.id, new_password)

    # ---- role management ----

    def update_role(self, user_id: str, role: str) -> User:
        return self.provider.update_user_role(user_id, role)

    # ---- JWT decode helper ----

    def decode_access(self, token: str) -> dict:
        return decode_access_token(token)


def get_auth_service(db: Session) -> AuthService:
    """FastAPI dependency that produces an AuthService bound to a request-scoped session."""
    return AuthService(db)