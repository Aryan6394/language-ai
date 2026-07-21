"""
Business logic for the Language domain.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.language import get_languages
from app.models.language import Language


class LanguageService:
    """
    Service layer for Language operations.
    """

    @staticmethod
    async def get_languages(
        db: AsyncSession,
    ) -> list[Language]:
        return await get_languages(db)