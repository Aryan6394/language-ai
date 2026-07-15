# LinguaAI — ARCHITECTURE.md

High-level system architecture. Scoped entirely to free-tier services (per `PLAN.md` Section 4a). No implementation code — structure and data flow only.

---

## 1. System Overview (text diagram)

```
                        ┌─────────────────────────┐
                        │        Client App        │
                        │  (mobile and/or web —    │
                        │   see Open Decisions)     │
                        └────────────┬─────────────┘
                                     │  HTTPS (REST/JSON)
                                     ▼
                        ┌─────────────────────────┐
                        │      Backend API         │
                        │  (auth, business logic,  │
                        │   quota enforcement)      │
                        └───┬─────────┬─────────┬──┘
                            │         │         │
              ┌─────────────┘         │         └─────────────┐
              ▼                       ▼                       ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────────┐
     │   PostgreSQL     │     │      Redis      │     │  External Free-Tier │
     │ (primary data     │     │ (cache, session, │     │  APIs (called via   │
     │  store)           │     │  streak state,    │     │  backend, not client)│
     └────────────────┘     │  leaderboard)   │     └────────────────────┘
                             └────────────────┘                │
                                                    ┌───────────┼────────────┐
                                                    ▼           ▼            ▼
                                              ┌──────────┐ ┌──────────┐ ┌──────────┐
                                              │ LLM API   │ │ Dictionary│ │  Push    │
                                              │ (free      │ │  API      │ │  Notif.  │
                                              │  quota)    │ │ (free tier)│ │ (free)   │
                                              └──────────┘ └──────────┘ └──────────┘

     Client-side only (no backend round trip needed):
     ┌─────────────────────────────────────────┐
     │  Browser Web Speech API                    │
     │  - Speech-to-Text (speaking exercises)     │
     │  - Text-to-Speech (word/lesson pronunciation)│
     └─────────────────────────────────────────┘
```

**Key architectural decision:** speech recognition and speech synthesis happen **client-side** via the browser's built-in Web Speech API. This avoids sending audio to a backend/cloud STT service entirely — it's the main reason the free-tier constraint is achievable. The backend only ever receives the **transcribed text**, never raw audio, for scoring purposes (see Section 4).

---

## 2. Components

### 2.1 Client App
- Responsible for: UI rendering, capturing microphone input, calling Web Speech API locally, playing TTS audio, local caching of the current lesson for offline resilience.
- Talks to Backend API only over authenticated HTTPS calls.
- Does **not** call the LLM, dictionary, or any third-party API directly — all external calls are proxied through the backend so API keys are never exposed client-side and so quota enforcement is centralized.

### 2.2 Backend API
Responsible for:
- Authentication & session management
- Business logic: streaks, points, learning path assembly, spaced-repetition scheduling
- **Quota gatekeeper**: every call that would hit the LLM or an external API passes through a per-user daily counter before being allowed through
- Orchestrating calls to external free-tier services and shaping their responses for the client
- Persisting all state to PostgreSQL

### 2.3 PostgreSQL (Primary Data Store)
- Source of truth for users, learning paths, lessons, word entries, attempts, points log.
- See `DATABASE.md` for full schema.

