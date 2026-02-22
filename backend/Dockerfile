FROM python:3.12-slim

WORKDIR /app

# Install ffmpeg for audio conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Download Vosk models
RUN mkdir -p /app/models_vosk && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip -O /tmp/ru.zip && \
    unzip -q /tmp/ru.zip -d /app/models_vosk && \
    rm /tmp/ru.zip && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -O /tmp/en.zip && \
    unzip -q /tmp/en.zip -d /app/models_vosk && \
    rm /tmp/en.zip

COPY pyproject.toml .
RUN pip install --no-cache-dir . 2>/dev/null || \
    pip install --no-cache-dir fastapi uvicorn sqlalchemy asyncpg alembic pydantic pydantic-settings httpx vosk python-multipart

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
