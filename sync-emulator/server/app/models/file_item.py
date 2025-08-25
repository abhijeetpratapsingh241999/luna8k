from sqlalchemy import Column, String, Integer, DateTime, LargeBinary
from sqlalchemy.sql import func
from ..db.database import Base

class FileItem(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True)
    device_id = Column(String, index=True)
    path = Column(String, index=True)
    size = Column(Integer)
    mtime = Column(DateTime(timezone=True))
    hash = Column(String, index=True)
    content = Column(LargeBinary, nullable=True)  # optional, for small files
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
