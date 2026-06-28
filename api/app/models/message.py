"""Conversation ORM (re-exported from conversation.py for backward compat)."""
from app.models.conversation import Conversation, Message

__all__ = ["Conversation", "Message"]