"""
CRUD functions for the Language model.
"""

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