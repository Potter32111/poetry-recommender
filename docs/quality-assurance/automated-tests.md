# Automated Tests

## Testing Framework
- **Pytest**: Used for both unit and integration tests.
- **Httpx**: Used for testing FastAPI endpoints asynchronously.

## Test Types and Locations

### 🧪 Unit Tests
- **Location**: `backend/tests/`
- **Scope**: Individual components like the SM-2 algorithm, voice evaluation logic, and utility functions.
- **Example**: `backend/tests/test_spaced_rep.py`

### 🔗 Integration Tests
- **Location**: `backend/tests/`
- **Scope**: Testing the interaction between the FastAPI app, the database, and the external services (Vosk STT).
- **Example**: `backend/tests/test_api.py`

## Running Tests
```bash
docker-compose exec backend pytest
```

## Quality Assurance Tools
- **Ruff**: Fast Python linter and code formatter.
- **Mypy**: Static type checker for Python.
- **Vosk**: Offline Speech-to-Text for voice recitation verification.
