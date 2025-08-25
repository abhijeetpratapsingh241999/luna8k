from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import Contact, Device, FileObject, Message, Notification
from ..schemas import (
    ContactUpsert,
    ContactRead,
    DeviceCreate,
    DeviceRead,
    FileUpsert,
    FileRead,
    MessageUpsert,
    MessageRead,
    NotificationCreate,
    NotificationRead,
)


router = APIRouter(prefix="/sync", tags=["sync"])


def get_or_create_device(db: Session, device_id: str, name: str) -> Device:
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        device = Device(device_id=device_id, name=name, last_seen_at=datetime.utcnow())
        db.add(device)
        db.commit()
        db.refresh(device)
    else:
        device.last_seen_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
    return device


@router.post("/device", response_model=DeviceRead)
def register_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    device = get_or_create_device(db, payload.device_id, payload.name)
    return device


@router.post("/{device_id}/contacts:upsert", response_model=List[ContactRead])
def upsert_contacts(
    device_id: str = Path(..., description="Stable device ID"),
    items: List[ContactUpsert] = None,
    db: Session = Depends(get_db),
):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    results: list[Contact] = []
    for item in items or []:
        contact = db.execute(
            select(Contact).where(Contact.device_id == device.id, Contact.phone == item.phone)
        ).scalar_one_or_none()
        if contact is None:
            contact = Contact(device_id=device.id, name=item.name, phone=item.phone, email=item.email, updated_at=item.updated_at)
            db.add(contact)
        else:
            if item.updated_at >= contact.updated_at:
                contact.name = item.name
                contact.email = item.email
                contact.updated_at = item.updated_at
        results.append(contact)
    db.commit()
    for c in results:
        db.refresh(c)
    return results


@router.post("/{device_id}/messages:upsert", response_model=List[MessageRead])
def upsert_messages(
    device_id: str,
    items: List[MessageUpsert],
    db: Session = Depends(get_db),
):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    results: list[Message] = []
    for item in items or []:
        message = db.execute(
            select(Message).where(Message.device_id == device.id, Message.external_id == item.external_id)
        ).scalar_one_or_none()
        if message is None:
            message = Message(
                device_id=device.id,
                external_id=item.external_id,
                sender=item.sender,
                recipient=item.recipient,
                content=item.content,
                sent_at=item.sent_at,
                updated_at=item.updated_at,
            )
            db.add(message)
        else:
            if item.updated_at >= message.updated_at:
                message.sender = item.sender
                message.recipient = item.recipient
                message.content = item.content
                message.sent_at = item.sent_at
                message.updated_at = item.updated_at
        results.append(message)
    db.commit()
    for m in results:
        db.refresh(m)
    return results


@router.post("/{device_id}/files:upsert", response_model=List[FileRead])
def upsert_files(device_id: str, items: List[FileUpsert], db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    results: list[FileObject] = []
    for item in items or []:
        fo = db.execute(
            select(FileObject).where(FileObject.device_id == device.id, FileObject.external_id == item.external_id)
        ).scalar_one_or_none()
        if fo is None:
            fo = FileObject(
                device_id=device.id,
                external_id=item.external_id,
                path=item.path,
                mime_type=item.mime_type,
                size_bytes=item.size_bytes,
                updated_at=item.updated_at,
            )
            db.add(fo)
        else:
            if item.updated_at >= fo.updated_at:
                fo.path = item.path
                fo.mime_type = item.mime_type
                fo.size_bytes = item.size_bytes
                fo.updated_at = item.updated_at
        results.append(fo)
    db.commit()
    for f in results:
        db.refresh(f)
    return results


@router.post("/{device_id}/notifications", response_model=NotificationRead)
def create_notification(device_id: str, item: NotificationCreate, db: Session = Depends(get_db)):
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    notif = Notification(device_id=device.id, title=item.title, body=item.body)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

