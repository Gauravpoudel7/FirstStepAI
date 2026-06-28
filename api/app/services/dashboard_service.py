"""Dashboard summary service — assembles a per-user dashboard payload.

For the MVP we derive everything from the Employee profile (no separate
projects table yet) and seed deterministic upcoming-holidays + announcements.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from app.schemas.dashboard import (
    AIUsage,
    Announcement,
    DashboardSummary,
    UpcomingHoliday,
)

if TYPE_CHECKING:
    from app.models.user import User


ANNOUNCEMENTS = [
    Announcement(
        title="Q3 Compliance Training",
        body="All employees must complete the new compliance training by end of month.",
        created_at=datetime.utcnow().isoformat(),
    ),
    Announcement(
        title="New AI Assistant Available",
        body="FirstStepAI is now live for all staff — ask anything about HR policies or your profile.",
        created_at=datetime.utcnow().isoformat(),
    ),
]


def _holidays_for(year: int) -> list[UpcomingHoliday]:
    return [
        UpcomingHoliday(date=f"{year}-12-25", name="Christmas Day"),
        UpcomingHoliday(date=f"{year}-12-31", name="New Year's Eve"),
        UpcomingHoliday(date=f"{year + 1}-01-01", name="New Year's Day"),
    ]


def build_summary(user: "User") -> DashboardSummary:
    profile = user.employee
    today = date.today()
    holidays = [h for h in _holidays_for(today.year) if date.fromisoformat(h.date) >= today][:3]

    return DashboardSummary(
        full_name=user.full_name,
        role=user.role,
        department=profile.department if profile else "",
        designation=profile.designation if profile else "",
        leave_balance=profile.leave_balance if profile else 0,
        active_projects=len(profile.projects) if profile and profile.projects else 0,
        upcoming_holidays=holidays,
        announcements=ANNOUNCEMENTS,
        ai_usage=AIUsage(messages_today=0, tokens_this_week=0),
    )