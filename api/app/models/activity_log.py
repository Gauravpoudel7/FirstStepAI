"""Activity log — append-only audit trail."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID, ip_column, json_column


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    # Use Integer (not BigInteger) so SQLite assigns ROWID-based autoincrement values
    # automatically when the column is omitted. BigInteger → BIGINT on SQLite, which
    # does NOT auto-populate id; we need an explicit Python default in that case.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String, nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String, nullable=True)
    ip: Mapped[str | None] = mapped_column(ip_column(), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    extra: Mapped[dict] = mapped_column("metadata", json_column(), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )