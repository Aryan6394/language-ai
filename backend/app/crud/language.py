"""
CRUD functions for the Language model.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language import Language


async def get_languages(
    db: AsyncSession,
) -> list[Language]:
    """
    Return all active languages ordered alphabetically.
    """

    result = await db.execute(
        select(Language)
        .where(Language.is_active.is_(True))
        .order_by(Language.name)
    )

    return result.scalars().all()


async def get_language_by_id(
    db: AsyncSession,
    language_id: UUID,
) -> Language | None:
    """
    Return a language by its ID if it exists and is active.
    """

    result = await db.execute(
        select(Language).where(
            Language.id == language_id,
            Language.is_active.is_(True),
        )
    )

    return result.scalar_one_or_none()