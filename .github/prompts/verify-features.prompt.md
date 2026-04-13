---
description: "End-to-end feature test: walk through all 7 required features and verify each one works correctly."
mode: "agent"
agent: "swp-explore"
---

## Task: Verify All 7 Required Features (Read-Only Audit)

Walk through the code for each of the 7 required features and verify the full chain from bot handler → API client → backend endpoint → service → DB works correctly. Flag any broken links.

### Features to verify

1. **Elicit user preferences by chatting**
   - Bot: /start → language selection → mood input flow
   - API: POST /api/v1/users/ (create), PATCH /api/v1/users/ (update prefs)
   - Verify: FSM states work, preferences saved to DB

2. **Check user history and learner profile**
   - Bot: profile button → shows stats
   - API: GET /api/v1/memorization/progress/{telegram_id}
   - Verify: Response includes all needed fields

3. **Choose appropriate items**
   - Bot: mood search → recommendations
   - API: GET /api/v1/recommendations/?telegram_id=...&mood=...
   - Verify: Vector search works, fallback to random exists

4. **Check memorization**
   - Bot: voice message → transcription → scoring
   - API: POST /api/v1/memorization/check-voice/{telegram_id}/{poem_id}
   - Verify: FSM sets state, audio uploaded, voice_evaluator processes it

5. **Recommend an item**
   - Bot: "New poems" → surprise/mood/URL
   - API: POST /api/v1/memorization/recommend/{telegram_id}
   - Verify: Due poems prioritized, new poems served

6. **Record the outcome of recommendation**
   - Bot: score buttons (0-5) → review recorded
   - API: POST /api/v1/memorization/review/{telegram_id}/{poem_id}
   - Verify: SM-2 calculated, XP awarded, history appended

7. **Keep track of memorization and help to revise**
   - Bot: review button → due poems shown
   - API: GET /api/v1/memorization/due/{telegram_id}
   - Scheduler: notifications for due reviews
   - Verify: SM-2 scheduling, streak tracking, notifications

### For each feature report

- ✅ Working correctly, or
- ⚠️ Works but has issue: [describe]
- ❌ Broken: [describe exact failure point]
