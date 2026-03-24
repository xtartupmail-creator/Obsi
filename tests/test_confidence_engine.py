import pytest
import math
from datetime import datetime, timedelta, timezone

from confidence_engine import ConfidenceEngine, DecayConfig


def _expected(decay: DecayConfig, base: float, elapsed_hours: float) -> float:
    return base * math.exp(-decay.lambda_per_hour * elapsed_hours)


def test_decay_for_elapsed_minutes() -> None:
    decay = DecayConfig(half_life_hours=6.0)
    engine = ConfidenceEngine(decay=decay)

    now = datetime(2026, 3, 24, 12, 0, tzinfo=timezone.utc)
    observed = now - timedelta(minutes=30)

    actual = engine.calculate_path_confidence(observed_at=observed, now=now, base_confidence=1.0)

    assert actual == pytest.approx(_expected(decay, 1.0, 0.5))


def test_decay_for_elapsed_hours() -> None:
    decay = DecayConfig(half_life_hours=6.0)
    engine = ConfidenceEngine(decay=decay)

    now = datetime(2026, 3, 24, 12, 0, tzinfo=timezone.utc)
    observed = now - timedelta(hours=6)

    actual = engine.calculate_path_confidence(observed_at=observed, now=now, base_confidence=0.8)

    assert actual == pytest.approx(_expected(decay, 0.8, 6.0))


def test_decay_for_elapsed_multiple_days() -> None:
    decay = DecayConfig(half_life_hours=6.0)
    engine = ConfidenceEngine(decay=decay)

    now = datetime(2026, 3, 24, 12, 0, tzinfo=timezone.utc)
    observed = now - timedelta(days=2, hours=3)

    actual = engine.calculate_path_confidence(observed_at=observed, now=now, base_confidence=1.0)

    assert actual == pytest.approx(_expected(decay, 1.0, 51.0))


def test_negative_elapsed_clamped_to_zero() -> None:
    decay = DecayConfig(half_life_hours=6.0)
    engine = ConfidenceEngine(decay=decay)

    now = datetime(2026, 3, 24, 12, 0, tzinfo=timezone.utc)
    observed = now + timedelta(minutes=5)

    actual = engine.calculate_path_confidence(observed_at=observed, now=now, base_confidence=0.7)

    assert actual == pytest.approx(0.7)


def test_naive_datetimes_interpreted_as_utc() -> None:
    decay = DecayConfig(half_life_hours=6.0)
    engine = ConfidenceEngine(decay=decay)

    now = datetime(2026, 3, 24, 12, 0)
    observed = datetime(2026, 3, 24, 6, 0)

    actual = engine.calculate_path_confidence(observed_at=observed, now=now, base_confidence=1.0)

    assert actual == pytest.approx(_expected(decay, 1.0, 6.0))
