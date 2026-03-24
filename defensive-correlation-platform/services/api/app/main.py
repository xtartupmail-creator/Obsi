from fastapi import FastAPI
from .routers import findings, chains, hints

app = FastAPI(title="Defensive Exposure Correlation API", version="0.2.0")
app.include_router(findings.router)
app.include_router(chains.router)
app.include_router(hints.router)

@app.get("/healthz")
def health():
    return {"ok": True}
