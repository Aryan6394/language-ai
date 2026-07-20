"""Factory for resolving a provider identifier to a concrete AIProvider.

This module is the single location responsible for mapping provider
identifiers (e.g. Mock, Ollama, OpenAI) to their concrete
implementations.

Application services should depend only on `AIProvider` and obtain
instances through `ProviderFactory.create()`. This keeps business logic
provider-agnostic and allows switching providers through configuration
rather than code changes.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from app.providers.base import AIProvider, ProviderError
from app.providers.mock_provider import MockProvider
from app.providers.types import ProviderType
from app.providers.ollama_provider import OllamaProvider
logger = logging.getLogger(__name__)


class UnknownProviderError(ProviderError):
    """Raised when an unknown AI provider is requested."""


class ProviderFactory:
    """Factory for creating AI provider instances.

    The factory maintains a registry mapping provider identifiers to
    concrete provider implementations. New providers can be added by
    registering them without modifying business logic.
    """

    _registry: ClassVar[dict[ProviderType, type[AIProvider]]] = {
    ProviderType.MOCK: MockProvider,
    ProviderType.OLLAMA: OllamaProvider,
}

    @classmethod
    def create(
        cls,
        provider_name: str | ProviderType,
        **kwargs: Any,
    ) -> AIProvider:
        """Create an AI provider instance.

        Args:
            provider_name:
                Provider identifier as either a string or ProviderType.
            **kwargs:
                Arguments forwarded to the provider constructor.

        Returns:
            A configured AIProvider instance.

        Raises:
            UnknownProviderError:
                If the provider is not registered.
        """

        if isinstance(provider_name, str):
            if not provider_name.strip():
                raise ValueError("Provider name cannot be empty.")

            try:
                provider_name = ProviderType(provider_name.strip().lower())
            except ValueError as exc:
                available = ", ".join(
                    provider.value for provider in cls.available_providers()
                )
                logger.error(
                    "Unknown provider '%s'. Available providers: %s",
                    provider_name,
                    available,
                )
                raise UnknownProviderError(
                    f"Unknown AI provider '{provider_name}'. "
                    f"Available providers: {available}."
                ) from exc

        provider_cls = cls._registry.get(provider_name)

        if provider_cls is None:
            available = ", ".join(
                provider.value for provider in cls.available_providers()
            )
            logger.error(
                "Provider '%s' is not registered. Available providers: %s",
                provider_name.value,
                available,
            )
            raise UnknownProviderError(
                f"Provider '{provider_name.value}' is not registered."
            )

        logger.info(
            "Creating provider '%s' (%s)",
            provider_name.value,
            provider_cls.__name__,
        )

        return provider_cls(**kwargs)

    @classmethod
    def register(
        cls,
        provider_name: ProviderType,
        provider_cls: type[AIProvider],
    ) -> None:
        """Register a provider implementation.

        Args:
            provider_name:
                Identifier used to resolve the provider.
            provider_cls:
                AIProvider implementation.

        Raises:
            TypeError:
                If provider_cls is not a subclass of AIProvider.
        """

        if not issubclass(provider_cls, AIProvider):
            raise TypeError(
                f"{provider_cls!r} is not a subclass of AIProvider."
            )

        if provider_name in cls._registry:
            logger.warning(
                "Overwriting existing provider registration for '%s'.",
                provider_name.value,
            )

        cls._registry[provider_name] = provider_cls

        logger.info(
            "Registered provider '%s' -> %s",
            provider_name.value,
            provider_cls.__name__,
        )

    @classmethod
    def available_providers(cls) -> list[ProviderType]:
        """Return all registered provider identifiers."""

        return sorted(cls._registry.keys(), key=lambda provider: provider.value)