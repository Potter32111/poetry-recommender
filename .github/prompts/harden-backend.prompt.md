---
description: "Harden backend: ML model preloading, error handling, recommendations timeout fix, audio validation."
mode: "agent"
agent: "backend-harden"
---

## Task: Harden Backend — Error Handling and Reliability

### 1. Preload ML Model on Startup

In `backend/app/main.py` lifespan, load the sentence-transformers model so the first request doesn't timeout:
```python
from app.services.ml import ml_service
# In lifespan:
await ml_service.ensure_loaded()  # Add this method to ml.py
```
In `backend/app/services/ml.py`, add `ensure_loaded()` that calls `load_model()` with a log message.

### 2. Fix Recommendations Timeout

In `backend/app/api/recommendations.py`, the real-time `parser.search_and_parse(mood)` can take 30+ seconds and block the response. Fix:
- Wrap in `asyncio.wait_for(..., timeout=10.0)`
- If timeout, log warning and continue with local DB results
- This keeps the fallback working while not blocking users

### 3. Add Error Handling to Voice Evaluator

In `backend/app/services/voice_evaluator.py`:
- Wrap FFmpeg subprocess in try/except with a clear error message
- Add max file size check (reject >10MB audio)
- Handle Vosk model not found with `HTTPException(503, "Voice recognition temporarily unavailable")`

### 4. Add Error Handling to Recommendations

In `backend/app/api/recommendations.py`:
- Wrap `ml_service.generate_embedding()` in try/except
- If ml_service fails, fall through to random fallback (already exists, just needs the guard)
- Log the error but don't crash

### 5. Validate Audio Upload

In `backend/app/api/memorization.py` `check_voice` endpoint:
- Check `audio.content_type` starts with `"audio/"` or is `"application/octet-stream"` (Telegram sends this)
- Check file size: `audio_bytes = await audio.read()` then `if len(audio_bytes) > 10 * 1024 * 1024: raise HTTPException(413)`
- Return clear error for invalid input

### 6. Smart Poem Text Truncation

In `bot/app/handlers/start.py` where poem text is displayed:
- Current: `text[:3500]` — can cut mid-word or mid-line
- Fix: truncate at last `\n` before 3500 chars, add "..." indicator

### Verification

```bash
cd backend && ruff check app tests
```
