from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp

from .entities import Finding, ScoreBreakdown
from .types import ChainStatus


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def temporal_decay(current: datetime, previous: datetime, half_life_hours: float = 24.0) -> float:
    delta_hours = max(0.0, (current - previous).total_seconds() / 3600.0)
    lam = 0.693 / max(half_life_hours, 0.1)
    return exp(-lam * delta_hours)


@dataclass(slots=True)
class LinkScoreInput:
    tag_overlap: float
    vector_overlap: float
    temporal: float
    tactic_progression: float
    asset_match: float


def link_score(inp: LinkScoreInput) -> float:
    return (
        0.35 * inp.tag_overlap
        + 0.25 * inp.vector_overlap
        + 0.20 * inp.temporal
        + 0.10 * inp.tactic_progression
        + 0.10 * inp.asset_match
    )


def status_from_score(score: float) -> ChainStatus:
    if score >= 0.70:
        return ChainStatus.CRITICAL
    if score >= 0.50:
        return ChainStatus.VALIDATED
    if score >= 0.30:
        return ChainStatus.CANDIDATE
    return ChainStatus.POTENTIAL


def default_breakdown_from_finding(finding: Finding, step_count: int) -> ScoreBreakdown:
    sev_map = {"low": 0.2, "medium": 0.4, "high": 0.7, "critical": 0.9}
    severity_weight = sev_map.get(finding.severity.lower(), 0.3)
    confidence = min(1.0, max(0.0, finding.confidence))

    objective = min(1.0, 0.5 * severity_weight + 0.5 * confidence)
    exploitability = min(1.0, 0.6 * severity_weight + 0.4 * confidence)
    blast = min(1.0, 0.4 * severity_weight + 0.6 * (step_count / 10.0))
    detection = max(0.0, 1.0 - confidence)
    completeness = min(1.0, step_count / 8.0)

    return ScoreBreakdown(
        objective_proximity=objective,
        exploitability_risk=exploitability,
        blast_radius=blast,
        detection_likelihood=detection,
        chain_completeness=completeness,
    )


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
