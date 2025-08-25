from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="device")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="device")
    files: Mapped[list["FileObject"]] = relationship("FileObject", back_populates="device")


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("device_id", "phone", name="uq_contact_device_phone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(64))
    email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device: Mapped[Device] = relationship("Device", back_populates="contacts")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("device_id", "external_id", name="uq_msg_device_external"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str] = mapped_column(String(64))
    sender: Mapped[str] = mapped_column(String(128))
    recipient: Mapped[str] = mapped_column(String(128))
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device: Mapped[Device] = relationship("Device", back_populates="messages")


class FileObject(Base):
    __tablename__ = "files"
    __table_args__ = (
        UniqueConstraint("device_id", "external_id", name="uq_file_device_external"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str] = mapped_column(String(64))
    path: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device: Mapped[Device] = relationship("Device", back_populates="files")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(128))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

