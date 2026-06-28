"""LLM service abstraction — wraps any provider behind a uniform async iterator."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Sequence

Message = dict  # {"role": "system"|"user"|"assistant", "content": str}


class LLMService(ABC):
    """Common interface for chat completions with streaming."""

    @abstractmethod
    def stream(self, messages: Sequence[Message], **kwargs) -> Iterator[str]:
        """Yield content chunks (synchronous generator)."""

    @abstractmethod
    async def astream(self, messages: Sequence[Message], **kwargs) -> AsyncIterator[str]:
        """Yield content chunks (async generator)."""

    def invoke(self, messages: Sequence[Message], **kwargs) -> str:
        return "".join(self.stream(messages, **kwargs))

    @property
    @abstractmethod
    def model_name(self) -> str: ...