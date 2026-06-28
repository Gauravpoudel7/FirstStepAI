"""Abstract base class for authentication providers.

Future SSO / LDAP providers (AzureAD, GoogleWorkspace, Okta, AD) implement
this interface and can be swapped in via the AUTH_PROVIDER env var without
touching the rest of the codebase.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from auth.models import User


class AuthProvider(ABC):
    """Pluggable auth backend."""

    @abstractmethod
    def authenticate(self, email: str, password: str) -> User: ...

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def list_users(self) -> list[User]: ...

    @abstractmethod
    def reset_password(self, email: str, new_password: str) -> bool: ...

    @abstractmethod
    def update_user_role(self, user_id: str, role: str) -> bool: ...