"""
Password hashing (DATABASE.md Section 1.1: `users.password_hash`;
ARCHITECTURE.md Section 5: "passwords hashed (standard practice, not
detailed here per 'no code' scope)" — this file is that detail, now that
we're implementing it).

Why this is needed
-------------------
`users.password_hash` must never store a plaintext password. If the
database were ever leaked or read by anyone with access (an attacker,
a careless query, a backup dump), a plaintext password column would
immediately compromise every user's account — and, since people reuse
passwords, likely their accounts on other sites too.

Hashing solves this one-way: `hash_password` turns a plaintext password
into a string that is computationally infeasible to reverse back into
the original password. At login, we don't decrypt the stored hash — we
hash the freshly submitted password the same way and compare
(`verify_password`), which is a correctness check, not a decryption.

Two more properties matter here, both handled by the algorithm rather
than by this file's code:
  - **Salting**: each hash embeds a unique random salt, so two users
    with the same password get different `password_hash` values, and
    precomputed "rainbow table" attacks don't work.
  - **Deliberate slowness**: the algorithm is intentionally expensive
    to compute, so brute-forcing many guesses against a stolen hash is
    slow even for an attacker with significant hardware.

How this implementation works
-------------------------------
`pwdlib` is used with `PasswordHash.recommended()`, which currently
selects Argon2id — the algorithm recommended by OWASP for new
applications, winner of the 2015 Password Hashing Competition, and
resistant to both GPU-cracking and side-channel attacks. Using
`.recommended()` rather than pinning an algorithm directly also means
the underlying default can be upgraded by a `pwdlib` version bump
later without changing any code here.

Authentication (JWT)
---------------------
As of the Authentication milestone, this file also issues and verifies
JSON Web Tokens for login sessions. A JWT is how the API proves, on
every subsequent request, "this request really is from user X" without
re-checking a password every time: the client logs in once (via
`verify_password` against the DB), receives a signed token, and then
presents that token on future requests. `decode_access_token` checks
the signature (proving *this* API issued it, using `secret_key` — see
app/core/config.py) and the expiration (`exp` claim), so a stolen but
expired token, or a token with a forged/altered payload, is rejected.

Scope note: only hash/verify password and create/verify access token
are implemented here, per current task requirements. No refresh tokens,
no logout/revocation, no routes, no CRUD — this file doesn't know what
a login endpoint is, it just provides the primitives one would use.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

# A single, module-level PasswordHash instance. `.recommended()` bundles
# a primary hasher (used for new hashes) with any legacy hashers pwdlib
# knows how to verify — so if the recommended algorithm ever changes,
# old hashes created under the previous default can still be verified.
_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Turn a plaintext password into a salted, algorithm-tagged hash
    string suitable for storing in `users.password_hash`.

    The returned string is self-describing (it encodes which algorithm,
    parameters, and salt were used), so `verify_password` doesn't need
    to be told any of that separately later.
    """
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Check whether a plaintext password matches a previously stored hash.

    Returns True/False rather than raising on mismatch, so callers
    (e.g. a future login flow) can handle "wrong password" as an
    ordinary case, not an exception.
    """
    return _password_hash.verify(password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token for the given subject (the
    authenticated user's id, as a string).

    `expires_delta` lets a caller override the default expiry (rarely
    needed); when omitted, `settings.access_token_expire_minutes` is
    used.
    """

    settings = get_settings()

    expire_at = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode = {
        "sub": str(subject),
        "exp": expire_at,
    }

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT access token.

    Returns:
        The decoded JWT payload.

    Raises:
        JWTError:
            If the token is invalid, malformed, expired,
            or missing the required 'sub' claim.
    """

    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    if "sub" not in payload:
        raise JWTError("Missing subject")

    return payload


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]