"""Projects endpoints — list/create/get/update/delete (Phase 7)."""
from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    status: str
    owner_id: str
    start_date: str | None = None
    end_date: str | None = None
    tags: list[str] = []
    member_ids: list[str] = []
    created_at: str

    @classmethod
    def from_orm_project(cls, p) -> "ProjectOut":
        return cls(
            id=p.id,
            name=p.name,
            description=p.description or "",
            status=p.status,
            owner_id=p.owner_id,
            start_date=p.start_date.isoformat() if p.start_date else None,
            end_date=p.end_date.isoformat() if p.end_date else None,
            tags=p.tags or [],
            member_ids=[m.employee_id for m in (p.members or [])],
            created_at=p.created_at.isoformat(),
        )


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    status: str = "active"
    start_date: date | None = None
    end_date: date | None = None
    tags: list[str] = []
    member_ids: list[str] = []


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    tags: list[str] | None = None


@router.get("", response_model=list[ProjectOut])
def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ProjectOut]:
    projects = project_service.list_projects(db, current_user)
    return [ProjectOut.from_orm_project(p) for p in projects]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    current_user: Annotated[User, Depends(require_role("manager", "admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectOut:
    project = project_service.create_project(
        db,
        current_user,
        name=body.name,
        description=body.description,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
        tags=body.tags,
        member_ids=body.member_ids,
    )
    return ProjectOut.from_orm_project(project)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectOut:
    project = project_service.get_project(db, current_user, project_id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    return ProjectOut.from_orm_project(project)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    body: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectOut:
    project = project_service.update_project(
        db,
        current_user,
        project_id,
        name=body.name,
        description=body.description,
        status=body.status,
        start_date=body.start_date,
        end_date=body.end_date,
        tags=body.tags,
    )
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found or not editable")
    return ProjectOut.from_orm_project(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    ok = project_service.delete_project(db, current_user, project_id)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found or not deletable")


@router.get("/employees/options", response_model=list[dict])
def list_employee_options(
    current_user: Annotated[User, Depends(require_role("manager", "admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    """Roster for the create-project member picker."""
    employees = project_service.list_employees(db)
    return [
        {
            "id": e.id,
            "employee_id": e.employee_id,
            "name": e.user.full_name if e.user else "",
            "department": e.department,
        }
        for e in employees
    ]