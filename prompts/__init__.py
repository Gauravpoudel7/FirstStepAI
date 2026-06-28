"""Prompts package — system prompt, welcome message, per-role suggestions."""
from .system import SYSTEM_PROMPT
from .welcome import WELCOME_MESSAGE
from .suggested import SUGGESTED_PROMPTS

__all__ = ["SYSTEM_PROMPT", "WELCOME_MESSAGE", "SUGGESTED_PROMPTS"]
