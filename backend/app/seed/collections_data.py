"""Seed data for curated poem collections."""

COLLECTIONS = [
    {
        "slug": "russian-classics",
        "title_ru": "Русская классика",
        "title_en": "Russian Classics",
        "description_ru": "Великие стихи Пушкина, Лермонтова, Тютчева и других классиков",
        "description_en": "Great poems by Pushkin, Lermontov, Tyutchev and other masters",
        "cover_emoji": "🏛",
        "filter": {"authors": ["Пушкин", "Pushkin", "Лермонтов", "Lermontov", "Тютчев", "Tyutchev"]},
    },
    {
        "slug": "love-poems",
        "title_ru": "Стихи о любви",
        "title_en": "Love Poems",
        "description_ru": "Самые проникновенные стихи о любви",
        "description_en": "The most touching poems about love",
        "cover_emoji": "💖",
        "filter": {"themes": ["love", "любовь"]},
    },
    {
        "slug": "nature",
        "title_ru": "Природа",
        "title_en": "Nature",
        "description_ru": "Красота природы в стихах",
        "description_en": "Beauty of nature in verse",
        "cover_emoji": "🌿",
        "filter": {"themes": ["nature", "природа"]},
    },
    {
        "slug": "silver-age",
        "title_ru": "Серебряный век",
        "title_en": "Silver Age",
        "description_ru": "Поэзия Серебряного века русской литературы",
        "description_en": "Poetry from the Silver Age of Russian literature",
        "cover_emoji": "✒️",
        "filter": {"era": "silver_age"},
    },
    {
        "slug": "short-and-sweet",
        "title_ru": "Коротко и ёмко",
        "title_en": "Short & Sweet",
        "description_ru": "Короткие стихи, которые легко выучить",
        "description_en": "Short poems that are easy to memorize",
        "cover_emoji": "⚡",
        "filter": {"max_lines": 8},
    },
]
