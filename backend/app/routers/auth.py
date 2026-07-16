"""
Authentication router.

Endpoints:
  - POST /auth/register : create a new account
  - POST /auth/login    : authenticate and receive a JWT access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
)
from app.db.session import get_db
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    existing_user = get_user_by_email(db, user.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    return create_user(db, user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.

    Swagger UI's Authorize button uses OAuth2 Password Flow, which
    submits credentials as application/x-www-form-urlencoded.
    OAuth2PasswordRequestForm parses those fields automatically.
    """

    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )