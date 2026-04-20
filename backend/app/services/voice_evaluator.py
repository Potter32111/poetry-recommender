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
    from fastapi import HTTPException

    lang = "ru" if language in ("ru", "both") else "en"
    if lang not in _models:
        model_path = MODEL_PATHS.get(lang)
        if not model_path or not os.path.isdir(model_path):
            raise HTTPException(
                status_code=503,
                detail="Voice recognition temporarily unavailable",
            )
        logger.info("Loading Vosk model for '%s' from %s", lang, model_path)
        _models[lang] = Model(model_path)
    return _models[lang]


# ─── Audio Conversion ───────────────────────────────────────

MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB


def convert_ogg_to_wav(ogg_bytes: bytes) -> bytes:
    """Convert OGG/OGA audio to raw PCM 16kHz mono using ffmpeg."""
    if len(ogg_bytes) > MAX_AUDIO_SIZE:
        raise ValueError(
            f"Audio file too large ({len(ogg_bytes)} bytes). Maximum is {MAX_AUDIO_SIZE} bytes."
        )

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_f:
        ogg_f.write(ogg_bytes)
        ogg_path = ogg_f.name

    # We use .raw extension instead of .wav since we extract raw PCM
    wav_path = ogg_path.replace(".ogg", ".raw")

    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", ogg_path,
                "-ar", "16000",
                "-ac", "1",
                "-f", "s16le", # Raw PCM 16-bit little-endian (no header)
                wav_path,
            ],
            capture_output=True,
            check=True,
            timeout=30,
        )
        with open(wav_path, "rb") as f:
            return f.read()
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timed out while converting audio")
        raise RuntimeError("Audio conversion timed out")
    except subprocess.CalledProcessError as e:
        logger.error("FFmpeg conversion failed: %s", e.stderr)
        raise RuntimeError(f"Audio conversion failed: {e.stderr!r}")
    finally:
        for p in (ogg_path, wav_path):
            try:
                os.unlink(p)
            except OSError:
                pass


# ─── Speech-to-Text ─────────────────────────────────────────

def transcribe(audio_bytes: bytes, language: str) -> str:
    """Transcribe audio bytes (OGG) to text using Vosk."""
    pcm_data = convert_ogg_to_wav(audio_bytes)
    model = get_vosk_model(language)
    rec = KaldiRecognizer(model, 16000)

    # Feed raw PCM audio in chunks
    chunk_size = 4000
    for i in range(0, len(pcm_data), chunk_size):
        rec.AcceptWaveform(pcm_data[i : i + chunk_size])

    result = json.loads(rec.FinalResult())
    text = result.get("text", "")
    logger.info("Vosk transcribed text: '%s'", text)
    return text


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
    word_details: list[dict]  # [{"word": str, "status": "correct"|"missed"|"close", "similar_to": str|None}]


def _accuracy_to_sm2(accuracy: float, method: str = "voice") -> int:
    """Map accuracy percentage (0-100) to SM-2 score (0-5).

    Voice thresholds are more lenient because Vosk small models
    typically max out at 70-80% even for perfect recitation.
    """
    if method == "text":
        if accuracy < 20:
            return 0
        elif accuracy < 35:
            return 1
        elif accuracy < 50:
            return 2
        elif accuracy < 60:
            return 3
        elif accuracy < 75:
            return 4
        else:
            return 5
    else:
        # Voice: shifted thresholds for Vosk STT inaccuracies
        if accuracy < 15:
            return 0
        elif accuracy < 30:
            return 1
        elif accuracy < 45:
            return 2
        elif accuracy < 55:
            return 3
        elif accuracy < 70:
            return 4
        else:
            return 5


def _generate_feedback(accuracy: float, missed: list[str], language: str) -> tuple[str, str]:
    """Generate human-readable feedback and next_steps suggestion."""
    is_ru = language in ("ru", "both")

    if accuracy >= 85 and not missed:
        feedback = "Отлично! Стих выучен почти идеально! 🌟" if is_ru else "Excellent! Almost perfect recitation! 🌟"
        next_steps = "memorized"
    elif accuracy >= 55:
        if missed:
            feedback = (
                f"Хорошо! Большая часть верно, но пропущено {len(missed)} строк(и)."
                if is_ru
                else f"Good job! Most of it is correct, but {len(missed)} line(s) missed."
            )
        else:
            feedback = (
                "Хорошо! Вы прочитали всё, хотя алгоритм не расслышал некоторые слова четко." 
                if is_ru else 
                "Good job! You recited everything, even though the AI misheard some words."
            )
        next_steps = "repeat"
    elif accuracy >= 35:
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


# Common Russian stopwords to reduce omission penalty
RU_STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", 
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", 
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", 
    "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", 
    "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", 
    "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", 
    "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", 
    "сам", "чтоб", "без", "будто", "человек", "чего", "раз", "тоже", "себе", "под", 
    "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", 
    "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", 
    "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", 
    "два", "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", 
    "нас", "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", 
    "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", 
    "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"
}

