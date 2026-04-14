from sqlalchemy.orm import Session
from app.models.radiography_model import Radiography


def create_radiography(db: Session, data) -> Radiography:
    try:
        radiography = Radiography(
            full_name=data["full_name"] if isinstance(data, dict) else data.full_name,
            patient_code=data["patient_code"] if isinstance(data, dict) else data.patient_code,
            clinical_description=data["clinical_description"] if isinstance(data, dict) else data.clinical_description,
            study_date=data["study_date"] if isinstance(data, dict) else data.study_date,
            image_url=data["image_url"] if isinstance(data, dict) else data.image_url,
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