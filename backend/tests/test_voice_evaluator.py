import pytest
from app.services.voice_evaluator import compare_texts, EvaluationResult

def test_compare_texts_perfect_match():
    """Test comparison where the transcribed text is exactly equivalent to the original poem."""
    original = "The quick brown fox jumps over the lazy dog."
    transcribed = "The quick brown fox jumps over the lazy dog"
    
    result = compare_texts(transcribed, original, language="en")
    
    # Needs perfect score
    assert result.accuracy_percent == 100.0
    assert result.sm2_score == 5
    assert len(result.missed_lines) == 0
    assert result.next_steps == "memorized"

def test_compare_texts_fuzzy_match():
    """Test that a slight transcription error (typo/homophone) is still handled smoothly."""
    # A single word slightly misspelled but should be caught by fuzzy matcher
    original = "To be or not to be that is the question"
    transcribed = "To b or not to be thay is the queston"
    
    result = compare_texts(transcribed, original, language="en")
    
    # Should get a high score, maybe not 100, but certainly > 85
    assert result.accuracy_percent > 85.0
    assert result.sm2_score >= 4
    assert len(result.missed_lines) == 0

def test_compare_texts_missed_lines():
    """Test that missing lines are properly identified."""
    original = "Roses are red\nViolets are blue\nSugar is sweet\nAnd so are you"
    # Omitted "Sugar is sweet"
    transcribed = "Roses are red violets are blue and so are you"
    
    result = compare_texts(transcribed, original, language="en")
    
    assert len(result.missed_lines) == 1
    assert "Sugar is sweet" in result.missed_lines[0]
    # Accuracy should be lower due to missed words
    assert result.accuracy_percent < 100.0
    assert result.sm2_score < 5

def test_compare_texts_empty_transcription():
    """Test fallback when nothing is transcribed."""
    original = "Hello world"
    transcribed = ""
    result = compare_texts(transcribed, original, language="en")
    
    assert result.accuracy_percent == 0.0
    assert result.sm2_score == 0
    assert len(result.missed_lines) == 1
    assert result.missed_lines[0] == "Hello world"
