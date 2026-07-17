"""
CRUD functions for user language enrollment.
"""

import uuid

from sqlalchemy.orm import Session, joinedload

from app.models.language import Language, UserLanguage
from app.models.user import User
from app.schemas.user_language import UserLanguageCreate


def get_language_by_id(
    db: Session,
    language_id: uuid.UUID,
) -> Language | None:
    """
    Retrieve a language by its primary key.
    """
    return db.get(Language, language_id)


def get_user_language(
    db: Session,
    user_id: uuid.UUID,
    language_id: uuid.UUID,
) -> UserLanguage | None:
    """
    Return an existing enrollment if one exists.
    """
    return (
        db.query(UserLanguage)
        .filter(
            UserLanguage.user_id == user_id,
            UserLanguage.language_id == language_id,
        )
        .first()
    )


def create_user_language(
    db: Session,
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
    db.commit()
    db.refresh(enrollment)

    return enrollment


def get_user_languages(
    db: Session,
    user_id: uuid.UUID,
) -> list[UserLanguage]:
    """
    Return all languages the user is enrolled in.
    """

    return (
        db.query(UserLanguage)
        .options(joinedload(UserLanguage.language))
        .filter(UserLanguage.user_id == user_id)
        .order_by(UserLanguage.started_at)
        .all()
    )