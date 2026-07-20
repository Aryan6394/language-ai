"""Dictionary service (ARCHITECTURE.md, Section 6 & 8).

Implements the cache-first, AI-fallback dictionary lookup flow: check
the database first, and only fall back to an AI provider when no entry
exists yet, persisting whatever the AI returns so the next lookup for
the same word is a cache hit.

This module is the Service layer for the Dictionary domain. It must
never execute SQL directly (that's `crud/dictionary.py`'s job), never
define a FastAPI route (that's `routers/dictionary.py`'s job), and
never import a concrete AI provider (Ollama, OpenAI, ...) — only the
`AIProvider` abstraction, injected via the constructor.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dictionary as crud
from app.models import DictionaryEntry
from app.providers.base import AIProvider, ProviderError
from app.schemas.dictionary import DictionaryEntryData

logger = logging.getLogger(__name__)


class DictionaryService:
    """Orchestrates dictionary lookups using a cache-first strategy.

    The service is responsible for business logic only. It coordinates
    CRUD operations and AI lookups but never performs SQL directly or
    knows about FastAPI routing.
    """

    def __init__(self, provider: AIProvider) -> None:
        """Initialize the service.

        Args:
            provider: The AI provider implementation injected by the
                dependency layer.
        """
        self._provider = provider

    async def lookup(
        self,
        session: AsyncSession,
        *,
        word: str,
        language: str,
    ) -> DictionaryEntry:
        """Look up a word using a cache-first strategy.

        Flow:
            1. Check the database cache.
            2. Return immediately on cache hit.
            3. Query the AI provider on cache miss.
            4. Validate the AI response.
            5. Persist the new entry.
            6. Return the stored entry.

        Args:
            session: Active database session.
            word: Word or phrase to look up.
            language: Language code.

        Returns:
            The matching DictionaryEntry ORM model.
        """
        cached_entry = await crud.get_entry(
            session,
            word=word,
            language=language,
        )

        if cached_entry is not None:
            logger.info(
                "Dictionary cache hit for word=%r language=%r",
                word,
                language,
            )
            return cached_entry

        logger.info(
            "Dictionary cache miss for word=%r language=%r; querying AI provider",
            word,
            language,
        )

        entry_data = await self._lookup_ai(
            word=word,
            language=language,
        )

        return await crud.create_entry(
            session,
            entry_data,
        )

    async def _lookup_ai(
        self,
        *,
        word: str,
        language: str,
    ) -> DictionaryEntryData:
        """Resolve a dictionary entry using the configured AI provider.

        Builds the prompt, sends it to the provider, parses the response,
        and validates it against the DictionaryEntryData schema.

        Args:
            word: Word or phrase to look up.
            language: Language code.

        Returns:
            A validated DictionaryEntryData instance.

        Raises:
            ValueError: If the provider fails, returns invalid JSON,
                or returns data that does not match the expected schema.
        """
        prompt = self._build_prompt(
            word=word,
            language=language,
        )

        logger.debug("Dictionary lookup prompt:\n%s", prompt)

        try:
            raw_response = await self._provider.generate(prompt)

            logger.debug(
                "Raw AI response:\n%s",
                raw_response,
            )

        except ProviderError as exc:
            logger.exception(
                "AI provider failed for word=%r language=%r",
                word,
                language,
            )

            raise ValueError(
                f"AI provider failed to generate a dictionary entry: {exc}"
            ) from exc

        parsed_response = self._parse_response(raw_response)

        return self._validate_response(parsed_response)

    @staticmethod
    def _build_prompt(
        *,
        word: str,
        language: str,
    ) -> str:
        """Build the prompt sent to the AI provider."""

        schema_description = (
            "{\n"
            '  "word": "...",\n'
            '  "language": "...",\n'
            '  "readings": [\n'
            "    {\n"
            '      "script": "...",\n'
            '      "reading": "..."\n'
            "    }\n"
            "  ],\n"
            '  "senses": [\n'
            "    {\n"
            '      "part_of_speech": "...",\n'
            '      "definitions": ["..."],\n'
            '      "examples": ["..."]\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        return (
            "You are a multilingual dictionary.\n\n"
            "Return ONLY valid JSON.\n"
            "Do NOT wrap the JSON in markdown.\n"
            "Do NOT use ```json.\n"
            "Do NOT include explanations.\n"
            "Do NOT include comments.\n"
            "Do NOT include extra keys.\n"
            "If a field is unknown, return an empty array instead of guessing.\n\n"
            "The JSON must exactly match this schema:\n\n"
            f"{schema_description}\n\n"
            f'Look up the word "{word}" in the language "{language}". '
            'Set "word" to the exact input word and '
            '"language" to the exact input language.'
        )

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any]:
        """Parse the AI provider response into a JSON object.

        The provider should return plain JSON. If it wraps the JSON in
        Markdown code fences (for example ```json ... ```), the fences
        are stripped before parsing.

        Args:
            response: Raw text returned by the AI provider.

        Returns:
            Parsed JSON object.

        Raises:
            ValueError: If the response is not valid JSON or is not a
                JSON object.
        """
        response = response.strip()

        # Strip Markdown code fences if present.
        if response.startswith("```"):
            lines = response.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(lines).strip()

        try:
            parsed = json.loads(response)

        except json.JSONDecodeError as exc:
            logger.error(
                "AI provider returned invalid JSON: %s",
                exc,
            )

            raise ValueError(
                f"AI provider returned invalid JSON: {exc}"
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "AI provider returned valid JSON, "
                f"but not a JSON object (got {type(parsed).__name__})."
            )

        return parsed

    @staticmethod
    def _validate_response(
        data: dict[str, Any],
    ) -> DictionaryEntryData:
        """Validate AI response against the dictionary schema.

        Args:
            data: Parsed JSON object.

        Returns:
            Validated DictionaryEntryData instance.

        Raises:
            ValueError: If the response does not conform to the schema.
        """
        try:
            return DictionaryEntryData.model_validate(data)

        except ValidationError as exc:
            logger.error(
                "AI provider response failed schema validation: %s",
                exc,
            )

            raise ValueError(
                f"AI provider response failed schema validation: {exc}"
            ) from exc