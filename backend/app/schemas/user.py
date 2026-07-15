"""
Pydantic schemas for the `User` model (DATABASE.md, Section 1.1).

Milestone 2 (Authentication) scope note: this file implements only
request/response schemas. Deliberately NOT included here:
  - CRUD functions
  - Routers/endpoints
  - Password hashing (UserCreate/UserLogin carry a plain `password`
    field; turning that into `password_hash` happens in a future
    app/core/security.py + CRUD layer, not here)
  - JWT issuance/validation

NOTE:
`EmailStr` requires the `email-validator` package.
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

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    native_language_id: Optional[uuid.UUID] = None