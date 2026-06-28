"""Settings service — read/patch UserSettings (theme, language, telemetry)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models.settings import UserSettings

if TYPE_CHECKING:
    from app.models.user import User


def get_or_create(db: Session, user: "User") -> UserSettings:
    settings = db.get(UserSettings, user.id)
    if settings is None:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def patch_settings(
    db: Session,
    user: "User",
    *,
    theme: str | None = None,
    language: str | None = None,
    anonymized_telemetry: bool | None = None,
    notification_prefs: dict | None = None,
) -> UserSettings:
    settings = get_or_create(db, user)
    if theme is not None:
        settings.theme = theme
    if language is not None:
        settings.language = language
    if anonymized_telemetry is not None:
        settings.anonymized_telemetry = anonymized_telemetry
    if notification_prefs is not None:
        settings.notification_prefs = notification_prefs
    db.commit()
    db.refresh(settings)
    return settings