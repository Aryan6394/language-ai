"""
SQLAlchemy models for the Languages domain (DATABASE.md, Section 2):
  - languages       : master reference list of every language the
                      platform supports (Section 2.1)
  - user_languages  : join table of which languages a user is actively
                      learning (Section 2.2)
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
from sqlalchemy.orm import relationship

from app.db.base import Base


class Language(Base):
    """
    Master reference list of every language the platform supports.
    """

    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ISO 639-1 code (e.g. en, hi, ja)
    code = Column(String(10), unique=True, nullable=False, index=True)

    # English/display name
    name = Column(String(100), nullable=False)

    # Native language name
    native_name = Column(String(100), nullable=False)

    # Can users learn this language?
    is_learnable = Column(Boolean, nullable=False, default=False)

    # Is the application translated into this language?
    is_ui_supported = Column(Boolean, nullable=False, default=False)

    # Admin enable/disable flag
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    user_languages = relationship(
        "UserLanguage",
        back_populates="language",
    )


class UserLanguageLevel(str, enum.Enum):
    """Learning level."""

    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class UserLanguageStatus(str, enum.Enum):
    """Learning status."""

    active = "active"
    paused = "paused"
    completed = "completed"


class UserLanguage(Base):
    """
    Join table recording which languages a user is learning.
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
    cefr_estimate = Column(
        String(10),
        nullable=True,
    )

    # Relationships
    language = relationship(
        "Language",
        back_populates="user_languages",
    )

    user = relationship(
        "User",
        back_populates="languages",
    )