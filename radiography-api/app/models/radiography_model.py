from sqlalchemy import Column, DateTime, Integer, String, func
from app.db.database import Base

class Radiography(Base):
    __tablename__ = "radiographies"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    diagnosis = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())