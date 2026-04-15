from typing import Optional
from sqlalchemy.orm import Session
from app.models.radiography_model import Radiography


class RadiographyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Radiography:
        try:
            new_item = Radiography(
                full_name=data["full_name"],
                patient_code=data["patient_code"],
                clinical_description=data["clinical_description"],
                study_date=data["study_date"],
                image_url=data.get("image_url"),
            )
            self.db.add(new_item)
            self.db.commit()
            self.db.refresh(new_item)
            return new_item
        except Exception:
            self.db.rollback()
            raise

    def get_all(self) -> list[Radiography]:
        return self.db.query(Radiography).all()

    def get_by_id(self, item_id: int) -> Optional[Radiography]:
        return self.db.query(Radiography).filter(Radiography.id == item_id).first()

    def get_by_patient_code(self, patient_code: str) -> Optional[Radiography]:
        return (
            self.db.query(Radiography)
            .filter(Radiography.patient_code == patient_code)
            .first()
        )

    def update(self, item_id: int, data: dict) -> Optional[Radiography]:
        item = self.get_by_id(item_id)
        if not item:
            return None

        for key, value in data.items():
            setattr(item, key, value)

        try:
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception:
            self.db.rollback()
            raise

    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False

        try:
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise