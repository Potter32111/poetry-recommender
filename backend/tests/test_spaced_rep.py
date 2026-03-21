import pytest
from datetime import datetime, timedelta, timezone

from app.services.spaced_rep import calculate_sm2, SM2Result

def test_calculate_sm2_quality_less_than_3():
    """Test SM-2 calculation when quality score is less than 3 (failed recall)."""
    # Initial state
    quality = 2
    repetitions = 3
    ease_factor = 2.5
    interval_days = 7

    result = calculate_sm2(
        quality=quality,
        repetitions=repetitions,
        ease_factor=ease_factor,
        interval_days=interval_days
    )

    # When quality < 3, it's a failed recall
    assert result.repetitions == 0
    assert result.interval_days == 1
    assert result.status == "learning"
    # Ease factor logic applies to < 3? No, in the logic "if quality < 3: reset parameters" 
    # but the ease factor remains the same in the returned object (although wait, let's check code).
    # Ah, the code says:
    # if quality < 3:
    #     repetitions = 0, interval_days = 1, status = "learning"
    # Actually wait, in original SM-2 ease factor stays same on fail, or doesn't it recalculate?
    # Our code returned round(ease_factor, 2). So it should be 2.5.
    assert result.ease_factor == 2.5

def test_calculate_sm2_quality_greater_equals_3():
    """Test SM-2 calculation when quality score is >= 3 (successful recall)."""
    # 1. First successful repetition
    res1 = calculate_sm2(quality=4, repetitions=0, ease_factor=2.5, interval_days=0)
    assert res1.interval_days == 1
    assert res1.repetitions == 1
    assert res1.status == "reviewing"
    # Calculate expected EF: 2.5 + (0.1 - (5 - 4) * (0.08 + (5 - 4) * 0.02))
    # = 2.5 + (0.1 - 1 * 0.1) = 2.5 + 0.0 = 2.5
    assert res1.ease_factor == 2.5

    # 2. Second successful repetition
    res2 = calculate_sm2(quality=5, repetitions=1, ease_factor=2.5, interval_days=1)
    assert res2.interval_days == 6
    assert res2.repetitions == 2
    assert res2.ease_factor == 2.6  # 2.5 + 0.1 = 2.6 (since quality=5 -> 0.1)

    # 3. Third successful repetition (interval = round(interval * EF))
    res3 = calculate_sm2(quality=5, repetitions=2, ease_factor=2.6, interval_days=6)
    assert res3.interval_days == round(6 * 2.6)
    assert res3.repetitions == 3
    assert res3.ease_factor == 2.7

def test_calculate_sm2_memorized_status():
    """Test transition to 'memorized' status."""
    res = calculate_sm2(quality=5, repetitions=4, ease_factor=2.5, interval_days=10)
    assert res.status == "memorized"
    assert res.repetitions == 5

def test_calculate_sm2_invalid_quality():
    """Test exception raising for invalid quality score."""
    with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
        calculate_sm2(quality=6, repetitions=0, ease_factor=2.5, interval_days=0)
