"""Application configuration loaded from environment / .env file.

Ported from the existing config/settings.py and extended with API-specific
settings (database, JWT, CORS, cookies). All defaults are safe for local dev.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Database / Redis ----
    DATABASE_URL: str = "postgresql+psycopg://firststepai:firststepai@localhost:5432/firststepai"
    ASYNC_DATABASE_URL: str = (
        "postgresql+asyncpg://firststepai:firststepai@localhost:5432/firststepai"
    )
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- LLM ----
    HF_TOKEN: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    LLM_PROVIDER: str = "groq"  # groq | mock

    # ---- Auth ----
    AUTH_SECRET: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_SECONDS: int = 900  # 15 min
    JWT_REFRESH_TTL_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    REMEMBER_ME_MAX_AGE: int = 60 * 60 * 24 * 30  # 30 days
    RESET_TOKEN_MAX_AGE: int = 60 * 15  # 15 min
    BCRYPT_ROUNDS: int = 12

    # ---- CORS / Cookies ----
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173"
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str = ""

    # ---- Company / branding ----
    COMPANY_NAME: str = "Umbrella Corporation"
    COMPANY_LOGO_URL: str = (
        "https://upload.wikimedia.org/wikipedia/commons/0/0e/Umbrella_Corporation_logo.svg"
    )
    COMPANY_FAVICON: str = "⛛"
    THEME: str = "dark"  # dark | light

    # ---- Storage ----
    # Relative paths here are resolved against the `api/` package root, NOT
    # the process cwd. The previous behavior used ``Path("./data/...")``
    # resolved at import-time against whatever directory uvicorn happened to
    # be launched from. When the API was started from the repo root (e.g.
    # ``uvicorn api.app.main:app`` from a tooling shell) the policies PDF
    # silently resolved to a non-existent ``<cwd>/data/umbrella_corp_policies.pdf``
    # and ``bootstrap_vectorstore`` no-op'd — so the bundled policies never
    # got indexed, the vector store only contained ad-hoc admin uploads,
    # and the chatbot returned ungrounded / junk retrievals.
    DATA_DIR: str = "_default_data_dir"
    VECTORSTORE_PATH: str = "_default_vectorstore"
    UPLOADS_PATH: str = "_default_uploads"
    POLICIES_PDF: str = "_default_policies_pdf"

    @property
    def _api_root(self) -> Path:
        # ``app/config/settings.py`` → ../../  → repo-relative ``api/``.
        return Path(__file__).resolve().parent.parent.parent

    @property
    def data_dir(self) -> Path:
        return self._api_root / "data"

    @property
    def vectorstore_path(self) -> Path:
        return self.data_dir / "vectorstore"

    @property
    def uploads_path(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def policies_pdf(self) -> Path:
        return self.data_dir / "umbrella_corp_policies.pdf"

    # ---- Misc ----
    ANONYMIZED_TELEMETRY: bool = False
    LOG_LEVEL: str = "INFO"

    # ---- Runtime mode ----
    # "dev" enables behaviors that are unsafe in production: returning password
    # reset tokens in API responses, using zero-vector embeddings, etc. Set to
    # "production" (or any non-"dev" value) to lock those paths down.
    ENV: str = "dev"
    RAG_ALLOW_ZERO_EMBEDDINGS: bool = False

    @property
    def is_dev(self) -> bool:
        return self.ENV.lower() == "dev"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
