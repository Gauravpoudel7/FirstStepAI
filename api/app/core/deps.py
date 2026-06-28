"""FastAPI dependencies: get_db, get_current_user, require_role, require_permission."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, UnauthorizedError, UserNotFoundError
from app.core.rbac import Role, can_access
from app.db.session import get_db
from app.models.user import User
from app.security.jwt import JWTError
from app.services.auth_service import AuthService

# Optional Bearer scheme — token may come from Authorization header OR cookie
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(request: Request, creds: HTTPAuthorizationCredentials | None) -> str | None:
    if creds and creds.scheme.lower() == "bearer":
        return creds.credentials
    return request.cookies.get("access_token")


def get_auth_service_dep(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


def get_current_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    token = _extract_token(request, creds)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    svc = AuthService(db)
    try:
        payload = svc.decode_access(token)
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token claims")
    user = svc.get_user(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def require_role(*roles: Role | str):
    """Dependency factory: ensures the current user has one of the listed roles."""
    role_values: list[str] = []
    for r in roles:
        role_values.append(r.value if isinstance(r, Role) else r)

    def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in role_values:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, f"Requires one of: {', '.join(role_values)}"
            )
        return user

    return _check


def require_permission(permission: str | Role):
    perm_value = permission.value if isinstance(permission, Role) else permission

    def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not can_access(user.role, perm_value):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Missing permission: {perm_value}")
        return user

    return _check


# Re-exported convenience
__all__ = [
    "get_auth_service_dep",
    "get_current_user",
    "require_role",
    "require_permission",
    "InvalidCredentialsError",
    "UnauthorizedError",
    "UserNotFoundError",
]