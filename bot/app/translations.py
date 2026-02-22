"""Translations dictionary for UI i18n."""

# bot/app/translations.py

texts = {
    "ru": {
        # Menus
        "btn_new": "📖 Новые стихи",
        "btn_review": "🔄 Повторение",
        "btn_profile": "🏆 Мой профиль",
        "btn_settings": "⚙️ Настройки",
        "btn_cancel": "❌ Отмена",
        
        # New Poem Flow
        "btn_surprise": "🎲 Случайный",
        "btn_mood": "🎭 По настроению",
        "btn_url": "🌐 Из ссылки",
        "msg_new_poem": "Как будем искать новый стих?",
        "msg_ask_mood": "🧠 По какому настроению или теме нужен стих? Напиши пару слов (например: 'Осень и грусть'):",
        "msg_ask_url": "🔗 Отправь ссылку на страницу со стихом (например stihi.ru):",
        "msg_analyzing": "🔄 Ищу подходящий стих...",
        "msg_not_found": "😔 Пока нет подходящих стихов. Попробуй позже!",
        
        # Action Flow
        "btn_recite": "🎤 Прочитать вслух",
        "btn_flashcard": "📝 Вспомнить",
        "btn_skip": "⏭ Пропустить",
        "msg_recite_prompt": "🎤 Запиши голосовое сообщение со стихом наизусть (удерживая микрофон 🎙). Я проверю точность!",
        "msg_flashcard_prompt": "📝 Постарайся рассказать стих по памяти, а затем честно оцени свой результат:",
        
        # Review Scores
        "score_0": "0 😵 Забыл всё",
        "score_1": "1 😰 Плохо",
        "score_2": "2 😕 Сложно",
        "score_3": "3 🤔 Нормально",
        "score_4": "4 😊 Хорошо",
        "score_5": "5 🌟 Идеально",
        
        # Profile
        "msg_profile": (
            "👤 **Профиль**\n\n"
            "🌟 Уровень: {level} (Опыт: {xp} / {next_level_xp})\n"
            "🔥 Ударный режим: {streak} дней подряд!\n\n"
            "📊 **Твои успехи:**\n"
            "📖 Изучаю: {learning}\n"
            "🔄 На повторении: {reviewing}\n"
            "✨ Выучено: {memorized}\n"
            "📋 Всего стихов: {total}\n"
            "⏰ Ждут повторения сегодня: {due}"
        ),
        
        # Settings
        "msg_settings": "⚙️ Настройки\nВыбери, что хочешь изменить:",
        "btn_ui_lang": "🇺🇳 Язык интерфейса",
        "btn_poem_lang": "📚 Язык стихов",
        "btn_notif_time": "⏰ Время уведомлений",
        
        # Notifications
        "push_review": "🔔 Привет! У тебя {count} стихотворения ждут повторения, чтобы не сгорел твой ударный режим (🔥 {streak} дней)!",
        "push_poem_of_day": "🌟 Стих дня: {author} - {title}. Хочешь выучить?",
        "btn_start_review": "🔄 Начать повторение",
        "btn_read_poem": "📖 Посмотреть стих",
        
        # Gamification events
        "msg_level_up": "🎉 **ПОЗДРАВЛЯЕМ! Новый {level} уровень!** 🎉",
        "msg_xp_gain": "✨ Получено +{xp} XP!"
    },
    
    "en": {
        # Menus
        "btn_new": "📖 New Poems",
        "btn_review": "🔄 Review Due",
        "btn_profile": "🏆 My Profile",
        "btn_settings": "⚙️ Settings",
        "btn_cancel": "❌ Cancel",
        
        # New Poem Flow
        "btn_surprise": "🎲 Surprise me",
        "btn_mood": "🎭 By mood",
        "btn_url": "🌐 From URL",
        "msg_new_poem": "How would you like to find a new poem?",
        "msg_ask_mood": "🧠 What mood or topic are you looking for? Write a few words:",
        "msg_ask_url": "🔗 Send a link to a poem:",
        "msg_analyzing": "🔄 Searching for the best match...",
        "msg_not_found": "😔 No poems found right now. Try again later!",
        
        # Action Flow
        "btn_recite": "🎤 Recite",
        "btn_flashcard": "📝 Self-check",
        "btn_skip": "⏭ Skip",
        "msg_recite_prompt": "🎤 Record a voice message reciting the poem from memory. I will grade it!",
        "msg_flashcard_prompt": "📝 Try to recite the poem from memory, then rate your recall:",
        
        # Review Scores
        "score_0": "0 😵 Blank",
        "score_1": "1 😰 Wrong",
        "score_2": "2 😕 Hard",
        "score_3": "3 🤔 OK",
        "score_4": "4 😊 Good",
        "score_5": "5 🌟 Perfect",
        
        # Profile
        "msg_profile": (
            "👤 **Profile**\n\n"
            "🌟 Level: {level} (XP: {xp} / {next_level_xp})\n"
            "🔥 Daily Streak: {streak} days!\n\n"
            "📊 **Your Progress:**\n"
            "📖 Learning: {learning}\n"
            "🔄 Reviewing: {reviewing}\n"
            "✨ Memorized: {memorized}\n"
            "📋 Total poems: {total}\n"
            "⏰ Due for review: {due}"
        ),
        
        # Settings
        "msg_settings": "⚙️ Settings\nWhat would you like to change?",
        "btn_ui_lang": "🇺🇳 UI Language",
        "btn_poem_lang": "📚 Poetry Language",
        "btn_notif_time": "⏰ Notification Time",
        
        # Notifications
        "push_review": "🔔 Hi! You have {count} poems due for review! Keep your streak alive (🔥 {streak} days)!",
        "push_poem_of_day": "🌟 Poem of the Day: {author} - {title}. Want to learn it?",
        "btn_start_review": "🔄 Start Review",
        "btn_read_poem": "📖 Read Poem",
        
        # Gamification events
        "msg_level_up": "🎉 **CONGRATULATIONS! You reached Level {level}!** 🎉",
        "msg_xp_gain": "✨ Gained +{xp} XP!"
    }
}

def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Get a translated string by key. Defaults to russian if key or lang missing."""
    lang_dict = texts.get(lang, texts["ru"])
    translation = lang_dict.get(key, texts["ru"].get(key, key))
    if kwargs:
        return translation.format(**kwargs)
    return translation
