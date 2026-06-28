"""Chat endpoint — Server-Sent Events streaming."""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.conversation import Message
from app.models.user import User
from app.services.chat_service import (
    _employee_block,
    _retrieve_context,
    get_or_create_conversation,
)
from app.services.llm import get_llm_service
from app.services.prompts.system import build_system_prompt

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    stream: bool = True


def _sse_format(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_frames(db: Session, user: User, message: str, conversation_id: str | None):
    # Measure total request latency (retrieval + LLM), not just LLM time.
    start = time.time()

    convo = await asyncio.to_thread(get_or_create_conversation, db, user, conversation_id)
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=convo.id,
        role="user",
        content=message,
    )
    db.add(user_msg)
    await asyncio.to_thread(db.commit)

    context_text, sources = await asyncio.to_thread(_retrieve_context, user, message)
    if sources:
        yield _sse_format("sources", sources)

    system_prompt = build_system_prompt(
        company_name=get_settings().COMPANY_NAME,
        employee_information=_employee_block(user),
        retrieved_policy_information=context_text,
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in convo.messages
        if m.role in ("user", "assistant")
    ][-10:]
    # Append the current user message exactly once. Without this, the LLM sees
    # only system + prior history and responds to nothing — the most common
    # cause of "the chatbot ignores my message" reports.
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": message},
    ]

    if convo.title == "New conversation":
        # ASCII ellipsis to avoid mid-grapheme boundaries on multi-byte input.
        convo.title = (message[:48] + "...") if len(message) > 48 else message
        await asyncio.to_thread(db.commit)

    llm = get_llm_service()
    buffer: list[str] = []
    try:
        async for chunk in llm.astream(messages):
            if chunk:
                buffer.append(chunk)
                yield _sse_format("token", {"text": chunk})
    except Exception as exc:
        yield _sse_format("error", {"code": "llm_error", "message": str(exc)})
        return

    full_text = "".join(buffer).strip()
    asst = Message(
        id=str(uuid.uuid4()),
        conversation_id=convo.id,
        role="assistant",
        content=full_text,
        sources=sources or None,
        latency_ms=int((time.time() - start) * 1000),
    )
    db.add(asst)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, asst)
    yield _sse_format(
        "done",
        {"conversation_id": convo.id, "message_id": asst.id},
    )


@router.post("/chat/message")
async def chat_message(
    body: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StreamingResponse:
    # Eagerly touch the relationship to fail fast on detached-instance issues.
    _ = current_user.employee
    return StreamingResponse(
        _stream_frames(db, current_user, body.message, body.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )