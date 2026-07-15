# LinguaAI — FOLDER_STRUCTURE.md

Proposed repository layout. Structure only — no logic, no implementation. File purposes are noted as one-line comments for orientation; they describe *what would eventually live there*, not how it works. Backend layout follows standard FastAPI project conventions (routers / schemas / models / services / core separation) and mirrors the entities in `DATABASE.md` and the routers in `API.md`.

---

## 1. Repository Root

```
linguaai/
├── PLAN.md
├── TASKS.md
├── ARCHITECTURE.md
├── DATABASE.md
├── API.md
├── FOLDER_STRUCTURE.md
├── README.md                     # project overview, setup instructions (to be written)
├── .gitignore
├── backend/
├── frontend/
└── infra/
```

---

## 2. Backend — `backend/` (FastAPI)

```
backend/
├── app/
│   ├── main.py                   # FastAPI app entrypoint, router registration
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # environment/settings loader
│   │   ├── security.py           # token/password handling utilities
│   │   └── quota.py              # daily quota check, used as a dependency
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py            # DB session/connection setup
│   │   └── base.py               # ORM base class, model registry
│   │
│   ├── models/                   # ORM models — one file per DATABASE.md entity group
│   │   ├── __init__.py
│   │   ├── user.py               # users, user_settings
│   │   ├── language.py           # languages, user_languages
│   │   ├── lesson.py             # units, lessons, lesson_attempts
│   │   ├── vocabulary.py         # vocabulary_entries, vocabulary_cache, vocabulary_review_log
│   │   ├── achievement.py        # achievements, user_achievements
│   │   ├── xp.py                 # xp_log
│   │   └── progress.py           # user_progress, unit_progress
│   │
│   ├── schemas/                  # Pydantic request/response models — mirrors API.md
│   │   ├── __init__.py
│   │   ├── common.py             # PaginatedResponse, ErrorResponse
│   │   ├── auth.py               # SignupRequest, LoginRequest, TokenResponse
│   │   ├── user.py               # UserOut, UserUpdate, UserSettingsOut/Update
│   │   ├── language.py           # LanguageOut, UserLanguageOut/Create/Update
│   │   ├── lesson.py             # UnitOut, LessonOut, LessonAttemptCreate/Out
│   │   ├── vocabulary.py         # VocabularyEntryOut/Create/Update, VocabularyReviewCreate
│   │   ├── achievement.py        # AchievementOut, UserAchievementOut
│   │   ├── xp.py                 # XpSummaryOut, XpLogEntryOut
│   │   └── progress.py           # UserProgressOut, UnitProgressOut
│   │
│   ├── routers/                  # one router per API.md section
│   │   ├── __init__.py
│   │   ├── auth.py               # /auth/*
│   │   ├── users.py              # /users/me, /users/me/settings
│   │   ├── languages.py          # /languages, /users/me/languages
│   │   ├── units.py              # /languages/{id}/units
│   │   ├── lessons.py            # /units/{id}/lessons, /lessons/*, attempts
│   │   ├── vocabulary.py         # /users/me/vocabulary/*
│   │   ├── achievements.py       # /achievements, /users/me/achievements
│   │   ├── xp.py                 # /users/me/xp*
│   │   ├── progress.py           # /users/me/progress*
│   │   └── quota.py              # /users/me/quota
│   │
│   ├── services/                 # business-logic layer, placeholder only
│   │   ├── __init__.py
│   │   ├── llm_service.py        # lesson/content generation via LLM API
│   │   ├── dictionary_service.py # word lookup, cache-first
│   │   ├── quota_service.py      # quota counters, cache reuse logic
│   │   ├── xp_service.py         # XP award + rollup updates
│   │   ├── srs_service.py        # spaced-repetition scheduling
│   │   └── achievement_service.py# achievement-unlock checks
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_client.py       # Redis connection/client setup
│   │
│   └── dependencies.py           # shared FastAPI Depends: get_current_user, pagination, etc.
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # shared test fixtures
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_languages.py
│   ├── test_lessons.py
│   ├── test_vocabulary.py
│   ├── test_achievements.py
│   ├── test_xp.py
│   ├── test_progress.py
│   └── test_quota.py
│
├── alembic/                      # DB migrations (if using Alembic with SQLAlchemy)
│   ├── versions/
│   └── env.py
│
├── requirements.txt              # backend dependencies
├── .env.example                  # sample environment variables (no real secrets)
└── pyproject.toml                # project metadata / tooling config
```

---

## 3. Frontend — `frontend/`

Layout kept framework-agnostic since platform choice (web vs. mobile vs. both) is still an open decision in `TASKS.md`. Shown here as a generic component-based structure.

```
frontend/
├── src/
│   ├── screens/                  # one folder per major flow from ARCHITECTURE.md / TASKS.md wireframes
│   │   ├── onboarding/           # language + level selection, placement check
│   │   ├── home/                 # daily practice, streak, today's lesson
│   │   ├── lesson/                # reading/speaking/listening exercise screens
│   │   ├── vocabulary/            # word list, add word, review queue
│   │   ├── progress/              # dashboard, per-language progress
│   │   ├── achievements/          # achievement gallery
│   │   └── settings/              # notification prefs, daily goal, account
│   │
│   ├── components/                # shared UI building blocks (buttons, cards, streak badge, etc.)
│   │
│   ├── api/                       # thin client wrappers, one file per API.md router
│   │   ├── authApi.*
│   │   ├── userApi.*
│   │   ├── languageApi.*
│   │   ├── lessonApi.*
│   │   ├── vocabularyApi.*
│   │   ├── achievementApi.*
│   │   ├── xpApi.*
│   │   ├── progressApi.*
│   │   └── quotaApi.*
│   │
│   ├── speech/                    # client-side Web Speech API wrappers (STT/TTS), per ARCHITECTURE.md
│   │   ├── speechToText.*
│   │   └── textToSpeech.*
│   │
│   ├── state/                     # app state management (auth session, current user, active language)
│   │
│   └── assets/                    # icons, achievement badge images, fonts
│
├── public/                        # static assets (web) or platform config (mobile)
└── package.json
```

---

## 4. Infra — `infra/`

```
infra/
├── docker-compose.yml             # local dev: backend + postgres + redis
├── postgres/
│   └── init/                      # optional seed/init scripts (schema seed data, not logic)
└── redis/
    └── redis.conf                 # local dev config
```

---

## 5. Notes on This Structure

- Every file listed is a **placeholder location**, not a populated implementation — the comments describe intended purpose only, matching the "structure only" scope of this request.
- `models/`, `schemas/`, and `routers/` are each split into the same seven domain groupings used throughout `DATABASE.md` and `API.md` (Users, Languages, Lessons, Vocabulary, Achievements, XP, Progress) so the three documents and the codebase stay easy to cross-reference.
- `services/` exists as a layer separate from `routers/` specifically so quota-checking, caching, and external API calls (LLM, dictionary) stay out of route handlers — matching the quota-gatekeeper design in `ARCHITECTURE.md`.
- No `alembic/` migration content, no `docker-compose.yml` service definitions, and no `.env.example` values are filled in here — those are implementation, out of scope per this request.

---

## 6. Open Questions (feed into `TASKS.md`)

- ORM choice (SQLAlchemy assumed above) — confirm before scaffolding `models/` and `alembic/`.
- Final frontend framework choice will determine whether `frontend/src/screens` uses a router-based folder convention (e.g. Next.js `app/` or `pages/`) or a plain component-tree convention (e.g. React Native `screens/`).
