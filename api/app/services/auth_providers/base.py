"""AuthProvider ABC — pluggable auth backends (local DB, AzureAD, Google, LDAP)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class AuthProvider(ABC):
    """Abstract base for auth backends. Mirrors the existing AuthProvider ABC."""

    @abstractmethod
    def authenticate(self, email: str, password: str) -> "User":
        """Return the User on success; raise InvalidCredentialsError on failure."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> "User | None":
        ...

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> "User | None":
        ...

    @abstractmethod
    def list_users(self) -> list["User"]:
        ...

    @abstractmethod
    def create_user(self, user: "User", password: str) -> "User":
        ...

    @abstractmethod
    def reset_password(self, user_id: str, new_password: str) -> None:
        ...

    @abstractmethod
    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        ...

    @abstractmethod
    def update_user_role(self, user_id: str, role: str) -> "User":
        ...

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        ...