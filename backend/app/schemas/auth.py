"""
Pydantic schemas for the authentication flow (login + JWT).

Scope note: schemas only. No CRUD, no routers, no JWT logic itself
(that's app/core/security.py) — these are just the request/response
shapes the auth router uses.

NOTE ON OVERLAP: `app/schemas/user.py` already defines `UserLogin`
(email + password). `LoginRequest` below duplicates that shape. This is
intentional rather than an oversight: keeping auth-domain schemas
self-contained in this file means future login-specific fields (e.g. a
"remember me" flag, or a captcha token) can be added here without
touching the User schemas file, which is scoped to the User resource
itself, not the auth flow around it.
"""

from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Request body for POST /auth/login.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Response returned after a successful login.
    """

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenPayload(BaseModel):
    """
    Decoded JWT payload.
    """

    sub: Optional[str] = None
    exp: Optional[int] = None


class ChangePasswordRequest(BaseModel):
    """
    Request body for changing the authenticated user's password.
    """

    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    """
    Generic success response.
    """

    message: str