---
description: "Extract get_user_lang() to shared util, fix duplicate code between start.py and voice.py."
mode: "agent"
agent: "bot-polish"
---

## Task: Deduplicate Bot Code

### 1. Extract `get_user_lang()` to Shared Module

`get_user_lang()` is copy-pasted in both `bot/app/handlers/start.py` and `bot/app/handlers/voice.py`.

Create `bot/app/utils.py`:
```python
"""Shared utility functions for bot handlers."""
import logging
from app.services.api_client import api

logger = logging.getLogger(__name__)

async def get_user_lang(telegram_id: int) -> str:
    """Get user's UI language from backend, defaulting to 'ru'."""
    try:
        user = await api.get_user(telegram_id)
        return user.get("ui_language", "ru")
    except Exception:
        return "ru"
```

Then in both `start.py` and `voice.py`:
- Remove local `get_user_lang()` definition
- Add `from app.utils import get_user_lang`

### 2. Verify No Circular Imports

After change, verify the bot starts without import errors.

### Verification

```bash
cd bot && python -c "from app.utils import get_user_lang; print('OK')"
```
