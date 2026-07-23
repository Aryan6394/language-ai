"""
FastAPI application entry point.

Scope (per current task): only the app instance, settings-driven
title/version, CORS middleware, a basic health check, and mounting the
auth router (registration only — see app/router/auth.py).

Deliberately excluded, per requirements:
  - Authentication logic itself (that lives in app/router/auth.py,
    app/crud/user.py, app/core/security.py — this file just mounts it)
  - Login, JWT, current-user dependencies
  - Database logic beyond wiring in the router
  - Any other business features (e.g. the previously implemented
    Vocabulary router remains unmounted)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

from app.routers.auth import router as auth_router
from app.routers.dictionary import router as dictionary_router
from app.routers.languages import router as language_router
from app.routers.users import router as user_router
from app.routers.vocabulary import router as vocabulary_router
from app.routers.review import router as review_router

settings = get_settings()

app = FastAPI(
    title="LinguaAI API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(language_router)
app.include_router(dictionary_router)
app.include_router(vocabulary_router)
app.include_router(review_router)
# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------
# A minimal, dependency-free endpoint to confirm the process is up and
# responding. Deliberately does not check DB/Redis connectivity here —
# that would pull in database logic, which is out of scope for this file.
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}