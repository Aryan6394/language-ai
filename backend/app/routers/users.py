from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.crud.user import update_user
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
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

    Only the fields defined in UserUpdate are editable.
    """

    return update_user(
        db=db,
        db_user=current_user,
        user_update=user_update,
    )