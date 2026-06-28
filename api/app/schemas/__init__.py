"""Pydantic schemas (request/response) for the API.

Per-domain submodules are added in their respective phases. Today we expose
auth/profile/employee schemas; chat/document/etc. land as Phase 4+.
"""
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

__all__ = [
    "ChangePasswordRequest",
    "DemoAccountRow",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "LoginRequest",
    "LoginResponse",
    "ResetPasswordRequest",
    "TokenResponse",
    "UserOut",
    "UserUpdate",
]