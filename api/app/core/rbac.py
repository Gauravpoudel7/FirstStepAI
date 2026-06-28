"""Role-based access control.

The role -> permission matrix is the single source of truth used by:
  - the chat system prompt (declares what the employee is allowed to ask)
  - the RAG retriever (filters out documents tagged above the user's role)
  - the UI (hides admin tabs, gates pages)
  - FastAPI dependencies (require_role / require_permission)
"""
from __future__ import annotations

from enum import Enum
from typing import Iterable


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


# Preserved verbatim from core/rbac.py
ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.EMPLOYEE: frozenset(
        {Permission.READ_PUBLIC_DOCS, Permission.READ_ENGINEERING_DOCS}
    ),
    Role.MANAGER: frozenset(
        {
            Permission.READ_PUBLIC_DOCS,
            Permission.READ_ENGINEERING_DOCS,
            Permission.READ_HR_POLICIES,
        }
    ),
    Role.HR: frozenset(
        {
            Permission.READ_PUBLIC_DOCS,
            Permission.READ_ENGINEERING_DOCS,
            Permission.READ_HR_POLICIES,
            Permission.READ_FINANCE_DOCS,
            Permission.VIEW_ALL_PROFILES,
        }
    ),
    Role.ADMIN: frozenset(set(Permission)),  # all permissions
}


def permissions_for_role(role: Role | str) -> frozenset[Permission]:
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return frozenset()
    return ROLE_PERMISSIONS.get(role, frozenset())


def can_access(role: Role | str, permission: Permission | str) -> bool:
    """True if the given role has the permission. Role may be a string or enum."""
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return False
    if isinstance(permission, str):
        try:
            permission = Permission(permission)
        except ValueError:
            return False
    return permission in permissions_for_role(role)


def allowed_doc_roles(role: Role | str) -> list[str]:
    """Roles a doc may be tagged with for this user to retrieve it.

    Admin can read everything; every other role can read docs marked 'all'
    in addition to its own role.
    """
    if isinstance(role, str):
        role_value = role
    else:
        role_value = role.value
    if role_value == Role.ADMIN.value or role_value == "admin":
        return ["all", "employee", "manager", "hr", "admin"]
    return [role_value, "all"]


def role_badge_color(role: Role | str) -> str:
    """Hex color for the role badge in the UI."""
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return "#9ca3af"
    return {
        Role.ADMIN: "#ef4444",
        Role.HR: "#10b981",
        Role.MANAGER: "#3b82f6",
        Role.EMPLOYEE: "#7c3aed",
    }.get(role, "#9ca3af")


def all_roles() -> Iterable[Role]:
    return [Role.ADMIN, Role.HR, Role.MANAGER, Role.EMPLOYEE]
