"""
Pydantic schemas for the `User` model (DATABASE.md, Section 1.1).

This module contains only request and response schemas for the User model.
Business logic belongs in services, persistence belongs in CRUD, and HTTP
handling belongs in routers.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import AccountStatus


class UserCreate(BaseModel):
    """
    Request schema for creating a new user account.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=100)
    native_language_id: Optional[uuid.UUID] = None


class UserLogin(BaseModel):
    """
    Request schema for user login.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Response schema returned to the client.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: Optional[EmailStr] = None
    display_name: str
    native_language_id: Optional[uuid.UUID] = None
    is_guest: bool
    account_status: AccountStatus
    created_at: datetime
    last_active_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    """
    Request schema for updating user profile information.
    """

    display_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    native_language_id: Optional[uuid.UUID] = None