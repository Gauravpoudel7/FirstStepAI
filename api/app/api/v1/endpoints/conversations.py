"""Conversation endpoints — list, create, rename, delete, messages."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    preview: str | None = None


class ConversationPatch(BaseModel):
    title: str | None = None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: list | None = None
    feedback: str | None = None
    created_at: str


class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str  # "up" | "down"


def _conv_out(conv: Conversation, preview: str | None = None) -> ConversationOut:
    return ConversationOut(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        preview=preview,
    )


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
) -> list[ConversationOut]:
    # Fetch the conversation + its first message via a single window-function
    # subquery. The previous implementation lazy-loaded `c.messages` per row
    # (an N+1 — one full messages fetch per conversation).
    first_msg_subq = (
        select(
            Message.conversation_id.label("conversation_id"),
            Message.content.label("content"),
            func.row_number()
            .over(
                partition_by=Message.conversation_id,
                order_by=Message.created_at.asc(),
            )
            .label("rn"),
        )
        .subquery()
    )
    stmt = (
        select(Conversation, first_msg_subq.c.content)
        .outerjoin(
            first_msg_subq,
            (first_msg_subq.c.conversation_id == Conversation.id)
            & (first_msg_subq.c.rn == 1),
        )
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    rows = db.execute(stmt).all()
    out: list[ConversationOut] = []
    for c, preview_text in rows:
        preview = (preview_text[:80] if preview_text else None)
        if q and q.lower() not in c.title.lower() and (preview is None or q.lower() not in preview.lower()):
            continue
        out.append(_conv_out(c, preview))
    return out


class ConversationCreate(BaseModel):
    title: str | None = None


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    body: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ConversationOut:
    import uuid

    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=(body.title or "New conversation").strip() or "New conversation",
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return _conv_out(conv)


@router.patch("/{conversation_id}", response_model=ConversationOut)
def rename_conversation(
    conversation_id: str,
    body: ConversationPatch,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ConversationOut:
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    if body.title is not None:
        conv.title = body.title.strip() or conv.title
    db.commit()
    db.refresh(conv)
    # Fetch just the first message instead of lazy-loading the whole
    # relationship to read one row.
    first_msg = db.execute(
        select(Message.content)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
        .limit(1)
    ).scalar_one_or_none()
    preview = first_msg[:80] if first_msg else None
    return _conv_out(conv, preview)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    db.delete(conv)
    db.commit()


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[MessageOut]:
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    msgs = (
        db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [
        MessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=m.sources,
            feedback=m.feedback,
            created_at=m.created_at.isoformat(),
        )
        for m in msgs
    ]


@router.post("/feedback", status_code=status.HTTP_200_OK)
def submit_feedback(
    body: FeedbackRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    if body.feedback not in ("up", "down"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "feedback must be 'up' or 'down'"
        )
    msg = db.get(Message, body.message_id)
    if not msg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    conv = db.get(Conversation, msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    msg.feedback = body.feedback
    db.commit()
    return {"status": "ok"}