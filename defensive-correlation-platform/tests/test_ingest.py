from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_chains_health():
    r = client.get("/v1/chains/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
