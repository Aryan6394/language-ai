# LinguaAI

An AI-powered app for learning spoken languages — reading, speaking, and vocabulary building — with a personalized learning path based on your experience level (Beginner / Intermediate / Expert), plus daily streaks, points/XP, and a personal word list. Built entirely on free-tier tools and services.

---

## What Makes It Different

- **Open-ended conversation roleplay** via LLM, not scripted multiple-choice trees
- **User-imported content** — paste a song, article, or message and get vocab/exercises generated from it
- **On-demand grammar explanations** ("why is it 'la' not 'el' here?") instead of pure repetition
- **"Explain my mistake" loop** on wrong answers
- **CEFR-mapped proficiency (A1–C2)**, not just XP
- **Honest gamification** — no hearts/lives, no guilt-driven streak notifications

See `PLAN.md` for the full breakdown, including what was intentionally cut to stay free-tier feasible (e.g. phoneme-level pronunciation scoring, live tutoring calls).

---

## Project Documentation

| Doc | Contents |
|---|---|
| [`PLAN.md`](./PLAN.md) | Vision, feature phases, tech stack, free-tier constraints, roadmap |
| [`TASKS.md`](./TASKS.md) | Full backlog by phase, plus cross-cutting workstreams (QA, legal, infra) |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System diagram, component responsibilities, request flows, quota strategy |
| [`DATABASE.md`](./DATABASE.md) | Full schema across Users, Languages, Lessons, Vocabulary, Achievements, XP, Progress |
| [`API.md`](./API.md) | REST API design in FastAPI conventions (routers, schemas, status codes) |
| [`FOLDER_STRUCTURE.md`](./FOLDER_STRUCTURE.md) | Proposed repo layout, backend and frontend |

Read them in the order above if you're new to the project — each one builds on the last.

---

## Implementation Status

| Domain | Status |
|---|---|
| Vocabulary | ✅ Implemented (models, schemas, CRUD, router) |
| Auth / Users | ⏳ Not yet implemented — a temporary placeholder (`X-User-Id` header) stands in for real auth |
| Languages | ⏳ Not yet implemented |
| Lessons | ⏳ Not yet implemented |
| Achievements | ⏳ Not yet implemented |
| XP | ⏳ Not yet implemented |
| Progress | ⏳ Not yet implemented |
| Frontend | ⏳ Not started |

---

## Repository Layout

```
linguaai/
├── PLAN.md
├── TASKS.md
├── ARCHITECTURE.md
├── DATABASE.md
├── API.md
├── FOLDER_STRUCTURE.md
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint (mounts implemented routers)
│   │   ├── db/                # engine, session, declarative base
│   │   ├── models/             # SQLAlchemy models, by domain
│   │   ├── schemas/             # Pydantic request/response models, by domain
│   │   ├── crud/                # DB access + domain logic, by domain
│   │   ├── router/              # FastAPI routers, by domain
│   │   └── dependencies.py      # shared dependencies (auth placeholder, pagination)
│   └── requirements.txt
└── frontend/                    # not started
```

Full proposed layout (including domains not yet built) is in `FOLDER_STRUCTURE.md`.

---

## Getting Started (Backend)

**Requirements:** Python 3.11+, PostgreSQL

```bash
cd backend
pip install -r requirements.txt
```

Set your database connection (defaults to a local Postgres instance if unset):

```bash
export DATABASE_URL="postgresql://linguaai:linguaai@localhost:5432/linguaai"
```

Run the API:

```bash
uvicorn app.main:app --reload
```

- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

**Note on auth:** since the Users/Auth backend isn't implemented yet, Vocabulary endpoints require a temporary `X-User-Id` header (any valid UUID) in place of a real bearer token. This will be replaced once the Auth domain is built — see `TASKS.md`.

### Currently Available Endpoints

```
GET/POST          /users/me/vocabulary
GET               /users/me/vocabulary/review-queue
GET/PATCH/DELETE  /users/me/vocabulary/{vocab_id}
POST              /users/me/vocabulary/{vocab_id}/review
```

Full endpoint reference for all domains (including ones not yet implemented) is in `API.md`.

---

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL + Redis
- **AI/Language services:** LLM API (rate-limited per user), browser Web Speech API for STT/TTS (client-side, no audio sent to the backend), free-tier dictionary/translation API
- **Frontend:** not yet chosen — platform decision (web / mobile / both) is an open item in `TASKS.md`

Full rationale for each choice is in `PLAN.md` and `ARCHITECTURE.md`.

---

## Next Steps

See `TASKS.md` for the full backlog. Immediate priorities:
1. Implement Auth/Users backend to replace the temporary `X-User-Id` placeholder
2. Implement Languages backend
3. Implement Lessons backend (reading/speaking/listening + LLM content generation with quota gatekeeping)
