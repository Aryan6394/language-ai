"""SQLAlchemy model for dictionary entries."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.dictionary_reading import DictionaryReading
    from app.models.dictionary_sense import DictionarySense


class DictionaryEntry(Base):
    """Represents a dictionary entry for a word or phrase."""

    __tablename__ = "dictionary_entries"

    __table_args__ = (
        UniqueConstraint(
            "word",
            "language",
            name="uq_dictionary_word_language",
        ),
        Index(
            "ix_dictionary_word_language",
            "word",
            "language",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    word: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    readings: Mapped[list["DictionaryReading"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    senses: Mapped[list["DictionarySense"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"DictionaryEntry("
            f"id={self.id}, "
            f"word={self.word!r}, "
            f"language={self.language!r})"
        )