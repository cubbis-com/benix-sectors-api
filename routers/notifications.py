"""
WhatsApp Notifications & Alert Router.
Integrates with WhatsApp Reporting Gateway for automated briefing and alerts.
"""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
import httpx
from config import settings
from services.briefing_service import generate_daily_market_briefing

router = APIRouter(prefix="/notifications", tags=["WhatsApp Notifications"])

class WhatsAppSendRequest(BaseModel):
    to: Optional[str] = Field(None, description="Destination phone number (e.g. 6281805040354)")
    message: str = Field(..., description="Message text (supports WhatsApp markdown)")

class WhatsAppBroadcastResponse(BaseModel):
    status: str
    target: str
    briefing_timestamp: str
    gateway_response: dict

async def send_wa_message(to: str, message: str) -> dict:
    """Send text to WhatsApp Gateway API."""
    headers = {
        "Authorization": f"Bearer {settings.WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to,
        "message": message
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(settings.WA_GATEWAY_URL, json=payload, headers=headers)
        return res.json()

@router.post("/whatsapp/send", summary="Send Custom WhatsApp Message")
async def send_whatsapp(payload: WhatsAppSendRequest):
    target = payload.to or settings.WA_DEFAULT_TARGET
    result = await send_wa_message(to=target, message=payload.message)
    return {
        "status": "success",
        "target": target,
        "result": result
    }

@router.post("/whatsapp/broadcast-briefing", response_model=WhatsAppBroadcastResponse, summary="Generate & Broadcast Market Briefing to WhatsApp")
async def broadcast_market_briefing(to: Optional[str] = None):
    """
    Pulls real-time / cached Sectors API data, formats an executive market brief,
    and sends it directly to WhatsApp.
    """
    target = to or settings.WA_DEFAULT_TARGET
    briefing = await generate_daily_market_briefing()
    wa_res = await send_wa_message(to=target, message=briefing["message"])

    return WhatsAppBroadcastResponse(
        status="sent",
        target=target,
        briefing_timestamp=briefing["timestamp"],
        gateway_response=wa_res
    )
