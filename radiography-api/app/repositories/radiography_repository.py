from sqlalchemy.orm import Session
from app.models.radiography_model import Radiography


def create_radiography(db: Session, data) -> Radiography:
    try:
        radiography = Radiography(
            image_url=data["image_url"] if isinstance(data, dict) else data.image_url,
            diagnosis=data["diagnosis"] if isinstance(data, dict) else data.diagnosis,
        )
        db.add(radiography)
        db.commit()
        db.refresh(radiography)
        return radiography
    except Exception:
        db.rollback()
        raise


def get_all_radiographies(db: Session) -> list[Radiography]:
    return db.query(Radiography).all()


def get_radiography_by_id(db: Session, id: int) -> Radiography | None:
    return db.query(Radiography).filter(Radiography.id == id).first()