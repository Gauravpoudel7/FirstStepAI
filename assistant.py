"""Back-compat shim — the `Assistant` class has moved to
`services.chat_service.ChatService`. Re-export for any external imports.
"""
from services.chat_service import ChatService as Assistant  # noqa: F401

__all__ = ["Assistant"]
