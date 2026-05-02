from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.mt5_handler import process_mt5_signal

router = APIRouter()

class MT5Payload(BaseModel):
    action: str
    ticket: int
    symbol: str
    type: str
    price: float
    sl: float
    tp: float

@router.post("/webhook/mt5")
async def mt5_webhook(payload: MT5Payload, request: Request):
    client = getattr(request.app.state, "bot", None)
    if not client:
        raise HTTPException(status_code=500, detail="Pyrogram Client not initialized in app state")
    
    # Process signal in background or await directly
    await process_mt5_signal(client, payload.model_dump())
    
    return {"status": "success"}
