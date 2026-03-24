from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities import Finding
from app.domain.linking import choose_link
from app.domain.scoring import default_breakdown_from_finding
from app.domain.types import LinkDecision
from app.repositories.chains_repo import ChainsRepository
from app.repositories.findings_repo import FindingsRepository
from app.repositories.hints_repo import HintsRepository


@dataclass(slots=True)
class PipelineResult:
    decision: str
    chain_id: UUID | None
    score: float
    reasons: list[str]


class IngestPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.findings = FindingsRepository(db)
        self.chains = ChainsRepository(db)
        self.hints = HintsRepository(db)

    def run(self, finding: Finding) -> PipelineResult:
        self.findings.upsert_asset(finding.tenant_id, finding.asset_id)
        self.findings.insert_finding(finding)

        candidates = self.chains.candidate_snapshots(finding)
        outcome = choose_link(finding, candidates)

        if outcome.decision == LinkDecision.SEED:
            cid = self.chains.create_chain(finding.tenant_id)
            self.chains.append_finding(finding.tenant_id, cid, finding.finding_id)
            step_count = self.chains.chain_step_count(cid)
            br = default_breakdown_from_finding(finding, step_count)
            score = self.chains.set_chain_score(
                cid,
                br.objective_proximity,
                br.exploitability_risk,
                br.blast_radius,
                br.detection_likelihood,
                br.chain_completeness,
            )
            self.db.commit()
            return PipelineResult(decision=LinkDecision.SEED.value, chain_id=cid, score=score, reasons=outcome.reasons)

        if outcome.chain_id is None:
            self.db.commit()
            return PipelineResult(decision=LinkDecision.ORPHAN.value, chain_id=None, score=outcome.score, reasons=outcome.reasons)

        self.chains.append_finding(finding.tenant_id, outcome.chain_id, finding.finding_id)

        if outcome.decision == LinkDecision.MERGE and outcome.bridge_chain_id:
            merged = self.chains.merge_chains(finding.tenant_id, outcome.chain_id, outcome.bridge_chain_id)
            outcome.chain_id = merged

        step_count = self.chains.chain_step_count(outcome.chain_id)
        br = default_breakdown_from_finding(finding, step_count)
        score = self.chains.set_chain_score(
            outcome.chain_id,
            br.objective_proximity,
            br.exploitability_risk,
            br.blast_radius,
            br.detection_likelihood,
            br.chain_completeness,
        )

        self.hints.enqueue_hints(finding.tenant_id, finding.agent_id, finding.next_probe_hints)
        self.db.commit()

        return PipelineResult(decision=outcome.decision.value, chain_id=outcome.chain_id, score=score, reasons=outcome.reasons)
