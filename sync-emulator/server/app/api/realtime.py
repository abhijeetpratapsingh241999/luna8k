from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from ..db.database import AsyncSessionLocal
from ..models import Device
from ..services.security import current_api_key

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/heartbeat")
async def heartbeat_ws(websocket: WebSocket):
    # API key and device id via query params for simplicity in emulator
    await websocket.accept()
    device_id = websocket.query_params.get("device_id")
    api_key = websocket.query_params.get("api_key")
    if api_key != current_api_key():
        await websocket.close(code=4401)
        return
    if not device_id:
        await websocket.close(code=4400)
        return

    try:
        while True:
            # Receive any text frame as a heartbeat tick
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break

            async with AsyncSessionLocal() as db:  # type: AsyncSession
                result = await db.execute(select(Device).where(Device.id == device_id))
                device = result.scalar_one_or_none()
                if device is not None:
                    device.last_seen = func.now()
                    await db.commit()
    except WebSocketDisconnect:
        # Client disconnected
        return
