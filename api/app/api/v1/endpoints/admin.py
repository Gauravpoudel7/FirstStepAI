"""Admin endpoints — user list/role change, activity log summary (Phase 7)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_role
from app.core.rbac import Role
from app.db.session import get_db
from app.models.employee import Employee
from app.models.user import User
from app.services import activity_log_service

router = APIRouter(prefix="/admin", tags=["admin"])


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    department: str | None = None
    employee_id: str | None = None


class RoleUpdate(BaseModel):
    role: str


def _user_to_out(u: User) -> UserOut:
    emp: Employee | None = getattr(u, "employee", None)
    return UserOut(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        role=u.role,
        is_active=u.is_active,
        department=emp.department if emp else None,
        employee_id=emp.employee_id if emp else None,
    )


@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> list[UserOut]:
    users = list(
        db.scalars(
            select(User).options(joinedload(User.employee)).order_by(User.email)
        ).all()
    )
    return [_user_to_out(u) for u in users]


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_role(
    user_id: str,
    body: RoleUpdate,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> UserOut:
    valid = {r.value for r in Role}
    if body.role not in valid:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"role must be one of: {sorted(valid)}"
        )
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    target.role = body.role
    # Audit row first, then commit both in one transaction. Previously the
    # role change was committed before the audit row, so a failure in the
    # second commit left the role updated with no audit trail. With
    # commit=False the audit row is staged in the same session and committed
    # atomically with the role update below.
    activity_log_service.record(
        db,
        actor_id=current_user.id,
        action="role_update",
        resource_type="user",
        resource_id=target.id,
        extra={"new_role": body.role},
        commit=False,
    )
    db.commit()
    db.refresh(target)
    return _user_to_out(target)


@router.get("/activity-log")
def get_activity_log(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
    action: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    return activity_log_service.summary(db) if not action else {
        "entries": [
            {
                "id": r.id,
                "action": r.action,
                "actor_id": r.actor_id,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "ip": r.ip,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in activity_log_service.list_logs(db, action=action, limit=limit)
        ]
    }