"""Application configuration loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # LLM
    HF_TOKEN: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Auth
    AUTH_SECRET: str = "change-me-in-production"
    AUTH_PROVIDER: str = "local"  # local | azure_ad | google | ldap
    REMEMBER_ME_MAX_AGE: int = 60 * 60 * 24 * 30  # 30 days
    RESET_TOKEN_MAX_AGE: int = 60 * 15  # 15 minutes
    BCRYPT_ROUNDS: int = 12

    # Company / branding
    COMPANY_NAME: str = "Umbrella Corporation"
    COMPANY_LOGO_URL: str = (
        "https://upload.wikimedia.org/wikipedia/commons/0/0e/Umbrella_Corporation_logo.svg"
    )
    COMPANY_FAVICON: str = "⛛"
    THEME: str = "dark"  # dark | light

    # Storage
    DATA_DIR: str = "./data"
    VECTORSTORE_PATH: str = "./data/vectorstore"
    USERS_DB_PATH: str = "./data/users.json"
    FEEDBACK_PATH: str = "./data/feedback.json"
    POLICIES_PDF: str = "./data/umbrella_corp_policies.pdf"

    # Misc
    ANONYMIZED_TELEMETRY: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
