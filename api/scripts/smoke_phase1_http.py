"""Verify Phase 1 HTTP endpoints via FastAPI TestClient.

Uses an ephemeral SQLite DB and the same demo seed as smoke_phase1.py.
Proves login → /auth/me → /auth/refresh → /auth/logout all work over HTTP.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///./dev_http.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.core.rbac import ROLE_PERMISSIONS, permissions_for_role  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.employee import Employee  # noqa: E402
from app.models.role_permission import Permission as PermissionRow  # noqa: E402
from app.models.role_permission import RolePermission  # noqa: E402
from app.models.user import User  # noqa: E402
from app.security.password import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from sqlalchemy import delete  # noqa: E402

DEMO = [
    ("admin@umbrella.corp", "Alex Wesker", "admin", "EMP-001", "Chief Operations Officer", "Operations"),
    ("hr@umbrella.corp", "Lisa Trevor", "hr", "EMP-002", "HR Specialist", "HR"),
    ("manager@umbrella.corp", "William Birkin", "manager", "EMP-003", "Head of R&D", "R&D"),
    ("employee@umbrella.corp", "Jill Valentine", "employee", "EMP-004", "Security Operations Specialist", "Security"),
    ("demo@umbrella.corp", "Ada Wong", "employee", "EMP-005", "Field Intelligence Analyst", "Operations"),
]


def _reset() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _seed() -> None:
    with SessionLocal() as db:
        db.execute(delete(RolePermission))
        db.execute(delete(PermissionRow))
        db.execute(delete(Employee))
        db.execute(delete(User))
        db.commit()

        all_perms = sorted({p.value for role in ROLE_PERMISSIONS.values() for p in role})
        for name in all_perms:
            db.add(PermissionRow(name=name))
        db.commit()
        for role, perms in ROLE_PERMISSIONS.items():
            for perm in perms:
                db.add(RolePermission(role=role.value, permission=perm.value))
        db.commit()

        import uuid

        for email, full_name, role, emp_id, designation, department in DEMO:
            user_id = str(uuid.uuid4())
            db.add(User(
                id=user_id,
                email=email,
                full_name=full_name,
                role=role,
                password_hash=hash_password("demo123"),
                permissions=[p.value for p in permissions_for_role(role)],
            ))
            db.flush()
            db.add(Employee(
                id=str(uuid.uuid4()),
                user_id=user_id,
                employee_id=emp_id,
                designation=designation,
                department=department,
                office_location="HQ",
                leave_balance=10,
                hire_date=date(2020, 1, 1),
                projects=["Sample Project"],
                skills=["Skill A", "Skill B"],
            ))
        db.commit()


def _check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print(f"[http-smoke] DATABASE_URL = {get_settings().DATABASE_URL}")
    _reset()
    _seed()
    _check("seeded", True)

    client = TestClient(app)

    # 1. demo-accounts
    r = client.get("/api/v1/auth/demo-accounts")
    _check("GET /auth/demo-accounts", r.status_code == 200, f"{len(r.json())} rows")
    _check("5 demo accounts", len(r.json()) == 5)

    # 2. login demo@umbrella.corp
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@umbrella.corp", "password": "demo123"},
    )
    _check("POST /auth/login", r.status_code == 200, r.headers.get("set-cookie", "")[:80])
    _check(
        "login response has user",
        r.json().get("user", {}).get("email") == "demo@umbrella.corp",
    )

    # 3. /auth/me with the cookie
    cookies = r.cookies
    r = client.get("/api/v1/auth/me", cookies=cookies)
    _check("GET /auth/me", r.status_code == 200)
    _check("/auth/me role", r.json().get("role") == "employee")
    _check("/auth/me initials", r.json().get("initials") == "AW")

    # 4. /auth/me without cookie = 401
    fresh_client = TestClient(app)
    r = fresh_client.get("/api/v1/auth/me")
    _check("GET /auth/me unauthed = 401", r.status_code == 401)

    # 5. refresh rotates
    r = client.post("/api/v1/auth/refresh", cookies=cookies)
    _check("POST /auth/refresh", r.status_code == 200, f"expires_in={r.json().get('expires_in')}")
    new_cookies = r.cookies
    _check(
        "refresh rotated",
        new_cookies.get("refresh_token") != cookies.get("refresh_token"),
    )

    # 6. wrong password = 401
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@umbrella.corp", "password": "wrong"},
    )
    _check("wrong password = 401", r.status_code == 401)

    # 7. logout
    r = client.post("/api/v1/auth/logout", cookies=new_cookies)
    _check("POST /auth/logout", r.status_code == 200)

    # 8. healthz
    r = client.get("/healthz")
    _check("GET /healthz", r.status_code == 200 and r.json() == {"status": "ok"})

    # 9. RBAC enforcement: change-password wrong current
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@umbrella.corp", "password": "demo123"},
    )
    cookies = r.cookies
    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong", "new_password": "newpass123"},
        cookies=cookies,
    )
    _check("change-password wrong = 400", r.status_code == 400)

    r = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "demo123", "new_password": "newpass123"},
        cookies=cookies,
    )
    _check("change-password ok", r.status_code == 200)

    # 10. log in with new password to confirm change took effect
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@umbrella.corp", "password": "newpass123"},
    )
    _check("login with new password", r.status_code == 200)

    print()
    print("ALL PHASE 1 HTTP SMOKE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())