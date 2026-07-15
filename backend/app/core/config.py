"""
Centralized application settings, loaded from environment variables via
`.env` (see backend/.env.example).

Scope (per current task): foundation settings only — application identity,
environment/debug flags, database and cache connection strings, CORS, and
API prefix. Deliberately excluded, per requirements:
  - Authentication secrets (e.g. password hashing config)
  - JWT settings (signing key, algorithm, token expiry)
  - AI/LLM model settings (provider, API keys, quota limits)
  - Any other business logic

Those belong to their own domains once implemented (e.g. a future
app/core/security.py for auth/JWT, and a future service module for
AI/quota configuration).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Human-readable app name, shown in FastAPI's auto-generated docs (/docs, /redoc).
    app_name: str = "LinguaAI API"

    # App version string, also shown in the auto-generated docs. Bump on releases.
    app_version: str = "0.1.0"

      # Which environment this instance is running in (development | staging | production).
    # Used for environment-aware behavior (e.g. stricter CORS in production).
    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"
    # Enables verbose error output / auto-reload friendly behavior.
    # Should be False in production.
    debug: bool = True

    # SQLAlchemy connection string for the primary Postgres database.
    database_url: str = "postgresql://linguaai:linguaai@localhost:5432/linguaai"

    # Connection string for Redis, used for caching and future session/quota state.
    redis_url: str = "redis://localhost:6379/0"

    # Origins allowed to make cross-origin requests to this API (browser clients).
    # Should be tightened to real frontend domain(s) outside of local development.
    allowed_origins: list[str] = [
    "http://localhost:5173",
]

    # Prefix applied to all API routes (see API.md: base URL is /api/v1).
    api_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — read once per process."""
    return Settings()
