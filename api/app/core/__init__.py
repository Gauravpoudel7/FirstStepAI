"""Core cross-cutting concerns: exceptions, RBAC, dependencies."""
from app.core.exceptions import (
    AuthError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedError,
    UserNotFoundError,
)
from app.core.rbac import (
    ROLE_PERMISSIONS,
    allowed_doc_roles,
    can_access,
    permissions_for_role,
    role_badge_color,
)

__all__ = [
    "AuthError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "TokenInvalidError",
    "UnauthorizedError",
    "UserNotFoundError",
    "ROLE_PERMISSIONS",
    "allowed_doc_roles",
    "can_access",
    "permissions_for_role",
    "role_badge_color",
]
