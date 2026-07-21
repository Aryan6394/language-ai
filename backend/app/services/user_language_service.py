"""
Business logic for user language enrollment.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_language import (
    create_user_language,
    get_language_by_id,
    get_user_language,
    get_user_languages,
)
from app.models.language import UserLanguage
from app.models.user import User
from app.schemas.user_language import UserLanguageCreate


class UserLanguageService:
    """
    Service layer for user language enrollment.
    """

    @staticmethod
    async def enroll_language(
        db: AsyncSession,
        user: User,
        language_data: UserLanguageCreate,
    ) -> UserLanguage:
        """
        Enroll a user in a language.
        """

        language = await get_language_by_id(
            db,
            language_data.language_id,
        )

        if language is None:
            raise ValueError("Language not found.")

        existing = await get_user_language(
            db,
            user.id,
            language_data.language_id,
        )

        if existing is not None:
            raise ValueError("User is already enrolled in this language.")

        return await create_user_language(
            db,
            user,
            language_data,
        )

    @staticmethod
    async def get_user_languages(
        db: AsyncSession,
        user: User,
    ) -> list[UserLanguage]:
        """
        Return all languages enrolled by the user.
        """
        return await get_user_languages(
            db,
            user.id,
        )