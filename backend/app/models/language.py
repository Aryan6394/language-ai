"""
SQLAlchemy models for the Languages domain (DATABASE.md, Section 2):
  - languages       : master reference list of every language the
                      platform supports (Section 2.1)
  - user_languages  : join table of which languages a user is actively
                      learning (Section 2.2)

Milestone scope note: this file implements only the two ORM models
below. Deliberately NOT included here, per current task requirements:
  - Pydantic schemas
  - CRUD functions
  - Routers/endpoints
  - `relationship()` declarations — plain FK columns only, since nothing
    yet needs to traverse these relationships in code.
"""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Language(Base):
    """
    Master reference list of every language the platform supports.

    DATABASE.md Section 2.1.
    """

    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ISO 639-1 code (e.g. "en", "hi", "ja")
    code = Column(String(10), unique=True, nullable=False, index=True)

    # English/display name
    name = Column(String(100), nullable=False)

    # Native language name (e.g. 日本語, हिन्दी)
    native_name = Column(String(100), nullable=False)

    # Can users learn this language?
    is_learnable = Column(Boolean, nullable=False, default=False)

    # Is the application translated into this language?
    is_ui_supported = Column(Boolean, nullable=False, default=False)

    # Admin soft-delete / enable-disable flag.
    is_active = Column(Boolean, nullable=False, default=True)


class UserLanguageLevel(str, enum.Enum):
    """Mirrors DATABASE.md's user_languages.level enum."""

    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class UserLanguageStatus(str, enum.Enum):
    """Mirrors DATABASE.md's user_languages.status enum."""

    active = "active"
    paused = "paused"
    completed = "completed"


class UserLanguage(Base):
    """
    Join table recording which languages a user is learning.

    DATABASE.md Section 2.2.
    """

    __tablename__ = "user_languages"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "language_id",
            name="uq_user_languages_user_language",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User enrolled in the language
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Language being learned
    language_id = Column(
        UUID(as_uuid=True),
        ForeignKey("languages.id"),
        nullable=False,
        index=True,
    )

    level = Column(
        Enum(UserLanguageLevel, name="user_language_level"),
        nullable=False,
    )

    status = Column(
        Enum(UserLanguageStatus, name="user_language_status"),
        nullable=False,
        default=UserLanguageStatus.active,
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # e.g. A1, A2, B1...
    cefr_estimate = Column(String(10), nullable=True)