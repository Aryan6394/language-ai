"""
Pydantic schemas for the Language domain.
"""

import uuid

from pydantic import BaseModel, ConfigDict


class LanguageResponse(BaseModel):
    """
    Response returned for a supported language.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    native_name: str
    is_learnable: bool
    is_ui_supported: bool