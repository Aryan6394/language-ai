"""
API endpoints for user language enrollment.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.user import User
from app.schemas.user_language import (
    UserLanguageCreate,
    UserLanguageDetail,
    UserLanguageResponse,
)
from app.services.user_language_service import UserLanguageService
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/users/me/languages",
    tags=["User Languages"],
)


@router.post(
    "",
    response_model=UserLanguageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_language(
    language_data: UserLanguageCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Enroll the authenticated user in a language.
    """
    try:
        return await UserLanguageService.enroll_language(
            db,
            current_user,
            language_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[UserLanguageDetail],
)
async def list_user_languages(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Return all languages the authenticated user is learning.
    """
    return await UserLanguageService.get_user_languages(
        db,
        current_user,
    )