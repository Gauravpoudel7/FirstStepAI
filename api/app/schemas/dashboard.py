"""Dashboard schemas."""
from __future__ import annotations

from pydantic import BaseModel


class UpcomingHoliday(BaseModel):
    date: str
    name: str


class Announcement(BaseModel):
    title: str
    body: str
    created_at: str


class AIUsage(BaseModel):
    messages_today: int
    tokens_this_week: int


class DashboardSummary(BaseModel):
    full_name: str
    role: str
    department: str
    designation: str
    leave_balance: int
    active_projects: int
    upcoming_holidays: list[UpcomingHoliday] = []
    announcements: list[Announcement] = []
    ai_usage: AIUsage = AIUsage(messages_today=0, tokens_this_week=0)
