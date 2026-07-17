"""
CRUD functions for the Vocabulary domain (DATABASE.md, Section 4).

Covers the three vocabulary tables:
  - vocabulary_entries    (4.1) — personal word list per user
  - vocabulary_cache      (4.2) — shared, cost-saving dictionary lookups
  - vocabulary_review_log (4.3) — append-only spaced-repetition history

Only data-access logic lives here.  No FastAPI routes, no HTTPException,
no Depends() — those belong to the router layer.

Improved:
  - Duplicate create raises ValueError instead of silent return
  - search_vocabulary searches word, meaning, and example_sentence
  - update_vocabulary_entry validates duplicate words on rename
  - Pagination parameters clamped to >= 1
  - Empty search/query strings skip the ILIKE filter
  - create_review_log verifies entry ownership
"""

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.vocabulary import (
    VocabularyCache,
    VocabularyEntry,
    VocabularyReviewLog,
)
from app.schemas.vocabulary import (
    VocabularyEntryCreate,
    VocabularyEntryUpdate,
)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _normalize_word(word: str) -> str:
    """Trim, lowercase, and collapse repeated whitespace in *word*.

    Applied before every insert or lookup so that comparisons are
    consistent and the ``vocabulary_cache`` unique constraint on
    ``(word, language_id)`` works correctly.
    """

    return re.sub(r"\s+", " ", word.strip().lower())


def _update_srs(entry: VocabularyEntry, was_correct: bool) -> None:
    """Advance or reset the spaced-repetition schedule on *entry*.

    Mutates ``entry.srs_stage`` and ``entry.srs_due_at`` in place — the
    caller is responsible for committing the enclosing transaction.

    Incorrect answer:
        Stage resets to 0; next review is now (immediate re-study).

    Correct answer:
        Stage 0 → +1 day, Stage 1 → +3 days, Stage 2 → +7 days,
        Stage 3 → +14 days, Stage ≥4 → +30 days.
        Stage is then incremented by one.
    """

    now = datetime.now(timezone.utc)

    if not was_correct:
        entry.srs_stage = 0
        entry.srs_due_at = now
        return

    intervals = {0: 1, 1: 3, 2: 7, 3: 14}
    days = intervals.get(entry.srs_stage, 30)

    entry.srs_due_at = now + timedelta(days=days)
    entry.srs_stage += 1


# ---------------------------------------------------------------------------
# VocabularyEntry CRUD
# ---------------------------------------------------------------------------


def create_vocabulary_entry(
    db: Session,
    user_id: uuid.UUID,
    schema: VocabularyEntryCreate,
) -> VocabularyEntry:
    """Create a new vocabulary entry for the given user.

    The word is normalized before insertion.  If a matching
    ``vocabulary_cache`` row exists for the same word + language, its
    ``meaning``, ``example_sentence``, ``part_of_speech``, and ``ipa``
    values are used to fill any fields that the caller did not supply —
    this is the "cache-first resolution" described in the model
    docstring.

    Raises:
        ValueError: If a duplicate ``(user_id, language_id, word)``
            combination already exists.
    """

    normalized = _normalize_word(schema.word)

    # Duplicate guard — same user + language + normalized word.
    existing = (
        db.query(VocabularyEntry)
        .filter(
            VocabularyEntry.user_id == user_id,
            VocabularyEntry.language_id == schema.language_id,
            VocabularyEntry.word == normalized,
        )
        .first()
    )
    if existing is not None:
        raise ValueError("Vocabulary entry already exists for this language.")

    # Cache-first resolution: fill gaps from the shared cache.
    cached = get_cached_vocabulary(db, normalized, schema.language_id)

    meaning = schema.meaning
    example_sentence = schema.example_sentence
    part_of_speech = schema.part_of_speech
    ipa = schema.ipa

    if cached is not None:
        if meaning is None:
            meaning = cached.meaning
        if example_sentence is None:
            example_sentence = cached.example_sentence
        if part_of_speech is None:
            part_of_speech = cached.part_of_speech
        if ipa is None:
            ipa = cached.ipa

    entry = VocabularyEntry(
        user_id=user_id,
        language_id=schema.language_id,
        word=normalized,
        meaning=meaning,
        example_sentence=example_sentence,
        part_of_speech=part_of_speech,
        ipa=ipa,
        tags=schema.tags,
    )

    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
    except Exception:
        db.rollback()
        raise

    return entry


