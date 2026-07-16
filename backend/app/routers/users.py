from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

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