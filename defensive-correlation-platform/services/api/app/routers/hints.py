from fastapi import APIRouter

router = APIRouter(prefix="/v1/hints", tags=["hints"])

@router.get("/next")
def next_hint():
    return {"items": []}
