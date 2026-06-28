"""Verify Phase 3 HTTP endpoints via FastAPI TestClient.

Ephemeral SQLite DB. Covers:
  - /api/v1/dashboard/summary
  - /api/v1/profile/me (GET / PATCH)
  - /api/v1/profile (list, RBAC 403 for non-HR/ADMIN)
  - /api/v1/profile/{id} (RBAC)
  - /api/v1/auth/change-password (success + wrong current)
  - /api/v1/auth/forgot-password
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///./phase3_http.db")

from fastapi.testclient import TestClient  # noqa: E402

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
    ("admin@umbrella.corp", "Alex Wesker", "admin", "EMP-001", "Chief Operations Officer", "Operations", 12, ["Corporate Espionage Ops", "Umbrella History Briefing"]),
    ("hr@umbrella.corp", "Lisa Trevor", "hr", "EMP-002", "HR Specialist", "HR", 18, ["Diversity Hiring", "Onboarding"]),
    ("manager@umbrella.corp", "William Birkin", "manager", "EMP-003", "Head of R&D", "R&D", 9, ["Tyrant Project", "G-Virus Research"]),
    ("employee@umbrella.corp", "Jill Valentine", "employee", "EMP-004", "Security Operations Specialist", "Security", 7, ["Mansion Incident Aftermath", "Weapon Training"]),
    ("demo@umbrella.corp", "Ada Wong", "employee", "EMP-005", "Field Intelligence Analyst", "Operations", 5, ["Corporate Espionage Ops"]),
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

        for email, full_name, role, emp_id, designation, department, leave, projects in DEMO:
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
                leave_balance=leave,
                hire_date=date(2020, 1, 1),
                projects=projects,
                skills=["Skill A", "Skill B"],
            ))
        db.commit()


def _check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print("[phase3-http-smoke] starting")
    _reset()
    _seed()

    # ----- demo login -----
    employee_client = TestClient(app)
    r = employee_client.post("/api/v1/auth/login", json={
        "email": "demo@umbrella.corp", "password": "demo123",
    })
    _check("POST /login (employee)", r.status_code == 200, f"cookies={list(r.cookies.keys())}")
    cookies = r.cookies

    # ----- /auth/me -----
    r = employee_client.get("/api/v1/auth/me", cookies=cookies)
    _check("GET /me (employee)", r.status_code == 200)
    me = r.json()
    _check("/me email", me["email"] == "demo@umbrella.corp")
    _check("/me has employee_profile", "employee_profile" in me)

    # ----- /dashboard/summary -----
    r = employee_client.get("/api/v1/dashboard/summary", cookies=cookies)
    _check("GET /dashboard/summary", r.status_code == 200, r.text[:80])
    summary = r.json()
    _check("summary.full_name", summary.get("full_name") == "Ada Wong")
    _check("summary.role", summary.get("role") == "employee")
    _check("summary.leave_balance (>=0)", summary.get("leave_balance", -1) >= 0)
    _check("summary.upcoming_holidays is list", isinstance(summary.get("upcoming_holidays"), list))
    _check("summary.announcements is list", isinstance(summary.get("announcements"), list))

    # ----- /profile/me GET -----
    r = employee_client.get("/api/v1/profile/me", cookies=cookies)
    _check("GET /profile/me", r.status_code == 200)
    p = r.json()
    _check("profile.me full_name", p.get("full_name") == "Ada Wong")
    _check("profile.me has employee_id", p.get("employee_id") is not None)

    # ----- /profile/me PATCH -----
    r = employee_client.patch("/api/v1/profile/me", cookies=cookies, json={
        "phone_number": "+1-555-0199",
        "office_location": "Raccoon City HQ",
    })
    _check("PATCH /profile/me", r.status_code == 200)
    p = r.json()
    _check("profile.me phone updated", p.get("phone_number") == "+1-555-0199")
    _check("profile.me office updated", p.get("office_location") == "Raccoon City HQ")

    # ----- /profile list as employee = 403 -----
    r = employee_client.get("/api/v1/profile", cookies=cookies)
    _check("GET /profile (employee = 403)", r.status_code == 403)

    # ----- /profile/{id} as employee = 403 -----
    r = employee_client.get("/api/v1/profile/EMP-001", cookies=cookies)
    _check("GET /profile/{id} (employee = 403)", r.status_code == 403)

    # ----- change-password wrong current = 401 -----
    r = employee_client.post("/api/v1/auth/change-password", cookies=cookies, json={
        "current_password": "WRONG", "new_password": "demo1234",
    })
    _check("POST /change-password (wrong current = 401/403)",
           r.status_code in (400, 401, 403),
           f"got {r.status_code}")

    # ----- change-password correct current = 200 -----
    r = employee_client.post("/api/v1/auth/change-password", cookies=cookies, json={
        "current_password": "demo123", "new_password": "demo1234",
    })
    _check("POST /change-password (correct = 200)", r.status_code == 200, r.text[:80])
    # restore demo1234 for downstream tests (must also be >= 8 chars)
    r = employee_client.post("/api/v1/auth/change-password", cookies=cookies, json={
        "current_password": "demo1234", "new_password": "demo12345",
    })
    _check("POST /change-password (restore = 200)", r.status_code == 200, r.text[:80])

    # ----- forgot-password = 200 (no enumeration) -----
    r = employee_client.post("/api/v1/auth/forgot-password", json={
        "email": "demo@umbrella.corp",
    })
    _check("POST /forgot-password (200)", r.status_code == 200)

    # ----- forgot-password unknown email = 200 (still generic) -----
    r = employee_client.post("/api/v1/auth/forgot-password", json={
        "email": "ghost@example.com",
    })
    _check("POST /forgot-password (unknown email = 200)", r.status_code == 200)

    # ----- admin login + list + single fetch -----
    admin_client = TestClient(app)
    r = admin_client.post("/api/v1/auth/login", json={
        "email": "admin@umbrella.corp", "password": "demo123",
    })
    _check("POST /login (admin)", r.status_code == 200)
    admin_cookies = r.cookies

    r = admin_client.get("/api/v1/profile", cookies=admin_cookies)
    _check("GET /profile (admin)", r.status_code == 200)
    profiles = r.json()
    _check("admin sees all 5 profiles", len(profiles) == 5, f"got {len(profiles)}")

    r = admin_client.get("/api/v1/profile/EMP-004", cookies=admin_cookies)
    _check("GET /profile/{id} (admin)", r.status_code == 200)
    target = r.json()
    _check("admin fetched Jill Valentine", target.get("full_name") == "Jill Valentine")

    r = admin_client.get("/api/v1/profile/EMP-NONEXISTENT", cookies=admin_cookies)
    _check("GET /profile/{nonexistent} (admin = 404)", r.status_code == 404)

    # ----- profile list filtered by department -----
    r = admin_client.get("/api/v1/profile", cookies=admin_cookies, params={"department": "Operations"})
    _check("GET /profile?department=Operations (admin)", r.status_code == 200)
    filtered = r.json()
    _check("only Operations profiles", all(p["department"] == "Operations" for p in filtered),
           f"{[p['department'] for p in filtered]}")

    print("[phase3-http-smoke] ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())