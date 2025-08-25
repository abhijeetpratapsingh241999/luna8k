from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from ..db.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # e.g., android, ios, emulator
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    capabilities = Column(JSON, nullable=True)
