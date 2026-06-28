"""Profile endpoints — read/update current user's employee profile."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.employee import Employee
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileOut(BaseModel):
    employee_id: str | None = None
    full_name: str
    email: str
    phone_number: str = ""
    designation: str = ""
    department: str = ""
    manager_name: str = ""
    office_location: str = ""
    leave_balance: int = 0
    hire_date: str | None = None
    salary: float = 0.0
    projects: list[str] = []
    skills: list[str] = []
    role: str


def _to_out(user: User) -> ProfileOut:
    e: Employee | None = user.employee
    return ProfileOut(
        employee_id=e.employee_id if e else None,
        full_name=user.full_name,
        email=user.email,
        phone_number=e.phone_number if e else "",
        designation=e.designation if e else "",
        department=e.department if e else "",
        manager_name=(e.manager.user.full_name if e and e.manager and e.manager.user else ""),
        office_location=e.office_location if e else "",
        leave_balance=e.leave_balance if e else 0,
        hire_date=e.hire_date.isoformat() if e and e.hire_date else None,
        salary=float(e.salary) if e and e.salary else 0.0,
        projects=list(e.projects or []) if e else [],
        skills=list(e.skills or []) if e else [],
        role=user.role,
    )


@router.get("/me", response_model=ProfileOut)
def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]) -> ProfileOut:
    return _to_out(current_user)


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None
    office_location: str | None = None


@router.patch("/me", response_model=ProfileOut)
def update_my_profile(
    body: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProfileOut:
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.phone_number is not None and current_user.employee:
        current_user.employee.phone_number = body.phone_number
    if body.office_location is not None and current_user.employee:
        current_user.employee.office_location = body.office_location
    db.commit()
    db.refresh(current_user)
    return _to_out(current_user)


@router.get("", response_model=list[ProfileOut])
@router.get("/", response_model=list[ProfileOut])  # type: ignore[misc]  # noqa: E501
def list_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
    department: str | None = None,
) -> list[ProfileOut]:
    """List employees (HR/ADMIN only)."""
    if current_user.role not in ("hr", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requires HR or admin role")
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload

    from app.models.user import User as UserModel

    # joinedload(employee) avoids the N+1 that would happen on the `e.department`,
    # `e.manager.user.full_name`, etc. accesses inside `_to_out`. The previous
    # implementation fired one lazy-load query per user.
    stmt = (
        select(UserModel)
        .options(joinedload(UserModel.employee))
        .where(UserModel.is_active.is_(True))
    )
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (UserModel.full_name.ilike(like)) | (UserModel.email.ilike(like))
        )
    if department:
        # SQL-side filter on the joined Employee row instead of post-filtering
        # every active user in Python.
        stmt = stmt.join(Employee, Employee.user_id == UserModel.id).where(
            Employee.department == department
        )
    users = list(db.execute(stmt.order_by(UserModel.full_name)).scalars())
    return [_to_out(u) for u in users]  # noqa: E501


@router.get("/{employee_id}", response_model=ProfileOut)
def get_employee_profile(
    employee_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProfileOut:
    """Fetch a single employee profile by employee_id (HR/ADMIN only)."""
    if current_user.role not in ("hr", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requires HR or admin role")
    from sqlalchemy import select

    target = db.execute(
        select(User).join(Employee, Employee.user_id == User.id).where(Employee.employee_id == employee_id)
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return _to_out(target)