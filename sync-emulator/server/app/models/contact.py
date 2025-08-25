from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..db.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True)
    device_id = Column(String, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

