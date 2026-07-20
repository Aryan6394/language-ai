"""
Authentication business logic.

This service contains the business rules for user registration and
login. It delegates database access to the CRUD layer and keeps the
router focused on HTTP concerns.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthServiceError(Exception):
    """Base class for authentication service exceptions."""


class UserAlreadyExistsError(AuthServiceError):
    """Raised when attempting to register an existing email."""


class InvalidCredentialsError(AuthServiceError):
    """Raised when login credentials are invalid."""


class AuthService:
    """Authentication business logic."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_in: UserCreate,
    ) -> User:
        """
        Register a new user.

        Raises:
            UserAlreadyExistsError: If the email is already registered.
        """

        existing_user = await get_user_by_email(db, user_in.email)

        if existing_user:
            raise UserAlreadyExistsError(
                "A user with this email already exists."
            )

        return await create_user(db, user_in)

    @staticmethod
    async def authenticate(
        db: AsyncSession,
        credentials: LoginRequest,
    ) -> TokenResponse:
        """
        Authenticate a user and return an access token.

        Raises:
            InvalidCredentialsError: If the email or password is invalid.
        """

        user = await authenticate_user(
            db,
            credentials.email,
            credentials.password,
        )

        if user is None:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        access_token = create_access_token(
            subject=str(user.id)
        )

        return TokenResponse(
            access_token=access_token
        )