"""Auth facade — login / logout / forgot-password / reset / remember-me.

Provider-agnostic; pass any `AuthProvider` implementation. The default is
`LocalAuthProvider`, but `AzureADAuthProvider` / `LdapAuthProvider` can drop
in later without changing this file.
"""
from __future__ import annotations

from typing import Optional

from auth.models import User
from auth.providers.base import AuthProvider
from auth.providers.local import LocalAuthProvider
from auth.security import safe_verify_token, sign_token
from config.settings import get_settings
from core.exceptions import InvalidCredentialsError, UserNotFoundError


_service: Optional["AuthService"] = None


class AuthService:
    def __init__(self, provider: AuthProvider):
        self.provider = provider

    # ---------- login / logout ----------

    def login(self, email: str, password: str, remember: bool = False) -> User:
        user = self.provider.authenticate(email, password)
        return user

    def logout(self) -> None:
        # SessionManager handles the state mutation; the service is stateless
        # beyond the provider reference. Kept here for symmetry / future hooks.
        return None

    # ---------- user lookups ----------

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.provider.get_user_by_email(email)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.provider.get_user_by_id(user_id)

    def list_users(self) -> list[User]:
        return self.provider.list_users()

    # ---------- password reset ----------

    def request_password_reset(self, email: str) -> str:
        """Generate a reset token for the given email.

        Demo-only behaviour: the token is returned in-band rather than emailed.
        Production should SMTP the link and never expose the token to the UI.
        """
        user = self.provider.get_user_by_email(email)
        if not user:
            # Generic response to avoid email enumeration.
            raise UserNotFoundError("If the email exists, a reset link has been sent.")
        return sign_token({"uid": user.id, "email": user.email}, max_age=get_settings().RESET_TOKEN_MAX_AGE)

    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        payload = safe_verify_token(token, max_age=get_settings().RESET_TOKEN_MAX_AGE)
        if not payload:
            raise InvalidCredentialsError("Reset link is invalid or has expired.")
        email = payload.get("email")
        if not email:
            raise InvalidCredentialsError("Reset link is malformed.")
        return self.provider.reset_password(email, new_password)

    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        # Re-authenticate to confirm current password.
        self.provider.authenticate(user.email, current_password)
        return self.provider.reset_password(user.email, new_password)

    # ---------- role mgmt (admin) ----------

    def update_user_role(self, user_id: str, role: str) -> bool:
        return self.provider.update_user_role(user_id, role)


def get_auth_service() -> AuthService:
    """Singleton accessor."""
    global _service
    if _service is None:
        _service = AuthService(LocalAuthProvider())
    return _service