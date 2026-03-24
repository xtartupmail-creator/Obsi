from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities import Hint


class HintsRepository:
    def __init__(self, db: Session):
        self.db = db

    def enqueue_hints(self, tenant_id: UUID, source_agent: str, hints: list[Hint]) -> None:
        for h in hints:
            self.db.execute(
                text(
                    """
                    insert into finding_links (link_id, tenant_id, source_id, target_id, link_type, confidence, link_reason)
                    values (gen_random_uuid(), :tid, gen_random_uuid(), gen_random_uuid(), 'bridge', :conf, :reason)
                    """
                ),
                {"tid": str(tenant_id), "conf": h.priority / 10.0, "reason": f"hint:{source_agent}->{h.agent}:{h.target}"},
            )

    def list_next(self, tenant_id: UUID, limit: int = 25) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                select finding_id, next_probe_hints, created_at
                from agent_findings
                where tenant_id = :tid
                  and jsonb_array_length(next_probe_hints) > 0
                order by created_at desc
                limit :limit
                """
            ),
            {"tid": str(tenant_id), "limit": limit},
        ).mappings().all()

        out: list[dict] = []
        for r in rows:
            hints = r["next_probe_hints"]
            if isinstance(hints, str):
                hints = json.loads(hints)
            out.append({"finding_id": str(r["finding_id"]), "hints": hints, "created_at": r["created_at"].isoformat()})
        return out
