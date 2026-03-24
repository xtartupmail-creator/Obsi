from __future__ import annotations

from app.integrations.opa_client import OPAClient


def check_policy(payload: dict) -> tuple[bool, list[str]]:
    client = OPAClient()
    try:
        return client.evaluate(payload)
    except Exception:
        # safe fallback: deny if cannot evaluate
        return False, ["policy_unavailable"]
