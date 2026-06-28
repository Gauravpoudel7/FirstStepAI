"""Mock LLM service for offline / test runs."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Sequence

from app.services.llm.base import LLMService


class MockLLMService(LLMService):
    """Deterministic streaming stub — returns the user message echoed back.

    Useful for tests and offline development.
    """

    def __init__(self, prefix: str = "[mock] ") -> None:
        self._prefix = prefix
        self._model = "mock-llm"

    def stream(self, messages: Sequence[dict], **kwargs) -> Iterator[str]:
        user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        response = (
            f"{self._prefix}I received your question about: \"{user}\". "
            "This is a deterministic mock response — no LLM is actually running. "
            "Connect a Groq API key to enable real streaming."
        )
        for word in response.split(" "):
            yield word + " "

    async def astream(self, messages: Sequence[dict], **kwargs) -> AsyncIterator[str]:
        for token in self.stream(messages, **kwargs):
            yield token
            await asyncio.sleep(0)  # yield to event loop

    @property
    def model_name(self) -> str:
        return self._model