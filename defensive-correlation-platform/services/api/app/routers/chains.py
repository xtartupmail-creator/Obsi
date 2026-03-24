from fastapi import APIRouter

router = APIRouter(prefix="/v1/chains", tags=["chains"])

@router.get("/health")
def health_chain():
    return {"ok": True}
