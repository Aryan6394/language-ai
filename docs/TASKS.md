# LinguaAI — TASKS.md

Derived from `PLAN.md`. Organized by phase, plus cross-cutting workstreams.
No implementation detail here — planning/backlog only.

---

## 0. Plan Fixes (do first — resolve inconsistencies in PLAN.md)

- [x] Reword Section 3 "Speaking Practice" — removed "phoneme-level tips," replaced with word/sentence-level accuracy (text-diff), to match the Free-Tier Constraints in Section 4a.
- [x] Updated Section 5 "Tech Stack" — removed phoneme-comparison pronunciation scoring entirely (not achievable on free tier, not planned at all).
- [ ] Decide: is "Listening comprehension exercises" in or out of Phase 2? Add back explicitly (achievable free, using LLM-generated text + browser TTS as the "audio") or note as cut, with reasoning.
- [ ] Add a short "Assumptions" note to PLAN.md (target user, launch region, expected user volume) — affects free-tier quota planning.

---

## 1. Foundational Decisions (blocking — needed before design/build starts)

- [ ] Confirm target platform: mobile app / web app / both
- [ ] Pick initial launch language(s) and native/base language(s) supported
- [ ] Decide placement test vs. pure self-report for level assignment
- [ ] Choose LLM provider + confirm free-tier quota limits (requests/day, tokens/request)
- [ ] Choose STT/TTS approach (confirm Web Speech API browser/language coverage is sufficient)
- [ ] Choose dictionary/translation API and confirm free-tier coverage for target languages
- [ ] Decide monetization model (free / freemium / subscription) — affects quota design
- [ ] Decide data residency / privacy posture (where user data & audio are stored, retention period)

---

## 2. Design & UX

- [ ] Wireframe: onboarding flow (language + level selection, optional placement check)
- [ ] Wireframe: home/daily practice screen (streak, points, today's lesson, review queue)
- [ ] Wireframe: word list screen (add word, view meaning/pronunciation, search/filter)
- [ ] Wireframe: speaking exercise screen (record, playback, feedback display)
- [ ] Wireframe: reading exercise screen
- [ ] Wireframe: progress dashboard
- [ ] Wireframe: settings screen (notification prefs, daily goal, edit/delete word, account deletion)
- [ ] Wireframe: guest mode entry point / signup prompt
- [ ] Define visual identity (tone: motivating but not punitive — per differentiators)
- [ ] Accessibility pass: screen-reader labels, caption/text fallback for TTS audio, font scaling

---

## 3. Phase 1 — MVP Backlog

**Accounts & Access**
- [ ] Sign up / login / password reset
- [ ] Guest mode (try core flow without account)
- [ ] Account deletion / data export request flow

**Onboarding & Learning Path**
- [ ] Language & level selection
- [ ] Optional placement check (if decided in Section 1)
- [ ] AI-generated learning path (units → lessons) per language/level

**Practice Loop**
- [ ] Reading exercises (passage + comprehension questions)
- [ ] Speaking exercises (record → transcribe → text-diff accuracy feedback)
- [ ] Daily streak tracking + reset logic
- [ ] Points system (define full list of point-earning actions)
- [ ] Progress dashboard (lessons completed, words learned, accuracy trend)

**Vocabulary**
- [ ] "Add word" flow (manual entry)
- [ ] Auto-fetch pronunciation (TTS), meaning, example sentence, part of speech
- [ ] Personal word list view
- [ ] Search/filter/tag within word list
- [ ] Edit/delete word entries

**Reliability & Limits**
- [ ] Graceful UX when daily LLM/API quota is exceeded (message + fallback, not silent failure)
- [ ] Handle mic permission denied / unsupported browser for speech features
- [ ] Offline/low-connectivity fallback behavior (at least a clear error state)

**Cross-cutting for MVP**
- [ ] Basic analytics event list (signup, lesson complete, word added, streak break, quota hit)
- [ ] Privacy/consent notice for audio recording, shown before first speaking exercise
- [ ] In-app feedback/bug report mechanism (even a simple form/email link)

---

## 4. Phase 2 — Engagement & Personalization Backlog

- [ ] Spaced repetition scheduling for vocabulary review
- [ ] Adaptive difficulty logic based on error/performance patterns
- [ ] Conversation roleplay practice (LLM-driven, capped turns/day)
- [ ] "Explain my mistake" on-demand grammar explanation
- [ ] Content import: paste-your-own text → generate vocab/exercises
- [ ] CEFR-mapped proficiency scoring (A1–C2) layered on exercise data
- [ ] Notifications/reminders (streak protection) — with opt-out and non-guilt-tripping copy
- [ ] Achievements/badges
- [ ] Settings: daily goal customization, notification preferences
- [ ] Support for a second target language per user (if not already in MVP)
- [ ] Decide & implement: listening comprehension exercises (resolve Task 0 item)

---

## 5. Phase 3 — Community Backlog

- [ ] Leaderboard/ranking (points-based, own backend)
- [ ] Shared/public word lists between users
- [ ] Content moderation plan + basic filtering for public word lists/profiles
- [ ] Async challenges (e.g., "7-day streak sprint")
- [ ] Public profile pages (stats, achievements)
- [ ] Reporting/blocking mechanism for community content

---

## 6. Cross-Cutting Workstreams (span all phases)

**QA & Testing**
- [ ] Define test plan for speech recognition accuracy across devices/browsers/accents
- [ ] Define test plan for LLM-generated content quality (accuracy, appropriateness, difficulty calibration)
- [ ] Define regression testing approach for streak/points logic (date edge cases, timezones)

**Legal & Compliance**
- [ ] Privacy policy covering audio recording storage/use
- [ ] Terms of service
- [ ] Confirm compliance needs if minors may use the app (e.g., COPPA-style considerations)
- [ ] Data retention/deletion policy

**Infra & Ops**
- [ ] Rate-limiting design for LLM calls (per-user daily caps)
- [ ] Monitoring/alerting for free-tier quota usage (avoid hard outages when limits hit)
- [ ] Backup strategy for user data (word lists, progress)

**Analytics**
- [ ] Finalize analytics event taxonomy (full list, not just MVP subset)
- [ ] Retention/drop-off dashboards (streak breaks, lesson abandonment)

---

## 7. Open Decisions Carried Over from PLAN.md

- [ ] Which languages to support at launch
- [ ] Placement test vs. self-report
- [ ] Native app vs. cross-platform vs. web-first
- [ ] Monetization model
