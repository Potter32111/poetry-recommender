---
applyTo: "backend/**"
description: "Backend conventions for FastAPI, SQLAlchemy, and service patterns. Use when editing or creating backend Python files."
---

# Backend Conventions

## Models (`app/models/`)

- Import `Base` from `app.database` — never define `DeclarativeBase` locally
- Register every new model in `app/models/__init__.py` (import with `# noqa: F401`)
- UUID primary keys: `id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`
- Use `Mapped[type]` annotations (SQLAlchemy 2.0 style), not legacy `Column()`
- JSONB for list/dict fields: `themes: Mapped[list] = mapped_column(JSONB, default=list)`
- Timestamps: `server_default=func.now()` for created_at, `onupdate=func.now()` for updated_at
- Relationships: use `lazy="selectin"` to avoid N+1 queries
- pgvector: guarded by `HAS_VECTOR` flag — falls back to `Text` if library unavailable

## Routers (`app/api/`)

- Each router file defines its own prefix: `router = APIRouter(prefix="/poems")`
- Aggregator (`api/router.py`) uses `safe_include()` **without** `prefix=`
- `/api/v1` applied once in `main.py` — never add it elsewhere
- DB dependency: `db: AsyncSession = Depends(get_db)`
- Single-row queries: `scalar_one_or_none()` then raise `HTTPException(404)` if None
- Partial updates: `model_dump(exclude_unset=True)` → `setattr()` loop
- Status code 201 for created resources

## Schemas (`app/schemas/`)

- Pydantic V2: `model_config = ConfigDict(from_attributes=True)`
- Use `str | None = None` (3.10+ union syntax), `list[str]` (not `List[str]`)
- Separate schemas: `XxxCreate` (input), `XxxResponse` (full), `XxxBrief` (lightweight)
- Response schemas must exactly match model columns (schema-model alignment rule)

## Services (`app/services/`)

- Module-level async functions, not classes (exception: `PoemParser` uses class for session lifecycle)
- Receive `db: AsyncSession` as parameter — never create sessions inside services
- Return structured data via `@dataclass` when multiple values needed
- Use `logger = logging.getLogger(__name__)`, never `print()`

## Query Patterns

```python
result = await db.execute(select(Model).where(...))
items = list(result.scalars().all())

# NOT: not_in() — use notin_()
query = select(Poem).where(Poem.id.notin_(exclude_ids))
```
