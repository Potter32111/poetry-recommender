---
description: "Fix two orphan callbacks: notification time picker doesn't save, finder 'Any author' chip does nothing."
mode: "agent"
agent: "bot-polish"
---

## Task: Fix Two Orphan Callback Buttons

A static analysis of `bot/app/keyboards/menus.py` vs handlers found two `callback_data` values that have **no matching handler** — pressing those buttons does nothing.

---

### Bug 1: Notification time picker — no handler for `notif_HHMM`

`notification_time_keyboard()` in `menus.py` generates buttons with `callback_data=f"notif_{time.replace(':', '')}"` (e.g., `notif_0800`, `notif_1000`, etc.). But `start.py` has no `@router.callback_query(F.data.startswith("notif_"))` handler.

**What to do:**
- Add `cb_notif_time` callback handler in `start.py` that:
  - Parses the HHMM from the callback data (`callback.data.replace("notif_", "")` → "0800" → format as "08:00").
  - Calls `api.update_user(telegram_id, notification_time=formatted_time)`.
  - Edits the message to show a confirmation using `t("msg_notif_saved", lang, time=...)` (add this translation key in both languages if missing).
  - Returns to settings menu via `settings_keyboard(lang)`.
  - Calls `callback.answer()`.
- Use the same null-guard pattern as other callback handlers.

---

### Bug 2: Finder "Any author" chip — `finder_author_any` not handled

`finder_author_keyboard()` in `menus.py` (around line 344) creates a button `callback_data="finder_author_any"`. The handler `cb_finder_author` matches `F.data.startswith("finder_author_")` so it does receive the callback — BUT the handler logic likely treats the suffix (`"any"`) as the literal author name and stores `author="any"` in state, which then gets passed to the backend as `?author=any` and filters out everything.

**What to do:**
- Read `cb_finder_author` in `start.py` (around line 770).
- Add a special case at the top: if the suffix is `"any"`, treat it as `author=None` (skip the filter), same effect as `finder_skip` for the author step.
- After setting `author=None`, transition to the confirmation state and show the summary, just like the regular path.

---

### Verification

1. After tapping a notification time chip in Settings → 🔔 Notification Time, the user sees a confirmation and the time is persisted (verify by re-opening settings — backend should return the new value).
2. In the poem finder, tapping "🎲 Any" on the author step proceeds to the confirmation screen with no author filter.
3. No new orphan callbacks introduced. Run a mental check: `grep callback_data` in `menus.py` and ensure each prefix has a handler.
