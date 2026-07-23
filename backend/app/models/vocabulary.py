"""SQLAlchemy models for the Vocabulary domain."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VocabularyCacheSource(str, enum.Enum):

    DICTIONARY_API = "dictionary_api"
    LLM = "llm"


class VocabularyEntry(Base):

    __tablename__ = "vocabulary_entries"
    __table_args__ = (
        CheckConstraint("srs_stage >= 0", name="ck_vocabulary_entries_srs_stage_non_negative"),
        Index("ix_vocabulary_entries_user_language", "user_id", "language_id"),
        Index("ix_vocabulary_entries_srs_due_at", "srs_due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    language_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False
    )

    word: Mapped[str] = mapped_column(String, nullable=False)
    meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_sentence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    part_of_speech: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ipa: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    srs_stage: Mapped[int] = mapped_column(default=0, nullable=False)
    srs_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User")
    language: Mapped["Language"] = relationship("Language")

    review_logs: Mapped[list["VocabularyReviewLog"]] = relationship(
        "VocabularyReviewLog", back_populates="vocabulary_entry", cascade="all, delete-orphan"
    )


class VocabularyCache(Base):

    __tablename__ = "vocabulary_cache"
    __table_args__ = (
        UniqueConstraint(
            "word",
            "language_id",
            name="uq_vocabulary_cache_word_language",
        ),
        Index(
            "ix_vocabulary_cache_language_id",
            "language_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    word: Mapped[str] = mapped_column(String, nullable=False)
    language_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("languages.id", ondelete="CASCADE"), nullable=False
    )

    meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_sentence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    part_of_speech: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ipa: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    source: Mapped[VocabularyCacheSource] = mapped_column(
        Enum(VocabularyCacheSource, name="vocabulary_cache_source"), nullable=False
    )
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    language: Mapped["Language"] = relationship("Language")


class VocabularyReviewLog(Base):

    __tablename__ = "vocabulary_review_log"
    __table_args__ = (
        Index("ix_vocabulary_review_log_vocabulary_entry_id", "vocabulary_entry_id"),
        Index("ix_vocabulary_review_log_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    vocabulary_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocabulary_entries.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    was_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vocabulary_entry: Mapped["VocabularyEntry"] = relationship("VocabularyEntry", back_populates="review_logs")

    user: Mapped["User"] = relationship("User")