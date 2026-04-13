---
description: "Fix bot UX: add back buttons, loading states, notification time picker, poem difficulty display, and consistent navigation."
mode: "agent"
agent: "bot-polish"
---

## Task: Fix Bot UX — Navigation, Loading, and Display

### 1. Back Buttons in All Flows

Add "⬅️ Back" or "🏠 Home" buttons:
- **Mood input flow**: After `msg_ask_mood`, add cancel button
- **URL input flow**: After `msg_ask_url`, add cancel button
- **Settings submenus** (language pickers): add "⬅️ Back to Settings"
- **After poem display**: add "🏠 Main Menu" alongside poem actions

### 2. Loading States

Add `⏳` processing messages for operations >1 second:
- Before recommendation fetch (mood-based search can be slow)
- Before leaderboard load
- Delete the loading message after result arrives

### 3. Notification Time Picker

Implement the settings → notification time flow (currently "Feature in development!"):
- Show inline keyboard with time options: 08:00, 10:00, 12:00, 14:00, 18:00, 20:00, 22:00
- On selection, call `api.update_user(telegram_id, notification_time=selected_time)`
- Confirm: "✅ Notifications set to {time}"
- Callback data: `f"notif_{hour}"`

### 4. Poem Display Improvements

When showing a poem to the user, include metadata:
- `⭐` for difficulty (e.g., ⭐⭐⭐ for difficulty 3.0)
- `📏 {lines_count} lines` 
- `🏷️ {themes}` if themes exist
- `📅 {era}` if era exists

Show first 8 lines as preview with "Show full text ▼" button.

### 5. State Cleanup Safety

Wrap all FSM flows with `try/finally` to ensure `state.clear()` runs even on error:
```python
try:
    # ... handler logic
finally:
    await state.clear()
```
Apply to: `handle_voice()`, `handle_mood_input()`, `handle_url_input()`

### 6. Consistent Keyboard Language

Audit all places `poem_action_keyboard()` is called — ensure `lang` is always passed, never relying on default `"ru"`.
