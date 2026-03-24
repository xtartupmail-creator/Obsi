from __future__ import annotations

from app.orchestration.coordinator import Coordinator
from app.schemas import FindingEvent


def ingest_finding(db, finding: FindingEvent):
    coord = Coordinator(db)
    result = coord.ingest(finding)
    return result.decision, result.chain_id, result.score, result.reasons
