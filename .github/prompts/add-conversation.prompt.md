---
description: "Add conversational features to the bot: /help, unknown message handling, encouragement, tips, poem-of-the-day greeting."
mode: "agent"
agent: "bot-polish"
---

## Task: Add Conversational Polish to the Bot

The bot feels robotic. Add personality and helpful conversational features.

### 1. `/help` Command

Add a `/help` handler in `bot/app/handlers/start.py` that shows:
```
📚 Poetry Bot — Your poetry companion!

Commands:
/start — Main menu
/review — Review due poems
/recommend — Get a new poem
/progress — Your stats
/leaderboard — Top learners
/help — This message

Tips:
🎤 Send a voice message to check your recitation
🎭 Try different moods for varied recommendations
🔥 Review daily to keep your streak!
```
Translate to both RU and EN.

### 2. Unknown Message Handler

Add a fallback handler (register LAST) that catches any text message not handled by other handlers:
```python
@router.message()
async def handle_unknown(message: Message, state: FSMContext):
```
Respond with helpful suggestions based on what they typed:
- If contains poem-like text (multiple lines with \n): suggest "Looks like a poem! Try /recommend to find it."
- If contains "?": answer with "Try /help for available commands"
- Otherwise: friendly "I work best with voice messages and menu buttons! Try /help 😊"

### 3. Welcome Messages

When user first registers (`/start` flow), add a warm welcome:
- RU: "Привет! 👋 Я помогу тебе учить стихи наизусть. Начнём?"
- EN: "Hi there! 👋 I'll help you memorize classic poems. Shall we begin?"

### 4. Encouragement After Reviews

After a self-review score submission, add motivational messages:
- Score 5: "🌟 Perfect recall! You're a poetry master!"
- Score 3-4: "💪 Great progress! Keep it up!"
- Score 0-2: "📖 That's OK! Spaced repetition will help. Try again tomorrow!"
Translate to both languages.

### 5. Empty State Messages

When user has no poems due for review: show a friendly message suggesting they learn a new poem, not just "No poems due."

### Add all new keys to `bot/app/translations.py` in both `"ru"` and `"en"`.
