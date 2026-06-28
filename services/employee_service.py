"""Employee service — load and refresh the logged-in employee's profile."""
from __future__ import annotations

from auth.models import EmployeeProfile, User
from auth.services import get_auth_service


def get_employee_profile(user: User) -> EmployeeProfile:
    """Return the employee's profile (re-read fresh from the user database).

    The in-session User object is used as a fallback if the database read fails
    (e.g. during role edits mid-session).
    """
    svc = get_auth_service()
    fresh = svc.get_user_by_id(user.id)
    if fresh and fresh.employee_profile:
        return fresh.employee_profile
    return user.employee_profile