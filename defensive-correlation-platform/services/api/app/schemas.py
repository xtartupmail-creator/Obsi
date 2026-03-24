from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Hint(BaseModel):
    agent: str
    target: str
    priority: int = Field(ge=1, le=10)
    reason: str | None = None


class FindingEvent(BaseModel):
    finding_id: UUID
    tenant_id: UUID
    run_id: UUID | None = None
    agent_id: str
    asset_id: UUID
    finding_type: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    technique_ids: list[str] = []
    tactic_phase: str | None = None
    chain_tags: list[str] = []
    attack_vector_tags: list[str] = []
    next_probe_hints: list[Hint] = []
    raw_evidence: dict[str, Any] = {}
    created_at: datetime
    environment: str | None = None


class IngestResponse(BaseModel):
    finding_id: UUID
    action: str
    chain_id: UUID | None = None
    score: float = 0.0
    reasons: list[str] = []
