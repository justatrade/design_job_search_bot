from fastapi import APIRouter, HTTPException
from src.telegram.instance import tg
from src.models.auth import CodeSchema

router = APIRouter()

@router.post("/auth/start", tags=["Auth"])
async def start_auth():
    try:
        await tg.send_code()
        return {"status": "code_sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/confirm", tags=["Auth"])
async def confirm_auth(data: CodeSchema):
    try:
        await tg.confirm_code(data.code)
        return {"status": "authorized"}
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except NotImplementedError as ne:
        raise HTTPException(status_code=501, detail=str(ne))
