"""
Shared FastAPI dependencies used across routers.

NOTE:
`get_current_user_id` is a TEMPORARY placeholder kept for legacy routers.

New authentication-aware routes should instead depend on
`get_current_user`.
"""

import uuid

from fastapi import Depends, Header, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload


# --------------------------------------------------------------------------
# Legacy dependency
# --------------------------------------------------------------------------

def get_current_user_id(
    x_user_id: str = Header(
        ...,
        alias="X-User-Id",
        description="Temporary authentication placeholder",
    ),
) -> uuid.UUID:
    """
    Temporary authentication dependency.

    Returns the UUID supplied in the X-User-Id header.
    """

    try:
        return uuid.UUID(x_user_id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id header must be a valid UUID",
        )


# --------------------------------------------------------------------------
# Shared pagination
# --------------------------------------------------------------------------

class PaginationParams:
    """Shared limit/offset query parameters."""

    def __init__(
        self,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        self.limit = limit
        self.offset = offset


# --------------------------------------------------------------------------
# OAuth2
# --------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


# --------------------------------------------------------------------------
# Authentication dependency
# --------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate a Bearer token and return the corresponding user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = decode_access_token(token)

        token_data = TokenPayload(**payload)

        if token_data.sub is None:
            raise credentials_exception

        user_id = uuid.UUID(token_data.sub)

    except (JWTError, ValidationError, ValueError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)

    if user is None:
        raise credentials_exception

    return user