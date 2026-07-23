"""
Thin FastAPI router for vocabulary review endpoints.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import (
    DueVocabularyResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.services.review_service import ReviewService

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)

DBSession = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    "/due",
    response_model=list[DueVocabularyResponse],
    summary="Get vocabulary due for review",
)
async def get_due_reviews(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of vocabulary entries to return.",
    ),
) -> list[DueVocabularyResponse]:
    """
    Return vocabulary entries currently due for review.
    """

    return await ReviewService.get_due_reviews(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.post(
    "/{vocabulary_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a vocabulary review",
)
async def submit_review(
    vocabulary_id: UUID,
    review: ReviewCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """
    Submit a review for a vocabulary entry.
    """

    try:
        return await ReviewService.submit_review(
            db=db,
            user_id=current_user.id,
            vocabulary_id=vocabulary_id,
            review=review,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc