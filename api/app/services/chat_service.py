"""Chat service — orchestrates retrieval + LLM streaming + persistence."""
from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from app.config import get_settings
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.services.llm import get_llm_service
from app.services.prompts.system import build_system_prompt
from app.services.rag import RoleAwareRetriever, build_vectorstore, load_vectorstore

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _employee_block(user: User) -> str:
    e = user.employee
    if not e:
        return f"Name: {user.full_name}\nRole: {user.role}\n"
    lines = [
        f"Name: {user.full_name}",
        f"Email: {user.email}",
        f"Role: {user.role}",
        f"Employee ID: {e.employee_id}",
        f"Department: {e.department or '—'}",
        f"Designation: {e.designation or '—'}",
        f"Office: {e.office_location or '—'}",
        f"Leave balance: {e.leave_balance} days",
        f"Projects: {', '.join(e.projects or []) or '—'}",
        f"Skills: {', '.join(e.skills or []) or '—'}",
    ]
    return "\n".join(lines)


def _retrieve_context(user: User, query: str, k: int = 4) -> tuple[str, list[dict]]:
    """Run role-filtered retrieval. Returns (concatenated_text, sources)."""
    try:
        embeddings = load_vectorstore.__module__  # avoid unused
        from app.services.rag.embeddings import build_embeddings

        embeddings = build_embeddings()
        vs = load_vectorstore(embeddings)
        base = vs.as_retriever(search_kwargs={"k": k})
        retriever = RoleAwareRetriever(base_retriever=base, user_role=str(user.role), k=k)
        docs = retriever.invoke(query)
    except Exception:
        # Log with traceback so failures are diagnosable. Silently swallowing
        # here used to mask the "chatbot returns plausible but ungrounded
        # answers" symptom — usually the zero-vector embeddings fallback.
        logger.exception(
            "RAG retrieval failed for user=%s role=%s; returning empty context.",
            getattr(user, "id", None), getattr(user, "role", None),
        )
        return "", []
    if not docs:
        return "", []
    text = "\n\n---\n\n".join(d.page_content for d in docs)
    sources = [
        {
            "doc_id": (d.metadata.get("source") or "unknown"),
            "title": (d.metadata.get("source") or "Document"),
            "chunk_id": str(i),
        }
        for i, d in enumerate(docs)
    ]
    return text, sources


def get_or_create_conversation(db: "Session", user: User, conversation_id: str | None) -> Conversation:
    if conversation_id:
        convo = db.get(Conversation, conversation_id)
        if convo and convo.user_id == user.id:
            return convo
    convo = Conversation(id=str(uuid.uuid4()), user_id=user.id, title="New conversation")
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo


def _history_messages(db: "Session", conversation: Conversation, limit: int = 10) -> list[dict]:
    msgs = list(conversation.messages)[-limit:]
    return [{"role": m.role, "content": m.content} for m in msgs if m.role in ("user", "assistant")]


def _persist_message(
    db: "Session",
    conversation: Conversation,
    role: str,
    content: str,
    sources: list[dict] | None = None,
    tokens: int | None = None,
    latency_ms: int | None = None,
) -> Message:
    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        role=role,
        content=content,
        sources=sources or None,
        tokens=tokens,
        latency_ms=latency_ms,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


async def stream_chat(
    db: "Session",
    user: User,
    message: str,
    conversation_id: str | None,
) -> AsyncIterator[dict]:
    """Yield structured frames for the SSE endpoint.

    Frame shapes:
      {"event": "sources", "data": [...]}
      {"event": "token",   "data": {"text": "..."}}
      {"event": "done",    "data": {"conversation_id": "...", "message_id": "..."}}
      {"event": "error",   "data": {"code": "...", "message": "..."}}
    """
    convo = get_or_create_conversation(db, user, conversation_id)
    _persist_message(db, convo, role="user", content=message)

    context_text, sources = _retrieve_context(user, message)
    if sources:
        yield {"event": "sources", "data": sources}

    employee_block = _employee_block(user)
    system_prompt = build_system_prompt(
        company_name=get_settings().COMPANY_NAME,
        employee_information=employee_block,
        retrieved_policy_information=context_text,
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    messages.extend(_history_messages(db, convo, limit=10))
    messages.append({"role": "user", "content": message})

    # Update conversation title from the first user message.
    if convo.title == "New conversation":
        convo.title = (message[:48] + "…") if len(message) > 48 else message
        db.commit()

    llm = get_llm_service()
    buffer: list[str] = []
    try:
        async for chunk in llm.astream(messages):
            if chunk:
                buffer.append(chunk)
                yield {"event": "token", "data": {"text": chunk}}
    except Exception as exc:
        yield {
            "event": "error",
            "data": {"code": "llm_error", "message": str(exc)},
        }
        return

    full_text = "".join(buffer).strip()
    assistant_msg = _persist_message(
        db,
        convo,
        role="assistant",
        content=full_text,
        sources=sources or None,
    )
    yield {
        "event": "done",
        "data": {
            "conversation_id": convo.id,
            "message_id": assistant_msg.id,
        },
    }