### 2.4 Redis (Cache / Ephemeral State)
- Session tokens
- Daily quota counters (reset at midnight per user timezone or UTC — decision pending, see Open Decisions)
- Leaderboard sorted sets (Phase 3 only)
- Short-lived cache of LLM-generated content to avoid redundant calls (e.g., caching a generated lesson for a given language/level/unit combination so multiple users on the same path don't each burn a separate LLM call)

### 2.5 External Free-Tier Services (all called server-side)
| Service | Purpose | Notes |
|---|---|---|
| LLM API | Lesson generation, conversation roleplay, grammar explanations, "explain my mistake" | Rate-limited by backend quota gatekeeper |
| Dictionary/Translation API | Word meaning, example sentence, part of speech, IPA | Cached in DB after first fetch — never re-fetched for the same word/language pair |
| Push notification service | Streak reminders | Free tier (e.g., web push / FCM-style); opt-in only |

### 2.6 Client-Side Web Speech API
- STT: transcribes user's spoken attempt to text, done in-browser
- TTS: reads words/sentences aloud, done in-browser
- No server round-trip, no audio storage required — this also simplifies the privacy/consent story since raw audio never leaves the device in the MVP

---

## 3. Request Flow Examples

### 3.1 Daily Lesson Load
1. Client requests today's lesson for the user's active learning path.
2. Backend checks: does a cached lesson already exist for this user/path/day? If yes, return it (no LLM call).
3. If not, backend checks quota gatekeeper → if under daily cap, calls LLM API to generate lesson content → caches result in DB → returns to client.
4. If quota exceeded, backend returns a fallback: a previously-cached generic lesson for that level, with a flag telling the client to show the "quota reached" message (per `TASKS.md` reliability item).

### 3.2 Speaking Exercise
1. Client captures audio locally, runs it through Web Speech API → gets transcribed text.
2. Client sends only the transcribed text (not audio) to the backend, along with the target sentence.
3. Backend runs a text-diff comparison, returns an accuracy score + which words were off.
4. No audio ever hits the backend in the MVP — keeps storage cost and privacy scope minimal.

### 3.3 Add Word to Vocabulary List
1. Client sends the new word + target language to backend.
2. Backend checks DB: has this exact word/language pair already been looked up by any user? If yes, reuse cached meaning/IPA/example — no external call.
3. If not cached, backend calls Dictionary API, stores result, returns to client.
4. Client uses Web Speech API locally to play pronunciation on demand (no TTS audio file stored).

---

## 4. Quota & Rate-Limiting Strategy (architectural, not code)

- Every external LLM/API call is metered per user per day in Redis.
- A shared cache layer (DB-backed) deduplicates identical requests across users — e.g., a generated "Beginner Spanish Unit 3" lesson is generated once and reused, not regenerated per user.
- When a user's personal daily cap is hit, backend serves cached/fallback content and returns a status flag the client uses to show a friendly limit-reached message — never a hard error.
- A global daily cap (across all users) is also tracked so the app doesn't exceed the account-wide free quota; if approaching the global cap, backend can throttle by favoring cache hits over fresh generation.

---

## 5. Security & Privacy Notes

- API keys for LLM/dictionary/push services live only in the backend environment — never shipped to the client.
- No raw audio is transmitted or stored in the MVP architecture (STT happens client-side, only text is sent).
- All client-backend traffic over HTTPS.
- Auth tokens short-lived with refresh; passwords hashed (standard practice, not detailed here per "no code" scope).

---

## 6. Deployment View (conceptual, free-tier hosting)

- Backend + PostgreSQL + Redis hosted on a free/low-cost tier suitable for early-stage load (specific provider to be chosen — see Open Decisions in `TASKS.md`).
- Client: if web-first, hosted as a static/SSR app on a free-tier hosting platform; if mobile, distributed via app stores with backend hosted separately.
- No dedicated media/CDN infra required in MVP since no audio files are stored server-side.

---

## 7. Explicitly Out of Architecture Scope (per free-tier constraint)

- No WebRTC/live-call infrastructure (live tutoring/exchange — deferred per `PLAN.md`)
- No dedicated speech-analysis microservice or trained phoneme model
- No audio storage/CDN pipeline
- No third-party paid moderation service (Phase 3 moderation is a basic in-house filter)

---

## 8. Open Architecture Questions (feed into `TASKS.md` Section 1)

- Timezone handling for streak reset and quota reset (UTC vs. user-local)
- Whether learning-path/lesson cache is keyed at (language, level, unit) granularity or needs per-user variation sooner than expected
- Hosting provider choice for backend/DB/Redis within free-tier limits
