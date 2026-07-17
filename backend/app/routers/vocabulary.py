"""Vocabulary routes for the authenticated user."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.vocabulary import (
    create_review_log,
    create_vocabulary_entry,
    delete_vocabulary_entry,
    get_due_vocabulary,
    get_user_vocabulary,
    get_vocabulary_entry_by_id,
    search_vocabulary,
    update_vocabulary_entry,
)
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.vocabulary import VocabularyEntry
from app.schemas.auth import MessageResponse
from app.schemas.vocabulary import (
    VocabularyEntryCreate,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
    VocabularyReviewLogCreate,
    VocabularyReviewLogResponse,
)

router = APIRouter(
    prefix="/vocabulary",
    tags=["Vocabulary"],
)


def _get_entry_for_user(
    db: Session,
    entry_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> VocabularyEntry:
    """Return an entry if it exists and belongs to the current user."""

    entry = get_vocabulary_entry_by_id(
        db=db,
        entry_id=entry_id,
        user_id=current_user_id,
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary entry not found",
        )

    return entry


@router.post(
    "",
    response_model=VocabularyEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a vocabulary entry",
)
def create_entry(
    entry_data: VocabularyEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VocabularyEntryResponse:
    """Create a vocabulary entry for the authenticated user."""

    try:
        return create_vocabulary_entry(
            db=db,
            user_id=current_user.id,
            schema=entry_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[VocabularyEntryResponse],
    summary="List vocabulary entries",
)
def list_entries(
    language_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VocabularyEntryResponse]:
    """Return the authenticated user's vocabulary entries."""

    return get_user_vocabulary(
        db=db,
        user_id=current_user.id,
        language_id=language_id,
        page=page,
        page_size=page_size,
        search=search,
    )


@router.get(
    "/search",
    response_model=list[VocabularyEntryResponse],
    summary="Search vocabulary entries",
)
def search_entries(
    query: str = Query(..., min_length=1),
    language_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VocabularyEntryResponse]:
    """Search the authenticated user's vocabulary by keyword."""

    return search_vocabulary(
        db=db,
        user_id=current_user.id,
        query=query,
        language_id=language_id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/due",
    response_model=list[VocabularyEntryResponse],
    summary="Get due vocabulary entries",
)
def get_due_entries(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VocabularyEntryResponse]:
    """Return spaced-repetition entries due for review."""

    return get_due_vocabulary(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get(
    "/{entry_id}",
    response_model=VocabularyEntryResponse,
    summary="Get a vocabulary entry",
)
def get_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VocabularyEntryResponse:
    """Return a single vocabulary entry owned by the authenticated user."""

    return _get_entry_for_user(db, entry_id, current_user.id)


@router.patch(
    "/{entry_id}",
    response_model=VocabularyEntryResponse,
    summary="Update a vocabulary entry",
)
def update_entry(
    entry_id: uuid.UUID,
    entry_update: VocabularyEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VocabularyEntryResponse:
    """Update a vocabulary entry owned by the authenticated user."""

    entry = _get_entry_for_user(db, entry_id, current_user.id)

    try:
        return update_vocabulary_entry(
            db=db,
            entry=entry,
            schema=entry_update,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vocabulary entry",
)
def delete_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a vocabulary entry owned by the authenticated user."""

    entry = _get_entry_for_user(db, entry_id, current_user.id)
    delete_vocabulary_entry(db=db, entry=entry)


@router.post(
    "/{entry_id}/review",
    response_model=VocabularyReviewLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a review",
)
def review_entry(
    entry_id: uuid.UUID,
    review_data: VocabularyReviewLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VocabularyReviewLogResponse:
    """Log a spaced-repetition review result for a vocabulary entry."""

    entry = _get_entry_for_user(db, entry_id, current_user.id)

    try:
        return create_review_log(
            db=db,
            entry=entry,
            user_id=current_user.id,
            was_correct=review_data.was_correct,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
