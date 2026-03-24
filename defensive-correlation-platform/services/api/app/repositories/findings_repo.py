from __future__ import annotations

from dataclasses import asdict
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities import Finding


class FindingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_asset(self, tenant_id: UUID, asset_id: UUID, fqdn: str | None = None, ip: str | None = None) -> None:
        self.db.execute(
            text(
                """
                insert into assets (asset_id, tenant_id, fqdn, ip_address)
                values (:asset_id, :tenant_id, :fqdn, cast(:ip as inet))
                on conflict (asset_id) do update
                set fqdn = coalesce(excluded.fqdn, assets.fqdn),
                    ip_address = coalesce(excluded.ip_address, assets.ip_address)
                """
            ),
            {"asset_id": str(asset_id), "tenant_id": str(tenant_id), "fqdn": fqdn, "ip": ip},
        )

    def insert_finding(self, finding: Finding) -> None:
        payload: dict[str, Any] = asdict(finding)
        payload["finding_id"] = str(finding.finding_id)
        payload["tenant_id"] = str(finding.tenant_id)
        payload["asset_id"] = str(finding.asset_id)
        payload["next_probe_hints"] = [asdict(h) for h in finding.next_probe_hints]

        self.db.execute(
            text(
                """
                insert into agent_findings (
                    finding_id, tenant_id, agent_id, asset_id, finding_type, severity, confidence,
                    technique_ids, tactic_phase, chain_tags, attack_vector_tags,
                    next_probe_hints, raw_evidence, created_at
                ) values (
                    :finding_id, :tenant_id, :agent_id, :asset_id, :finding_type, :severity, :confidence,
                    :technique_ids, :tactic_phase, :chain_tags, :attack_vector_tags,
                    cast(:next_probe_hints as jsonb), cast(:raw_evidence as jsonb), :created_at
                ) on conflict (finding_id) do nothing
                """
            ),
            {
                **payload,
                "next_probe_hints": str(payload["next_probe_hints"]).replace("'", '"'),
                "raw_evidence": str(payload["raw_evidence"]).replace("'", '"'),
            },
        )

    def get_finding(self, finding_id: UUID) -> dict[str, Any] | None:
        row = self.db.execute(
            text("select * from agent_findings where finding_id = :id"),
            {"id": str(finding_id)},
        ).mappings().first()
        return dict(row) if row else None
