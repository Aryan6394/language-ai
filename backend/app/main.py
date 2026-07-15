"""
FastAPI application entry point.

Scope (per current task): only the app instance, settings-driven
title/version, CORS middleware, and a basic health check.

Deliberately excluded, per requirements:
  - Authentication (no login/token logic)
  - Routers (no domain routers, including the previously implemented
    Vocabulary router, are mounted here)
  - Database logic (no DB session wiring or queries)
  - Any other business features

Those are added in their own, separate passes as each domain is built.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

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
# Health check
# --------------------------------------------------------------------------
# A minimal, dependency-free endpoint to confirm the process is up and
# responding. Deliberately does not check DB/Redis connectivity here —
# that would pull in database logic, which is out of scope for this file.
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
