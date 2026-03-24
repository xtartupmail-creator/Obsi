from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db import get_db

router = APIRouter(prefix="/v1/chains", tags=["chains"])


@router.get("/health")
def health_chain():
    return {"ok": True}


@router.get("")
def list_chains(tenant_id: str = Query(...), status: str | None = None, db: Session = Depends(get_db)):
    sql = "select chain_id, chain_score, chain_status, step_count, updated_at from risk_chains where tenant_id = :tid"
    params = {"tid": tenant_id}
    if status:
        sql += " and chain_status = :status"
        params["status"] = status
    sql += " order by updated_at desc limit 200"

    rows = db.execute(text(sql), params).mappings().all()
    return {"items": [dict(r) for r in rows]}


@router.get("/{chain_id}/nodes")
def chain_nodes(chain_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            select cn.step_number, af.finding_id, af.agent_id, af.severity, af.confidence, af.created_at
            from chain_nodes cn
            join agent_findings af on af.finding_id = cn.finding_id
            where cn.chain_id = :cid
            order by cn.step_number asc
            """
        ),
        {"cid": chain_id},
    ).mappings().all()
    return {"items": [dict(r) for r in rows]}
