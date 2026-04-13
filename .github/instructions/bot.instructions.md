---
applyTo: "bot/**"
description: "Bot conventions for aiogram 3.x handlers, FSM states, keyboards, and backend API communication. Use when editing or creating bot Python files."
---

# Bot Conventions

## Handlers (`app/handlers/`)

- Each file creates a `Router()` and registers handlers with decorators
- Voice router registered first (FSM priority over general text handlers)
- All handlers are async; use `await` for all I/O
- Null guard at top of every handler: `if not callback.from_user or not callback.message: return`
- Callback handlers must end with `await callback.answer()` to dismiss loading state
- Private helpers prefixed with `_` (e.g., `_send_recommendation()`)
- Use `logger.info()`/`logger.error()` — never `print()`

## FSM States

- Defined as `StatesGroup` subclasses directly in handler files
- Enter: `await state.set_state(StateClass.state_name)`
- Store data: `await state.update_data(key=value)`
- Read data: `data = await state.get_data()`
- Exit: `await state.clear()`
- Global cancel handler: `@router.callback_query(F.data == "cancel")`

## Keyboards (`app/keyboards/menus.py`)

- Each keyboard is a function returning `InlineKeyboardMarkup` or `ReplyKeyboardMarkup`
- Accept `lang` parameter for i18n
- Callback data uses prefix + ID pattern: `f"recite_{poem_id}"`, `f"score_{poem_id}_{score}"`

## Backend Communication (`app/services/api_client.py`)

- Singleton `APIClient` with `httpx.AsyncClient`
- Base URL from `bot_settings.backend_url` (default: `http://backend:8000`)
- All endpoints under `/api/v1/` — do not duplicate prefix
- Voice uploads: `files={"audio": ("voice.ogg", audio_bytes, "audio/ogg")}` with `timeout=60.0`
- Standard requests: `timeout=30.0`
- Always `resp.raise_for_status()`; callers handle exceptions

## i18n (`app/translations.py`)

- All UI strings in centralized `texts` dict with `"ru"` / `"en"` keys
- Access via `t(key, lang, **format_args)` helper
- Keys use snake_case with prefixes: `btn_`, `msg_`, `score_`
