"""Ollama implementation of the AI provider interface."""

from __future__ import annotations

import logging
from typing import Any

from ollama import AsyncClient, ResponseError

from app.providers.base import (
    AIProvider,
    ChatMessage,
    ProviderGenerationError,
)

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """AI provider backed by a local Ollama server."""

    def __init__(
        self,
        model: str = "gemma3:4b",
        host: str = "http://localhost:11434",
    ) -> None:
        self._client = AsyncClient(host=host)
        self._model = model

    async def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Generate a text completion using Ollama."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        logger.debug("Ollama generate() called.")

        try:
            response = await self._client.generate(
                model=self._model,
                prompt=prompt,
                **kwargs,
            )

            return response.response

        except ResponseError as exc:
            logger.exception("Ollama generation failed.")
            raise ProviderGenerationError(str(exc)) from exc

        except Exception as exc:
            logger.exception("Unexpected Ollama error.")
            raise ProviderGenerationError(str(exc)) from exc

    async def chat(
        self,
        messages: list[ChatMessage],
        **kwargs: Any,
    ) -> str:
        print(">>> OLLAMA PROVIDER CALLED <<<")

        if not messages:
            raise ValueError("At least one message is required.")

        logger.debug(
            "Ollama chat() called with %d message(s).",
            len(messages),
        )

        try:
            response = await self._client.chat(
                model=self._model,
                messages=[
                    {
                        "role": message.role.value,
                        "content": message.content,
                    }
                    for message in messages
                ],
                **kwargs,
            )

            return response.message.content

        except ResponseError as exc:
            logger.exception("Ollama chat failed.")
            raise ProviderGenerationError(str(exc)) from exc

        except Exception as exc:
            logger.exception("Unexpected Ollama error.")
            raise ProviderGenerationError(str(exc)) from exc