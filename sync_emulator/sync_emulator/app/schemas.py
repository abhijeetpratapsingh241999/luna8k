from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    device_id: str
    name: str


class DeviceRead(BaseModel):
    id: int
    device_id: str
    name: str
    last_seen_at: datetime

    class Config:
        from_attributes = True


class ContactUpsert(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContactRead(BaseModel):
    id: int
    device_id: int
    name: str
    phone: str
    email: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageUpsert(BaseModel):
    external_id: str
    sender: str
    recipient: str
    content: str
    sent_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MessageRead(BaseModel):
    id: int
    device_id: int
    external_id: str
    sender: str
    recipient: str
    content: str
    sent_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUpsert(BaseModel):
    external_id: str
    path: str
    mime_type: str
    size_bytes: int
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FileRead(BaseModel):
    id: int
    device_id: int
    external_id: str
    path: str
    mime_type: str
    size_bytes: int
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    title: str
    body: str


class NotificationRead(BaseModel):
    id: int
    device_id: int
    title: str
    body: str
    created_at: datetime

    class Config:
        from_attributes = True

