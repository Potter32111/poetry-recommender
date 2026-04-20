"""Translations dictionary for UI i18n."""

# bot/app/translations.py

texts = {
    "ru": {
        # Menus
        "btn_new": "📖 Новые стихи",
        "btn_review": "🔄 Повторение",
        "btn_profile": "🏆 Мой профиль",
        "btn_settings": "⚙️ Настройки",
        "btn_favorites": "⭐ Избранное",
        "btn_history": "📜 История",
        "btn_leaderboard_short": "🏅 Лидеры",
        "btn_help_short": "❓ Помощь",
        "btn_cancel": "❌ Отмена",
        "btn_back": "⬅️ Назад",
        
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
            "🌟 Уровень: {level}\n"
            "{xp_bar} {xp}/{next_level_xp} XP\n"
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
        "msg_xp_gain": "✨ Получено +{xp} XP!",

        # Voice check
        "msg_voice_result": "🎤 **Результат проверки:**",
        "msg_voice_missed": "❌ **Пропущено:**",
        "msg_voice_more_missed": "_...и ещё {count} строк(и)_",
        "msg_voice_status": "{emoji} Статус: {status}",
        "msg_voice_next_interval": "📅 Следующий повтор через: {days} дн.",
        "msg_voice_tip": "📋 **Рекомендация:** {tip}",
        "msg_voice_next_repeat": "🔄 Попробуйте ещё раз",
        "msg_voice_next_read": "📖 Перечитайте стих",
        "msg_voice_next_memorized": "🌟 Стих выучен!",
        "msg_voice_word_summary": "📊 {correct}/{total} слов совпало",
        "msg_voice_close_word": "💬 _{said}_ → _{expected}_",
        "msg_processing": "⏳ Анализирую ваше чтение...",
        "msg_voice_error": "❌ Не удалось обработать голосовое сообщение. Попробуйте ещё раз.",
        "msg_no_poem_selected": "❌ Ошибка: стих не выбран. Попробуйте /review.",
        "msg_voice_not_text": "🎤 Отправьте **голосовое сообщение**, а не текст.\nНажмите и удерживайте кнопку микрофона 🎙️",
        "msg_voice_retry": "🎤 Попробуйте ещё раз! Запишите голосовое сообщение:",
        "msg_voice_load_error": "❌ Не удалось загрузить стих.",

        # Stanza mode
        "btn_stanza_mode": "📝 По строфам",
        "msg_stanza_header": "📖 Строфа {current}/{total}:",
        "msg_stanza_completed": "✅ Строфа {n} — выучена!",
        "msg_stanza_all_done": "🎉 Все строфы выучены! Стих теперь в твоей памяти!",
        "msg_stanza_progress": "Прогресс: {bar} ({done}/{total})",
        "btn_stanza_recite": "🎤 Рассказать строфу",
        "btn_stanza_type": "⌨️ Написать",
        "btn_stanza_next": "➡️ Следующая",
        "btn_stanza_know_all": "✅ Знаю всё",
        "btn_stanza_retry": "🔄 Ещё раз",
        "btn_stanza_show": "👀 Подсмотреть",
        "msg_stanza_fail": "❌ Точность: {accuracy}%. Попробуй ещё раз или подсмотри строфу.",
        "msg_stanza_success": "✅ Точность: {accuracy}%! Отлично!",
        "msg_stanza_recite_prompt": "🎤 Запиши голосовое сообщение со строфой наизусть:",
        "msg_stanza_type_prompt": "⌨️ Напиши строфу наизусть:",
        "msg_stanza_peek": "👀 Вот текст строфы:\n\n{text}",
        "msg_stanza_single": "📖 Этот стих состоит из одной строфы. Используй обычный режим.",

        # Errors & misc
        "msg_feature_wip": "🚧 Функция в разработке!",
        "msg_error_generic": "❌ Что-то пошло не так. Попробуйте ещё раз.",
        "msg_error_review": "❌ Не удалось сохранить результат повторения.",
        "msg_error_recommend": "❌ Не удалось загрузить рекомендацию.",
        "msg_no_due_reviews": "✅ Отлично! Нет стихов для повторения.",
        "msg_saved": "✅ Сохранено!",
        "msg_leaderboard_title": "🏆 **Таблица лидеров** 🏆",
        "msg_leaderboard_empty": "🏆 Таблица лидеров пока пуста.",
        "msg_leaderboard_error": "❌ Не удалось загрузить таблицу лидеров.",
        "msg_leaderboard_row": "{emoji} **{name}** — Ур. {level} ({xp} XP) 🔥{streak}",

        # Help
        "msg_help": (
            "📚 **Poetry Bot — Ваш поэтический помощник!**\n\n"
            "Команды:\n"
            "/start — Главное меню\n"
            "/review — Повторить стихи\n"
            "/recommend — Новый стих\n"
            "/progress — Ваша статистика\n"
            "/leaderboard — Таблица лидеров\n"
            "/settings — Настройки\n"
            "/help — Это сообщение\n\n"
            "Подсказки:\n"
            "🎤 Отправьте голосовое для проверки декламации\n"
            "🎭 Попробуйте разные настроения для рекомендаций\n"
            "🔥 Повторяйте каждый день, чтобы не терять прогресс!"
        ),

        # Welcome
        "msg_welcome": "Привет! 👋 Я помогу тебе учить стихи наизусть. Начнём?",
        "msg_welcome_back": (
            "👋 С возвращением, {name}!\n\n"
            "⏰ Ожидает повторения: {due}\n"
            "🔥 Ударный режим: {streak} дней"
        ),
        "msg_whats_next": "Что дальше?",
        "msg_voice_no_context": "🎤 Сначала выбери стих и нажми «🎤 Прочитать», а затем отправляй голосовое.",
        "btn_new_poem": "📖 Новый стих",

        # Encouragement after review
        "msg_encourage_perfect": "🌟 Идеальное повторение! Ты — мастер поэзии!",
        "msg_encourage_good": "💪 Отличный прогресс! Продолжай в том же духе!",
        "msg_encourage_low": "📖 Ничего страшного! Интервальное повторение поможет. Попробуй снова завтра!",

        # Friendly empty state
        "msg_no_due_friendly": "✅ Все стихи повторены! 🎉\nПопробуй выучить что-то новое — нажми «{btn_new}».",

        # Unknown message
        "msg_unknown_poem": "Похоже на стих! Попробуй /recommend, чтобы найти его.",
        "msg_unknown_question": "Попробуй /help, чтобы посмотреть доступные команды.",
        "msg_unknown_default": "Я лучше работаю с голосовыми сообщениями и кнопками меню! Попробуй /help 😊",

        # Recitation prompts & hints
        "msg_hints_penalty": "💡 Использовано подсказок: {count} (−{xp} XP)",
        "msg_type_prompt": "⌨️ Напиши стих по памяти:",
        "msg_type_not_voice": "Пожалуйста, напиши текст стиха, а не голосовое сообщение.",
        "msg_no_more_hints": "Подсказок больше нет.",
        "msg_hint_line": "💡 Подсказка: _{words}..._",
        "btn_hint": "💡 Подсказка",
        "btn_show_full": "📖 Показать весь стих",
        "btn_more_review": "🔄 Ещё повторения",
        "btn_main_menu": "🏠 Главное меню",

        # Profile sub-actions
        "btn_achievements": "🏅 Достижения",
        "btn_my_history": "📜 Моя история",
        "btn_my_favorites": "⭐ Моё избранное",
        "btn_my_stats": "📊 Моя статистика",
        "btn_back_to_menu": "🔙 В главное меню",

        # Settings — expanded
        "btn_notifications_toggle": "🔔 Уведомления",
        "btn_length_pref": "🎵 Длина стихов",
        "btn_reset_progress": "🗑 Сбросить прогресс",
        "msg_notifications_on": "🔔 Уведомления включены!",
        "msg_notifications_off": "🔕 Уведомления отключены.",
        "msg_notif_saved": "✅ Время уведомлений установлено: {time}",
        "msg_length_pref_title": "🎵 Предпочтительная длина стихов:",
        "btn_length_short": "Короткие",
        "btn_length_medium": "Средние",
        "btn_length_long": "Длинные",
        "btn_length_any": "Любые",
        "msg_length_saved": "✅ Предпочтение сохранено: {choice}",
        "msg_reset_confirm": "⚠️ Вы уверены? Это удалит весь прогресс, XP, уровень и ударный режим.",
        "btn_reset_yes": "🗑 Да, удалить всё",
        "btn_reset_no": "❌ Отмена",
        "msg_reset_done": "✅ Прогресс полностью сброшен.",

        # Help — interactive
        "msg_help_title": "❓ **Помощь**\nВыбери тему:",
        "btn_help_learn": "📖 Как учить стихи",
        "btn_help_voice": "🎤 Советы по голосу",
        "btn_help_xp": "🔥 Очки и ударный режим",
        "btn_help_contact": "💬 Контакт / Баг-репорт",
        "msg_help_learn": (
            "📖 **Как учить стихи**\n\n"
            "1. Нажми «📖 Новые стихи» для нового стиха\n"
            "2. Прочитай его несколько раз\n"
            "3. Используй «📝 По строфам» для пошагового запоминания\n"
            "4. Когда будешь готов — нажми «🎤 Прочитать вслух»\n"
            "5. Бот проверит точность и запланирует повторение\n"
            "6. Повторяй по расписанию — интервалы будут расти!"
        ),
        "msg_help_voice": (
            "🎤 **Советы по распознаванию голоса**\n\n"
            "• Говори чётко и не слишком быстро\n"
            "• Минимизируй фоновый шум\n"
            "• Держи телефон на расстоянии 15–20 см\n"
            "• Удерживай кнопку микрофона во время записи\n"
            "• Если распознавание плохое — попробуй «⌨️ Написать»"
        ),
        "msg_help_xp": (
            "🔥 **Очки опыта и ударный режим**\n\n"
            "• Каждое повторение даёт XP\n"
            "• Чем точнее — тем больше XP\n"
            "• Новый уровень каждые level×100 XP\n"
            "• Ударный режим — занимайся каждый день!\n"
            "• Пропуск дня обнулит серию"
        ),
        "msg_help_contact": (
            "💬 **Связь / Баг-репорт**\n\n"
            "Нашёл баг или есть идея?\n"
            "Напиши нам: @poetry\\_bot\\_support"
        ),
        "btn_help_back": "⬅️ К списку помощи",

        # Recommendation reasons
        "msg_rec_reason_mood": "По вашему настроению: {mood}",
        "msg_rec_reason_time": "Идеально для {season} {time_of_day}",
        "msg_rec_reason_author": "Вам нравится {author} — попробуйте это",
        "msg_rec_reason_discover": "Классика, достойная открытия",
        "season_winter": "зимы",
        "season_spring": "весны",
        "season_summer": "лета",
        "season_autumn": "осени",
        "time_morning": "утра",
        "time_afternoon": "дня",
        "time_evening": "вечера",
        "time_night": "ночи",

        # Poem Finder flow
        "msg_finder_mood": "🔍 Давай найдём идеальный стих. Какое настроение?",
        "msg_finder_length": "✅ Отлично: {mood}. Какой длины стих?",
        "msg_finder_era": "✅ Длина: {length}. Какая эпоха?",
        "msg_finder_author": "✅ Эпоха: {era}. Любимый автор?",
        "msg_finder_confirm": "🔍 Ищем: {summary}\n",
        "msg_finder_no_results": "😔 Ничего не нашлось с такими фильтрами. Попробуй изменить параметры.",
        "msg_finder_more": "Не то, что нужно?",
        "msg_finder_freetext": "✏️ Введи текстом:",
        "msg_finder_same_as_last": "🔁 Как в прошлый раз",
        "btn_finder_find": "🔍 Найти!",
        "btn_finder_restart": "🔄 Начать заново",
        "btn_finder_different": "🔄 Другие фильтры",
        "btn_finder_surprise": "🎲 Удиви меня",
        "btn_finder_freetext": "🆓 Свободный текст",
        "btn_finder_skip": "⏭ Пропустить",
        "btn_finder_search_author": "🔍 Найти по имени",
        # Finder mood chips
        "mood_sad": "😢 Грусть",
        "mood_love": "💖 Любовь",
        "mood_inspirational": "🌅 Вдохновение",
        "mood_reflective": "🌧 Размышление",
        "mood_joyful": "🎉 Радость",
        "mood_philosophical": "🤔 Философия",
        "mood_nature": "🌿 Природа",
        "mood_patriotic": "🔥 Патриотика",
        # Finder length chips
        "length_short": "📏 Короткий (≤12 строк)",
        "length_medium": "📐 Средний (13–30)",
        "length_long": "📜 Длинный (30+)",
        "length_any": "🎲 Любой",
        # Finder era chips
        "era_classic": "🕰 Классика (до 1900)",
        "era_silver_age": "✒️ Серебряный век (1900–1925)",
        "era_soviet": "📻 Советская (1925–1991)",
        "era_modern": "💻 Современная (1991+)",
        "era_any": "🎲 Любая",

        # Favorites
        "btn_fav_add": "⭐ В избранное",
        "btn_fav_remove": "💔 Убрать из избранного",
        "msg_fav_added": "⭐ Добавлено в избранное!",
        "msg_fav_removed": "💔 Убрано из избранного.",
        "msg_fav_empty": "У тебя пока нет избранных стихов. Нажми ⭐ на стихе, чтобы сохранить.",
        "msg_fav_title": "⭐ **Избранное** ({count})",

        # History
        "msg_hist_title": "📜 **История** ({count})",
        "msg_hist_empty": "Истории пока нет — начни учить свой первый стих!",
        "msg_hist_row": "{emoji} **{title}** — _{author}_ · {date}",
        "btn_hist_review": "🔄 Повторить",
        "btn_hist_read": "📖 Читать",
        "btn_hist_filter_all": "Все",
        "btn_hist_filter_learning": "📖 Учу",
        "btn_hist_filter_reviewing": "🔄 Повторяю",
        "btn_hist_filter_memorized": "🌟 Выучено",

        # Collections
        "btn_collections": "📚 Коллекции",
        "msg_collections_title": "📚 **Коллекции**",
        "msg_collection_intro": "{emoji} **{title}** — {count} стихов",

        # Pagination
        "btn_prev_page": "⬅️ Назад",
        "btn_next_page": "➡️ Далее",

        # Achievements
        "msg_badge_unlocked": "🎉 Новый значок!\n{emoji} **{title}** — {description}",
        "msg_achievements_title": "🏅 **Достижения**",
        "msg_badge_locked": "🔒 {title}",
        "msg_badge_unlocked_row": "{emoji} **{title}** — {description}\n    _{date}_",

        # Daily Challenge
        "msg_challenge_title": "🎯 **Ежедневное задание:**",
        "msg_challenge_progress": "🎯 {goal}: {progress}/{target}",
        "msg_challenge_completed": "🎉 Задание выполнено! +50 XP бонус!",
        "goal_review_n_poems": "Повторить {n} стихов",
        "goal_memorize_one_stanza": "Запомнить 1 строфу",
        "goal_voice_recite_one": "Прочитать вслух 1 стих",
        "goal_learn_new_poem": "Выучить новый стих",

        # Streak Freeze
        "msg_freeze_used": "🧊 Использована заморозка серии! Осталось: {n}",
        "msg_freeze_count": "🧊 Заморозки: {n}/3",

        # TTS
        "btn_listen": "🔊 Слушать",
        "msg_tts_generating": "🎵 Генерирую аудио...",
        "msg_tts_too_long": "❌ Стих слишком длинный для озвучки (>50 строк).",
        "msg_tts_error": "❌ Не удалось сгенерировать аудио.",

        # Celebration cascade
        "msg_celebration_xp": "✨ +{xp} XP",
        "msg_celebration_level": "🎉 Новый уровень! Теперь ты Уровень {level}",
        "msg_celebration_challenge": "🎯 Задание: {progress}/{target}",
        "msg_celebration_badge": "🏅 Новый значок: {title} {emoji}",
        "msg_celebration_freeze": "🧊 Заморозка серии использована! Осталось: {n}",
    },
    
    "en": {
        # Menus
        "btn_new": "📖 New Poems",
        "btn_review": "🔄 Review Due",
        "btn_profile": "🏆 My Profile",
        "btn_settings": "⚙️ Settings",
        "btn_favorites": "⭐ Favorites",
        "btn_history": "📜 History",
        "btn_leaderboard_short": "🏅 Leaders",
        "btn_help_short": "❓ Help",
        "btn_cancel": "❌ Cancel",
        "btn_back": "⬅️ Back",
        
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
            "🌟 Level: {level}\n"
            "{xp_bar} {xp}/{next_level_xp} XP\n"
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
        "msg_xp_gain": "✨ Gained +{xp} XP!",

        # Voice check
        "msg_voice_result": "🎤 **Voice check result:**",
        "msg_voice_missed": "❌ **Missed:**",
        "msg_voice_more_missed": "_...and {count} more line(s)_",
        "msg_voice_status": "{emoji} Status: {status}",
        "msg_voice_next_interval": "📅 Next review in: {days} day(s)",
        "msg_voice_tip": "📋 **Tip:** {tip}",
        "msg_voice_next_repeat": "🔄 Try again",
        "msg_voice_next_read": "📖 Re-read the poem",
        "msg_voice_next_memorized": "🌟 Poem memorized!",
        "msg_voice_word_summary": "📊 {correct}/{total} words matched",
        "msg_voice_close_word": "💬 _{said}_ → _{expected}_",
        "msg_processing": "⏳ Analyzing your recitation...",
        "msg_voice_error": "❌ Voice processing failed. Try again.",
        "msg_no_poem_selected": "❌ No poem selected. Try /review.",
        "msg_voice_not_text": "🎤 Send a **voice message**, not text.\nPress and hold the microphone button 🎙️",
        "msg_voice_retry": "🎤 Try again! Record a voice message:",
        "msg_voice_load_error": "❌ Could not load the poem.",

        # Stanza mode
        "btn_stanza_mode": "📝 By stanza",
        "msg_stanza_header": "📖 Stanza {current}/{total}:",
        "msg_stanza_completed": "✅ Stanza {n} — learned!",
        "msg_stanza_all_done": "🎉 All stanzas learned! The poem is now memorized!",
        "msg_stanza_progress": "Progress: {bar} ({done}/{total})",
        "btn_stanza_recite": "🎤 Recite stanza",
        "btn_stanza_type": "⌨️ Type it",
        "btn_stanza_next": "➡️ Next",
        "btn_stanza_know_all": "✅ I know it all",
        "btn_stanza_retry": "🔄 Try again",
        "btn_stanza_show": "👀 Peek",
        "msg_stanza_fail": "❌ Accuracy: {accuracy}%. Try again or peek at the stanza.",
        "msg_stanza_success": "✅ Accuracy: {accuracy}%! Great job!",
        "msg_stanza_recite_prompt": "🎤 Record a voice message reciting this stanza:",
        "msg_stanza_type_prompt": "⌨️ Type the stanza from memory:",
        "msg_stanza_peek": "👀 Here's the stanza text:\n\n{text}",
        "msg_stanza_single": "📖 This poem has only one stanza. Use the normal mode.",

        # Errors & misc
        "msg_feature_wip": "🚧 Feature coming soon!",
        "msg_error_generic": "❌ Something went wrong. Try again.",
        "msg_error_review": "❌ Failed to save review.",
        "msg_error_recommend": "❌ Failed to load recommendation.",
        "msg_no_due_reviews": "✅ No poems due for review!",
        "msg_saved": "✅ Saved!",
        "msg_leaderboard_title": "🏆 **Global Leaderboard** 🏆",
        "msg_leaderboard_empty": "🏆 The leaderboard is currently empty.",
        "msg_leaderboard_error": "❌ Failed to load leaderboard.",
        "msg_leaderboard_row": "{emoji} **{name}** — Lvl {level} ({xp} XP) 🔥{streak}",

        # Help
        "msg_help": (
            "📚 **Poetry Bot — Your poetry companion!**\n\n"
            "Commands:\n"
            "/start — Main menu\n"
            "/review — Review due poems\n"
            "/recommend — Get a new poem\n"
            "/progress — Your stats\n"
            "/leaderboard — Top learners\n"
            "/settings — Settings\n"
            "/help — This message\n\n"
            "Tips:\n"
            "🎤 Send a voice message to check your recitation\n"
            "🎭 Try different moods for varied recommendations\n"
            "🔥 Review daily to keep your streak!"
        ),

        # Welcome
        "msg_welcome": "Hi there! 👋 I'll help you memorize classic poems. Shall we begin?",
        "msg_welcome_back": (
            "👋 Welcome back, {name}!\n\n"
            "⏰ Due for review: {due}\n"
            "🔥 Streak: {streak} days"
        ),
        "msg_whats_next": "What's next?",
        "msg_voice_no_context": "🎤 Tap a poem's 🎤 Recite button first, then send your voice message.",
        "btn_new_poem": "📖 New poem",

        # Encouragement after review
        "msg_encourage_perfect": "🌟 Perfect recall! You're a poetry master!",
        "msg_encourage_good": "💪 Great progress! Keep it up!",
        "msg_encourage_low": "📖 That's OK! Spaced repetition will help. Try again tomorrow!",

        # Friendly empty state
        "msg_no_due_friendly": "✅ All poems reviewed! 🎉\nTry learning something new — tap \"{btn_new}\".",

        # Unknown message
        "msg_unknown_poem": "Looks like a poem! Try /recommend to find it.",
        "msg_unknown_question": "Try /help for available commands.",
        "msg_unknown_default": "I work best with voice messages and menu buttons! Try /help 😊",

        # Recitation prompts & hints
        "msg_hints_penalty": "💡 Hints used: {count} (−{xp} XP)",
        "msg_type_prompt": "⌨️ Type the poem from memory:",
        "msg_type_not_voice": "Please type the poem text, not send voice here.",
        "msg_no_more_hints": "No more hints available.",
        "msg_hint_line": "💡 Hint: _{words}..._",
        "btn_hint": "💡 Hint",
        "btn_show_full": "📖 Show full poem",
        "btn_more_review": "🔄 More reviews",
        "btn_main_menu": "🏠 Main menu",

        # Profile sub-actions
        "btn_achievements": "🏅 Achievements",
        "btn_my_history": "📜 My History",
        "btn_my_favorites": "⭐ My Favorites",
        "btn_my_stats": "📊 My Stats",
        "btn_back_to_menu": "🔙 Back to Menu",

        # Settings — expanded
        "btn_notifications_toggle": "🔔 Notifications",
        "btn_length_pref": "🎵 Poem Length",
        "btn_reset_progress": "🗑 Reset Progress",
        "msg_notifications_on": "🔔 Notifications enabled!",
        "msg_notifications_off": "🔕 Notifications disabled.",
        "msg_notif_saved": "✅ Notification time set to {time}",
        "msg_length_pref_title": "🎵 Preferred poem length:",
        "btn_length_short": "Short",
        "btn_length_medium": "Medium",
        "btn_length_long": "Long",
        "btn_length_any": "Any",
        "msg_length_saved": "✅ Preference saved: {choice}",
        "msg_reset_confirm": "⚠️ Are you sure? This will delete all progress, XP, level, and streak.",
        "btn_reset_yes": "🗑 Yes, delete everything",
        "btn_reset_no": "❌ Cancel",
        "msg_reset_done": "✅ Progress has been completely reset.",

        # Help — interactive
        "msg_help_title": "❓ **Help**\nChoose a topic:",
        "btn_help_learn": "📖 How to learn poems",
        "btn_help_voice": "🎤 Voice tips",
        "btn_help_xp": "🔥 Streak & XP",
        "btn_help_contact": "💬 Contact / Bug report",
        "msg_help_learn": (
            "📖 **How to learn poems**\n\n"
            "1. Tap \"📖 New Poems\" to get a new poem\n"
            "2. Read it a few times\n"
            "3. Use \"📝 By stanza\" for step-by-step memorization\n"
            "4. When ready — tap \"🎤 Recite\"\n"
            "5. The bot checks accuracy and schedules a review\n"
            "6. Review on schedule — intervals will grow!"
        ),
        "msg_help_voice": (
            "🎤 **Voice recognition tips**\n\n"
            "• Speak clearly and not too fast\n"
            "• Minimize background noise\n"
            "• Hold the phone 15–20 cm away\n"
            "• Hold the mic button while recording\n"
            "• If recognition is poor — try \"⌨️ Type it\""
        ),
        "msg_help_xp": (
            "🔥 **XP and Streak**\n\n"
            "• Each review earns XP\n"
            "• Higher accuracy = more XP\n"
            "• New level every level×100 XP\n"
            "• Streak — practice every day!\n"
            "• Missing a day resets the streak"
        ),
        "msg_help_contact": (
            "💬 **Contact / Bug report**\n\n"
            "Found a bug or have a suggestion?\n"
            "Write to us: @poetry\\_bot\\_support"
        ),
        "btn_help_back": "⬅️ Back to Help",

        # Recommendation reasons
        "msg_rec_reason_mood": "Based on your mood: {mood}",
        "msg_rec_reason_time": "Perfect for a {season} {time_of_day}",
        "msg_rec_reason_author": "You enjoy {author} — you might like this",
        "msg_rec_reason_discover": "A classic worth discovering",
        "season_winter": "winter",
        "season_spring": "spring",
        "season_summer": "summer",
        "season_autumn": "autumn",
        "time_morning": "morning",
        "time_afternoon": "afternoon",
        "time_evening": "evening",
        "time_night": "night",

        # Poem Finder flow
        "msg_finder_mood": "🔍 Let's find your perfect poem. What mood?",
        "msg_finder_length": "✅ Got it: {mood}. How long should it be?",
        "msg_finder_era": "✅ Length: {length}. Era preference?",
        "msg_finder_author": "✅ Era: {era}. Any favorite author?",
        "msg_finder_confirm": "🔍 Searching for: {summary}\n",
        "msg_finder_no_results": "😔 No poems found with those filters. Try different ones.",
        "msg_finder_more": "Not what you wanted?",
        "msg_finder_freetext": "✏️ Type your answer:",
        "msg_finder_same_as_last": "🔁 Same as last time",
        "btn_finder_find": "🔍 Find it!",
        "btn_finder_restart": "🔄 Start over",
        "btn_finder_different": "🔄 Try different filters",
        "btn_finder_surprise": "🎲 Surprise me",
        "btn_finder_freetext": "🆓 Free text",
        "btn_finder_skip": "⏭ Skip",
        "btn_finder_search_author": "🔍 Search by name",
        # Finder mood chips
        "mood_sad": "😢 Sad / Melancholy",
        "mood_love": "💖 Love",
        "mood_inspirational": "🌅 Inspirational",
        "mood_reflective": "🌧 Rainy / Reflective",
        "mood_joyful": "🎉 Joyful",
        "mood_philosophical": "🤔 Philosophical",
        "mood_nature": "🌿 Nature",
        "mood_patriotic": "🔥 Patriotic",
        # Finder length chips
        "length_short": "📏 Short (≤12 lines)",
        "length_medium": "📐 Medium (13–30)",
        "length_long": "📜 Long (30+)",
        "length_any": "🎲 Any",
        # Finder era chips
        "era_classic": "🕰 Classic (pre-1900)",
        "era_silver_age": "✒️ Silver Age (1900–1925)",
        "era_soviet": "📻 Soviet (1925–1991)",
        "era_modern": "💻 Modern (1991+)",
        "era_any": "🎲 Any",

        # Favorites
        "btn_fav_add": "⭐ Save to favorites",
        "btn_fav_remove": "💔 Remove from favorites",
        "msg_fav_added": "⭐ Added to favorites!",
        "msg_fav_removed": "💔 Removed from favorites.",
        "msg_fav_empty": "You haven't saved any poems yet. Tap ⭐ on a poem to save it.",
        "msg_fav_title": "⭐ **Favorites** ({count})",

        # History
        "msg_hist_title": "📜 **History** ({count})",
        "msg_hist_empty": "No history yet — start learning your first poem!",
        "msg_hist_row": "{emoji} **{title}** — _{author}_ · {date}",
        "btn_hist_review": "🔄 Review",
        "btn_hist_read": "📖 Read",
        "btn_hist_filter_all": "All",
        "btn_hist_filter_learning": "📖 Learning",
        "btn_hist_filter_reviewing": "🔄 Reviewing",
        "btn_hist_filter_memorized": "🌟 Memorized",

        # Collections
        "btn_collections": "📚 Collections",
        "msg_collections_title": "📚 **Collections**",
        "msg_collection_intro": "{emoji} **{title}** — {count} poems",

        # Pagination
        "btn_prev_page": "⬅️ Prev",
        "btn_next_page": "➡️ Next",

        # Achievements
        "msg_badge_unlocked": "🎉 New badge unlocked!\n{emoji} **{title}** — {description}",
        "msg_achievements_title": "🏅 **Achievements**",
        "msg_badge_locked": "🔒 {title}",
        "msg_badge_unlocked_row": "{emoji} **{title}** — {description}\n    _{date}_",

        # Daily Challenge
        "msg_challenge_title": "🎯 **Daily Challenge:**",
        "msg_challenge_progress": "🎯 {goal}: {progress}/{target}",
        "msg_challenge_completed": "🎉 Challenge completed! +50 XP bonus!",
        "goal_review_n_poems": "Review {n} poems",
        "goal_memorize_one_stanza": "Memorize 1 stanza",
        "goal_voice_recite_one": "Voice-recite 1 poem",
        "goal_learn_new_poem": "Learn a new poem",

        # Streak Freeze
        "msg_freeze_used": "🧊 Streak freeze used! Remaining: {n}",
        "msg_freeze_count": "🧊 Freezes: {n}/3",

        # TTS
        "btn_listen": "🔊 Listen",
        "msg_tts_generating": "🎵 Generating audio...",
        "msg_tts_too_long": "❌ Poem is too long for TTS (>50 lines).",
        "msg_tts_error": "❌ Failed to generate audio.",

        # Celebration cascade
        "msg_celebration_xp": "✨ +{xp} XP",
        "msg_celebration_level": "🎉 Level up! You are now Level {level}",
        "msg_celebration_challenge": "🎯 Challenge: {progress}/{target}",
        "msg_celebration_badge": "🏅 New badge: {title} {emoji}",
        "msg_celebration_freeze": "🧊 Streak freeze used! Remaining: {n}",
    }
}

def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Get a translated string by key. Defaults to russian if key or lang missing."""
    lang_dict = texts.get(lang, texts["ru"])
    translation = lang_dict.get(key, texts["ru"].get(key, key))
    if kwargs:
        return translation.format(**kwargs)
    return translation
