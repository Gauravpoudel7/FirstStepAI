"""SQLAlchemy engine + session factory.

Pluggable: uses Postgres when DATABASE_URL points at one (production /
docker-compose), and SQLite when DATABASE_URL is unset or starts with
sqlite:/// (local dev without Docker). The same ORM models work for both.
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()


def _build_engine() -> Engine:
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        future=True,
    )


engine: Engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a session and ensures cleanup.

    Rolls back any pending transaction on exception so the session doesn't
    hold a failed transaction across requests — SQLAlchemy logs a warning
    otherwise when ``db.close()`` finds an in-progress txn.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def is_sqlite() -> bool:
    """True when the configured engine targets SQLite (dev fallback)."""
    return str(engine.url).startswith("sqlite")


def ensure_sqlite_schema() -> bool:
    """Create ORM tables in an empty SQLite DB at startup.

    Returns True when tables were created. SQLite is the local-dev fallback —
    if the file is missing, empty, or schema-less, every authenticated
    endpoint hangs on the first SELECT. Postgres is left alone because
    docker-compose + alembic handle its schema; auto-creating tables there
    would mask real migration drift.

    This must run AFTER every model module is imported so that
    ``Base.metadata`` is populated. Call from FastAPI's lifespan startup.
    """
    if not is_sqlite():
        return False

    parsed = urlparse(str(engine.url))
    db_path = parsed.path or ""
    if db_path and db_path != ":memory:":
        # SQLite URLs are sqlite:///./relative.db or sqlite:////abs/path.db;
        # urlparse strips the leading slash from the path so we reattach it.
        if db_path.startswith("/"):
            target = Path(db_path)
        else:
            target = Path(db_path.lstrip("/"))
        if target.exists() and target.stat().st_size > 0:
            # Non-empty file → assume schema is present (or deliberately
            # empty). Skip create_all to avoid clobbering prod-shaped DBs.
            return False

    # Import all model modules so Base.metadata sees them.
    from app.db import base  # noqa: F401  (registers declarative Base)
    import app.models  # noqa: F401  (imports every ORM model)

    base.Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    return bool(inspector.get_table_names())