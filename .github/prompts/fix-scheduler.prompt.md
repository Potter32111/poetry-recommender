---
description: "Fix scheduler notifications: localize messages, use t() for translation, respect user's notification_time and ui_language."
mode: "agent"
agent: "bot-polish"
---

## Task: Fix Scheduler Notifications

### Current Problem

`bot/app/scheduler.py` sends hardcoded English notification regardless of user's language. It also doesn't include personalized content.

### Fix

1. Read `bot/app/scheduler.py` fully
2. In `process_daily_notifications()`:
   - Fetch due users from `GET /api/v1/memorization/due/all` (returns `telegram_id`, `ui_language`, `notification_time`)
   - For each user, check current hour matches their `notification_time`
   - Use `t("push_review", user["ui_language"], count=..., streak=...)` for the message
   - Add inline keyboard with "🔄 Start Review" button

3. Add a "Poem of the Day" feature:
   - Once daily (at a separate schedule), pick a random poem
   - Send to users who haven't reviewed today
   - Use `t("push_poem_of_day", lang, author=poem.author, title=poem.title)`
   - Add "📖 Read Poem" inline button

### Translation Keys Already Exist

Check `bot/app/translations.py` — keys `push_review`, `push_poem_of_day`, `btn_start_review`, `btn_read_poem` are already defined in both languages.

### Verification

Read the final file and verify no hardcoded strings remain.
