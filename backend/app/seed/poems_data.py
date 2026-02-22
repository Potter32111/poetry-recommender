"""Classic poems collection for seeding the database."""

POEMS = [
    # === ENGLISH POEMS ===
    {
        "title": "The Road Not Taken",
        "author": "Robert Frost",
        "language": "en",
        "difficulty": 2,
        "themes": ["choice", "life", "nature"],
        "era": "modern",
        "text": (
            "Two roads diverged in a yellow wood,\n"
            "And sorry I could not travel both\n"
            "And be one traveler, long I stood\n"
            "And looked down one as far as I could\n"
            "To where it bent in the undergrowth;\n\n"
            "Then took the other, as just as fair,\n"
            "And having perhaps the better claim,\n"
            "Because it was grassy and wanted wear;\n"
            "Though as for that the passing there\n"
            "Had worn them really about the same,\n\n"
            "And both that morning equally lay\n"
            "In leaves no step had trodden black.\n"
            "Oh, I kept the first for another day!\n"
            "Yet knowing how way leads on to way,\n"
            "I doubted if I should ever come back.\n\n"
            "I shall be telling this with a sigh\n"
            "Somewhere ages and ages hence:\n"
            "Two roads diverged in a wood, and I—\n"
            "I took the one less traveled by,\n"
            "And that has made all the difference."
        ),
    },
    {
        "title": "Stopping by Woods on a Snowy Evening",
        "author": "Robert Frost",
        "language": "en",
        "difficulty": 2,
        "themes": ["nature", "contemplation", "winter"],
        "era": "modern",
        "text": (
            "Whose woods these are I think I know.\n"
            "His house is in the village though;\n"
            "He will not see me stopping here\n"
            "To watch his woods fill up with snow.\n\n"
            "My little horse must think it queer\n"
            "To stop without a farmhouse near\n"
            "Between the woods and frozen lake\n"
            "The darkest evening of the year.\n\n"
            "He gives his harness bells a shake\n"
            "To ask if there is some mistake.\n"
            "The only other sound's the sweep\n"
            "Of easy wind and downy flake.\n\n"
            "The woods are lovely, dark and deep,\n"
            "But I have promises to keep,\n"
            "And miles to go before I sleep,\n"
            "And miles to go before I sleep."
        ),
    },
    {
        "title": "Sonnet 18",
        "author": "William Shakespeare",
        "language": "en",
        "difficulty": 3,
        "themes": ["love", "beauty", "time"],
        "era": "renaissance",
        "text": (
            "Shall I compare thee to a summer's day?\n"
            "Thou art more lovely and more temperate:\n"
            "Rough winds do shake the darling buds of May,\n"
            "And summer's lease hath all too short a date;\n\n"
            "Sometime too hot the eye of heaven shines,\n"
            "And often is his gold complexion dimm'd;\n"
            "And every fair from fair sometime declines,\n"
            "By chance or nature's changing course untrimm'd;\n\n"
            "But thy eternal summer shall not fade,\n"
            "Nor lose possession of that fair thou ow'st;\n"
            "Nor shall death brag thou wander'st in his shade,\n"
            "When in eternal lines to time thou grow'st:\n\n"
            "So long as men can breathe or eyes can see,\n"
            "So long lives this, and this gives life to thee."
        ),
    },
    {
        "title": "If—",
        "author": "Rudyard Kipling",
        "language": "en",
        "difficulty": 3,
        "themes": ["wisdom", "perseverance", "manhood"],
        "era": "victorian",
        "text": (
            "If you can keep your head when all about you\n"
            "Are losing theirs and blaming it on you,\n"
            "If you can trust yourself when all men doubt you,\n"
            "But make allowance for their doubting too;\n\n"
            "If you can wait and not be tired by waiting,\n"
            "Or being lied about, don't deal in lies,\n"
            "Or being hated, don't give way to hating,\n"
            "And yet don't look too good, nor talk too wise:\n\n"
            "If you can dream — and not make dreams your master;\n"
            "If you can think — and not make thoughts your aim;\n"
            "If you can meet with Triumph and Disaster\n"
            "And treat those two impostors just the same;\n\n"
            "Yours is the Earth and everything that's in it,\n"
            "And — which is more — you'll be a Man, my son!"
        ),
    },
    {
        "title": "I Wandered Lonely as a Cloud",
        "author": "William Wordsworth",
        "language": "en",
        "difficulty": 2,
        "themes": ["nature", "beauty", "solitude"],
        "era": "romantic",
        "text": (
            "I wandered lonely as a cloud\n"
            "That floats on high o'er vales and hills,\n"
            "When all at once I saw a crowd,\n"
            "A host, of golden daffodils;\n"
            "Beside the lake, beneath the trees,\n"
            "Fluttering and dancing in the breeze.\n\n"
            "Continuous as the stars that shine\n"
            "And twinkle on the milky way,\n"
            "They stretched in never-ending line\n"
            "Along the margin of a bay:\n"
            "Ten thousand saw I at a glance,\n"
            "Tossing their heads in sprightly dance.\n\n"
            "The waves beside them danced; but they\n"
            "Out-did the sparkling waves in glee:\n"
            "A poet could not but be gay,\n"
            "In such a jocund company:\n"
            "I gazed — and gazed — but little thought\n"
            "What wealth the show to me had brought:\n\n"
            "For oft, when on my couch I lie\n"
            "In vacant or in pensive mood,\n"
            "They flash upon that inward eye\n"
            "Which is the bliss of solitude;\n"
            "And then my heart with pleasure fills,\n"
            "And dances with the daffodils."
        ),
    },
    {
        "title": "Do Not Go Gentle into That Good Night",
        "author": "Dylan Thomas",
        "language": "en",
        "difficulty": 4,
        "themes": ["death", "defiance", "life"],
        "era": "modern",
        "text": (
            "Do not go gentle into that good night,\n"
            "Old age should burn and rave at close of day;\n"
            "Rage, rage against the dying of the light.\n\n"
            "Though wise men at their end know dark is right,\n"
            "Because their words had forked no lightning they\n"
            "Do not go gentle into that good night.\n\n"
            "Good men, the last wave by, crying how bright\n"
            "Their frail deeds might have danced in a green bay,\n"
            "Rage, rage against the dying of the light.\n\n"
            "Wild men who caught and sang the sun in flight,\n"
            "And learn, too late, they grieved it on its way,\n"
            "Do not go gentle into that good night.\n\n"
            "Grave men, near death, who see with blinding sight\n"
            "Blind eyes could blaze like meteors and be gay,\n"
            "Rage, rage against the dying of the light.\n\n"
            "And you, my father, there on the sad height,\n"
            "Curse, bless, me now with your fierce tears, I pray.\n"
            "Do not go gentle into that good night.\n"
            "Rage, rage against the dying of the light."
        ),
    },
    # === RUSSIAN POEMS ===
    {
        "title": "Я вас любил",
        "author": "Александр Пушкин",
        "language": "ru",
        "difficulty": 2,
        "themes": ["love", "farewell", "devotion"],
        "era": "romantic",
        "text": (
            "Я вас любил: любовь ещё, быть может,\n"
            "В душе моей угасла не совсем;\n"
            "Но пусть она вас больше не тревожит;\n"
            "Я не хочу печалить вас ничем.\n\n"
            "Я вас любил безмолвно, безнадежно,\n"
            "То робостью, то ревностью томим;\n"
            "Я вас любил так искренно, так нежно,\n"
            "Как дай вам бог любимой быть другим."
        ),
    },
    {
        "title": "Зимнее утро",
        "author": "Александр Пушкин",
        "language": "ru",
        "difficulty": 3,
        "themes": ["nature", "winter", "joy"],
        "era": "romantic",
        "text": (
            "Мороз и солнце; день чудесный!\n"
            "Ещё ты дремлешь, друг прелестный —\n"
            "Пора, красавица, проснись:\n"
            "Открой сомкнуты негой взоры\n"
            "Навстречу северной Авроры,\n"
            "Звездою севера явись!\n\n"
            "Вечор, ты помнишь, вьюга злилась,\n"
            "На мутном небе мгла носилась;\n"
            "Луна, как бледное пятно,\n"
            "Сквозь тучи мрачные желтела,\n"
            "И ты печальная сидела —\n"
            "А нынче... погляди в окно."
        ),
    },
    {
        "title": "Парус",
        "author": "Михаил Лермонтов",
        "language": "ru",
        "difficulty": 1,
        "themes": ["freedom", "solitude", "sea"],
        "era": "romantic",
        "text": (
            "Белеет парус одинокой\n"
            "В тумане моря голубом!..\n"
            "Что ищет он в стране далёкой?\n"
            "Что кинул он в краю родном?..\n\n"
            "Играют волны — ветер свищет,\n"
            "И мачта гнётся и скрыпит...\n"
            "Увы, — он счастия не ищет\n"
            "И не от счастия бежит!\n\n"
            "Под ним струя светлей лазури,\n"
            "Над ним луч солнца золотой...\n"
            "А он, мятежный, просит бури,\n"
            "Как будто в бурях есть покой!"
        ),
    },
    {
        "title": "Не выходи из комнаты",
        "author": "Иосиф Бродский",
        "language": "ru",
        "difficulty": 4,
        "themes": ["solitude", "freedom", "philosophy"],
        "era": "modern",
        "text": (
            "Не выходи из комнаты, не совершай ошибку.\n"
            "Зачем тебе Солнце, если ты куришь Шипку?\n"
            "За дверью бессмысленно всё, особенно — возглас счастья.\n"
            "Только в уборную — и сразу же возвращайся.\n\n"
            "О, не выходи из комнаты, не вызывай мотора.\n"
            "Потому что пространство сделано из коридора\n"
            "и кончается счётчиком. А если войдёт живая\n"
            "милка, пасть разевая, — Loss выгоняй, не раздевая.\n\n"
            "Не выходи из комнаты; считай, что тебя продуло.\n"
            "Что интересней на свете стены и стула?\n"
            "Зачем выходить оттуда, куда вернёшься вечером\n"
            "таким же, каким ты был, тем более — искалеченным?"
        ),
    },
    {
        "title": "Мне нравится, что вы больны не мной",
        "author": "Марина Цветаева",
        "language": "ru",
        "difficulty": 3,
        "themes": ["love", "freedom", "acceptance"],
        "era": "modern",
        "text": (
            "Мне нравится, что вы больны не мной,\n"
            "Мне нравится, что я больна не вами,\n"
            "Что никогда тяжёлый шар земной\n"
            "Не уплывёт под нашими ногами.\n\n"
            "Мне нравится, что можно быть смешной —\n"
            "Распущенной — и не играть словами,\n"
            "И не краснеть удушливой волной,\n"
            "Слегка соприкоснувшись рукавами.\n\n"
            "Мне нравится ещё, что вы при мне\n"
            "Спокойно обнимаете другую,\n"
            "Не прочите мне в адовом огне\n"
            "Гореть за то, что я не вас целую."
        ),
    },
    {
        "title": "Жди меня",
        "author": "Константин Симонов",
        "language": "ru",
        "difficulty": 2,
        "themes": ["love", "war", "hope"],
        "era": "modern",
        "text": (
            "Жди меня, и я вернусь.\n"
            "Только очень жди,\n"
            "Жди, когда наводят грусть\n"
            "Жёлтые дожди,\n"
            "Жди, когда снега метут,\n"
            "Жди, когда жара,\n"
            "Жди, когда других не ждут,\n"
            "Позабыв вчера.\n\n"
            "Жди, когда из дальних мест\n"
            "Писем не придёт,\n"
            "Жди, когда уж надоест\n"
            "Всем, кто вместе ждёт.\n\n"
            "Жди меня, и я вернусь,\n"
            "Не желай добра\n"
            "Всем, кто знает наизусть,\n"
            "Что забыть пора."
        ),
    },
    {
        "title": "Нам не дано предугадать",
        "author": "Фёдор Тютчев",
        "language": "ru",
        "difficulty": 1,
        "themes": ["philosophy", "words", "compassion"],
        "era": "romantic",
        "text": (
            "Нам не дано предугадать,\n"
            "Как слово наше отзовётся, —\n"
            "И нам сочувствие даётся,\n"
            "Как нам даётся благодать..."
        ),
    },
    {
        "title": "Silentium!",
        "author": "Фёдор Тютчев",
        "language": "ru",
        "difficulty": 3,
        "themes": ["silence", "inner world", "philosophy"],
        "era": "romantic",
        "text": (
            "Молчи, скрывайся и таи\n"
            "И чувства и мечты свои —\n"
            "Пускай в душевной глубине\n"
            "Встают и заходят оне\n"
            "Безмолвно, как звёзды в ночи, —\n"
            "Любуйся ими — и молчи.\n\n"
            "Как сердцу высказать себя?\n"
            "Другому как понять тебя?\n"
            "Поймёт ли он, чем ты живёшь?\n"
            "Мысль изречённая есть ложь.\n"
            "Взрывая, возмутишь ключи, —\n"
            "Питайся ими — и молчи.\n\n"
            "Лишь жить в себе самом умей —\n"
            "Есть целый мир в душе твоей\n"
            "Таинственно-волшебных дум;\n"
            "Их оглушит наружный шум,\n"
            "Дневные разгонят лучи, —\n"
            "Внимай их пенью — и молчи!.."
        ),
    },
    {
        "title": "Invictus",
        "author": "William Ernest Henley",
        "language": "en",
        "difficulty": 3,
        "themes": ["courage", "defiance", "fate"],
        "era": "victorian",
        "text": (
            "Out of the night that covers me,\n"
            "Black as the pit from pole to pole,\n"
            "I thank whatever gods may be\n"
            "For my unconquerable soul.\n\n"
            "In the fell clutch of circumstance\n"
            "I have not winced nor cried aloud.\n"
            "Under the bludgeonings of chance\n"
            "My head is bloody, but unbowed.\n\n"
            "Beyond this place of wrath and tears\n"
            "Looms but the Horror of the shade,\n"
            "And yet the menace of the years\n"
            "Finds and shall find me unafraid.\n\n"
            "It matters not how strait the gate,\n"
            "How charged with punishments the scroll,\n"
            "I am the master of my fate,\n"
            "I am the captain of my soul."
        ),
    },
    {
        "title": "Ozymandias",
        "author": "Percy Bysshe Shelley",
        "language": "en",
        "difficulty": 3,
        "themes": ["power", "time", "decay"],
        "era": "romantic",
        "text": (
            "I met a traveller from an antique land,\n"
            "Who said — \"Two vast and trunkless legs of stone\n"
            "Stand in the desert. . . . Near them, on the sand,\n"
            "Half sunk a shattered visage lies, whose frown,\n"
            "And wrinkled lip, and sneer of cold command,\n"
            "Tell that its sculptor well those passions read\n"
            "Which yet survive, stamped on these lifeless things,\n"
            "The hand that mocked them, and the heart that fed;\n"
            "And on the pedestal, these words appear:\n"
            "My name is Ozymandias, King of Kings;\n"
            "Look on my Works, ye Mighty, and despair!\n"
            "Nothing beside remains. Round the decay\n"
            "Of that colossal Wreck, boundless and bare\n"
            "The lone and level sands stretch far away.\""
        ),
    },
]
