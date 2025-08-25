from sqlalchemy import Column, String, DateTime, Text
from ..db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    device_id = Column(String, index=True)
    direction = Column(String, nullable=False)  # inbound | outbound
    contact_id = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True)

