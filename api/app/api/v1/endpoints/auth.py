"""Auth endpoints — login, logout, refresh, password management, demo accounts."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import get_current_user
from app.core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.core.rbac import permissions_for_role
from app.db.session import get_db
from app.models.employee import Employee
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    DemoAccountRow,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
    UserUpdate,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ---- cookie helpers ----

def _set_cookies(response: Response, access: str, refresh: str, refresh_max_age: int) -> None:
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TTL_SECONDS,
        path="/",
        domain=settings.COOKIE_DOMAIN or None,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=refresh_max_age,
        path="/api/v1/auth",
        domain=settings.COOKIE_DOMAIN or None,
    )


def _clear_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/", domain=settings.COOKIE_DOMAIN or None)
    response.delete_cookie(
        "refresh_token", path="/api/v1/auth", domain=settings.COOKIE_DOMAIN or None
    )


# ---- profile serialization ----

def _user_out(user: User) -> UserOut:
    profile_dict: dict | None = None
    if user.employee is not None:
        profile_dict = _employee_dict(user.employee)
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        permissions=list(user.permissions or [p.value for p in permissions_for_role(user.role)]),
        must_reset_password=user.must_reset_password,
        employee_profile=profile_dict,
        initials=user.initials,
    )


def _employee_dict(emp: Employee) -> dict:
    return {
        "employee_id": emp.employee_id,
        "phone_number": emp.phone_number,
        "designation": emp.designation,
        "department": emp.department,
        "manager_id": emp.manager_id,
        "manager_name": (emp.manager.user.full_name if emp.manager and emp.manager.user else ""),
        "office_location": emp.office_location,
        "leave_balance": emp.leave_balance,
        "hire_date": emp.hire_date.isoformat() if emp.hire_date else "",
        "salary": float(emp.salary or 0),
        "projects": list(emp.projects or []),
        "skills": list(emp.skills or []),
        "role": emp.user.role if emp.user else "employee",
    }


# ---- endpoints ----

DEMO_ACCOUNTS = [
    DemoAccountRow(
        email="admin@umbrella.corp",
        full_name="Alex Wesker",
        role="admin",
        default_password="demo123",
    ),
    DemoAccountRow(
        email="hr@umbrella.corp",
        full_name="Lisa Trevor",
        role="hr",
        default_password="demo123",
    ),
    DemoAccountRow(
        email="manager@umbrella.corp",
        full_name="William Birkin",
        role="manager",
        default_password="demo123",
    ),
    DemoAccountRow(
        email="employee@umbrella.corp",
        full_name="Jill Valentine",
        role="employee",
        default_password="demo123",
    ),
    DemoAccountRow(
        email="demo@umbrella.corp",
        full_name="Ada Wong",
        role="employee",
        default_password="demo123",
    ),
]


@router.get("/demo-accounts", response_model=list[DemoAccountRow])
def get_demo_accounts() -> list[DemoAccountRow]:
    """Advertise demo accounts on the login page."""
    return DEMO_ACCOUNTS


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    svc = AuthService(db)
    try:
        user, access, access_ttl, refresh, refresh_expires = svc.login(
            body.email, body.password, body.remember_me
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    refresh_max_age = settings.REMEMBER_ME_MAX_AGE if body.remember_me else settings.JWT_REFRESH_TTL_SECONDS
    _set_cookies(response, access, refresh, refresh_max_age)
    return LoginResponse(user=_user_out(user), must_reset_password=user.must_reset_password)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Rotate refresh; return new access + refresh cookies."""
    raw = request.cookies.get("refresh_token")
    svc = AuthService(db)
    try:
        user, access, access_ttl, new_refresh, new_expires = svc.refresh(raw)
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    # SQLite returns naive datetimes; Postgres returns aware. Normalize.
    if new_expires.tzinfo is None:
        new_expires = new_expires.replace(tzinfo=timezone.utc)
    refresh_max_age = max(
        0,
        int((new_expires - datetime.now(timezone.utc)).total_seconds()),
    )
    _set_cookies(response, access, new_refresh, refresh_max_age)
    return TokenResponse(expires_in=access_ttl)


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    raw = request.cookies.get("refresh_token")
    AuthService(db).logout(raw)
    _clear_cookies(response)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return _user_out(current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserOut:
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.theme is not None:
        current_user.theme = body.theme
    db.commit()
    db.refresh(current_user)
    return _user_out(current_user)


@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    try:
        AuthService(db).change_password(current_user.id, body.current_password, body.new_password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    return {"ok": True}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    body: ForgotPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ForgotPasswordResponse:
    """Issue a reset token. Always returns ok:true to avoid email enumeration.

    The dev token is only ever included in the response when running in dev
    mode (`settings.ENV == "dev"`). In any other environment, callers always
    see the generic confirmation message — leaking the token would allow
    anyone to take over a known account.
    """
    dev_token = AuthService(db).request_password_reset(body.email)
    if settings.is_dev:
        return ForgotPasswordResponse(
            ok=True,
            dev_token=dev_token,
            message=(
                "Reset link sent (in production)"
                if dev_token
                else "If the email is registered, a reset link will be sent."
            ),
        )
    return ForgotPasswordResponse(
        ok=True,
        dev_token=None,
        message="If the email is registered, a reset link will be sent.",
    )


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    try:
        AuthService(db).confirm_password_reset(body.token, body.new_password)
    except (TokenExpiredError, TokenInvalidError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return {"ok": True}