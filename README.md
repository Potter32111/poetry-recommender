# 📚 Poetry: A Conversational Recommender System

A Telegram bot that recommends classic poems and helps users memorize them through spaced repetition. Supports English and Russian poetry.

[**Try the Bot**](https://t.me/poetry_recommender_bot) · [**API Docs**](http://localhost:8000/docs)

---

## Goals & Description

The goal of this project is to help users **discover, learn, and memorize classic poetry** through an engaging Telegram bot. The system uses **spaced repetition (SM-2 algorithm)** to schedule optimal review times and maximize long-term retention.

### Key Features
- 📖 Recommend poems based on language preference
- 🧠 SM-2 spaced repetition for memorization tracking
- 🎤 **Voice recitation check** — recite a poem, get automatic accuracy scoring
- 🔄 Daily review reminders for poems due
- 📊 Progress dashboard (new / learning / reviewing / memorized)
- 🎯 Score-based recall rating (0–5) or automatic voice evaluation
- 🇬🇧🇷🇺 Classic poems in English and Russian
- 🔇 Fully offline STT (Vosk) — no external API keys needed

## Usage

### Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and set language preference |
| `/recommend` | Get a new poem recommendation |
| `/review` | Review poems due today |
| `/progress` | View memorization statistics |
| `/help` | Show available commands |

### API Endpoints

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/` | Create or get user |
| GET | `/users/{telegram_id}` | Get user profile |
| PATCH | `/users/{telegram_id}` | Update preferences |
| GET | `/poems/` | List poems (filter by language, author) |
| GET | `/poems/{id}` | Get poem details |
| POST | `/memorization/recommend/{telegram_id}` | Get recommendation |
| POST | `/memorization/review/{telegram_id}/{poem_id}` | Submit review score |
| POST | `/memorization/check-voice/{telegram_id}/{poem_id}` | Voice recitation check |
| GET | `/memorization/progress/{telegram_id}` | Get stats |
| GET | `/memorization/due/{telegram_id}` | Get due reviews |

Full interactive docs available at: `http://localhost:8000/docs`

## Installation & Deployment

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Step-by-Step Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Potter32111/poetry-recommender.git
   cd poetry-recommender
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your tokens:**
   ```env
   DB_PASSWORD=your_secure_password
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   GOOGLE_API_KEY=your_google_api_key  # optional
   ```

4. **Build and start services:**
   ```bash
   docker-compose up -d --build
   ```

5. **Seed the database with poems:**
   ```bash
   docker-compose exec backend python -m app.seed.seed_poems
   ```

6. **Verify:**
   ```bash
   # Check health
   curl http://localhost:8000/health
   # → {"status":"ok"}

   # Check poems loaded
   curl http://localhost:8000/api/v1/poems/count
   # → {"count":16}
   ```

7. **Open Telegram** and message your bot with `/start`!

### Stopping
```bash
docker-compose down        # Stop services
docker-compose down -v     # Stop and remove data
```

## Architecture

### Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python 3.12) |
| Bot | aiogram 3.x (Python) |
| Database | PostgreSQL 16 |
| Containerization | Docker + Docker Compose |
| Memorization | SM-2 Spaced Repetition |
| Speech-to-Text | Vosk (offline, ~85MB models) |
| Audio Processing | ffmpeg |

### Static View

```
┌─────────────────┐     HTTP      ┌─────────────────┐     SQL       ┌───────────┐
│  Telegram Bot    │──────────────▶│  FastAPI Backend │──────────────▶│ PostgreSQL│
│  (aiogram 3.x)  │◀──────────────│  /api/v1/*       │◀──────────────│           │
│  + FSM (voice)  │               │  + Vosk STT      │               └───────────┘
└─────────────────┘               └─────────────────┘
        │                                │
        │ Telegram API                   │ (in-process, offline)
        ▼                                ▼
   ┌──────────┐                   ┌──────────────┐
   │ Telegram  │                   │ Vosk Models  │
   │ Bot API   │                   │ (RU + EN)    │
   └──────────┘                   └──────────────┘
```

## License

[MIT](LICENSE)
