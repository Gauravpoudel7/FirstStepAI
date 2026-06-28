"""User settings (theme, language, telemetry) — 1:1 with users."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID, json_column


class UserSettings(Base):
    __tablename__ = "settings"

    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    theme: Mapped[str] = mapped_column(String, default="dark", nullable=False)
    language: Mapped[str] = mapped_column(String, default="en", nullable=False)
    notification_prefs: Mapped[dict] = mapped_column(
        json_column(), default=dict, nullable=False
    )
    anonymized_telemetry: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )