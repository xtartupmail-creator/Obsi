from __future__ import annotations

from fastapi import FastAPI

from .core.logging import configure_logging
from .routers import chains, findings, hints

configure_logging()

app = FastAPI(title="Defensive Exposure Correlation API", version="0.3.0")
app.include_router(findings.router)
app.include_router(chains.router)
app.include_router(hints.router)


@app.get("/healthz")
def health():
    return {"ok": True, "service": "correlation-api"}
