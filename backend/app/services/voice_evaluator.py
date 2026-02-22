"""Voice-based poem memorization evaluator.

Uses Vosk (offline STT) for speech-to-text and difflib for text comparison.
No external API keys required.
"""

import json
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from difflib import SequenceMatcher

from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

# ─── Vosk Model Management ──────────────────────────────────

_models: dict[str, Model] = {}

MODELS_DIR = os.environ.get("VOSK_MODELS_DIR", "/app/models_vosk")

MODEL_PATHS = {
    "ru": os.path.join(MODELS_DIR, "vosk-model-small-ru-0.22"),
    "en": os.path.join(MODELS_DIR, "vosk-model-small-en-us-0.15"),
}


def get_vosk_model(language: str) -> Model:
    """Get or load the Vosk model for the given language."""
    lang = "ru" if language in ("ru", "both") else "en"
    if lang not in _models:
        model_path = MODEL_PATHS.get(lang)
        if not model_path or not os.path.isdir(model_path):
            raise RuntimeError(
                f"Vosk model not found for '{lang}' at {model_path}. "
                "Make sure models are downloaded in the Docker image."
            )
        logger.info("Loading Vosk model for '%s' from %s", lang, model_path)
        _models[lang] = Model(model_path)
    return _models[lang]


# ─── Audio Conversion ───────────────────────────────────────

def convert_ogg_to_wav(ogg_bytes: bytes) -> bytes:
    """Convert OGG/OGA audio to WAV 16kHz mono using ffmpeg."""
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_f:
        ogg_f.write(ogg_bytes)
        ogg_path = ogg_f.name

    wav_path = ogg_path.replace(".ogg", ".wav")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", ogg_path,
                "-ar", "16000",
                "-ac", "1",
                "-f", "wav",
                wav_path,
            ],
            capture_output=True,
            check=True,
            timeout=30,
        )
        with open(wav_path, "rb") as f:
            return f.read()
    finally:
        for p in (ogg_path, wav_path):
            try:
                os.unlink(p)
            except OSError:
                pass


# ─── Speech-to-Text ─────────────────────────────────────────

def transcribe(audio_bytes: bytes, language: str) -> str:
    """Transcribe audio bytes (OGG) to text using Vosk."""
    wav_data = convert_ogg_to_wav(audio_bytes)
    model = get_vosk_model(language)
    rec = KaldiRecognizer(model, 16000)

    # Skip WAV header (44 bytes) and feed audio in chunks
    chunk_size = 4000
    data = wav_data[44:]

    for i in range(0, len(data), chunk_size):
        rec.AcceptWaveform(data[i : i + chunk_size])

    result = json.loads(rec.FinalResult())
    return result.get("text", "")


# ─── Text Comparison ────────────────────────────────────────

def _normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_lines(text: str) -> list[str]:
    """Split poem text into meaningful lines."""
    return [line.strip() for line in text.strip().split("\n") if line.strip()]


@dataclass
class EvaluationResult:
    """Result of comparing recited text with the original poem."""
    transcribed_text: str
    accuracy_percent: float
    sm2_score: int
    missed_lines: list[str]
    feedback: str
    next_steps: str  # "repeat" | "read_again" | "next_stanza" | "memorized"


def _accuracy_to_sm2(accuracy: float) -> int:
    """Map accuracy percentage (0-100) to SM-2 score (0-5)."""
    if accuracy < 20:
        return 0
    elif accuracy < 40:
        return 1
    elif accuracy < 55:
        return 2
    elif accuracy < 70:
        return 3
    elif accuracy < 85:
        return 4
    else:
        return 5


def _generate_feedback(accuracy: float, missed: list[str], language: str) -> tuple[str, str]:
    """Generate human-readable feedback and next_steps suggestion."""
    is_ru = language in ("ru", "both")

    if accuracy >= 90:
        feedback = "Отлично! Стих выучен почти идеально! 🌟" if is_ru else "Excellent! Almost perfect recitation! 🌟"
        next_steps = "memorized"
    elif accuracy >= 70:
        feedback = (
            f"Хорошо! Большая часть верно, но пропущено {len(missed)} строк(и)."
            if is_ru
            else f"Good job! Most of it is correct, but {len(missed)} line(s) missed."
        )
        next_steps = "repeat"
    elif accuracy >= 40:
        feedback = (
            "Неплохо, но нужно подучить. Попробуйте перечитать стих и повторить."
            if is_ru
            else "Not bad, but needs more practice. Re-read the poem and try again."
        )
        next_steps = "read_again"
    else:
        feedback = (
            "Пока сложно. Рекомендую внимательно перечитать стих несколько раз."
            if is_ru
            else "Needs more study. Read the poem carefully a few times first."
        )
        next_steps = "read_again"

    return feedback, next_steps


def compare_texts(transcribed: str, original: str, language: str) -> EvaluationResult:
    """Compare transcribed text with the original poem and evaluate accuracy."""
    norm_transcribed = _normalize(transcribed)
    norm_original = _normalize(original)

    # Overall accuracy via SequenceMatcher
    matcher = SequenceMatcher(None, norm_transcribed, norm_original)
    accuracy = round(matcher.ratio() * 100, 1)

    # Find missed lines
    original_lines = _split_lines(original)
    missed_lines = []
    for line in original_lines:
        norm_line = _normalize(line)
        if norm_line and norm_line not in norm_transcribed:
            # Check partial match too
            line_matcher = SequenceMatcher(None, norm_line, norm_transcribed)
            if line_matcher.ratio() < 0.5:
                missed_lines.append(line)

    sm2_score = _accuracy_to_sm2(accuracy)
    feedback, next_steps = _generate_feedback(accuracy, missed_lines, language)

    return EvaluationResult(
        transcribed_text=transcribed,
        accuracy_percent=accuracy,
        sm2_score=sm2_score,
        missed_lines=missed_lines,
        feedback=feedback,
        next_steps=next_steps,
    )


# ─── Public API ──────────────────────────────────────────────

async def evaluate(audio_bytes: bytes, poem_text: str, language: str) -> EvaluationResult:
    """Full pipeline: transcribe audio → compare with original → return evaluation.

    Args:
        audio_bytes: Raw OGG audio from Telegram voice message.
        poem_text: Original poem text to compare against.
        language: Language code ("ru", "en", or "both").

    Returns:
        EvaluationResult with accuracy, score, missed lines, feedback.
    """
    transcribed = transcribe(audio_bytes, language)

    if not transcribed.strip():
        return EvaluationResult(
            transcribed_text="",
            accuracy_percent=0.0,
            sm2_score=0,
            missed_lines=_split_lines(poem_text),
            feedback=(
                "Не удалось распознать речь. Попробуйте записать голосовое сообщение ещё раз, говоря чётко и без фонового шума."
                if language in ("ru", "both")
                else "Could not recognize speech. Try recording again, speaking clearly without background noise."
            ),
            next_steps="repeat",
        )

    return compare_texts(transcribed, poem_text, language)
