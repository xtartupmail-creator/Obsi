from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import FindingEvent, IngestResponse
from ..services.event_bus import publish_ingested
from ..services.ingest_service import ingest_finding
from ..services.policy import check_policy

router = APIRouter(prefix="/v1/findings", tags=["findings"])


@router.post("", response_model=IngestResponse)
async def ingest(payload: FindingEvent, request: Request, db: Session = Depends(get_db)):
    allow, deny = check_policy(payload.model_dump(mode="json"))
    if not allow:
        raise HTTPException(status_code=403, detail={"policy_denied": deny})

    decision, chain_id, score, reasons = ingest_finding(db, payload)
    publish_ingested(
        tenant_id=str(payload.tenant_id),
        finding_id=str(payload.finding_id),
        asset_id=str(payload.asset_id),
        score=score,
        decision=decision,
        reasons=reasons,
    )

    return IngestResponse(
        finding_id=payload.finding_id,
        action=decision,
        chain_id=chain_id,
        score=score,
        reasons=reasons,
    )