EN_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't",
    "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}


def compare_texts(transcribed: str, original: str, language: str, method: str = "voice") -> EvaluationResult:
    """Compare transcribed text with the original poem using fuzzy length-weighted word matching."""
    norm_transcribed = _normalize(transcribed)
    norm_original = _normalize(original)

    orig_words = norm_original.split()
    rec_words = norm_transcribed.split()
    
    # Calculate overall accuracy
    if not orig_words or not rec_words:
        accuracy = 0.0
        word_details: list[dict] = []
    else:
        stopwords = EN_STOPWORDS if language == "en" else RU_STOPWORDS
        total_weight = 0.0
        matched_weight = 0.0
        used_rec_indices = set()
        
        # Word-level fuzzy greedy matching with proportional sliding window
        word_details: list[dict] = []
        for i, o_word in enumerate(orig_words):
            word_weight = max(1, len(o_word))
            if o_word in stopwords:
                word_weight = 0.5  # minimal penalty for missing stop words
            
            total_weight += word_weight
            best_match_idx = -1
            best_ratio = 0.0
            
            # Constrain window to prevent matching words completely out of order
            # Use proportional offset based on how far we are in the original poem
            search_start = max(0, int((i/len(orig_words)) * len(rec_words)) - 15)
            search_end = min(len(rec_words), int((i/len(orig_words)) * len(rec_words)) + 25)
            
            # Short words (<=3 chars) use stricter threshold to avoid false positives
            threshold = 0.7 if len(o_word) <= 3 else 0.55
            
            for j in range(search_start, search_end):
                r_word = rec_words[j]
                if j in used_rec_indices:
                    continue
                
                ratio = SequenceMatcher(None, o_word, r_word).ratio()
                if ratio > threshold and ratio > best_ratio:
                    best_match_idx = j
                    best_ratio = ratio
                    
            if best_match_idx != -1:
                used_rec_indices.add(best_match_idx)
                matched_weight += (word_weight * best_ratio)
                if best_ratio >= 0.99:
                    status = "correct"
                    similar_to = None
                else:
                    status = "close"
                    similar_to = rec_words[best_match_idx]
            else:
                status = "missed"
                similar_to = None
            
            if len(word_details) < 30:
                word_details.append({
                    "word": o_word,
                    "status": status,
                    "similar_to": similar_to,
                })
                
        accuracy = min(100.0, (matched_weight / total_weight) * 100.0) if total_weight > 0 else 0.0

    # Find missed lines with more lenient line-level matching
    original_lines = _split_lines(original)
    missed_lines = []
    
    # Pre-tokenize all recognized text for line matching
    used_line_rec_indices = set()
    cumulative_words = 0
    
    for line in original_lines:
        line_words = _normalize(line).split()
        if not line_words:
            continue
            
        line_total_weight = 0
        line_matched_weight = 0
        
        # Approximate center of this line in the transcribed text
        percent_through = cumulative_words / len(orig_words) if orig_words else 0
        expected_rec_center = int(percent_through * len(rec_words))
        
        for o_word in line_words:
            word_weight = max(1, len(o_word))
            line_total_weight += word_weight
            
            best_m = -1
            best_r = 0.0
            
            search_start = max(0, expected_rec_center - 15)
            search_end = min(len(rec_words), expected_rec_center + len(line_words) + 20)
            
            for j in range(search_start, search_end):
                r_word = rec_words[j]
                if j in used_line_rec_indices:
                    continue
                ratio = SequenceMatcher(None, o_word, r_word).ratio()
                line_threshold = 0.7 if len(o_word) <= 3 else 0.55
                if ratio > line_threshold and ratio > best_r:
                    best_m = j
                    best_r = ratio
                    
            if best_m != -1:
                used_line_rec_indices.add(best_m)
                line_matched_weight += (word_weight * best_r)
                
        # If less than 40% of the line weight was spoken correctly, it's "missed"
        line_accuracy = (line_matched_weight / line_total_weight) if line_total_weight > 0 else 0
        if line_accuracy < 0.40:
            missed_lines.append(line)
            
        cumulative_words += len(line_words)

    sm2_score = _accuracy_to_sm2(accuracy, method=method)
    feedback, next_steps = _generate_feedback(accuracy, missed_lines, language)

    return EvaluationResult(
        transcribed_text=transcribed,
        accuracy_percent=round(accuracy, 1),
        sm2_score=sm2_score,
        missed_lines=missed_lines,
        feedback=feedback,
        next_steps=next_steps,
        word_details=word_details if orig_words and rec_words else [],
    )


async def evaluate(audio_bytes: bytes, poem_text: str, language: str) -> EvaluationResult:
    """Full pipeline: transcribe audio → compare with original → return evaluation."""
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
            word_details=[],
        )

    return compare_texts(transcribed, poem_text, language)
