# LinguaAI — DATABASE.md

Full database design, organized around the seven core domains: **Users, Languages, Lessons, Vocabulary, Achievements, XP, Progress**. Described as entities/fields only — no SQL or backend code. Primary store: PostgreSQL, with a small amount of ephemeral state in Redis (noted at the end). Scoped to free-tier hosting per `PLAN.md`.

---

## 1. Users

### 1.1 `users`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| email | string, unique, nullable | null for guest accounts |
| password_hash | string, nullable | null for guest/social-only accounts |
| display_name | string | |
| native_language_id | UUID (FK → languages.id) | user's base/native language |
| is_guest | boolean | true until account is claimed with email |
| account_status | enum (active, deleted, suspended) | |
| created_at | timestamp | |
| last_active_at | timestamp | drives streak calculation |

**Indexes:** unique on `email`; index on `last_active_at`.

### 1.2 `user_settings`
| Field | Type | Notes |
|---|---|---|
| user_id | UUID (PK, FK → users.id) | |
| streak_reminders_enabled | boolean | |
| daily_goal_xp | integer, nullable | user-set daily goal |
| preferred_reminder_time | time, nullable | |
| ui_language_id | UUID (FK → languages.id) | app interface language, separate from native/target |

---

## 2. Languages

### 2.1 `languages`
Master reference list — every language the platform supports, either as a target-to-learn or as a native/UI language.

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| code | string, unique | e.g. "es", "hi", "fr" (ISO 639-1) |
| name | string | e.g. "Spanish" |
| native_name | string | e.g. "Español" |
| is_learnable | boolean | can be selected as a target language |
| is_ui_supported | boolean | app interface available in this language |
| is_active | boolean | admin toggle, e.g. to soft-disable a language |

### 2.2 `user_languages` (join table — languages a user is actively learning)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| language_id | UUID (FK → languages.id) | target language |
| level | enum (beginner, intermediate, expert) | may change over time via reassessment |
| status | enum (active, paused, completed) | supports learning multiple languages |
| started_at | timestamp | |
| cefr_estimate | string, nullable | e.g. "A2", derived from progress data |

**Indexes:** unique on `(user_id, language_id)`; index on `user_id`.

---

## 3. Lessons

### 3.1 `units`
Groups lessons into a sequence within a language + level.

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| language_id | UUID (FK → languages.id) | |
| level | enum (beginner, intermediate, expert) | |
| title | string | |
| sequence_order | integer | |
| cefr_target | string, nullable | e.g. "A1" |

### 3.2 `lessons`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| unit_id | UUID (FK → units.id) | |
| type | enum (reading, speaking, listening, conversation) | |
| title | string | |
| content | JSON/text | passage, target sentences, questions |
| generated_by | enum (llm, cached, seed) | tracks whether this consumed an LLM call |
| cache_key | string, nullable | language+level+unit+type signature, reused across users to save LLM calls |
| sequence_order | integer | |
| xp_reward | integer | base XP for completing this lesson |
| created_at | timestamp | |

**Indexes:** index on `cache_key`; index on `unit_id`.

### 3.3 `lesson_attempts`
A user's completion/attempt record for a lesson (distinct from raw progress tracking, see Section 7).

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| lesson_id | UUID (FK → lessons.id) | |
| transcribed_text | text, nullable | speaking attempts — text from client-side STT, never raw audio |
| target_text | text, nullable | what the user was meant to say/answer |
| accuracy_score | numeric (0–100), nullable | text-diff based |
| is_correct | boolean, nullable | for reading/quiz-style attempts |
| xp_awarded | integer | actual XP granted for this attempt (may be less than lesson.xp_reward on partial success) |
| attempted_at | timestamp | |

**Indexes:** index on `(user_id, attempted_at)`; index on `lesson_id`.

---

## 4. Vocabulary

### 4.1 `vocabulary_entries`
A user's personal word list.

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| language_id | UUID (FK → languages.id) | |
| word | string | as entered by the user |
| meaning | text | pulled from `vocabulary_cache` when available |
| example_sentence | text | |
| part_of_speech | string, nullable | |
| ipa | string, nullable | phonetic spelling |
| tags | string[] | user-defined categorization |
| date_added | timestamp | |
| srs_stage | integer | spaced-repetition stage |
| srs_due_at | timestamp, nullable | next review date |

**Indexes:** index on `(user_id, language_id)`; index on `srs_due_at`.

### 4.2 `vocabulary_cache` (shared, cost-saving cache)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| word | string | normalized/lowercased |
| language_id | UUID (FK → languages.id) | |
| meaning | text | |
| example_sentence | text | |
| part_of_speech | string, nullable | |
| ipa | string, nullable | |
| source | enum (dictionary_api, llm) | |
| fetched_at | timestamp | |

**Indexes:** unique on `(word, language_id)` — ensures the same word/language pair is never looked up twice across all users, keeping free-tier dictionary API usage low.

### 4.3 `vocabulary_review_log`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| vocabulary_entry_id | UUID (FK → vocabulary_entries.id) | |
| user_id | UUID (FK → users.id) | |
| was_correct | boolean | |
| reviewed_at | timestamp | |

---

## 5. Achievements

