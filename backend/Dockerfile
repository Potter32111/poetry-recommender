FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (only runtime needs like ffmpeg for audio, omitting gcc to save massive amounts of RAM)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpeg wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Models are downloaded if not present
COPY download_models.py /app/
RUN python /app/download_models.py

# Set pip env to avoid memory issues and timeouts
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

# Create requirements for explicit caching
# 1. Install heavy ML dependencies first (CPU only to save 2GB of bandwidth and memory)
# We omit torchvision as it is not strictly required by sentence-transformers and causes compile/OOM issues
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install sentence-transformers vosk

# 2. Install web and db dependencies
RUN pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic pydantic-settings httpx python-multipart pgvector beautifulsoup4 aiohttp apscheduler googlesearch-python

COPY pyproject.toml .
# Attempt to install project metadata if needed, but don't fail if we don't have src yet
RUN pip install -e . || true


COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
