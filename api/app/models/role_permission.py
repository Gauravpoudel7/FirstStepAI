"""Role-Permission seed tables. Mirrors core/rbac.py::ROLE_PERMISSIONS."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String, primary_key=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role: Mapped[str] = mapped_column(String, primary_key=True)
    permission: Mapped[str] = mapped_column(
        String,
        ForeignKey("permissions.name", ondelete="CASCADE"),
        primary_key=True,
    )