"""
CRUD functions for user language enrollment.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.language import Language, UserLanguage
from app.models.user import User
from app.schemas.user_language import UserLanguageCreate


async def get_language_by_id(
    db: AsyncSession,
    language_id: uuid.UUID,
) -> Language | None:
    """
    Retrieve a language by its primary key.
    """
    return await db.get(Language, language_id)


async def get_user_language(
    db: AsyncSession,
    user_id: uuid.UUID,
    language_id: uuid.UUID,
) -> UserLanguage | None:
    """
    Return an existing enrollment if one exists.
    """
    result = await db.execute(
        select(UserLanguage).where(
            UserLanguage.user_id == user_id,
            UserLanguage.language_id == language_id,
        )
    )

    return result.scalar_one_or_none()


async def create_user_language(
    db: AsyncSession,
    user: User,
    language_data: UserLanguageCreate,
) -> UserLanguage:
    """
    Enroll a user in a language.
    """

    enrollment = UserLanguage(
        user_id=user.id,
        language_id=language_data.language_id,
        level=language_data.level,
    )

    db.add(enrollment)

    await db.commit()
    await db.refresh(enrollment)

    return enrollment


async def get_user_languages(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[UserLanguage]:
    """
    Return all languages the user is enrolled in.
    """

    result = await db.execute(
        select(UserLanguage)
        .options(joinedload(UserLanguage.language))
        .where(UserLanguage.user_id == user_id)
        .order_by(UserLanguage.started_at)
    )

    return result.scalars().all()