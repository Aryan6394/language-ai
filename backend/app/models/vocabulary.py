"""SQLAlchemy models for the Vocabulary domain (DATABASE.md, Section 4).

This module implements exactly the three tables documented there:
  - vocabulary_entries    : a user's personal word list (4.1)
  - vocabulary_cache      : shared, cost-saving dictionary lookups,
                            de-duplicated across all users (4.2)
  - vocabulary_review_log : append-only spaced-repetition review
                            history (4.3)

DATABASE.md is the source of truth for the shape of this schema (which
tables exist, their fields, and documented indexes). Where DATABASE.md
does not specify an implementation detail — ON DELETE behavior, CHECK
constraints, which fields are nullable, additional indexes — this file
chooses a production-ready default and documents the reasoning inline,
per project convention. Nothing here introduces a table, column, or
constraint that changes the documented schema's shape.

Only models are defined here. No schemas, CRUD, routers, migrations,
or seed logic — those belong to their own modules in later tasks.
"""

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
    """Where a `vocabulary_cache` row's content came from.

    Mirrors DATABASE.md 4.2's documented enum (`dictionary_api`, `llm`)
    exactly — no additional values invented here.
    """

    DICTIONARY_API = "dictionary_api"
    LLM = "llm"


class VocabularyEntry(Base):
    """A single word/phrase in one user's personal vocabulary list.

    Matches DATABASE.md Section 4.1 field-for-field. `meaning`,
    `example_sentence`, `part_of_speech`, `ipa`, and `tags` are all
    nullable: DATABASE.md explicitly marks `part_of_speech`/`ipa` as
    nullable, and by the same logic a brand-new entry may be saved
    before its meaning/example have been resolved from
    `vocabulary_cache` (see the CRUD layer's cache-first resolution,
    implemented in a later task) — so those are treated as nullable
    too rather than assumed always-present at insert time.

    `srs_stage` defaults to 0 (not specified in DATABASE.md, but the
    natural starting point for "has not been reviewed yet") and is
    constrained to be non-negative.

    ON DELETE behavior (not specified in DATABASE.md):
      - `user_id` -> CASCADE: if a user's account is deleted, their
        personal word list has no reason to persist.
      - `language_id` -> RESTRICT (the SQLAlchemy/DB default, no
        `ondelete` set): languages are admin-managed reference data
        that should not be deletable while user vocabulary still
        references them, to avoid silently destroying user data as a
        side effect of a reference-data change.

    Attributes:
        id: Primary key (UUID, generated client-side).
        user_id: Owning user.
        language_id: Which language this word belongs to.
        word: The word/phrase as entered by the user.
        meaning: Definition/translation, often pulled from
            `vocabulary_cache`.
        example_sentence: An example sentence using the word.
        part_of_speech: Optional grammatical category, as free text
            per DATABASE.md (not an enum there).
        ipa: Optional phonetic (IPA) spelling.
        tags: User-defined categorization tags.
        date_added: When the entry was created.
        srs_stage: Spaced-repetition stage; higher means more firmly
            learned.
        srs_due_at: When this word is next due for review.
        user: The owning user (one-directional; see app/models/user.py).
        language: The associated language (one-directional; see
            app/models/language.py).
        review_logs: Related review history rows.
    """

    __tablename__ = "vocabulary_entries"
    __table_args__ = (
        CheckConstraint("srs_stage >= 0", name="ck_vocabulary_entries_srs_stage_non_negative"),
        # Documented in DATABASE.md 4.1: "index on (user_id, language_id)".
        Index("ix_vocabulary_entries_user_language", "user_id", "language_id"),
        # Documented in DATABASE.md 4.1: "index on srs_due_at".
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

    # One-directional relationships to User/Language: referenced by
    # class name string so this module does not import those model
    # classes (they live in app/models/user.py and app/models/language.py
    # respectively, neither of which is modified here). No
    # `back_populates`, since there is no reverse attribute declared on
    # the User/Language side.
    user: Mapped["User"] = relationship("User")
    language: Mapped["Language"] = relationship("Language")

    review_logs: Mapped[list["VocabularyReviewLog"]] = relationship(
        "VocabularyReviewLog", back_populates="vocabulary_entry", cascade="all, delete-orphan"
    )


class VocabularyCache(Base):
    """Shared, de-duplicated dictionary lookup, reused across all users.

    Matches DATABASE.md Section 4.2 exactly. The unique constraint on
    `(word, language_id)` is the mechanism DATABASE.md describes for
    "the same word/language pair is never looked up twice across all
    users" — enforced here at the database level, not just assumed by
    application logic.

    Note: DATABASE.md documents `word` as "normalized/lowercased" —
    that normalization is an application-layer responsibility (the
    CRUD layer must lowercase/normalize before insert); this schema
    enforces uniqueness on whatever value is actually stored, it does
    not itself perform the normalization.

    ON DELETE behavior (not specified in DATABASE.md):
      - `language_id` -> CASCADE: this table is purely a cache: if a
        language is removed, losing its cached lookups is harmless and
        they can be regenerated.

    Attributes:
        id: Primary key (UUID, generated client-side).
        word: The looked-up word, normalized/lowercased by the caller.
        language_id: Which language this lookup is for.
        meaning: Definition/translation.
        example_sentence: An example sentence using the word.
        part_of_speech: Optional grammatical category.
        ipa: Optional phonetic (IPA) spelling.
        source: Which upstream source produced this cached result.
        fetched_at: When this lookup was cached.
        language: The associated language (one-directional; see
            app/models/language.py).
    """

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

    # One-directional relationship to Language — see the note on
    # VocabularyEntry.user/.language above; same reasoning applies here.
    language: Mapped["Language"] = relationship("Language")


class VocabularyReviewLog(Base):
    """One completed spaced-repetition review attempt.

    Matches DATABASE.md Section 4.3 exactly: an append-only log of
    review outcomes (this table has no `updated_at` — rows are never
    edited, only inserted), distinct from `VocabularyEntry.srs_stage`/
    `srs_due_at`, which hold the current scheduling state.

    ON DELETE behavior (not specified in DATABASE.md):
      - `vocabulary_entry_id` -> CASCADE: a review log with no
        surviving entry to refer to is meaningless.
      - `user_id` -> CASCADE: if a user's account is deleted, their
        review history has no reason to persist either.

    Attributes:
        id: Primary key (UUID, generated client-side).
        vocabulary_entry_id: Which vocabulary entry was reviewed.
        user_id: Who performed the review (denormalized alongside
            `vocabulary_entry_id` per DATABASE.md, rather than requiring
            a join through `vocabulary_entries` to know the user).
        was_correct: Whether the review attempt was correct.
        reviewed_at: When the review happened.
        vocabulary_entry: The parent vocabulary entry.
        user: The user who performed the review (one-directional; see
            app/models/user.py).
    """

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

    # One-directional relationship to User — see the note on
    # VocabularyEntry.user/.language above; same reasoning applies here.
    user: Mapped["User"] = relationship("User")