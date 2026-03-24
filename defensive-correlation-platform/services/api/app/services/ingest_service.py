from sqlalchemy import text
from ..schemas import FindingEvent
from .chain_engine import decide_action, new_chain_id
from .event_bus import publish


def ingest_finding(db, finding: FindingEvent):
    db.execute(text("""
      insert into agent_findings (
        finding_id, tenant_id, run_id, agent_id, asset_id, finding_type, severity,
        confidence, technique_ids, tactic_phase, chain_tags, attack_vector_tags,
        next_probe_hints, raw_evidence, created_at
      ) values (
        :finding_id, :tenant_id, :run_id, :agent_id, :asset_id, :finding_type, :severity,
        :confidence, :technique_ids, :tactic_phase, :chain_tags, :attack_vector_tags,
        cast(:next_probe_hints as jsonb), cast(:raw_evidence as jsonb), :created_at
      ) on conflict (finding_id) do nothing;
    """), {
      "finding_id": str(finding.finding_id),
      "tenant_id": str(finding.tenant_id),
      "run_id": str(finding.run_id) if finding.run_id else None,
      "agent_id": finding.agent_id,
      "asset_id": str(finding.asset_id),
      "finding_type": finding.finding_type,
      "severity": finding.severity,
      "confidence": finding.confidence,
      "technique_ids": finding.technique_ids,
      "tactic_phase": finding.tactic_phase,
      "chain_tags": finding.chain_tags,
      "attack_vector_tags": finding.attack_vector_tags,
      "next_probe_hints": finding.model_dump_json(include={"next_probe_hints"}),
      "raw_evidence": finding.model_dump_json(include={"raw_evidence"}),
      "created_at": finding.created_at
    })

    action = decide_action(0.2)
    chain_id = None
    if action == "seed":
      chain_id = new_chain_id()
      db.execute(text("""
        insert into risk_chains (chain_id, tenant_id, chain_status)
        values (:chain_id, :tenant_id, 'POTENTIAL')
      """), {"chain_id": str(chain_id), "tenant_id": str(finding.tenant_id)})

    db.commit()

    publish(
      topic="finding.ingested.v1",
      key=str(finding.finding_id),
      payload={
        "schema_version": "v1",
        "tenant_id": str(finding.tenant_id),
        "finding_id": str(finding.finding_id),
        "asset_id": str(finding.asset_id),
        "chain_tags": finding.chain_tags,
        "attack_vector_tags": finding.attack_vector_tags,
        "created_at": finding.created_at.isoformat()
      }
    )

    return action, chain_id
