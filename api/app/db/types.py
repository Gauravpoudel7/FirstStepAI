"""Cross-dialect column types.

Lets the same ORM model work against both PostgreSQL (production) and SQLite
(local dev without Docker). At import time we pick types based on the engine.
"""
from __future__ import annotations

from sqlalchemy import JSON, CHAR, String
from sqlalchemy.types import TypeDecorator

from app.db.session import is_sqlite

# ---- UUID ----

class GUID(TypeDecorator):
    """Platform-independent GUID stored as 36-char string on SQLite, native
    UUID on Postgres. Always returns/accepts Python str.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID

            return dialect.type_descriptor(UUID(as_uuid=False))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


# ---- JSON container ----

def json_column():
    """JSONB on Postgres, JSON everywhere else."""
    if not is_sqlite():
        from sqlalchemy.dialects.postgresql import JSONB

        return JSONB(astext_type=String)
    return JSON


# ---- IP address ----

def ip_column():
    """INET on Postgres, plain String elsewhere."""
    if not is_sqlite():
        from sqlalchemy.dialects.postgresql import INET

        return INET
    return String(45)  # plenty for v4 + v6