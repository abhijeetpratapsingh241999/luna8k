from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import Contact, Device, FileObject, Message, Notification


router = APIRouter(prefix="/query", tags=["query"])


@router.get("/devices")
def list_devices(db: Session = Depends(get_db)):
    rows = db.execute(select(Device).order_by(Device.id.desc())).scalars().all()
    return rows


@router.get("/{device_id}/contacts")
def list_contacts(device_id: str, db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    rows = db.execute(select(Contact).where(Contact.device_id == device.id).order_by(Contact.id.desc())).scalars().all()
    return rows


@router.get("/{device_id}/messages")
def list_messages(device_id: str, db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    rows = db.execute(select(Message).where(Message.device_id == device.id).order_by(Message.id.desc())).scalars().all()
    return rows


@router.get("/{device_id}/files")
def list_files(device_id: str, db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    rows = db.execute(select(FileObject).where(FileObject.device_id == device.id).order_by(FileObject.id.desc())).scalars().all()
    return rows


@router.get("/{device_id}/notifications")
def list_notifications(device_id: str, db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    rows = db.execute(select(Notification).where(Notification.device_id == device.id).order_by(Notification.id.desc())).scalars().all()
    return rows

