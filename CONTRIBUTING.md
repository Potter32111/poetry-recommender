# Contributing Guide — Poetry Recommender

## Development Setup

```bash
# 1. Clone
git clone https://github.com/Potter32111/poetry-recommender.git
cd poetry-recommender

# 2. Copy env
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

# 3. Build and run
docker-compose up -d --build

# 4. Seed database
docker-compose exec backend python -m app.seed.seed_poems

# 5. Verify
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/poems/count
```

---

## Git Workflow (GitHub Flow)

### Branch Naming
```
feature/<short-description>   # New functionality
fix/<short-description>       # Bug fix
docs/<short-description>      # Documentation only
refactor/<short-description>  # Code refactoring
```

### Commit Messages (Conventional Commits)
```
feat: add stanza-by-stanza learning mode
fix: resolve double-prefixed API routes
docs: add architecture guide
refactor: unify Base class in database.py
test: add SM-2 algorithm unit tests
chore: update dependencies
```

### Pull Request Process
1. Create a branch from `main`
2. Make changes, commit with conventional messages
3. Push and create PR
4. PR title must reference the issue: `feat: add voice recitation (#12)`
5. At least one team member must review
6. All CI checks must pass
7. Merge via **squash merge**

---

## Code Style

### Python
- **Formatter/Linter**: `ruff` (config in `pyproject.toml`)
- **Type checking**: `mypy --strict`
- Target: Python 3.11+
- Use `async/await` everywhere in FastAPI handlers and services

### Key Conventions
- f-strings only for user-facing messages; use `%s` in `logger.*()` calls
- No `print()` in production code — use `logging`
- No mutable default arguments in function signatures
- Always type-hint function signatures

---

## Secrets Management

| Secret | Storage | Access |
|--------|---------|--------|
| `DB_PASSWORD` | `.env` file (gitignored) | docker-compose env substitution |
| `TELEGRAM_BOT_TOKEN` | `.env` file (gitignored) | bot container env |
| `GOOGLE_API_KEY` | `.env` file (gitignored) | backend container env |

### Rules
- **Never** commit secrets to the repository
- `.env` is in `.gitignore`
- `.env.example` contains placeholder values
- In CI/CD: use repository secrets (GitHub Actions / GitLab CI variables)
- No hardcoded credentials in Python files

---

## Testing

### Unit Tests
Location: `backend/tests/unit/`
```bash
docker-compose exec backend pytest tests/unit/ -v
```

### Integration Tests
Location: `backend/tests/integration/`
```bash
docker-compose exec backend pytest tests/integration/ -v
```

### Running All Tests
```bash
docker-compose exec backend pytest --cov=app -v
```

### What to Test
| Component | Test Type | Priority |
|-----------|-----------|----------|
| SM-2 algorithm | Unit | 🔴 Critical |
| Voice text comparison | Unit | 🔴 Critical |
| API endpoints | Integration | 🔴 Critical |
| Recommendation engine | Unit | 🟡 High |
| Poem parser | Unit | 🟡 High |
| Bot handlers | Integration | 🟢 Medium |

---

## Updating Guidelines

The files `ARCHITECTURE.md`, `CONTRIBUTING.md`, `.cursorrules`, and `AI_INSTRUCTIONS.md` are **living documents**. 
If new architectural patterns emerge, or the customer requests changes that alter the workflow, **update these documents immediately**. Consistency is key. Furthermore, the AI assistant is strictly instructed to automatically `git commit` and `git push` logic upon completing tasks to keep the repository safe.

---

## Adding Features Checklist

- [ ] Create/update DB model in `backend/app/models/`
- [ ] Add model to `models/__init__.py`
- [ ] Create Pydantic schemas in `backend/app/schemas/`
- [ ] Implement business logic in `backend/app/services/`
- [ ] Create API routes in `backend/app/api/`
- [ ] Register route in `backend/app/api/router.py`
- [ ] Add API client method in `bot/app/services/api_client.py`
- [ ] Create bot handler in `bot/app/handlers/`
- [ ] Write tests
- [ ] Update README if user-facing
