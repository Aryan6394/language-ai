"""
Authentication router.

Scope note: this file implements only the registration endpoint below.
Deliberately NOT included here, per current task requirements:
  - Login (no /auth/login, no credential verification against
    verify_password())
  - JWT issuance/validation (no token fields anywhere in this file)
  - A current-user dependency (nothing here reads or requires a token)

NAMING NOTE: API.md documents this endpoint as `POST /auth/signup`. This
task explicitly asked for `POST /register`, so that's what's implemented
here (mounted under this router's `/auth` prefix, i.e. `/auth/register`).
Flagging the mismatch rather than silently picking one — API.md may need
a small update later to match, or this endpoint may need renaming to
`/signup` once that's decided.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Checks for an existing account with the same email via
    get_user_by_email() first — if one exists, returns 400 rather than
    silently overwriting or creating a duplicate. Otherwise delegates
    to create_user(), which hashes the password before storing it
    (see app/core/security.py / app/crud/user.py).
    """
    existing_user = get_user_by_email(db, user.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    return create_user(db, user)