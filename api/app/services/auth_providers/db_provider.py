"""SQL-backed AuthProvider. Replaces LocalAuthProvider (JSON file)."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import InvalidCredentialsError, UserNotFoundError
from app.core.rbac import permissions_for_role
from app.models.employee import Employee
from app.models.user import User
from app.security.password import hash_password, verify_password
from app.services.auth_providers.base import AuthProvider

if TYPE_CHECKING:
    pass


class SQLAuthProvider(AuthProvider):
    """PostgreSQL-backed auth provider. Preserves the existing AuthProvider surface."""

    def __init__(self, db: Session):
        self.db = db

    # ---- helpers ----

    def _load_user(self, user_id: str) -> User:
        user = (
            self.db.execute(
                select(User).options(joinedload(User.employee)).where(User.id == user_id)
            )
            .unique()
            .scalar_one_or_none()
        )
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def _load_by_email(self, email: str) -> User | None:
        return (
            self.db.execute(
                select(User)
                .options(joinedload(User.employee))
                .where(User.email == email.lower())
            )
            .unique()
            .scalar_one_or_none()
        )

    # ---- interface ----

    def authenticate(self, email: str, password: str) -> User:
        user = self._load_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self._load_by_email(email)

    def get_user_by_id(self, user_id: str) -> User | None:
        return (
            self.db.execute(
                select(User).options(joinedload(User.employee)).where(User.id == user_id)
            )
            .unique()
            .scalar_one_or_none()
        )

    def list_users(self) -> list[User]:
        return list(
            self.db.execute(
                select(User).options(joinedload(User.employee)).order_by(User.full_name)
            )
            .unique()
            .scalars()
        )

    def create_user(
        self,
        *,
        email: str,
        full_name: str,
        role: str,
        password: str,
        employee_profile: dict | None = None,
    ) -> User:
        # Avoid duplicate email case-insensitively
        if self._load_by_email(email) is not None:
            raise InvalidCredentialsError("Email already exists")

        user_id = str(uuid4())
        user = User(
            id=user_id,
            email=email.lower(),
            full_name=full_name,
            role=role,
            password_hash=hash_password(password),
            permissions=[p.value for p in permissions_for_role(role)],
        )
        self.db.add(user)
        self.db.flush()  # need user.id for employee row

        if employee_profile:
            emp = Employee(
                id=str(uuid4()),
                user_id=user_id,
                employee_id=employee_profile.get("employee_id") or f"EMP-{user_id[:6].upper()}",
                phone_number=employee_profile.get("phone_number", ""),
                designation=employee_profile.get("designation", ""),
                department=employee_profile.get("department", ""),
                manager_id=employee_profile.get("manager_id"),
                office_location=employee_profile.get("office_location", ""),
                leave_balance=employee_profile.get("leave_balance", 0),
                hire_date=employee_profile.get("hire_date") or date.today(),
                salary=employee_profile.get("salary", 0),
                projects=employee_profile.get("projects", []),
                skills=employee_profile.get("skills", []),
            )
            self.db.add(emp)
        self.db.commit()
        self.db.refresh(user)
        return user

    def reset_password(self, user_id: str, new_password: str) -> None:
        user = self._load_user(user_id)
        user.password_hash = hash_password(new_password)
        user.must_reset_password = False
        self.db.commit()

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = self._load_user(user_id)
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")
        user.password_hash = hash_password(new_password)
        self.db.commit()

    def update_user_role(self, user_id: str, role: str) -> User:
        user = self._load_user(user_id)
        user.role = role
        user.permissions = [p.value for p in permissions_for_role(role)]
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: str) -> None:
        user = self._load_user(user_id)
        user.is_active = False
        self.db.commit()