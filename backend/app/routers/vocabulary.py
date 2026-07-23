"""Thin FastAPI router for vocabulary endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.vocabulary import (
    VocabularyEntryCreate,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
)
from app.services.vocabulary_service import VocabularyService

router = APIRouter(
    prefix="/vocabulary",
    tags=["Vocabulary"],
)

DBSession = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "",
    response_model=VocabularyEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a vocabulary entry",
)
async def create_entry(
    entry_data: VocabularyEntryCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> VocabularyEntryResponse:
    """Create a vocabulary entry for the authenticated user."""

    try:
        return await VocabularyService.create_vocabulary(
            db=db,
            user_id=current_user.id,
            vocabulary=entry_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[VocabularyEntryResponse],
    summary="List vocabulary entries",
)
async def list_entries(
    current_user: CurrentUser,
    db: DBSession,
    language_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
) -> list[VocabularyEntryResponse]:
    """Return the authenticated user's vocabulary entries."""

    return await VocabularyService.get_vocabulary(
        db=db,
        user_id=current_user.id,
        language_id=language_id,
        page=page,
        page_size=page_size,
        search=search,
    )


@router.get(
    "/{vocabulary_id}",
    response_model=VocabularyEntryResponse,
    summary="Get a vocabulary entry",
)
async def get_entry(
    vocabulary_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> VocabularyEntryResponse:
    """Return a single vocabulary entry owned by the authenticated user."""

    try:
        return await VocabularyService.get_vocabulary_by_id(
            db=db,
            user_id=current_user.id,
            vocabulary_id=vocabulary_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{vocabulary_id}",
    response_model=VocabularyEntryResponse,
    summary="Update a vocabulary entry",
)
async def update_entry(
    vocabulary_id: uuid.UUID,
    entry_update: VocabularyEntryUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> VocabularyEntryResponse:
    """Update a vocabulary entry owned by the authenticated user."""

    try:
        return await VocabularyService.update_vocabulary(
            db=db,
            user_id=current_user.id,
            vocabulary_id=vocabulary_id,
            vocabulary=entry_update,
        )
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{vocabulary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vocabulary entry",
)
async def delete_entry(
    vocabulary_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> Response:
    """Delete a vocabulary entry owned by the authenticated user."""

    try:
        await VocabularyService.delete_vocabulary(
            db=db,
            user_id=current_user.id,
            vocabulary_id=vocabulary_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
