# Architecture Guide — Poetry Recommender

> **Read this before writing any code.** These conventions prevent the import conflicts,
> double-prefixed routes, and schema–model mismatches that plagued the project.

---

## System Overview

```
┌─────────────────┐     HTTP/JSON   ┌─────────────────┐      SQL       ┌───────────────┐
│  Telegram Bot    │───────────────▶│  FastAPI Backend │──────────────▶│  PostgreSQL 16 │
│  (aiogram 3.x)  │◀───────────────│  /api/v1/*       │◀──────────────│  + pgvector    │
│  + FSM (voice)  │                │  + Vosk STT      │               └───────────────┘
└─────────────────┘                └─────────────────┘
        │                                  │
        │ Telegram API                     │ Offline STT
        ▼                                  ▼
   ┌──────────┐                   ┌──────────────┐
   │ Telegram  │                   │ Vosk Models  │
   │ Bot API   │                   │ (RU + EN)    │
   └──────────┘                   └──────────────┘
```

Three Docker containers: `db`, `backend`, `bot`.

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, lifespan, includes router with /api/v1 prefix
│   ├── config.py         # pydantic-settings for env vars
│   ├── database.py       # ⚠️ Base class, engine, session — SINGLE SOURCE OF TRUTH
│   ├── models/           # SQLAlchemy ORM models (one file per table)
│   │   ├── __init__.py   # Re-exports all models so Base.metadata sees them
│   │   ├── user.py
│   │   ├── poem.py
│   │   └── memorization.py
│   ├── schemas/          # Pydantic request/response schemas (mirror models)
│   ├── api/              # Route files — each defines its own prefix
│   │   ├── router.py     # Aggregates sub-routers — NO extra prefix here
│   │   ├── poems.py      # prefix="/poems"
│   │   ├── users.py      # prefix="/users"
│   │   ├── memorization.py
│   │   └── recommendations.py
│   ├── services/         # Business logic (no HTTP concerns)
│   │   ├── spaced_rep.py     # SM-2 algorithm
│   │   ├── recommender.py    # Poem selection logic
│   │   ├── voice_evaluator.py # Vosk STT + text comparison
│   │   ├── ml.py             # Sentence-transformer embeddings
│   │   └── parser.py         # Web poem scraper
│   └── seed/             # Database seed scripts
│       ├── poems_data.py
│       └── seed_poems.py
├── models_vosk/          # Downloaded Vosk language models
├── Dockerfile
└── pyproject.toml

bot/
├── app/
│   ├── main.py           # Bot entry point (aiogram Dispatcher)
│   ├── config.py         # Bot settings
│   ├── handlers/         # Telegram message/callback handlers
│   │   ├── start.py      # Commands: /start, /recommend, /review, /progress
│   │   └── voice.py      # Voice message FSM flow
│   ├── keyboards/        # Inline keyboard builders
│   └── services/
│       └── api_client.py # HTTP client to backend API
├── Dockerfile
└── pyproject.toml
```

---

## Critical Rules

### 1. Base Class — Single Source of Truth

```python
# ✅ ALWAYS import from database.py
from app.database import Base

# ❌ NEVER define Base in a model file
class Base(DeclarativeBase): ...  # WRONG
```

`Base` lives in `backend/app/database.py`. All models import it from there.

### 2. Route Prefixes — No Duplication

The `/api/v1` prefix is applied once in `main.py`:
```python
app.include_router(router, prefix="/api/v1")
```

Each sub-router declares its own prefix (e.g. `prefix="/poems"`).
The aggregator `router.py` does **NOT** add any prefix.

Final URL: `/api/v1/poems/`, `/api/v1/users/`, etc.

### 3. Schema–Model Alignment

Every field in a Pydantic `*Response` schema must exist as a column on the corresponding SQLAlchemy model.
If you add a field to a schema, add the column to the model first.

### 4. Adding a New Model

1. Create `backend/app/models/new_thing.py` with `from app.database import Base`
2. Add the class to `models/__init__.py`
3. Create corresponding schemas in `schemas/new_thing.py`
4. Create API routes in `api/new_thing.py` with `router = APIRouter(prefix="/new-things", ...)`
5. Register in `api/router.py`: `safe_include("new_thing", tags=["new_thing"])`

### 5. Adding a New Bot Handler

1. Create `bot/app/handlers/new_handler.py` with `router = Router()`
2. Import and register in `bot/app/main.py`: `dp.include_router(new_router)`
3. Add any needed API methods to `bot/app/services/api_client.py`

---

## Data Model

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│    users     │       │    poems     │       │  memorizations   │
├──────────────┤       ├──────────────┤       ├──────────────────┤
│ id (UUID PK) │       │ id (UUID PK) │       │ id (UUID PK)     │
│ telegram_id  │◄──┐   │ title        │◄──┐   │ user_id (FK)     │
│ username     │   │   │ author       │   │   │ poem_id (FK)     │
│ first_name   │   │   │ text         │   │   │ status           │
│ language_pref│   │   │ language     │   │   │ ease_factor      │
│ preferences  │   └───│ difficulty   │   └───│ interval_days    │
│ created_at   │       │ lines_count  │       │ repetitions      │
│ updated_at   │       │ themes (JSON)│       │ next_review_at   │
└──────────────┘       │ era          │       │ last_reviewed_at │
                       │ embedding    │       │ score_history    │
                       └──────────────┘       │ recommended_at   │
                                              └──────────────────┘
```

### SM-2 Status Flow
`new` → `learning` → `reviewing` → `memorized`

---

## API Versioning

All endpoints live under `/api/v1/`. The version prefix is added once in `main.py`.
The `/health` endpoint is outside the version prefix (at root level).

## Environment Variables

| Variable | Used By | Required |
|----------|---------|----------|
| `DATABASE_URL` | backend | Yes |
| `GOOGLE_API_KEY` | backend | No (for future LLM features) |
| `TELEGRAM_BOT_TOKEN` | bot | Yes |
| `BACKEND_URL` | bot | Yes (default: `http://backend:8000`) |
| `DB_PASSWORD` | docker-compose | Yes |
