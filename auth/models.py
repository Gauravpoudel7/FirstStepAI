"""Auth models — User, Role, Permission."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Role(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class Permission(str, Enum):
    READ_PUBLIC_DOCS = "read_public_docs"
    READ_HR_POLICIES = "read_hr_policies"
    READ_FINANCE_DOCS = "read_finance_docs"
    READ_ENGINEERING_DOCS = "read_engineering_docs"
    READ_RESTRICTED_DOCS = "read_restricted_docs"
    VIEW_ALL_PROFILES = "view_all_profiles"
    MANAGE_USERS = "manage_users"
    UPLOAD_DOCS = "upload_docs"
    VIEW_AUDIT_LOG = "view_audit_log"


class EmployeeProfile(BaseModel):
    """Extended employee fields the chatbot can talk about."""

    employee_id: str
    full_name: str
    email: str
    phone_number: str = ""
    designation: str = ""
    department: str = ""
    manager_id: Optional[str] = None
    manager_name: str = ""
    projects: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    office_location: str = ""
    leave_balance: int = 0
    hire_date: str = ""
    salary: float = 0.0
    permissions: list[str] = Field(default_factory=list)
    role: Role = Role.EMPLOYEE

    def to_readable_block(self) -> str:
        """Format the profile for system-prompt injection."""
        lines = [
            f"- Employee ID: {self.employee_id}",
            f"- Name: {self.full_name}",
            f"- Email: {self.email}",
            f"- Phone: {self.phone_number or 'N/A'}",
            f"- Designation: {self.designation or 'N/A'}",
            f"- Department: {self.department or 'N/A'}",
            f"- Manager: {self.manager_name or 'N/A'} (ID: {self.manager_id or 'N/A'})",
            f"- Office Location: {self.office_location or 'N/A'}",
            f"- Hire Date: {self.hire_date or 'N/A'}",
            f"- Leave Balance: {self.leave_balance} days",
            f"- Active Projects: {', '.join(self.projects) if self.projects else 'None'}",
            f"- Skills: {', '.join(self.skills) if self.skills else 'None'}",
            f"- Role: {self.role.value}",
            f"- Permissions: {', '.join(self.permissions) if self.permissions else 'None'}",
        ]
        return "\n".join(lines)


class User(BaseModel):
    """An authenticated user account. Persisted to data/users.json."""

    id: str
    email: str
    full_name: str
    role: Role = Role.EMPLOYEE
    password_hash: str
    employee_profile: EmployeeProfile
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ---------- helpers ----------

    def initials(self) -> str:
        parts = [p for p in self.full_name.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()