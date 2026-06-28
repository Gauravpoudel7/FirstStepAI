"""Verify Phase 5: SSE chat streaming + persistence."""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite:///./phase5_smoke.db")
os.environ.setdefault("LLM_PROVIDER", "mock")

import tempfile
TMP_VS = Path(tempfile.mkdtemp(prefix="firststepai_vs5_"))
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
from sqlalchemy import delete, select  # noqa: E402


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

        uid = str(uuid.uuid4())
        db.add(User(
            id=uid, email="demo@umbrella.corp", full_name="Ada Wong", role="employee",
            password_hash=hash_password("demo123"),
            permissions=[p.value for p in permissions_for_role("employee")],
        ))
        db.flush()
        db.add(Employee(
            id=str(uuid.uuid4()), user_id=uid, employee_id="EMP-005",
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
                import json
                data = json.loads(line[len("data: "):])
        if event and data is not None:
            frames.append((event, data))
    return frames


def main() -> int:
    print("[phase5-smoke] starting")
    _reset_db()
    _seed()

    c = TestClient(app)
    r = c.post("/api/v1/auth/login", json={"email": "demo@umbrella.corp", "password": "demo123"})
    _check("login employee", r.status_code == 200)
    ck = r.cookies

    # Stream a chat message
    r = c.post(
        "/api/v1/chat/message",
        cookies=ck,
        json={"message": "What is the leave policy?", "stream": True},
    )
    _check("POST /chat/message", r.status_code == 200)
    _check("SSE content-type", r.headers.get("content-type", "").startswith("text/event-stream"))
    frames = _parse_sse(r.text)
    _check("has 'done' frame", any(ev == "done" for ev, _ in frames), f"frames={[ev for ev, _ in frames]}")
    _check("has at least 1 'token' frame", any(ev == "token" for ev, _ in frames),
           f"token count = {sum(1 for ev, _ in frames if ev == 'token')}")

    token_text = "".join(d.get("text", "") for ev, d in frames if ev == "token")
    _check("token text non-empty", len(token_text) > 0, f"len={len(token_text)}")
    done_frame = next(d for ev, d in frames if ev == "done")
    convo_id = done_frame.get("conversation_id")
    msg_id = done_frame.get("message_id")
    _check("done has conversation_id", bool(convo_id))
    _check("done has message_id", bool(msg_id))

    # Persistence: conversation + 2 messages saved
    with SessionLocal() as db:
        convo = db.get(Conversation, convo_id)
        _check("conversation persisted", convo is not None)
        _check("conversation has 2 messages", len(convo.messages) == 2,
               f"got {len(convo.messages)}")
        roles = [m.role for m in convo.messages]
        _check("user + assistant persisted", roles == ["user", "assistant"], str(roles))

    # Second turn uses the same conversation
    r = c.post(
        "/api/v1/chat/message",
        cookies=ck,
        json={"message": "And sick leave?", "conversation_id": convo_id, "stream": True},
    )
    _check("POST /chat/message (2nd turn)", r.status_code == 200)
    frames2 = _parse_sse(r.text)
    _check("2nd turn has 'done'", any(ev == "done" for ev, _ in frames2))
    done2 = next(d for ev, d in frames2 if ev == "done")
    _check("2nd turn same conversation", done2.get("conversation_id") == convo_id)

    with SessionLocal() as db:
        convo = db.get(Conversation, convo_id)
        _check("conversation now has 4 messages", len(convo.messages) == 4,
               f"got {len(convo.messages)}")

    print("[phase5-smoke] ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())