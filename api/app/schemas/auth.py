"""Auth Pydantic schemas — login, tokens, password management."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# ---- Login ----

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    remember_me: bool = False


class DemoAccountRow(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    default_password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    permissions: list[str]
    must_reset_password: bool
    employee_profile: dict | None = None
    initials: str | None = None


class LoginResponse(BaseModel):
    user: UserOut
    must_reset_password: bool = False


class TokenResponse(BaseModel):
    expires_in: int


# ---- Password management ----

class ChangePasswordRequest(BaseModel):
    # Bcrypt silently truncates input at 72 bytes. Reject longer inputs at the
    # schema boundary with a clean 422 instead of letting them round-trip and
    # fail verification.
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


class ForgotPasswordResponse(BaseModel):
    """Returns a dev token so the user can complete the reset without an email."""

    ok: bool = True
    dev_token: str | None = None
    message: str


# ---- Profile updates ----

class UserUpdate(BaseModel):
    full_name: str | None = None
    theme: Literal["dark", "light"] | None = None