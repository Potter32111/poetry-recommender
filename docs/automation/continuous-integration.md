# Continuous Integration

## CI Pipeline (GitHub Actions)
- **File**: [.github/workflows/ci.yml](file:///.github/workflows/ci.yml)
- **Status**: [![CI](https://github.com/Potter32111/poetry-recommender/actions/workflows/ci.yml/badge.svg)](https://github.com/Potter32111/poetry-recommender/actions)

## Jobs and Tools

### 🧹 Linting
- **Tool**: `ruff`
- **Purpose**: Ensures code style consistency and catches obvious errors.

### 🔍 Static Analysis
- **Tool**: `mypy`
- **Purpose**: Verifies type hints to prevent runtime type errors.

### 🧪 Automated Testing
- **Tool**: `pytest`
- **Purpose**: Runs all unit and integration tests.
- **Coverage**: `pytest-cov` generates reports uploaded as artifacts.

### 🐳 Build Check
- **Tool**: `docker-compose`
- **Purpose**: Verifies that the containers build successfully in a clean environment.

## Continuous Deployment (Stub)
- **Status**: Manual deployment to VPS via Docker.
- **Planned**: Automated CD using GitHub Actions and SSH.
