FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpeg wget unzip gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Models are downloaded beforehand and copied to the container
COPY models_vosk /app/models_vosk

COPY pyproject.toml .
RUN pip install --no-cache-dir . 2>/dev/null || \
    pip install --no-cache-dir fastapi uvicorn sqlalchemy asyncpg alembic pydantic pydantic-settings httpx vosk python-multipart pgvector sentence-transformers beautifulsoup4 aiohttp apscheduler apscheduler


COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
