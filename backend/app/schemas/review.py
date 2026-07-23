"""
Pydantic schemas for vocabulary review (SRS) operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    """
    Request schema for submitting a vocabulary review.
    """

    rating: int = Field(
        ...,
        ge=0,
        le=4,
        description="Review rating (0=Again, 1=Hard, 2=Good, 3=Easy, 4=Perfect).",
        examples=[2],
    )


class ReviewResponse(BaseModel):
    """
    Response returned after successfully submitting a review.
    """

    id: UUID
    vocabulary_entry_id: UUID
    rating: int
    previous_stage: int
    new_stage: int
    srs_due_at: datetime | None
    reviewed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DueVocabularyResponse(BaseModel):
    """
    Response schema for vocabulary entries due for review.
    """

    id: UUID
    word: str
    meaning: str | None
    language_id: UUID

    srs_stage: int
    srs_due_at: datetime | None

    model_config = ConfigDict(from_attributes=True)