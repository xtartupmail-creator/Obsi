from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities import Finding, Hint
from app.orchestration.pipeline import IngestPipeline, PipelineResult
from app.schemas import FindingEvent


class Coordinator:
    def __init__(self, db: Session):
        self.pipeline = IngestPipeline(db)

    @staticmethod
    def to_domain(event: FindingEvent) -> Finding:
        hints = [Hint(agent=h.agent, target=h.target, priority=h.priority, reason=h.reason) for h in event.next_probe_hints]
        return Finding(
            finding_id=event.finding_id,
            tenant_id=event.tenant_id,
            agent_id=event.agent_id,
            asset_id=event.asset_id,
            finding_type=event.finding_type,
            severity=event.severity,
            confidence=event.confidence,
            chain_tags=event.chain_tags,
            attack_vector_tags=event.attack_vector_tags,
            technique_ids=event.technique_ids,
            tactic_phase=event.tactic_phase,
            next_probe_hints=hints,
            raw_evidence=event.raw_evidence,
            created_at=event.created_at,
        )

    def ingest(self, event: FindingEvent) -> PipelineResult:
        finding = self.to_domain(event)
        return self.pipeline.run(finding)
