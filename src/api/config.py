from fastapi import APIRouter
from src.telegram.instance import tg

router = APIRouter()

@router.post("/config/filtering/on", tags=["Config"])
async def enable_filtering():
    tg.toggle_filtering(True)
    return {"filtering": "enabled"}

@router.post("/config/filtering/off", tags=["Config"])
async def disable_filtering():
    tg.toggle_filtering(False)
    return {"filtering": "disabled"}
