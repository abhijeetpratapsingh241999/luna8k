from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.database import get_db
from ..models import Contact
from ..services.security import get_api_key

router = APIRouter(prefix="/contacts", tags=["contacts"], dependencies=[Depends(get_api_key)])


class ContactIn(BaseModel):
    id: str
    device_id: str
    name: str
    phone: str | None = None
    email: str | None = None


@router.post("/bulk")
async def upsert_contacts(contacts: list[ContactIn], db: AsyncSession = Depends(get_db)):
    for c in contacts:
        result = await db.execute(select(Contact).where(Contact.id == c.id))
        existing = result.scalar_one_or_none()
        if existing:
            existing.name = c.name
            existing.phone = c.phone
            existing.email = c.email
            existing.device_id = c.device_id
        else:
            db.add(Contact(id=c.id, device_id=c.device_id, name=c.name, phone=c.phone, email=c.email))
    await db.commit()
    return {"status": "ok", "count": len(contacts)}


@router.get("/{device_id}")
async def list_contacts(device_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.device_id == device_id))
    items = result.scalars().all()
    return [
        {"id": i.id, "device_id": i.device_id, "name": i.name, "phone": i.phone, "email": i.email}
        for i in items
    ]

