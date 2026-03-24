from __future__ import annotations

import requests

from app.config import settings


class OPAClient:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or settings.opa_url

    def evaluate(self, input_payload: dict) -> tuple[bool, list[str]]:
        response = requests.post(self.url, json={"input": input_payload}, timeout=2)
        response.raise_for_status()
        result = response.json().get("result", {})
        allow = bool(result.get("allow", False))
        deny = result.get("deny", [])
        if isinstance(deny, str):
            deny = [deny]
        return allow, deny
