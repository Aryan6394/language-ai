from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import change_password, update_user
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, MessageResponse
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
def get_current_user_profile(
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
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Update the authenticated user's profile.
    """

    return update_user(
        db=db,
        db_user=current_user,
        user_update=user_update,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change current user's password",
)
def change_current_user_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Change the authenticated user's password.
    """

    success = change_password(
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