def get_vocabulary_entry_by_id(
    db: Session,
    entry_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[VocabularyEntry]:
    """Retrieve a single vocabulary entry by primary key.

    Returns ``None`` if no entry exists or if the entry does not belong
    to *user_id* — callers never see another user's data.
    """

    return (
        db.query(VocabularyEntry)
        .filter(
            VocabularyEntry.id == entry_id,
            VocabularyEntry.user_id == user_id,
        )
        .first()
    )


def get_user_vocabulary(
    db: Session,
    user_id: uuid.UUID,
    language_id: Optional[uuid.UUID] = None,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
) -> list[VocabularyEntry]:
    """Return a paginated slice of the user's vocabulary list.

    Args:
        language_id: If supplied, only entries for that language are
            included.
        page: 1-indexed page number.
        page_size: Maximum entries per page.
        search: Optional case-insensitive substring search against the
            ``word`` column.

    Results are ordered newest-first (``date_added`` descending).
    """

    page = max(1, page)
    page_size = max(1, page_size)

    query = db.query(VocabularyEntry).filter(
        VocabularyEntry.user_id == user_id,
    )

    if language_id is not None:
        query = query.filter(VocabularyEntry.language_id == language_id)

    if search is not None and search.strip():
        query = query.filter(VocabularyEntry.word.ilike(f"%{search.strip()}%"))

    offset = (page - 1) * page_size

    return (
        query
        .order_by(VocabularyEntry.date_added.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


def search_vocabulary(
    db: Session,
    user_id: uuid.UUID,
    query: str,
    language_id: Optional[uuid.UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> list[VocabularyEntry]:
    """Full-text-style search across a user's vocabulary entries.

    Searches ``word``, ``meaning``, and ``example_sentence`` using
    case-insensitive ``ILIKE``.  Results are paginated newest-first.
    """

    page = max(1, page)
    page_size = max(1, page_size)

    stmt = db.query(VocabularyEntry).filter(
        VocabularyEntry.user_id == user_id,
    )

    if query is not None and query.strip():
        term = f"%{query.strip()}%"
        stmt = stmt.filter(
            or_(
                VocabularyEntry.word.ilike(term),
                VocabularyEntry.meaning.ilike(term),
                VocabularyEntry.example_sentence.ilike(term),
            )
        )

    if language_id is not None:
        stmt = stmt.filter(VocabularyEntry.language_id == language_id)

    offset = (page - 1) * page_size

    return (
        stmt
        .order_by(VocabularyEntry.date_added.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


def update_vocabulary_entry(
    db: Session,
    entry: VocabularyEntry,
    schema: VocabularyEntryUpdate,
) -> VocabularyEntry:
    """Partially update an existing vocabulary entry.

    Only fields explicitly supplied by the client (``exclude_unset``)
    are modified.  ``user_id``, ``language_id``, and ``date_added`` are
    never overwritten regardless of what the caller sends.
    """

    protected_fields = {"user_id", "language_id", "date_added"}
    update_data = schema.model_dump(exclude_unset=True)

    # If the word is being changed, check for duplicates.
    if "word" in update_data and update_data["word"] is not None:
        normalized_word = _normalize_word(update_data["word"])
        duplicate = (
            db.query(VocabularyEntry)
            .filter(
                VocabularyEntry.user_id == entry.user_id,
                VocabularyEntry.language_id == entry.language_id,
                VocabularyEntry.word == normalized_word,
                VocabularyEntry.id != entry.id,
            )
            .first()
        )
        if duplicate is not None:
            raise ValueError("Vocabulary entry already exists for this language.")

    for field, value in update_data.items():
        if field in protected_fields:
            continue
        if field == "word" and value is not None:
            value = _normalize_word(value)
        setattr(entry, field, value)

    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
    except Exception:
        db.rollback()
        raise

    return entry


def delete_vocabulary_entry(db: Session, entry: VocabularyEntry) -> None:
    """Delete a vocabulary entry and commit the transaction.

    Related ``vocabulary_review_log`` rows are removed automatically
    via the ``cascade="all, delete-orphan"`` relationship defined on
    the model.
    """

    try:
        db.delete(entry)
        db.commit()
    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------------------------------
# Review / SRS
# ---------------------------------------------------------------------------


def create_review_log(
    db: Session,
    entry: VocabularyEntry,
    user_id: uuid.UUID,
    was_correct: bool,
) -> VocabularyReviewLog:
    """Record a spaced-repetition review and update the entry's SRS state.

    Creates a new ``VocabularyReviewLog`` row and advances (or resets)
    ``entry.srs_stage`` / ``entry.srs_due_at`` via ``_update_srs``.
    Both mutations are committed in a single transaction.

    Returns:
        The newly created review-log row.
    """

    if entry.user_id != user_id:
        raise ValueError("Vocabulary entry does not belong to the specified user.")

    log = VocabularyReviewLog(
        vocabulary_entry_id=entry.id,
        user_id=user_id,
        was_correct=was_correct,
    )

    _update_srs(entry, was_correct)

    try:
        db.add(log)
        db.add(entry)
        db.commit()
        db.refresh(log)
        db.refresh(entry)
    except Exception:
        db.rollback()
        raise

    return log


def get_due_vocabulary(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 50,
) -> list[VocabularyEntry]:
    """Return vocabulary entries that are due for review.

    An entry is "due" when its ``srs_due_at`` is at or before the
    current UTC time.  Results are ordered oldest-due-first so the most
    overdue words surface at the top.
    """

    now = datetime.now(timezone.utc)

    return (
        db.query(VocabularyEntry)
        .filter(
            VocabularyEntry.user_id == user_id,
            VocabularyEntry.srs_due_at <= now,
        )
        .order_by(VocabularyEntry.srs_due_at.asc())
        .limit(limit)
        .all()
    )


# ---------------------------------------------------------------------------
# VocabularyCache helpers
# ---------------------------------------------------------------------------


def get_cached_vocabulary(
    db: Session,
    word: str,
    language_id: uuid.UUID,
) -> Optional[VocabularyCache]:
    """Look up a shared cache entry by normalized word and language.

    The word is normalized before the lookup to stay consistent with the
    unique constraint on ``vocabulary_cache(word, language_id)``.
    """

    normalized = _normalize_word(word)

    return (
        db.query(VocabularyCache)
        .filter(
            VocabularyCache.word == normalized,
            VocabularyCache.language_id == language_id,
        )
        .first()
    )


def create_cache_entry(
    db: Session,
    data: VocabularyCache,
) -> VocabularyCache:
    """Insert a new row into the shared vocabulary cache.

    The caller is responsible for constructing the ``VocabularyCache``
    instance (including normalizing the word).  This function handles
    the add / commit / refresh / rollback cycle.
    """

    try:
        db.add(data)
        db.commit()
        db.refresh(data)
    except Exception:
        db.rollback()
        raise

    return data
