"""Shared provider types used across the AI provider layer."""

from enum import StrEnum


class ProviderType(StrEnum):
    """Supported AI provider identifiers.

    These values are used throughout the application to reference AI
    providers in a type-safe manner. Adding a new provider requires
    adding a new enum member and registering it with
    ``ProviderFactory``.
    """

    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"