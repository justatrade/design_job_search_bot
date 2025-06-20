from fastapi import APIRouter
from src.telegram.instance import tg

router = APIRouter()

@router.get("/chats", tags=["Chats"])
async def get_chats():
    chats = await tg.get_chats()
    return {"chats": chats}
