---
applyTo: "**/tests/**"
description: "Test conventions for pytest-asyncio, fixture patterns, and test database setup. Use when writing or editing test files."
---

# Test Conventions

## Framework

- **pytest-asyncio** with `asyncio_mode = "auto"` — all async tests discovered automatically
- Test runner: `cd backend && pytest --cov=app tests/`

## Database Fixtures (`conftest.py`)

- Separate test engine with `NullPool` — no connection pooling in tests
- `TEST_DATABASE_URL` defaults to `poetry_bot_test` locally, overridden by `DATABASE_URL` env var in CI
- `setup_db` fixture (autouse, function-scoped): creates all tables before each test, drops after
- pgvector extension created before table setup: `CREATE EXTENSION IF NOT EXISTS vector`
- `async_session` fixture yields an `AsyncSession` for direct DB operations
- `client` fixture provides `AsyncClient` with `ASGITransport` — overrides `get_db` dependency

## Writing Tests

```python
@pytest.mark.asyncio
async def test_something(client: AsyncClient):
    response = await client.post("/api/v1/users/", json={"telegram_id": 12345})
    assert response.status_code == 201

async def test_db_operation(async_session: AsyncSession):
    result = await async_session.execute(select(Model))
    assert result.scalars().all() == []
```

## CI Environment

- PostgreSQL service: `pgvector/pgvector:pg16` with test credentials
- Vosk models dir: `VOSK_MODELS_DIR=/tmp/models_vosk`
- Additional CI deps: `aiosqlite`, `pytest-mock`
