from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from uuid import UUID

from .entities import Finding, LinkCandidate, LinkOutcome
from .scoring import LinkScoreInput, jaccard, link_score, temporal_decay
from .types import LinkDecision


@dataclass(slots=True)
class CandidateSnapshot:
    chain_id: UUID
    last_finding_id: UUID
    last_chain_tags: list[str]
    last_vector_tags: list[str]
    last_created_at: datetime
    same_asset: bool
    phase_progression: float = 0.7


def score_candidate(new: Finding, cand: CandidateSnapshot) -> LinkCandidate:
    tag_overlap = jaccard(set(new.chain_tags), set(cand.last_chain_tags))
    vec_overlap = jaccard(set(new.attack_vector_tags), set(cand.last_vector_tags))
    temporal = temporal_decay(new.created_at, cand.last_created_at)

    inp = LinkScoreInput(
        tag_overlap=tag_overlap,
        vector_overlap=vec_overlap,
        temporal=temporal,
        tactic_progression=cand.phase_progression,
        asset_match=1.0 if cand.same_asset else 0.5,
    )
    s = link_score(inp)

    reasons = [
        f"tag_overlap={tag_overlap:.3f}",
        f"vector_overlap={vec_overlap:.3f}",
        f"temporal={temporal:.3f}",
        f"phase={cand.phase_progression:.3f}",
        f"asset_match={1.0 if cand.same_asset else 0.5:.3f}",
    ]
    return LinkCandidate(chain_id=cand.chain_id, score=s, reasons=reasons)


def choose_link(new: Finding, candidates: Iterable[CandidateSnapshot]) -> LinkOutcome:
    scored = [score_candidate(new, c) for c in candidates]
    if not scored:
        return LinkOutcome(decision=LinkDecision.SEED, chain_id=None, score=0.0, reasons=["no_candidates"])

    scored.sort(key=lambda x: x.score, reverse=True)
    best = scored[0]

    if len(scored) > 1 and scored[1].score >= 0.60 and best.score >= 0.60 and scored[1].chain_id != best.chain_id:
        return LinkOutcome(
            decision=LinkDecision.MERGE,
            chain_id=best.chain_id,
            bridge_chain_id=scored[1].chain_id,
            score=best.score,
            reasons=best.reasons + [f"bridge_chain={scored[1].chain_id}"],
        )

    if best.score >= 0.60:
        return LinkOutcome(decision=LinkDecision.APPEND, chain_id=best.chain_id, score=best.score, reasons=best.reasons)

    if best.score >= 0.35:
        return LinkOutcome(decision=LinkDecision.ORPHAN, chain_id=best.chain_id, score=best.score, reasons=best.reasons)

    return LinkOutcome(decision=LinkDecision.SEED, chain_id=None, score=best.score, reasons=best.reasons)
