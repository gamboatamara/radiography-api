from sqlalchemy import Column, Date, DateTime, Integer, String, func
from app.db.database import Base


class Radiography(Base):
    __tablename__ = "radiographies"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    patient_code = Column(String(50), nullable=False, unique=True, index=True)
    clinical_description = Column(String(255), nullable=False)
    study_date = Column(Date, nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())