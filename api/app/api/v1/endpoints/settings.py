"""Settings endpoints — get/patch user-scoped settings; branding is public."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsOut(BaseModel):
    theme: str
    language: str
    notification_prefs: dict
    anonymized_telemetry: bool
    updated_at: str | None = None

    @classmethod
    def from_orm(cls, s) -> "SettingsOut":
        return cls(
            theme=s.theme,
            language=s.language,
            notification_prefs=s.notification_prefs or {},
            anonymized_telemetry=s.anonymized_telemetry,
            updated_at=s.updated_at.isoformat() if s.updated_at else None,
        )


class SettingsPatch(BaseModel):
    theme: str | None = None
    language: str | None = None
    anonymized_telemetry: bool | None = None
    notification_prefs: dict | None = None


@router.get("", response_model=SettingsOut)
def get_my_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SettingsOut:
    s = settings_service.get_or_create(db, current_user)
    return SettingsOut.from_orm(s)


@router.patch("", response_model=SettingsOut)
def patch_my_settings(
    body: SettingsPatch,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SettingsOut:
    s = settings_service.patch_settings(
        db,
        current_user,
        theme=body.theme,
        language=body.language,
        anonymized_telemetry=body.anonymized_telemetry,
        notification_prefs=body.notification_prefs,
    )
    return SettingsOut.from_orm(s)


@router.get("/branding")
def branding() -> dict[str, str]:
    """Public — used by LoginPage and TopBar before the user is logged in."""
    cfg = get_settings()
    return {
        "company_name": cfg.COMPANY_NAME,
        "logo_text": cfg.COMPANY_NAME,
        "theme_default": cfg.THEME,
    }