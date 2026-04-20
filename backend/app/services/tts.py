"""Text-to-speech service using gTTS."""

import hashlib
import logging
from pathlib import Path

from gtts import gTTS

logger = logging.getLogger(__name__)

_CACHE_DIR = Path("tts_cache")
_CACHE_DIR.mkdir(exist_ok=True)

_MAX_LINES = 50


def synthesize(text: str, language: str) -> bytes | None:
    """Generate MP3 audio for the given text.

    Returns MP3 bytes or None if the text is too long.
    """
    lines_count = len([ln for ln in text.split("\n") if ln.strip()])
    if lines_count > _MAX_LINES:
        return None

    # gTTS language codes
    lang_code = "ru" if language == "ru" else "en"

    # Cache key
    key = hashlib.sha256((text + lang_code).encode()).hexdigest()
    cache_path = _CACHE_DIR / f"{key}.mp3"

    if cache_path.exists():
        return cache_path.read_bytes()

    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(str(cache_path))
        return cache_path.read_bytes()
    except Exception as e:
        logger.error("TTS synthesis failed: %s", e)
        return None
