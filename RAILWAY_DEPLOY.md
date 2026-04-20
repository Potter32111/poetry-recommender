# Poetry Recommender — Railway Deployment Guide

## Architecture

Railway runs 3 services from this monorepo:

| Service | Dockerfile | Port | Notes |
|---------|-----------|------|-------|
| **db** | Railway Postgres Plugin | 5432 | Add via Railway dashboard |
| **backend** | `backend/Dockerfile` | 8000 | Heavy: torch, vosk, sentence-transformers |
| **bot** | `bot/Dockerfile` | — | No exposed port, long-running process |

## Step-by-Step Setup

### 1. Create Railway Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init
```

### 2. Add PostgreSQL with pgvector
In the Railway dashboard:
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. The `DATABASE_URL` variable will be auto-injected
3. **Important:** pgvector extension is NOT pre-installed on Railway Postgres.
   After the database is created, connect and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 3. Deploy Backend Service
In the Railway dashboard:
1. Click **"+ New"** → **"GitHub Repo"** → Select this repo
2. In **Settings**:
   - **Root Directory**: `backend`
   - **Builder**: `Dockerfile`
   - **Port**: `8000`
3. Add environment variables:
   - `DATABASE_URL` → Reference the Postgres plugin variable: `${{Postgres.DATABASE_URL}}`
     **BUT** replace `postgresql://` with `postgresql+asyncpg://` (Railway provides standard format, our app needs asyncpg)
   - `GOOGLE_API_KEY` → your key (optional)
   - `PORT` → `8000`

### 4. Deploy Bot Service
1. Click **"+ New"** → **"GitHub Repo"** → Select this repo (again)
2. In **Settings**:
   - **Root Directory**: `bot`
   - **Builder**: `Dockerfile`
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN` → your bot token from @BotFather
   - `BACKEND_URL` → Reference the backend: `${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000`
     (use the internal Railway URL for service-to-service communication)

### 5. Fix DATABASE_URL format
Railway's Postgres plugin provides URL in standard format:
```
postgresql://user:pass@host:port/dbname
```
Our app needs asyncpg format:
```
postgresql+asyncpg://user:pass@host:port/dbname
```

Set this in the backend's variables:
```
DATABASE_URL=postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
```

### 6. Verify Deployment
- Backend health: `https://<backend-url>.railway.app/health`
- Backend docs: `https://<backend-url>.railway.app/docs`
- Bot: send `/start` to your Telegram bot

## Environment Variables Summary

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `DATABASE_URL` | backend | Yes | PostgreSQL connection (asyncpg format) |
| `TELEGRAM_BOT_TOKEN` | bot | Yes | From @BotFather |
| `BACKEND_URL` | bot | Yes | Internal Railway URL of backend |
| `GOOGLE_API_KEY` | backend | No | For LLM features |
| `PORT` | backend | Yes | `8000` |

## ⚠️ Important Notes

1. **Memory:** The backend uses ~1.5GB RAM (torch + sentence-transformers). Railway's free tier might not suffice — use the **Hobby plan** ($5/month) or **Trial credits**.
2. **Build time:** First build takes 5–10 minutes due to downloading Vosk models and PyTorch.
3. **pgvector:** Must be manually enabled via SQL after Postgres is provisioned.
4. **Bot networking:** The bot uses `network_mode: host` in docker-compose. On Railway, use `BACKEND_URL` with the private Railway domain instead.
