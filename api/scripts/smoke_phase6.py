"""Verify Phase 6: /conversations CRUD + /messages + /feedback."""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///./phase6_smoke.db")
os.environ.setdefault("LLM_PROVIDER", "mock")

import tempfile
TMP_VS = Path(tempfile.mkdtemp(prefix="firststepai_vs6_"))
os.environ["VECTORSTORE_PATH"] = str(TMP_VS)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.rbac import ROLE_PERMISSIONS, permissions_for_role  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.conversation import Conversation, Message  # noqa: E402
from app.models.employee import Employee  # noqa: E402
from app.models.role_permission import Permission as PermissionRow  # noqa: E402
from app.models.role_permission import RolePermission  # noqa: E402
from app.models.user import User  # noqa: E402
from app.security.password import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from sqlalchemy import delete  # noqa: E402


def _reset_db() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _seed() -> None:
    with SessionLocal() as db:
        db.execute(delete(Message))
        db.execute(delete(Conversation))
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

        for email, full_name, role, emp_id in [
            ("demo@umbrella.corp", "Ada Wong", "employee", "EMP-005"),
            ("admin@umbrella.corp", "Alex Wesker", "admin", "EMP-001"),
        ]:
            uid = str(uuid.uuid4())
            db.add(User(
                id=uid, email=email, full_name=full_name, role=role,
                password_hash=hash_password("demo123"),
                permissions=[p.value for p in permissions_for_role(role)],
            ))
            db.flush()
            db.add(Employee(
                id=str(uuid.uuid4()), user_id=uid, employee_id=emp_id,
                designation="Field Intel", department="Operations",
                office_location="HQ", leave_balance=5, hire_date=date(2020, 1, 1),
            ))
        db.commit()


def _check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    frames = []
    for chunk in text.split("\n\n"):
        event = None
        data = None
        for line in chunk.splitlines():
            if line.startswith("event: "):
                event = line[len("event: "):]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: "):])
        if event and data is not None:
            frames.append((event, data))
    return frames


def main() -> int:
    print("[phase6-smoke] starting")
    _reset_db()
    _seed()

    c = TestClient(app)
    r = c.post("/api/v1/auth/login", json={"email": "demo@umbrella.corp", "password": "demo123"})
    _check("login", r.status_code == 200)
    ck = r.cookies

    # 1) List empty
    r = c.get("/api/v1/conversations", cookies=ck)
    _check("GET /conversations (empty)", r.status_code == 200)
    _check("starts with []", r.json() == [])

    # 2) Create a conversation
    r = c.post("/api/v1/conversations", cookies=ck, json={"title": "Leave policy Q's"})
    _check("POST /conversations", r.status_code == 201)
    conv = r.json()
    _check("has id", bool(conv.get("id")))
    _check("title persisted", conv["title"] == "Leave policy Q's")
    cid = conv["id"]

    # 3) Send 2 chat messages in the same conversation
    r1 = c.post("/api/v1/chat/message", cookies=ck, json={
        "message": "How many vacation days do I have?", "conversation_id": cid, "stream": True,
    })
    frames = _parse_sse(r1.text)
    _check("1st turn has done", any(ev == "done" for ev, _ in frames))
    msg1_id = next(d["message_id"] for ev, d in frames if ev == "done")

    r2 = c.post("/api/v1/chat/message", cookies=ck, json={
        "message": "And sick leave?", "conversation_id": cid, "stream": True,
    })
    frames2 = _parse_sse(r2.text)
    msg2_id = next(d["message_id"] for ev, d in frames2 if ev == "done")

    # 4) List messages
    r = c.get(f"/api/v1/conversations/{cid}/messages", cookies=ck)
    _check("GET /conversations/{id}/messages", r.status_code == 200)
    msgs = r.json()
    _check("4 messages persisted", len(msgs) == 4, f"got {len(msgs)}")
    _check("roles alternate user/assistant", [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"])

    # 5) Feedback thumbs up on first assistant msg
    r = c.post("/api/v1/conversations/feedback", cookies=ck, json={
        "message_id": msg1_id, "feedback": "up",
    })
    _check("POST /conversations/feedback (up)", r.status_code == 200)

    r = c.get(f"/api/v1/conversations/{cid}/messages", cookies=ck)
    msgs = r.json()
    _check("first assistant has feedback=up", msgs[1]["feedback"] == "up")

    # 6) Rename conversation
    r = c.patch(f"/api/v1/conversations/{cid}", cookies=ck, json={"title": "Time-off deep-dive"})
    _check("PATCH /conversations/{id}", r.status_code == 200)
    _check("title renamed", r.json()["title"] == "Time-off deep-dive")

    # 7) Search by title
    r = c.get("/api/v1/conversations", cookies=ck, params={"q": "time-off"})
    _check("GET /conversations?q=time-off", r.status_code == 200)
    _check("search returns the renamed conv", len(r.json()) == 1)

    r = c.get("/api/v1/conversations", cookies=ck, params={"q": "nomatch-xyz"})
    _check("search no-match returns []", r.json() == [])

    # 8) Delete
    r = c.delete(f"/api/v1/conversations/{cid}", cookies=ck)
    _check("DELETE /conversations/{id}", r.status_code == 204)

    r = c.get("/api/v1/conversations", cookies=ck)
    _check("after delete, list is empty", r.json() == [])

    # 9) Other users cannot see this user's conversations
    admin_c = TestClient(app)
    r = admin_c.post("/api/v1/auth/login", json={"email": "admin@umbrella.corp", "password": "demo123"})
    _check("admin login", r.status_code == 200)
    admin_ck = r.cookies
    r = admin_c.get(f"/api/v1/conversations/{cid}/messages", cookies=admin_ck)
    _check("cross-user fetch = 404", r.status_code == 404)

    print("[phase6-smoke] ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())