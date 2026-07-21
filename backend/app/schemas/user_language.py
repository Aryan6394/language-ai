import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.language import (
    UserLanguageLevel,
    UserLanguageStatus,
)


class LanguageSummary(BaseModel):
    """Basic language information."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    native_name: str


class UserLanguageCreate(BaseModel):
    """Request body for enrolling in a language."""

    language_id: uuid.UUID
    level: UserLanguageLevel


class UserLanguageResponse(BaseModel):
    """Response after enrollment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    language_id: uuid.UUID

    level: UserLanguageLevel
    status: UserLanguageStatus

    started_at: datetime
    cefr_estimate: str | None = None


class UserLanguageDetail(BaseModel):
    """Detailed enrolled language response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level: UserLanguageLevel
    status: UserLanguageStatus
    started_at: datetime
    cefr_estimate: str | None = None

    language: LanguageSummary