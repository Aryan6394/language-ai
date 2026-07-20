"""Mock implementation of the AI provider interface.

The mock provider is intended for local development and testing. It
implements the AIProvider interface without calling an external AI
service, allowing the application to function even when no real model is
configured.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.providers.base import (
    AIProvider,
    ChatMessage,
)

logger = logging.getLogger(__name__)


class MockProvider(AIProvider):
    """Deterministic mock AI provider for testing and development."""

    async def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Generate a deterministic JSON dictionary response.

        Args:
            prompt: Input prompt.
            **kwargs: Reserved for compatibility with future providers.

        Returns:
            A JSON string matching the dictionary schema.

        Raises:
            ValueError:
                If the prompt is empty.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        logger.debug("Mock generate() called.")

        match = re.search(
            r'Look up the word "(.*?)" in language "(.*?)"',
            prompt,
        )

        word = match.group(1) if match else "unknown"
        language = match.group(2) if match else "unknown"

        if language == "ja":
            readings = [
                {
                    "script": "hiragana",
                    "reading": word,
                }
            ]
            definitions = [
                "Mock Japanese definition",
            ]
            examples = [
                f"{word}！",
            ]
        else:
            readings = []
            definitions = [
                "Mock definition",
            ]
            examples = [
                f"Example using '{word}'.",
            ]

        response = {
            "word": word,
            "language": language,
            "readings": readings,
            "senses": [
                {
                    "part_of_speech": "noun",
                    "definitions": definitions,
                    "examples": examples,
                }
            ],
        }

        logger.debug("Mock response: %s", response)

        return json.dumps(
            response,
            ensure_ascii=False,
            indent=2,
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        **kwargs: Any,
    ) -> str:
        """Generate a deterministic chat response.

        Args:
            messages: Conversation history.
            **kwargs: Reserved for compatibility with future providers.

        Returns:
            A deterministic mock assistant response.

        Raises:
            ValueError:
                If the message list is empty.
        """
        if not messages:
            raise ValueError("At least one message is required.")

        last_message = messages[-1]

        logger.debug(
            "Mock chat() called with %d message(s).",
            len(messages),
        )

        return (
            "[MOCK] Assistant reply: "
            f"{last_message.content}"
        )