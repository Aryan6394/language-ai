from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import change_password, update_user
from app.services.user_language_service import UserLanguageService
from app.db.session import get_async_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    MessageResponse,
)
from app.schemas.user import (
    UserResponse,
    UserUpdate,
)
from app.schemas.user_language import (
    UserLanguageCreate,
    UserLanguageDetail,
    UserLanguageResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return the currently authenticated user's profile.
    """
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserResponse:
    """
    Update the authenticated user's profile.
    """

    return await update_user(
        db=db,
        db_user=current_user,
        user_update=user_update,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change current user's password",
)
async def change_current_user_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> MessageResponse:
    """
    Change the authenticated user's password.
    """

    success = await change_password(
        db=db,
        db_user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    return MessageResponse(
        message="Password updated successfully",
    )

@router.post(
    "/me/languages",
    response_model=UserLanguageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in a language",
)
async def enroll_language(
    language_data: UserLanguageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserLanguageResponse:
    """
    Enroll the authenticated user in a language.
    """

    try:
        return await UserLanguageService.enroll_language(
            db=db,
            user=current_user,
            language_data=language_data,
        )

    except ValueError as e:
        message = str(e)

        if message == "Language not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )


@router.get(
    "/me/languages",
    response_model=list[UserLanguageDetail],
    summary="Get enrolled languages",
)
async def get_my_languages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[UserLanguageDetail]:
    """
    Return all languages the authenticated user is enrolled in.
    """

    return await UserLanguageService.get_user_languages(
        db=db,
        user=current_user,
    )