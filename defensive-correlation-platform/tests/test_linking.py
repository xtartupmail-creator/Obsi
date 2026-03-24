from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities import Finding
from app.domain.linking import CandidateSnapshot, choose_link


def test_choose_link_seed_without_candidates():
    finding = Finding(
        finding_id=uuid4(),
        tenant_id=uuid4(),
        agent_id="EXT-01",
        asset_id=uuid4(),
        finding_type="exposure",
        severity="high",
        confidence=0.8,
        chain_tags=["a"],
        attack_vector_tags=["web"],
    )
    outcome = choose_link(finding, [])
    assert outcome.decision.value == "seed"


def test_choose_link_append_when_strong_overlap():
    asset_id = uuid4()
    finding = Finding(
        finding_id=uuid4(),
        tenant_id=uuid4(),
        agent_id="EXT-01",
        asset_id=asset_id,
        finding_type="exposure",
        severity="high",
        confidence=0.9,
        chain_tags=["credential-risk", "lateral"],
        attack_vector_tags=["identity", "smb"],
    )
    cand = CandidateSnapshot(
        chain_id=uuid4(),
        last_finding_id=uuid4(),
        last_chain_tags=["credential-risk", "lateral"],
        last_vector_tags=["identity", "smb"],
        last_created_at=datetime.now(timezone.utc),
        same_asset=True,
    )
    outcome = choose_link(finding, [cand])
    assert outcome.decision.value in {"append", "merge"}
