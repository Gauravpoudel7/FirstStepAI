"""Cross-cutting concerns: session management, RBAC, exceptions.

Note: this package re-exports SessionManager lazily because session.py depends
on `auth.models`. Importing `core.session` / `core.rbac` / `core.exceptions`
directly is safe; `from core import ...` only works after `auth` is installed.
"""
from .rbac import ROLE_PERMISSIONS, can_access, permissions_for_role, role_badge_color
from .exceptions import (
    AuthError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedError,
    UserNotFoundError,
)

__all__ = [
    "ROLE_PERMISSIONS",
    "can_access",
    "permissions_for_role",
    "role_badge_color",
    "AuthError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "TokenInvalidError",
    "UnauthorizedError",
    "UserNotFoundError",
]


def __getattr__(name: str):  # PEP 562 lazy attribute
    if name == "SessionManager":
        from .session import SessionManager

        return SessionManager
    raise AttributeError(name)
