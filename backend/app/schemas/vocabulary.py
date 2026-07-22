"""Pydantic schemas for the Vocabulary domain (DATABASE.md, Section 4).

Mirrors the three tables implemented in app/models/vocabulary.py:
  - vocabulary_entries    -> VocabularyEntryBase / Create / Update / Response
  - vocabulary_cache      -> VocabularyCacheResponse
  - vocabulary_review_log -> VocabularyReviewLogCreate / Response

`vocabulary_cache` has no Create/Update schema: it is an internal,
shared cache populated by the CRUD/service layer (cache-first
dictionary resolution), never written to directly by a client — so
only a response shape is needed.

Only schemas are defined here. No SQLAlchemy models, CRUD, routers,
Alembic migrations, or tests.
"""

import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.vocabulary import VocabularyCacheSource


class VocabularyEntryBase(BaseModel):
    """Fields common to creating and reading a vocabulary entry.

    Holds the "content" of an entry — everything except identity
    (`id`), ownership (`user_id`, set from the authenticated user, not
    the request body), and spaced-repetition scheduling state
    (`srs_stage`/`srs_due_at`, managed by the review flow rather than
    general create/edit).
    """

    word: str = Field(..., min_length=1, max_length=200, description="The word or phrase, as entered by the user.")
    meaning: str | None = Field(None, description="Definition/translation, often pulled from vocabulary_cache.")
    example_sentence: str | None = Field(None, description="An example sentence using the word.")
    part_of_speech: str | None = Field(
        None, max_length=50, description="Grammatical category, as free text (DATABASE.md does not enum this)."
    )
    ipa: str | None = Field(None, max_length=200, description="Optional phonetic (IPA) spelling.")
    tags: List[str] | None = Field(None, description="User-defined categorization tags.")


class VocabularyEntryCreate(VocabularyEntryBase):
    """Input shape for adding a new vocabulary entry.

    `language_id` is required here (which language this word belongs
    to) but not part of `VocabularyEntryBase`, since a response never
    needs to re-derive it separately from the base content fields —
    it's simply included again in `VocabularyEntryResponse` below.
    `user_id` is deliberately absent: ownership comes from the
    authenticated request context, never from client-supplied input.
    """

    language_id: uuid.UUID = Field(..., description="Which language this word belongs to.")


class VocabularyEntryUpdate(BaseModel):
    """Input shape for editing an existing vocabulary entry.

    All fields optional, so a client can send a partial update. Does
    NOT include `srs_stage`/`srs_due_at` — those are only ever advanced
    via a review submission (`VocabularyReviewLogCreate`), never set
    directly through a general edit endpoint.
    """

    word: str | None = Field(None, min_length=1, max_length=200)
    meaning: str | None = None
    example_sentence: str | None = None
    part_of_speech: str | None = Field(None, max_length=50)
    ipa: str | None = Field(None, max_length=200)
    tags: List[str] | None = None


class VocabularyEntryResponse(VocabularyEntryBase):
    """Full representation of a vocabulary entry, as returned to clients.

    Matches DATABASE.md Section 4.1 field-for-field: adds identity,
    ownership, and spaced-repetition scheduling state on top of the
    content fields inherited from `VocabularyEntryBase`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    language_id: uuid.UUID
    date_added: datetime
    srs_stage: int
    srs_due_at: datetime | None = None


class VocabularyCacheResponse(BaseModel):
    """Representation of a shared `vocabulary_cache` lookup.

    Matches DATABASE.md Section 4.2 field-for-field. Read-only from the
    API's perspective — there is no corresponding Create/Update schema
    (see module docstring).
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    word: str
    language_id: uuid.UUID
    meaning: str | None = None
    example_sentence: str | None = None
    part_of_speech: str | None = None
    ipa: str | None = None
    source: VocabularyCacheSource
    fetched_at: datetime


class VocabularyReviewLogCreate(BaseModel):
    """Input shape for submitting a spaced-repetition review result.

    Deliberately minimal: `vocabulary_entry_id` is expected to come
    from the URL path (e.g. `POST /vocabulary/{id}/review`) rather than
    the request body, and `user_id` from the authenticated request
    context — so the only thing the client actually decides is the
    outcome of the review.
    """

    was_correct: bool = Field(..., description="Whether the review attempt was correct.")


class VocabularyReviewLogResponse(BaseModel):
    """Representation of a single spaced-repetition review log row.

    Matches DATABASE.md Section 4.3 field-for-field.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vocabulary_entry_id: uuid.UUID
    user_id: uuid.UUID
    was_correct: bool
    reviewed_at: datetime