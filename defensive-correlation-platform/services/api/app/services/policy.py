import requests
from ..config import settings

def check_policy(payload: dict) -> tuple[bool, list[str]]:
    resp = requests.post(settings.opa_url, json={"input": payload}, timeout=2)
    resp.raise_for_status()
    result = resp.json().get("result", {})
    allow = result.get("allow", False)
    deny = result.get("deny", [])
    if isinstance(deny, str):
        deny = [deny]
    return allow, deny
