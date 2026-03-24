from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities import Finding
from app.domain.linking import CandidateSnapshot


class ChainsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_chain(self, tenant_id: UUID) -> UUID:
        cid = uuid4()
        self.db.execute(
            text("insert into risk_chains (chain_id, tenant_id, chain_status) values (:cid, :tid, 'POTENTIAL')"),
            {"cid": str(cid), "tid": str(tenant_id)},
        )
        return cid

    def append_finding(self, tenant_id: UUID, chain_id: UUID, finding_id: UUID) -> None:
        self.db.execute(
            text("select chain_append(:tid, :cid, :fid)"),
            {"tid": str(tenant_id), "cid": str(chain_id), "fid": str(finding_id)},
        )

    def merge_chains(self, tenant_id: UUID, chain_a: UUID, chain_b: UUID) -> UUID:
        row = self.db.execute(
            text("select chain_merge(:tid, :a, :b) as merged_chain_id"),
            {"tid": str(tenant_id), "a": str(chain_a), "b": str(chain_b)},
        ).mappings().first()
        return UUID(row["merged_chain_id"])

    def link_findings(self, tenant_id: UUID, source_id: UUID, target_id: UUID, confidence: float, reason: str) -> None:
        self.db.execute(
            text(
                """
                insert into finding_links (link_id, tenant_id, source_id, target_id, link_type, confidence, link_reason)
                values (gen_random_uuid(), :tid, :src, :dst, 'tag_overlap', :conf, :reason)
                """
            ),
            {
                "tid": str(tenant_id),
                "src": str(source_id),
                "dst": str(target_id),
                "conf": confidence,
                "reason": reason,
            },
        )

    def candidate_snapshots(self, finding: Finding) -> list[CandidateSnapshot]:
        cutoff = finding.created_at - timedelta(days=7)
        rows = self.db.execute(
            text(
                """
                select chain_id, last_finding_id, last_chain_tags, last_vector_tags, last_created_at, asset_id
                from vw_chain_candidates
                where tenant_id = :tenant_id
                  and last_created_at >= :cutoff
                """
            ),
            {"tenant_id": str(finding.tenant_id), "cutoff": cutoff},
        ).mappings().all()

        result: list[CandidateSnapshot] = []
        for r in rows:
            result.append(
                CandidateSnapshot(
                    chain_id=UUID(r["chain_id"]),
                    last_finding_id=UUID(r["last_finding_id"]),
                    last_chain_tags=list(r["last_chain_tags"] or []),
                    last_vector_tags=list(r["last_vector_tags"] or []),
                    last_created_at=r["last_created_at"].astimezone(timezone.utc)
                    if isinstance(r["last_created_at"], datetime)
                    else finding.created_at,
                    same_asset=str(r["asset_id"]) == str(finding.asset_id),
                )
            )
        return result

    def chain_step_count(self, chain_id: UUID) -> int:
        row = self.db.execute(
            text("select count(*) as c from chain_nodes where chain_id = :cid"), {"cid": str(chain_id)}
        ).mappings().first()
        return int(row["c"] if row else 0)

    def set_chain_score(self, chain_id: UUID, objective: float, exploitability: float, blast: float, detection: float, completeness: float) -> float:
        row = self.db.execute(
            text("select chain_rescore(:cid,:o,:e,:b,:d,:c) as score"),
            {"cid": str(chain_id), "o": objective, "e": exploitability, "b": blast, "d": detection, "c": completeness},
        ).mappings().first()
        return float(row["score"])
