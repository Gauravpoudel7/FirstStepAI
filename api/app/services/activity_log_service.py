"""Activity log service — append-only listing for admin analytics."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog

if TYPE_CHECKING:
    pass


def record(
    db: Session,
    *,
    actor_id: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    extra: dict | None = None,
    commit: bool = True,
) -> ActivityLog | None:
    """Insert an activity log row.

    When ``commit=False``, the row is added to the session but not flushed —
    callers can then commit multiple rows atomically with their own
    transaction (e.g. updating a user's role AND recording the audit row in
    one db.commit). When ``commit=True`` (default), the row is committed
    immediately.
    """
    entry = ActivityLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip=ip,
        user_agent=user_agent,
        extra=extra or {},
    )
    db.add(entry)
    if commit:
        db.commit()
        return entry
    db.flush()
    return entry


def list_logs(
    db: Session,
    *,
    action: str | None = None,
    limit: int = 100,
) -> list[ActivityLog]:
    stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
    if action:
        stmt = (
            select(ActivityLog)
            .where(ActivityLog.action == action)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
    return list(db.scalars(stmt).all())


def summary(db: Session) -> dict:
    """Aggregated counts for the analytics dashboard."""
    # Aggregate in SQL instead of loading every row. The previous loop loaded
    # the entire activity_log table just to count by action — a slow, O(N)
    # scan that grows unbounded with usage.
    count_rows = db.execute(
        select(ActivityLog.action, func.count(ActivityLog.id)).group_by(ActivityLog.action)
    ).all()
    counts: dict[str, int] = {action: int(count) for action, count in count_rows}
    recent = list_logs(db, limit=10)
    return {
        "counts_by_action": counts,
        "total": sum(counts.values()),
        "recent": [
            {
                "id": r.id,
                "action": r.action,
                "actor_id": r.actor_id,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "ip": r.ip,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "extra": r.extra,
            }
            for r in recent
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }