"""Document ORM model — metadata for indexed knowledge-base docs."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID, json_column

if TYPE_CHECKING:
    from app.models.user import User


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "doc_type IN ('policy','handbook','memo','form')",
            name="documents_doc_type_check",
        ),
        CheckConstraint(
            "required_role IN ('all','employee','manager','hr','admin')",
            name="documents_required_role_check",
        ),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    doc_type: Mapped[str] = mapped_column(String, default="policy", nullable=False)
    department: Mapped[str] = mapped_column(String, default="HR", nullable=False)
    required_role: Mapped[str] = mapped_column(
        String, default="all", nullable=False, index=True
    )
    source_path: Mapped[str | None] = mapped_column(String, nullable=True)
    checksum: Mapped[str] = mapped_column(String, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    extra: Mapped[dict] = mapped_column("metadata", json_column(), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    uploader: Mapped["User | None"] = relationship()