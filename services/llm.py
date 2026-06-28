"""LLM factory — Groq (Llama 3.1) by default."""
from __future__ import annotations

import os

from config.settings import get_settings


def build_llm():
    """Construct the chat model. Falls back gracefully if the API key is missing."""
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Set it in .env to enable the chatbot."
        )
    from langchain_groq import ChatGroq

    os.environ.setdefault("GROQ_API_KEY", settings.GROQ_API_KEY)
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        streaming=True,
        temperature=0.3,
    )