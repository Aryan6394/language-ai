"""
CRUD functions for the Language model.
"""

from sqlalchemy.orm import Session

from app.models.language import Language


def get_languages(db: Session) -> list[Language]:
    """
    Return all active languages ordered alphabetically.
    """

    return (
        db.query(Language)
        .filter(Language.is_active.is_(True))
        .order_by(Language.name)
        .all()
    )