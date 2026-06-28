"""Verify Phase 1 end-to-end: schema creation, demo accounts, login, JWT round-trip.

Usage (from api/):

    # 1. Set SQLite dev DB
    $env:DATABASE_URL="sqlite:///./dev.db"

    # 2. Run
    python scripts/smoke_phase1.py

What it does:
    1. Drops + creates all tables (SQLite or Postgres).
    2. Seeds RBAC permissions.
    3. Creates the five demo users (mirrors data/users.json seed).
    4. Asserts login works with demo123 for every account.
    5. Asserts /auth/me round-trips the JWT.
    6. Asserts wrong password is rejected with 401.
    7. Asserts refresh-token rotation produces a fresh access cookie.

Exits 0 on full success, non-zero on the first failed assertion.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import date
from pathlib import Path

# Add api/ to path so `app.*` imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Default to a local SQLite file if DATABASE_URL is not set
os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")

from app.config import get_settings  # noqa: E402
from app.core.rbac import ROLE_PERMISSIONS, permissions_for_role  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.employee import Employee  # noqa: E402
from app.models.role_permission import Permission as PermissionRow  # noqa: E402
from app.models.role_permission import RolePermission  # noqa: E402
from app.models.user import User  # noqa: E402
from app.security.jwt import (  # noqa: E402
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.security.password import hash_password, verify_password  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from sqlalchemy import delete  # noqa: E402

DEMO_USERS = [
    ("admin@umbrella.corp", "Alex Wesker", "admin", "EMP-001", "Chief Operations Officer", "Operations", "Raccoon City HQ — Executive Wing", 22, ["HIVE Control Expansion", "Executive AI Platform"]),
    ("hr@umbrella.corp", "Lisa Trevor", "hr", "EMP-002", "HR Specialist", "HR", "Raccoon City HQ — HR Wing", 15, ["Policy Compliance Review", "Onboarding Cohort Q3"]),
    ("manager@umbrella.corp", "William Birkin", "manager", "EMP-003", "Head of R&D", "R&D", "Underground Lab B-13", 12, ["G-Virus Stabilization", "Tyrant T-103 Iteration"]),
    ("employee@umbrella.corp", "Jill Valentine", "employee", "EMP-004", "Security Operations Specialist", "Security", "Raccoon City HQ — Security Wing", 9, ["S.T.A.R.S. Reactivation", "Outbreak Containment Drill"]),
    ("demo@umbrella.corp", "Ada Wong", "employee", "EMP-005", "Field Intelligence Analyst", "Operations", "Tokyo Field Office", 7, ["Corporate Espionage Ops", "Umbrella History Briefing"]),
]

DEFAULT_PASSWORD = "demo123"


def _seed_rbac(db) -> None:
    db.execute(delete(RolePermission))
    db.execute(delete(PermissionRow))
    db.commit()

    # Insert each unique permission once.
    all_perms = sorted({p.value for role in ROLE_PERMISSIONS.values() for p in role})
    for name in all_perms:
        db.add(PermissionRow(name=name))
    db.commit()

    # Then each (role, permission) pair.
    for role, perms in ROLE_PERMISSIONS.items():
        for perm in perms:
            db.add(RolePermission(role=role.value, permission=perm.value))
    db.commit()


def _seed_users(db) -> None:
    db.execute(delete(Employee))
    db.execute(delete(User))
    db.commit()

    emp_id_by_role: dict[str, str] = {}
    for email, full_name, role, emp_id, designation, department, office, leave, projects in DEMO_USERS:
        user_id = str(uuid.uuid4())
        u = User(
            id=user_id,
            email=email,
            full_name=full_name,
            role=role,
            password_hash=hash_password(DEFAULT_PASSWORD),
            permissions=[p.value for p in permissions_for_role(role)],
        )
        db.add(u)
        db.flush()
        e = Employee(
            id=str(uuid.uuid4()),
            user_id=user_id,
            employee_id=emp_id,
            designation=designation,
            department=department,
            office_location=office,
            leave_balance=leave,
            projects=projects,
            skills=["Surveillance", "Crisis Response", "Policy Review", "Tactical Planning"][: 2 + (hash(email) % 3)],
            hire_date=date(2020, 1, 1),
        )
        db.add(e)
        db.flush()
        emp_id_by_role[role] = e.id

    # Wire manager relationships: everyone reports to the admin (Alex Wesker)
    admin_emp_id = emp_id_by_role["admin"]
    db.execute(
        Employee.__table__.update().values(manager_id=admin_emp_id).where(Employee.id != admin_emp_id)
    )
    db.commit()


def _reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _check(label: str, ok: bool, detail: str = "") -> None:
    icon = "OK " if ok else "FAIL"
    print(f"  [{icon}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print(f"[smoke] DATABASE_URL = {get_settings().DATABASE_URL}")
    print("[smoke] resetting schema…")
    _reset_schema()
    _check("schema created", True)

    print("[smoke] seeding RBAC + demo users…")
    with SessionLocal() as db:
        _seed_rbac(db)
        _seed_users(db)
        total_users = db.query(User).count()
        total_perms = db.query(PermissionRow).count()
        total_role_perms = db.query(RolePermission).count()
    _check("users seeded", total_users == len(DEMO_USERS), f"{total_users} rows")
    _check("permissions seeded", total_perms >= 9, f"{total_perms} rows")
    _check("role_permissions seeded", total_role_perms > 0, f"{total_role_perms} rows")

    print("[smoke] verifying bcrypt verify(demo123)…")
    with SessionLocal() as db:
        sample = db.query(User).filter_by(email="demo@umbrella.corp").one()
        _check("demo123 verify", verify_password(DEFAULT_PASSWORD, sample.password_hash))

    print("[smoke] running auth round-trips via AuthService…")
    with SessionLocal() as db:
        svc = AuthService(db)
        for email, full_name, role, *_ in DEMO_USERS:
            user, access, ttl, refresh, refresh_expires = svc.login(email, DEFAULT_PASSWORD)
            _check(f"login({email})", user.email == email and access and refresh)
            payload = svc.decode_access(access)
            _check(
                f"jwt({email})",
                payload.get("sub") == user.id and payload.get("role") == role,
                f"role={payload.get('role')} ttl={ttl}",
            )
            # Refresh rotation
            user2, access2, _, refresh2, _ = svc.refresh(refresh)
            _check(f"refresh({email})", user2.id == user.id and access2 and refresh2 and refresh2 != refresh)

    print("[smoke] verifying invalid credentials raise…")
    with SessionLocal() as db:
        svc = AuthService(db)
        try:
            svc.login("demo@umbrella.corp", "wrong-password")
        except Exception as exc:
            _check("wrong password rejected", "Invalid" in str(exc) or "credentials" in str(exc).lower(), str(exc))
        else:
            _check("wrong password rejected", False, "no exception raised")

    print()
    print("ALL PHASE 1 SMOKE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())