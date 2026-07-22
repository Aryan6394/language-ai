"""
Service layer for the Vocabulary domain.

Contains business logic only.

Responsibilities:
- Validate referenced entities.
- Call CRUD functions.
- Raise business-level ValueError exceptions.
- Keep FastAPI/HTTP concerns out of the service layer.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.language import get_language_by_id
from app.crud.vocabulary import (
    create_vocabulary_entry,
    delete_vocabulary_entry,
    get_user_vocabulary,
    get_vocabulary_entry_by_id,
    search_vocabulary,
    update_vocabulary_entry,
)
from app.schemas.vocabulary import (
    VocabularyEntryCreate,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
)


class VocabularyService:
    """Business logic for vocabulary management."""

    @staticmethod
    async def create_vocabulary(
        db: AsyncSession,
        user_id: uuid.UUID,
        vocabulary: VocabularyEntryCreate,
    ) -> VocabularyEntryResponse:
        """
        Create a new vocabulary entry.

        Raises:
            ValueError:
                - Language not found.
                - Vocabulary entry already exists for this language.
        """

        language = await get_language_by_id(db, vocabulary.language_id)

        if language is None:
            raise ValueError("Language not found.")

        entry = await create_vocabulary_entry(
            db=db,
            user_id=user_id,
            schema=vocabulary,
        )

        return entry

    @staticmethod
    async def get_vocabulary(
        db: AsyncSession,
        user_id: uuid.UUID,
        language_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> list[VocabularyEntryResponse]:
        """
        Return the user's vocabulary entries.

        Supports:
        - language filtering
        - pagination
        - search
        """

        if search:
            return await search_vocabulary(
                db=db,
                user_id=user_id,
                query=search,
                language_id=language_id,
                page=page,
                page_size=page_size,
            )

        return await get_user_vocabulary(
            db=db,
            user_id=user_id,
            language_id=language_id,
            page=page,
            page_size=page_size,
            search=None,
        )

    @staticmethod
    async def get_vocabulary_by_id(
        db: AsyncSession,
        user_id: uuid.UUID,
        vocabulary_id: uuid.UUID,
    ) -> VocabularyEntryResponse:
        """
        Retrieve a single vocabulary entry.

        Raises:
            ValueError:
                Vocabulary entry not found.
        """

        entry = await get_vocabulary_entry_by_id(
            db=db,
            entry_id=vocabulary_id,
            user_id=user_id,
        )

        if entry is None:
            raise ValueError("Vocabulary entry not found.")

        return entry

    @staticmethod
    async def update_vocabulary(
        db: AsyncSession,
        user_id: uuid.UUID,
        vocabulary_id: uuid.UUID,
        vocabulary: VocabularyEntryUpdate,
    ) -> VocabularyEntryResponse:
        """
        Update a vocabulary entry.

        Raises:
            ValueError:
                - Vocabulary entry not found.
                - Vocabulary entry already exists for this language.
        """

        entry = await get_vocabulary_entry_by_id(
            db=db,
            entry_id=vocabulary_id,
            user_id=user_id,
        )

        if entry is None:
            raise ValueError("Vocabulary entry not found.")

        updated_entry = await update_vocabulary_entry(
            db=db,
            entry=entry,
            schema=vocabulary,
        )

        return updated_entry

    @staticmethod
    async def delete_vocabulary(
        db: AsyncSession,
        user_id: uuid.UUID,
        vocabulary_id: uuid.UUID,
    ) -> None:
        """
        Delete a vocabulary entry.

        Raises:
            ValueError:
                Vocabulary entry not found.
        """

        entry = await get_vocabulary_entry_by_id(
            db=db,
            entry_id=vocabulary_id,
            user_id=user_id,
        )

        if entry is None:
            raise ValueError("Vocabulary entry not found.")

        await delete_vocabulary_entry(
            db=db,
            entry=entry,
        )