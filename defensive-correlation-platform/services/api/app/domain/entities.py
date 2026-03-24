from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .types import ChainStatus, LinkDecision


@dataclass(slots=True)
class Hint:
    agent: str
    target: str
    priority: int
    reason: str | None = None


@dataclass(slots=True)
class Finding:
    finding_id: UUID
    tenant_id: UUID
    agent_id: str
    asset_id: UUID
    finding_type: str
    severity: str
    confidence: float
    chain_tags: list[str] = field(default_factory=list)
    attack_vector_tags: list[str] = field(default_factory=list)
    technique_ids: list[str] = field(default_factory=list)
    tactic_phase: str | None = None
    next_probe_hints: list[Hint] = field(default_factory=list)
    raw_evidence: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class RiskChain:
    chain_id: UUID = field(default_factory=uuid4)
    tenant_id: UUID | None = None
    chain_score: float = 0.0
    chain_status: ChainStatus = ChainStatus.POTENTIAL
    step_count: int = 0
    objective: str = "reduce exposure"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class LinkCandidate:
    chain_id: UUID
    score: float
    reasons: list[str]


@dataclass(slots=True)
class LinkOutcome:
    decision: LinkDecision
    chain_id: UUID | None
    bridge_chain_id: UUID | None = None
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoreBreakdown:
    objective_proximity: float
    exploitability_risk: float
    blast_radius: float
    detection_likelihood: float
    chain_completeness: float

    def weighted(self) -> float:
        return (
            0.35 * self.objective_proximity
            + 0.25 * self.exploitability_risk
            + 0.20 * self.blast_radius
            + 0.10 * self.detection_likelihood
            + 0.10 * self.chain_completeness
        )
