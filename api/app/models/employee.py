"""Employee ORM model — extended fields used by the LLM system prompt."""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID, json_column

if TYPE_CHECKING:
    from app.models.user import User


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    employee_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, default="", nullable=False)
    designation: Mapped[str] = mapped_column(String, default="", nullable=False)
    department: Mapped[str] = mapped_column(String, default="", nullable=False, index=True)
    manager_id: Mapped[str | None] = mapped_column(
        GUID(),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    office_location: Mapped[str] = mapped_column(String, default="", nullable=False)
    leave_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    projects: Mapped[list] = mapped_column(json_column(), default=list, nullable=False)
    skills: Mapped[list] = mapped_column(json_column(), default=list, nullable=False)
    extra: Mapped[dict] = mapped_column("metadata", json_column(), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="employee")
    manager: Mapped["Employee | None"] = relationship(
        "Employee", remote_side="Employee.id", foreign_keys=[manager_id]
    )

    def to_readable_block(self) -> str:
        """Format the profile for system-prompt injection (parity with auth/models.py)."""
        lines = [
            f"- Employee ID: {self.employee_id}",
            f"- Name: {self.user.full_name if self.user else 'N/A'}",
            f"- Email: {self.user.email if self.user else 'N/A'}",
            f"- Phone: {self.phone_number or 'N/A'}",
            f"- Designation: {self.designation or 'N/A'}",
            f"- Department: {self.department or 'N/A'}",
            f"- Manager: {(self.manager.user.full_name if self.manager and self.manager.user else 'N/A')}",
            f"- Office Location: {self.office_location or 'N/A'}",
            f"- Hire Date: {self.hire_date.isoformat() if self.hire_date else 'N/A'}",
            f"- Leave Balance: {self.leave_balance} days",
            f"- Active Projects: {', '.join(self.projects) if self.projects else 'None'}",
            f"- Skills: {', '.join(self.skills) if self.skills else 'None'}",
            f"- Role: {self.user.role if self.user else 'employee'}",
        ]
        return "\n".join(lines)