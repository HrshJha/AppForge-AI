"""Application configuration via Pydantic BaseSettings."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AppForge AI configuration – loaded from .env or environment variables."""

    # --- LLM ---
    LLM_PROVIDER: Literal["groq", "openai"] = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./appforge.db"

    # --- Auth ---
    JWT_SECRET: str = "appforge-dev-secret-change-in-prod"
    JWT_EXPIRY_HOURS: int = 24

    # --- Application ---
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://app-forge-ai-chi.vercel.app",
    ]

    # --- Pipeline ---
    MAX_PROMPT_LENGTH: int = 2000
    MAX_ENTITIES: int = 10
    MAX_REPAIR_PASSES: int = 3
    AMBIGUITY_THRESHOLD: float = 0.6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
