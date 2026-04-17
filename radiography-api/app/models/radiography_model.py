from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, func, text
from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Radiography(Base):
    __tablename__ = "radiographies"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    patient_code = Column(String(50), nullable=False, unique=True, index=True)
    clinical_description = Column(String(255), nullable=False)
    study_date = Column(Date, nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
    is_public = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
