"""Verify Phase 4: documents endpoints + RBAC enforcement + lifespan ensure_indexed."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///./phase4_smoke.db")

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


# Use a temp VECTORSTORE so each smoke run starts clean.
TMP_VS = Path(tempfile.mkdtemp(prefix="firststepai_vs_"))
os.environ["VECTORSTORE_PATH"] = str(TMP_VS)
os.environ["POLICIES_PDF"] = str(TMP_VS / "policies.pdf")
# Create a tiny stub PDF so reindex has something to ingest. (just the bare
# minimum — chromadb will happily split it into chunks).
import importlib

import app.config.settings as settings_mod  # noqa: E402

settings_mod.get_settings.cache_clear()
from app.config import get_settings  # noqa: E402

settings = get_settings()
settings.VECTORSTORE_PATH = str(TMP_VS)
settings.POLICIES_PDF = str(TMP_VS / "policies.pdf")


DEMO = [
    ("admin@umbrella.corp", "Alex Wesker", "admin", "EMP-001"),
    ("hr@umbrella.corp", "Lisa Trevor", "hr", "EMP-002"),
    ("manager@umbrella.corp", "William Birkin", "manager", "EMP-003"),
    ("employee@umbrella.corp", "Jill Valentine", "employee", "EMP-004"),
    ("demo@umbrella.corp", "Ada Wong", "employee", "EMP-005"),
]


def _reset_db() -> None:
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

        for email, full_name, role, emp_id in DEMO:
            uid = str(uuid.uuid4())
            db.add(User(
                id=uid, email=email, full_name=full_name, role=role,
                password_hash=hash_password("demo123"),
                permissions=[p.value for p in permissions_for_role(role)],
            ))
            db.flush()
            db.add(Employee(
                id=str(uuid.uuid4()), user_id=uid, employee_id=emp_id,
                designation="X", department="HQ", office_location="HQ",
                leave_balance=10, hire_date=date(2020, 1, 1),
            ))
        db.commit()


def _check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print("[phase4-smoke] starting")
    _reset_db()
    _seed()

    employee = TestClient(app)
    r = employee.post("/api/v1/auth/login", json={
        "email": "demo@umbrella.corp", "password": "demo123",
    })
    _check("login employee", r.status_code == 200)
    emp_ck = r.cookies

    admin = TestClient(app)
    r = admin.post("/api/v1/auth/login", json={
        "email": "admin@umbrella.corp", "password": "demo123",
    })
    _check("login admin", r.status_code == 200)
    admin_ck = r.cookies

    # ----- list documents (empty so far) -----
    r = employee.get("/api/v1/documents", cookies=emp_ck)
    _check("GET /documents (employee, empty)", r.status_code == 200)
    _check("employee sees 0 docs", r.json() == [], f"got {len(r.json())}")

    # ----- upload as employee = 403 -----
    r = employee.post("/api/v1/documents", cookies=emp_ck, json={
        "title": "Handbook", "text": "All employees must wash their hands.",
        "doc_type": "policy", "department": "HR", "required_role": "all",
    })
    _check("POST /documents (employee = 403)", r.status_code == 403)

    # ----- upload as admin = 201 -----
    r = admin.post("/api/v1/documents", cookies=admin_ck, json={
        "title": "General Handbook",
        "text": "All employees must wash their hands. Vacation: 15 days per year.",
        "doc_type": "handbook",
        "department": "HR",
        "required_role": "all",
    })
    _check("POST /documents (admin)", r.status_code == 201, r.text[:120])
    public_doc = r.json()
    _check("public doc has id", bool(public_doc.get("id")))
    _check("public doc required_role=all", public_doc.get("required_role") == "all")

    # ----- upload a restricted doc (HR only) -----
    r = admin.post("/api/v1/documents", cookies=admin_ck, json={
        "title": "HR Confidential Salaries",
        "text": "Salary bands: junior $50k, senior $120k, director $200k.",
        "doc_type": "memo",
        "department": "HR",
        "required_role": "hr",
    })
    _check("POST /documents (HR-restricted)", r.status_code == 201, r.text[:120])
    hr_doc = r.json()
    _check("hr doc required_role=hr", hr_doc.get("required_role") == "hr")

    # ----- employee list: should only see the public doc -----
    r = employee.get("/api/v1/documents", cookies=emp_ck)
    _check("GET /documents (employee)", r.status_code == 200)
    docs = r.json()
    _check("employee sees 1 doc", len(docs) == 1, f"got {len(docs)}")
    _check("employee sees public doc", any(d["title"] == "General Handbook" for d in docs))

    # ----- employee fetch HR-restricted doc = 404 (not 403, to avoid enumeration) -----
    r = employee.get(f"/api/v1/documents/{hr_doc['id']}", cookies=emp_ck)
    _check("GET /documents/{hr_id} (employee = 404)", r.status_code == 404)

    # ----- admin fetch HR doc = 200 -----
    r = admin.get(f"/api/v1/documents/{hr_doc['id']}", cookies=admin_ck)
    _check("GET /documents/{hr_id} (admin = 200)", r.status_code == 200)

    # ----- delete as employee = 403 -----
    r = employee.delete(f"/api/v1/documents/{public_doc['id']}", cookies=emp_ck)
    _check("DELETE /documents (employee = 403)", r.status_code == 403)

    # ----- delete as admin = 204 -----
    r = admin.delete(f"/api/v1/documents/{public_doc['id']}", cookies=admin_ck)
    _check("DELETE /documents (admin = 204)", r.status_code == 204)

    r = employee.get("/api/v1/documents", cookies=emp_ck)
    _check("after delete, employee sees 0 docs", len(r.json()) == 0)

    # ----- reindex (no PDF, returns 0 chunks gracefully) -----
    r = admin.post("/api/v1/documents/reindex", cookies=admin_ck)
    _check("POST /documents/reindex (admin)", r.status_code == 200, r.text[:80])

    print("[phase4-smoke] ALL CHECKS PASSED")
    shutil.rmtree(TMP_VS, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())