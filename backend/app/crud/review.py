"""
Async CRUD operations for vocabulary reviews.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import VocabularyEntry, VocabularyReviewLog


class ReviewCRUD:
    """CRUD operations for vocabulary reviews."""

    @staticmethod
    async def get_due_reviews(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
    ) -> list[VocabularyEntry]:
        """
        Return vocabulary entries due for review.
        """

        stmt = (
            select(VocabularyEntry)
            .where(
                VocabularyEntry.user_id == user_id,
                VocabularyEntry.srs_due_at.is_not(None),
                VocabularyEntry.srs_due_at <= datetime.utcnow(),
            )
            .order_by(VocabularyEntry.srs_due_at)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_vocabulary_by_id(
        db: AsyncSession,
        vocabulary_id: UUID,
        user_id: UUID,
    ) -> VocabularyEntry | None:
        """
        Return a vocabulary entry owned by the user.
        """

        stmt = select(VocabularyEntry).where(
            VocabularyEntry.id == vocabulary_id,
            VocabularyEntry.user_id == user_id,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_review_log(
        db: AsyncSession,
        review_log: VocabularyReviewLog,
    ) -> VocabularyReviewLog:
        """
        Persist a review log.
        """

        db.add(review_log)
        await db.flush()
        await db.refresh(review_log)

        return review_log

    @staticmethod
    async def update_vocabulary(
        db: AsyncSession,
        vocabulary: VocabularyEntry,
    ) -> VocabularyEntry:
        """
        Persist changes made to a vocabulary entry.
        """

        await db.flush()
        await db.refresh(vocabulary)

        return vocabulary