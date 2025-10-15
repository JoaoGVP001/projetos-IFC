from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["root"])
async def health():
    return {"status": "ok"}


