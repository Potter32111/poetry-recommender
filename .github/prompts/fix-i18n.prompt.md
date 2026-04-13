---
description: "Fix all hardcoded Russian/English strings in bot handlers to use t() translations. Add missing translation keys."
mode: "agent"
agent: "bot-polish"
---

## Task: Fix Bot i18n — All Strings Through Translations

Audit and fix ALL hardcoded strings in the bot. Every user-facing string must go through `t(key, lang)`.

### Files to fix

1. **`bot/app/handlers/voice.py`** — `_format_voice_result()` has hardcoded Russian labels ("Результат проверки", "Пропущено", etc.). Pass `lang` parameter and use `t()`.

2. **`bot/app/handlers/voice.py`** — Error messages hardcoded in Russian ("❌ Ошибка: стих не выбран", "⏳ Анализирую ваше чтение...", "❌ Не удалось обработать")

3. **`bot/app/handlers/start.py`** — Settings "Feature in development!" not translated

4. **`bot/app/handlers/start.py`** — Generic "❌ Error" messages not translated

5. **`bot/app/scheduler.py`** — Notification message hardcoded in English. Use `t("push_review", lang, count=..., streak=...)`

6. **`bot/app/keyboards/menus.py`** — Verify all keyboard builders receive and use `lang` parameter consistently

### Translation keys to add to `bot/app/translations.py`

Add these keys to BOTH `"ru"` and `"en"`:
- `msg_voice_result` — "🎤 Voice check result:"
- `msg_voice_accuracy` — "Accuracy: {percent}%"
- `msg_voice_missed` — "Missed lines:"
- `msg_voice_feedback` — feedback text
- `msg_processing` — "⏳ Analyzing your recitation..."
- `msg_voice_error` — "❌ Voice processing failed. Try again."
- `msg_no_poem_selected` — "No poem selected. Try /review."
- `msg_feature_wip` — "🚧 Feature coming soon!"
- `msg_error_generic` — "❌ Something went wrong. Try again."
- `msg_error_review` — "❌ Failed to save review."
- `msg_error_recommend` — "❌ Failed to load recommendation."

### Verification

After changes, grep for any remaining hardcoded Cyrillic or English user-facing strings:
```bash
grep -n '"[❌⏳🎤]' bot/app/handlers/*.py bot/app/scheduler.py
```

Run lint: `cd backend && ruff check app tests`
