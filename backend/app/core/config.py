"""
Centralized application settings loaded from environment variables.

This module is the single source of truth for application configuration.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.providers.types import ProviderType


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = "LinguaAI API"
    app_version: str = "0.1.0"

    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"

    debug: bool = True

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str
    redis_url: str

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    secret_key: str

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    # ------------------------------------------------------------------
    # AI
    # ------------------------------------------------------------------

    ai_provider: ProviderType = ProviderType.MOCK

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    allowed_origins: list[str] = [
        "http://localhost:5173",
    ]

    api_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()

__all__ = [
    "Settings",
    "get_settings",
    "settings",
]