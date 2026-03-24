from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class Hint(BaseModel):
    agent: str
    target: str
    priority: int = Field(ge=1, le=10)
    reason: Optional[str] = None

class FindingEvent(BaseModel):
    finding_id: UUID
    tenant_id: UUID
    run_id: Optional[UUID] = None
    agent_id: str
    asset_id: UUID
    finding_type: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    technique_ids: List[str] = []
    tactic_phase: Optional[str] = None
    chain_tags: List[str] = []
    attack_vector_tags: List[str] = []
    next_probe_hints: List[Hint] = []
    raw_evidence: Dict[str, Any] = {}
    created_at: datetime
    environment: Optional[str] = None

class IngestResponse(BaseModel):
    finding_id: UUID
    action: str
    chain_id: Optional[UUID] = None
