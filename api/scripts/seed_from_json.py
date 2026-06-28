"""One-shot importer for data/users.json.

Preserves the existing bcrypt password hashes (rounds=12) so all five demo
accounts keep working with their default `demo123` password. Verifies each
hash; flags failures with must_reset_password=True.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

from app.config import get_settings
from app.core.rbac import permissions_for_role
from app.db.session import SessionLocal
from app.models.employee import Employee
from app.models.user import User
from app.security.password import verify_password


DEFAULT_PASSWORD = "demo123"


def _coerce_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _import_users(json_path: Path) -> tuple[int, int, int]:
    """Returns (imported, skipped_existing, flagged_must_reset)."""
    settings = get_settings()
    if not json_path.exists():
        print(f"[seed] no users file at {json_path}; skipping user import")
        return 0, 0, 0

    raw = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        print(f"[seed] {json_path} is not a JSON list; skipping")
        return 0, 0, 0

    imported = 0
    skipped = 0
    flagged = 0
    default_password = DEFAULT_PASSWORD

    with SessionLocal() as db:
        # Pre-fetch existing emails to skip duplicates
        existing_emails = {
            row[0]
            for row in db.execute(select(User.email)).all()
        }

        for row in raw:
            email = (row.get("email") or "").lower()
            if not email or email in existing_emails:
                skipped += 1
                continue

            user_id = row.get("id") or str(uuid4())
            password_hash = row.get("password_hash") or ""
            role = row.get("role") or "employee"
            full_name = row.get("full_name") or email

            must_reset = False
            try:
                if password_hash and not verify_password(default_password, password_hash):
                    must_reset = True
                    flagged += 1
            except Exception:
                must_reset = True
                flagged += 1

            user = User(
                id=user_id,
                email=email,
                full_name=full_name,
                role=role,
                password_hash=password_hash,
                permissions=[p.value for p in permissions_for_role(role)],
                must_reset_password=must_reset,
            )
            db.add(user)
            db.flush()

            ep = row.get("employee_profile") or {}
            emp = Employee(
                id=str(uuid4()),
                user_id=user_id,
                employee_id=ep.get("employee_id") or f"EMP-{user_id[:6].upper()}",
                phone_number=ep.get("phone_number", ""),
                designation=ep.get("designation", ""),
                department=ep.get("department", ""),
                manager_id=None,  # set in a second pass below
                office_location=ep.get("office_location", ""),
                leave_balance=int(ep.get("leave_balance") or 0),
                hire_date=_coerce_date(ep.get("hire_date")) or date(2020, 1, 1),
                salary=float(ep.get("salary") or 0),
                projects=list(ep.get("projects") or []),
                skills=list(ep.get("skills") or []),
            )
            db.add(emp)
            db.flush()
            # second pass: manager_id by employee_id
            if ep.get("manager_id"):
                manager_emp = (
                    db.execute(
                        select(Employee).where(Employee.employee_id == ep["manager_id"])
                    ).scalar_one_or_none()
                )
                if manager_emp is not None:
                    emp.manager_id = manager_emp.id

            imported += 1
            existing_emails.add(email)

        db.commit()

    print(
        f"[seed] imported={imported} skipped={skipped} flagged_must_reset={flagged} "
        f"data_dir={settings.DATA_DIR}"
    )
    return imported, skipped, flagged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed users from data/users.json")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/users.json"),
        help="Path to users.json (default: data/users.json)",
    )
    args = parser.parse_args(argv)
    _import_users(args.source)
    return 0


if __name__ == "__main__":
    sys.exit(main())