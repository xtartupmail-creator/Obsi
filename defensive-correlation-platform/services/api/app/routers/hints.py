from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..repositories.hints_repo import HintsRepository

router = APIRouter(prefix="/v1/hints", tags=["hints"])


@router.get("/next")
def next_hint(tenant_id: str = Query(...), limit: int = Query(25, ge=1, le=200), db: Session = Depends(get_db)):
    repo = HintsRepository(db)
    return {"items": repo.list_next(tenant_id=tenant_id, limit=limit)}
