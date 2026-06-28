"""Project service — list/create/update/delete with role gating.

Visibility rules (parity with Phase 7 plan):
  - ADMIN sees all projects.
  - MANAGER+ sees projects they own OR projects they're a member of.
  - EMPLOYEE sees projects they're a member of.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.rbac import Role
from app.models.employee import Employee
from app.models.project import Project, ProjectMember

if TYPE_CHECKING:
    from app.models.user import User


def _employee_for(db: Session, user: "User") -> Employee | None:
    return db.scalar(select(Employee).where(Employee.user_id == user.id))


def _visible_query(db: Session, user: "User"):
    emp = _employee_for(db, user)
    if user.role == Role.ADMIN.value:
        return select(Project).options(selectinload(Project.members))
    if emp is None:
        return select(Project).where(Project.id == "__never__")
    member_project_ids = select(ProjectMember.project_id).where(
        ProjectMember.employee_id == emp.id
    )
    return (
        select(Project)
        .options(selectinload(Project.members))
        .where(or_(Project.owner_id == emp.id, Project.id.in_(member_project_ids)))
    )


def list_projects(db: Session, user: "User") -> list[Project]:
    return list(db.scalars(_visible_query(db, user).order_by(Project.created_at.desc())).all())


def get_project(db: Session, user: "User", project_id: str) -> Project | None:
    project = db.get(Project, project_id, options=[selectinload(Project.members)])
    if project is None:
        return None
    if user.role == Role.ADMIN.value:
        return project
    emp = _employee_for(db, user)
    if emp is None:
        return None
    if project.owner_id == emp.id:
        return project
    is_member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.employee_id == emp.id,
        )
    )
    return project if is_member else None


def create_project(
    db: Session,
    user: "User",
    *,
    name: str,
    description: str,
    status: str,
    start_date: date | None,
    end_date: date | None,
    tags: list[str],
    member_ids: list[str] | None = None,
) -> Project:
    emp = _employee_for(db, user)
    if emp is None:
        raise ValueError("User has no employee profile; cannot create projects")
    project = Project(
        id=str(uuid.uuid4()),
        name=name.strip(),
        description=(description or "").strip(),
        owner_id=emp.id,
        status=status or "active",
        start_date=start_date,
        end_date=end_date,
        tags=tags or [],
    )
    db.add(project)
    db.flush()
    # Owner is implicitly a member
    db.add(ProjectMember(project_id=project.id, employee_id=emp.id, role="owner"))
    for mid in member_ids or []:
        if mid == emp.id:
            continue
        db.add(ProjectMember(project_id=project.id, employee_id=mid, role="contributor"))
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    user: "User",
    project_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    tags: list[str] | None = None,
) -> Project | None:
    project = get_project(db, user, project_id)
    if project is None:
        return None
    # Only owner/admin can edit
    if user.role != Role.ADMIN.value:
        emp = _employee_for(db, user)
        if emp is None or project.owner_id != emp.id:
            return None
    if name is not None:
        project.name = name.strip()
    if description is not None:
        project.description = description.strip()
    if status is not None:
        project.status = status
    if start_date is not None:
        project.start_date = start_date
    if end_date is not None:
        project.end_date = end_date
    if tags is not None:
        project.tags = tags
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, user: "User", project_id: str) -> bool:
    project = db.get(Project, project_id)
    if project is None:
        return False
    if user.role != Role.ADMIN.value:
        emp = _employee_for(db, user)
        if emp is None or project.owner_id != emp.id:
            return False
    db.delete(project)
    db.commit()
    return True


def list_employees(db: Session) -> list[Employee]:
    return list(
        db.scalars(select(Employee).order_by(Employee.employee_id)).all()
    )