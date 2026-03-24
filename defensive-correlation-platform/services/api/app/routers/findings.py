from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import FindingEvent, IngestResponse
from ..services.ingest_service import ingest_finding
from ..services.policy import check_policy

router = APIRouter(prefix="/v1/findings", tags=["findings"])

@router.post("", response_model=IngestResponse)
def ingest(payload: FindingEvent, db: Session = Depends(get_db)):
    allow, deny = check_policy(payload.model_dump(mode="json"))
    if not allow:
        raise HTTPException(status_code=403, detail={"policy_denied": deny})

    action, chain_id = ingest_finding(db, payload)
    return IngestResponse(finding_id=payload.finding_id, action=action, chain_id=chain_id)
