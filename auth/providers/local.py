"""Local JSON-backed auth provider.

Users are persisted in `data/users.json` as a list of dicts. The file is read
once per request into memory and written atomically (via utils.file_utils).
For a real deployment with thousands of users, swap this out for a SQL
provider — the AuthProvider ABC stays the same.
"""
from __future__ import annotations

import threading
from typing import Optional

from auth.models import Role, User
from auth.providers.base import AuthProvider
from auth.security import hash_password, verify_password
from config.settings import get_settings
from core.exceptions import InvalidCredentialsError, UserNotFoundError
from utils.file_utils import read_json, write_json


class LocalAuthProvider(AuthProvider):
    _lock = threading.Lock()

    # ---------- low-level file access ----------

    def _load(self) -> list[dict]:
        data = read_json(get_settings().USERS_DB_PATH, default=[])
        if not isinstance(data, list):
            return []
        return data

    def _save(self, users: list[dict]) -> None:
        write_json(get_settings().USERS_DB_PATH, users)

    @staticmethod
    def _from_row(row: dict) -> User:
        return User(**row)

    @staticmethod
    def _to_row(user: User) -> dict:
        return user.model_dump(mode="json")

    # ---------- AuthProvider API ----------

    def authenticate(self, email: str, password: str) -> User:
        email_norm = (email or "").strip().lower()
        if not email_norm or not password:
            raise InvalidCredentialsError("Email and password are required.")
        with self._lock:
            for row in self._load():
                if row.get("email", "").lower() == email_norm:
                    if not verify_password(password, row.get("password_hash", "")):
                        raise InvalidCredentialsError("Invalid email or password.")
                    return self._from_row(row)
        # Generic message — do not reveal whether the email exists.
        raise InvalidCredentialsError("Invalid email or password.")

    def get_user_by_email(self, email: str) -> Optional[User]:
        email_norm = (email or "").strip().lower()
        with self._lock:
            for row in self._load():
                if row.get("email", "").lower() == email_norm:
                    return self._from_row(row)
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            for row in self._load():
                if row.get("id") == user_id:
                    return self._from_row(row)
        return None

    def list_users(self) -> list[User]:
        with self._lock:
            return [self._from_row(r) for r in self._load()]

    def reset_password(self, email: str, new_password: str) -> bool:
        if not new_password or len(new_password) < 6:
            raise InvalidCredentialsError("Password must be at least 6 characters.")
        email_norm = (email or "").strip().lower()
        new_hash = hash_password(new_password)
        with self._lock:
            users = self._load()
            for row in users:
                if row.get("email", "").lower() == email_norm:
                    row["password_hash"] = new_hash
                    self._save(users)
                    return True
        raise UserNotFoundError(f"No user with email {email}.")

    def update_user_role(self, user_id: str, role: str) -> bool:
        try:
            new_role = Role(role)
        except ValueError:
            return False
        with self._lock:
            users = self._load()
            for row in users:
                if row.get("id") == user_id:
                    row["role"] = new_role.value
                    row["employee_profile"]["role"] = new_role.value
                    self._save(users)
                    return True
        return False