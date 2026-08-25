from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "flowrebase-api"}


@router.get("/ready")
async def ready():
    return {"status": "ready"}
