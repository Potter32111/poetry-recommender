# Project Guidelines

## Overview

Poetry Recommender System — a Telegram bot for learning and memorizing classic poems (English + Russian) via spaced repetition (SM-2) and offline voice recognition (Vosk).

**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), asyncpg, PostgreSQL 16 + pgvector, aiogram 3.x, Vosk, sentence-transformers.

## Architecture

Three Docker Compose services: `db` (pgvector/pgvector:pg16), `backend` (FastAPI), `bot` (aiogram).

See [ARCHITECTURE.md](../ARCHITECTURE.md) for full component diagrams and structural rules.

### Critical Rules (prevent known regressions)

1. **Single `Base` class** — defined only in `backend/app/database.py`. All ORM models import `Base` from there. Never define `DeclarativeBase` in model files.
2. **No double-prefixing** — `/api/v1` is applied once in `backend/app/main.py`. The aggregator router (`api/router.py`) uses `safe_include()` without `prefix=`. Sub-routers define their own prefix (e.g., `APIRouter(prefix="/poems")`).
3. **Schema-model alignment** — Pydantic response schemas must exactly match SQLAlchemy model columns. If a schema needs `themes` (list) or `era` (str), the model must have matching `JSONB`/`String` columns.
4. **SQLAlchemy 2.0 async style** — Use `await session.execute(select(Model))` → `.scalars().all()`. Use `Poem.id.notin_(...)`, not `not_in`.
5. **No debug globals** — No global dicts to pass data between requests. Use `logger.info()` instead of `print()`.

## Build & Test

```bash
# Start all services
docker compose up --build

# Run backend tests (needs running PostgreSQL)
cd backend && pip install -e ".[dev]" && pytest --cov=app tests/

# Lint
cd backend && ruff check app tests

# Type check
cd backend && mypy app
```

- **CI pipeline**: `.github/workflows/ci.yml` — lint (ruff), test (pytest + pgvector), build (Docker)
- **Migrations**: `cd backend && alembic upgrade head` (Alembic is configured)
- **Test DB**: Uses `poetry_bot_test` database locally, overridden via `DATABASE_URL` in CI

## Conventions

- **Commits**: Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.). See [CONTRIBUTING.md](../CONTRIBUTING.md).
- **Python style**: Ruff with `line-length = 100`, target `py311`. Mypy strict mode.
- **Async everywhere**: All DB operations, API endpoints, and bot handlers are async.
- **Pydantic V2**: All schemas use Pydantic V2 with `model_config = ConfigDict(from_attributes=True)`.

## Key Directories

| Path | Purpose |
|------|---------|
| `backend/app/api/` | FastAPI routers |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/app/schemas/` | Pydantic request/response schemas |
| `backend/app/services/` | Business logic (spaced_rep, recommender, voice_evaluator, parser) |
| `backend/app/seed/` | DB seeding scripts |
| `backend/tests/` | Pytest async tests |
| `bot/app/handlers/` | Telegram command and message handlers |
| `bot/app/keyboards/` | Inline/reply keyboard builders |
| `bot/app/states/` | FSM states for conversation flows |

## Documentation

- [README.md](../README.md) — Deployment, features, troubleshooting
- [ARCHITECTURE.md](../ARCHITECTURE.md) — System design, structural rules, step-by-step guides for adding models/handlers
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Git workflow, code style, testing guidelines
- [TASKS_AND_ASSIGNMENTS.md](../TASKS_AND_ASSIGNMENTS.md) — Implementation audit and gap analysis
- [docs/](../docs/) — Formal architecture views, CI/CD docs, QA specs, Kanban process
