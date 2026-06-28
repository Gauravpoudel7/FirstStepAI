"""LLM factory — picks the configured provider at startup."""
from __future__ import annotations

from app.config import get_settings
from app.services.llm.base import LLMService
from app.services.llm.groq_provider import GroqLLMService
from app.services.llm.mock_provider import MockLLMService


def get_llm_service() -> LLMService:
    """Return an LLM service instance configured from current settings.

    The service is constructed fresh on each call. Caching via `lru_cache`
    would freeze the first-seen settings for the process lifetime — so a
    `GROQ_API_KEY` added to `.env` after the first request would never take
    effect, and the cached `MockLLMService` would keep returning
    `[no-key] …` placeholders forever.
    """
    settings = get_settings()
    provider = (settings.LLM_PROVIDER or "groq").lower()
    if provider == "mock":
        return MockLLMService()
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            # Fall back to mock if no key is configured — keeps the app
            # importable and the smoke tests running offline.
            return MockLLMService(prefix="[no-key] ")
        return GroqLLMService(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
        )
    raise ValueError(f"Unknown LLM provider: {provider}")