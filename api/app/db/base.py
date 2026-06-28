"""SQLAlchemy declarative Base used by all models and Alembic."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common declarative base. All ORM models inherit from this."""

    pass
