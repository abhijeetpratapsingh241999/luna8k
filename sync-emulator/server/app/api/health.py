from fastapi import APIRouter, Depends
from ..services.security import get_api_key, current_api_key

router = APIRouter(prefix="/health", tags=["health"])  # no dependency to allow fetching key

@router.get("")
async def health():
    return {"status": "ok"}

@router.get("/key")
async def show_key():
    # In a real system, do not expose this. Here we show it for the emulator.
    return {"api_key": current_api_key()}
