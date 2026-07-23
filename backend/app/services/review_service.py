from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.review import ReviewCRUD
from app.models.vocabulary import VocabularyReviewLog
from app.schemas.review import (
    DueVocabularyResponse,
    ReviewCreate,
    ReviewResponse,
)


class ReviewService:
    """Business logic for vocabulary reviews."""

    @staticmethod
    async def get_due_reviews(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
    ) -> list[DueVocabularyResponse]:
        """
        Return vocabulary entries due for review.
        """

        entries = await ReviewCRUD.get_due_reviews(
            db=db,
            user_id=user_id,
            limit=limit,
        )

        return [
            DueVocabularyResponse.model_validate(entry)
            for entry in entries
        ]

    @staticmethod
    async def submit_review(
        db: AsyncSession,
        user_id: UUID,
        vocabulary_id: UUID,
        review: ReviewCreate,
    ) -> ReviewResponse:
        """
        Submit a review and update SRS progress.

        Raises:
            ValueError:
                Vocabulary entry not found.
        """

        vocabulary = await ReviewCRUD.get_vocabulary_by_id(
            db=db,
            vocabulary_id=vocabulary_id,
            user_id=user_id,
        )

        if vocabulary is None:
            raise ValueError("Vocabulary entry not found.")

        previous_stage = vocabulary.srs_stage

        # Convert rating -> correctness
        was_correct = review.rating >= 2

        # -----------------------------
        # Simple SRS scheduling
        # -----------------------------
        if review.rating == 0:
            new_stage = 0
            interval = timedelta(minutes=10)

        elif review.rating == 1:
            new_stage = max(previous_stage - 1, 0)
            interval = timedelta(days=1)

        elif review.rating == 2:
            new_stage = previous_stage + 1
            interval = timedelta(days=new_stage)

        elif review.rating == 3:
            new_stage = previous_stage + 2
            interval = timedelta(days=new_stage * 2)

        else:  # rating == 4
            new_stage = previous_stage + 3
            interval = timedelta(days=new_stage * 4)

        vocabulary.srs_stage = new_stage
        vocabulary.srs_due_at = datetime.utcnow() + interval

        review_log = VocabularyReviewLog(
            vocabulary_entry_id=vocabulary.id,
            user_id=user_id,
            was_correct=was_correct,
        )

        await ReviewCRUD.create_review_log(
            db=db,
            review_log=review_log,
        )

        await ReviewCRUD.update_vocabulary(
            db=db,
            vocabulary=vocabulary,
        )

        await db.commit()

        return ReviewResponse(
            id=review_log.id,
            vocabulary_entry_id=vocabulary.id,
            rating=review.rating,
            previous_stage=previous_stage,
            new_stage=new_stage,
            srs_due_at=vocabulary.srs_due_at,
            reviewed_at=review_log.reviewed_at,
        )