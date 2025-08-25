from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.database import get_db
from ..models import Message
from ..services.security import get_api_key
import datetime as dt

router = APIRouter(prefix="/messages", tags=["messages"], dependencies=[Depends(get_api_key)])


class MessageIn(BaseModel):
    id: str
    device_id: str
    direction: str
    contact_id: str | None = None
    content: str
    timestamp: float  # epoch seconds


@router.post("/bulk")
async def upsert_messages(messages: list[MessageIn], db: AsyncSession = Depends(get_db)):
    for m in messages:
        result = await db.execute(select(Message).where(Message.id == m.id))
        existing = result.scalar_one_or_none()
        ts = dt.datetime.fromtimestamp(float(m.timestamp), tz=dt.timezone.utc)
        if existing:
            existing.device_id = m.device_id
            existing.direction = m.direction
            existing.contact_id = m.contact_id
            existing.content = m.content
            existing.timestamp = ts
        else:
            db.add(
                Message(
                    id=m.id,
                    device_id=m.device_id,
                    direction=m.direction,
                    contact_id=m.contact_id,
                    content=m.content,
                    timestamp=ts,
                )
            )
    await db.commit()
    return {"status": "ok", "count": len(messages)}


@router.get("/{device_id}")
async def list_messages(device_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.device_id == device_id))
    items = result.scalars().all()
    return [
        {
            "id": i.id,
            "device_id": i.device_id,
            "direction": i.direction,
            "contact_id": i.contact_id,
            "content": i.content,
            "timestamp": i.timestamp.timestamp() if i.timestamp else None,
        }
        for i in items
    ]