### 5.1 `achievements`
Master definition list (admin-managed, not per-user).

| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| code | string, unique | e.g. "streak_7", "words_100" |
| title | string | e.g. "One Week Strong" |
| description | text | |
| icon_key | string | reference to a static icon asset |
| criteria_type | enum (streak_days, words_added, lessons_completed, xp_total, accuracy_threshold) | |
| criteria_value | integer | e.g. 7 (days), 100 (words) |
| language_scoped | boolean | true if earned per-language rather than globally |

### 5.2 `user_achievements`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| achievement_id | UUID (FK → achievements.id) | |
| language_id | UUID (FK → languages.id), nullable | set if `language_scoped` |
| unlocked_at | timestamp | |

**Indexes:** unique on `(user_id, achievement_id, language_id)` — prevents duplicate unlocks.

---

## 6. XP

XP is tracked as an append-only event log plus denormalized rollups for fast reads, mirroring how points/streaks were designed in the original plan — renamed here to XP terminology per this schema's scope.

### 6.1 `xp_log`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| language_id | UUID (FK → languages.id), nullable | null for language-agnostic XP events (e.g. daily goal met across any language) |
| action_type | enum (lesson_complete, word_added, word_reviewed_correct, speaking_excellent, daily_goal_met, streak_milestone, achievement_unlocked) | |
| xp_amount | integer | |
| related_entity_id | UUID, nullable | e.g. lesson_id, vocabulary_entry_id, achievement_id |
| created_at | timestamp | |

**Indexes:** index on `(user_id, created_at)`; index on `(user_id, language_id)`.

### 6.2 Denormalized XP rollups (for fast dashboard/leaderboard reads)
Rather than a separate table, these are maintained as fields on existing entities:
- `users.total_xp` — sum across all languages, all time
- `user_languages.xp_in_language` — XP earned within that specific language

Both are updated whenever a row is written to `xp_log` (kept in sync at write time rather than computed live, to keep dashboard reads cheap on free-tier compute).

---

## 7. Progress

Progress is distinct from raw attempt/XP logs — it's the summarized state used to answer "where is this user in their learning journey," which powers the dashboard and CEFR estimate.

### 7.1 `user_progress` (one row per user + language)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| language_id | UUID (FK → languages.id) | |
| lessons_completed_count | integer | denormalized |
| words_learned_count | integer | denormalized, count of `vocabulary_entries` past a "learned" SRS stage |
| current_unit_id | UUID (FK → units.id), nullable | where the user currently is in the path |
| accuracy_rolling_avg | numeric | rolling average of `lesson_attempts.accuracy_score` |
| streak_count | integer | current consecutive-day streak |
| streak_last_incremented_date | date | prevents double-increment same day |
| updated_at | timestamp | |

**Indexes:** unique on `(user_id, language_id)`.

### 7.2 `unit_progress` (per-unit completion state, for path/map UI)
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| unit_id | UUID (FK → units.id) | |
| status | enum (locked, in_progress, completed) | |
| completed_at | timestamp, nullable | |

**Indexes:** unique on `(user_id, unit_id)`.

---

## 8. Redis-Resident State (not in PostgreSQL)

| Key pattern | Purpose | TTL / Reset |
|---|---|---|
| `session:{token}` | Auth session lookup | Session expiry |
| `quota:{user_id}:{date}` | Daily LLM/API call counter | Resets daily |
| `quota:global:{date}` | Account-wide daily call counter | Resets daily |
| `leaderboard:{language_id}:{period}` | Sorted set of user_id → XP (Phase 3) | Reset each period |
| `lesson_cache:{cache_key}` | Fast-path cache of generated lesson content | Long TTL |

---

## 9. Relationships Summary

```
languages 1───∞ user_languages ∞───1 users
languages 1───∞ units 1───∞ lessons 1───∞ lesson_attempts ∞───1 users
users 1───∞ vocabulary_entries ∞───1 languages
vocabulary_entries ∞───1 vocabulary_cache (via word+language match, not a hard FK)
vocabulary_entries 1───∞ vocabulary_review_log
achievements 1───∞ user_achievements ∞───1 users
users 1───∞ xp_log
users 1───1 user_progress (per language, via language_id)
units 1───∞ unit_progress ∞───1 users
users 1───1 user_settings
```

---

## 10. Free-Tier Sizing Notes

- `vocabulary_cache` and `lessons.cache_key` are the two biggest levers for staying within free-tier API quotas — both ensure repeated requests across users hit the cache instead of a fresh external (LLM/dictionary) call.
- No table stores raw audio or binary blobs — speech-to-text happens client-side (see `ARCHITECTURE.md`), so only transcribed text is ever persisted.
- `xp_log` and `lesson_attempts` are append-only and will grow fastest at scale; an archiving/rollup job is worth revisiting in `TASKS.md` once real usage data exists, but isn't needed at MVP volume.

---

## 11. Open Questions (feed into `TASKS.md`)

- Should `lesson_attempts.transcribed_text` be purged after N days for privacy minimization, even though it's text-only?
- Is XP awarded identically across all languages, or should harder/less-common languages award bonus XP?
- Should `user_progress.accuracy_rolling_avg` be a simple moving average or time-decayed (recent attempts weighted more)?
