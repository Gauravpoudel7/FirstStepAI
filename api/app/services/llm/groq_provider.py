"""Groq-backed LLM service (ported from services/llm.py)."""
from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Sequence

from app.services.llm.base import LLMService


class GroqLLMService(LLMService):
    """ChatGroq wrapper preserving the existing model + temp defaults."""

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.3,
        api_key: str = "",
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._api_key = api_key
        self._chat = None

    def _client(self):
        if self._chat is None:
            from langchain_groq import ChatGroq

            self._chat = ChatGroq(
                model=self._model,
                temperature=self._temperature,
                groq_api_key=self._api_key or None,
                streaming=True,
            )
        return self._chat

    def stream(self, messages: Sequence[dict], **kwargs) -> Iterator[str]:
        chat = self._client()
        for chunk in chat.stream(list(messages)):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield text

    async def astream(self, messages: Sequence[dict], **kwargs) -> AsyncIterator[str]:
        chat = self._client()
        async for chunk in chat.astream(list(messages)):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield text

    @property
    def model_name(self) -> str:
        return self._model