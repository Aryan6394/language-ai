"""
Authentication API routes.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_async_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> UserResponse:
    """
    Register a new user.
    """
    try:
        return await AuthService.register_user(
            db,
            user,
        )

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> TokenResponse:
    """
    Authenticate a user and return a JWT access token.
    """
    try:
        return await AuthService.authenticate(
            db,
            credentials,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
@router.post(
    "/token",
    response_model=TokenResponse,
)
async def token_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> TokenResponse:
    """
    OAuth2-compatible login endpoint for Swagger UI.
    """

    credentials = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    try:
        return await AuthService.authenticate(
            db,
            credentials,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc    