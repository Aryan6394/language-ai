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
from app.routers.users import router as user_router

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
# Load the cached Settings instance once at import time. This is the single
# source of truth for app identity (name/version) and CORS configuration —
# see app/core/config.py for what each field means.
settings = get_settings()

# --------------------------------------------------------------------------
# App instance
# --------------------------------------------------------------------------
# The FastAPI app is created with its title and version pulled from
# Settings rather than hardcoded, so they can change per environment
# (e.g. via .env) without touching this file. Title/version show up in
# the auto-generated docs at /docs and /redoc.
app = FastAPI(title=settings.app_name, version=settings.app_version)

# --------------------------------------------------------------------------
# CORS middleware
# --------------------------------------------------------------------------
# Allows browser-based frontend clients running on an allowed origin to
# call this API. `allowed_origins` comes from Settings so it can be
# tightened per environment (e.g. a real domain in production) without
# code changes. allow_methods/allow_headers are left open ("*") at this
# foundation stage; if that needs tightening later, it belongs to
# whichever domain motivates the restriction, not this entry point.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Routers
# --------------------------------------------------------------------------
# Only the auth router is mounted, and only its /register endpoint exists
# right now (see app/router/auth.py). Mounting is required here — an
# unmounted router would leave /auth/register unreachable, defeating the
# point of this task. No other routers (e.g. vocabulary) are included.
app.include_router(auth_router)
app.include_router(user_router)

# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------
# A minimal, dependency-free endpoint to confirm the process is up and
# responding. Deliberately does not check DB/Redis connectivity here —
# that would pull in database logic, which is out of scope for this file.
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}