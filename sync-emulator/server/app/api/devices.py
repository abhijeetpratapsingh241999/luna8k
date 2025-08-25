from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.database import get_db
from ..models import Device
from ..services.security import get_api_key

router = APIRouter(prefix="/devices", tags=["devices"], dependencies=[Depends(get_api_key)])

class DeviceIn(BaseModel):
    id: str
    name: str
    platform: str
    capabilities: dict | None = None

class DeviceOut(DeviceIn):
    last_seen: str | None = None

@router.post("/register", response_model=DeviceOut)
async def register_device(device: DeviceIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).where(Device.id == device.id))
    existing = result.scalar_one_or_none()
    if existing:
        existing.name = device.name
        existing.platform = device.platform
        existing.capabilities = device.capabilities
        await db.commit()
        return DeviceOut(**device.model_dump(), last_seen=existing.last_seen.isoformat() if existing.last_seen else None)

    d = Device(id=device.id, name=device.name, platform=device.platform, capabilities=device.capabilities)
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return DeviceOut(**device.model_dump(), last_seen=d.last_seen.isoformat() if d.last_seen else None)
