from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DecayConfig:
    """Configuration for time-based confidence decay."""

    half_life_hours: float = 6.0

    @property
    def lambda_per_hour(self) -> float:
        """Exponential decay lambda value per hour."""

        return math.log(2) / self.half_life_hours


class ConfidenceEngine:
    """Computes path confidence with exponential decay based on observation age."""

    def __init__(self, decay: DecayConfig | None = None) -> None:
        self.decay = decay or DecayConfig()

    @staticmethod
    def _to_utc_aware(value: datetime) -> datetime:
        """Return a timezone-aware datetime in UTC.

        Naive datetimes are interpreted as UTC to avoid mixed aware/naive
        arithmetic errors and to keep behavior deterministic across deployments.
        """

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def calculate_path_confidence(
        self,
        observed_at: datetime,
        now: datetime | None = None,
        base_confidence: float = 1.0,
    ) -> float:
        """Compute confidence decayed by elapsed time since observation."""

        now_utc = self._to_utc_aware(now or datetime.now(timezone.utc))
        observed_at_utc = self._to_utc_aware(observed_at)

        # Elapsed time in hours using total_seconds for minute-level precision.
        hours_elapsed = (now_utc - observed_at_utc).total_seconds() / 3600
        # Clamp negative durations in case of skewed host clocks.
        hours_elapsed = max(0.0, hours_elapsed)

        decayed_confidence = base_confidence * math.exp(-self.decay.lambda_per_hour * hours_elapsed)
        return max(0.0, min(1.0, decayed_confidence))
