from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.radiography_model import Radiography


class RadiographyRepository:
    PUBLIC_IMAGE_DURATION_HOURS = 24

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def build_public_expiration(cls, created_at: datetime) -> datetime:
        return cls._ensure_utc(created_at) + timedelta(
            hours=cls.PUBLIC_IMAGE_DURATION_HOURS
        )

    @classmethod
    def image_is_no_longer_public(cls, item: Radiography) -> bool:
        return cls._ensure_utc(item.expires_at) <= cls._utc_now()

    def _refresh_public_status(self, item: Optional[Radiography]) -> Optional[Radiography]:
        if not item:
            return None

        if item.is_public and self.image_is_no_longer_public(item):
            item.is_public = False
            try:
                self.db.commit()
                self.db.refresh(item)
            except Exception:
                self.db.rollback()
                raise

        return item

    def create(self, data: dict) -> Radiography:
        created_at = data.get("created_at") or self._utc_now()
        expires_at = data.get("expires_at") or self.build_public_expiration(created_at)

        try:
            new_item = Radiography(
                full_name=data["full_name"],
                patient_code=data["patient_code"],
                clinical_description=data["clinical_description"],
                study_date=data["study_date"],
                image_url=data.get("image_url"),
                created_at=created_at,
                is_public=data.get("is_public", True),
                expires_at=expires_at,
            )
            self.db.add(new_item)
            self.db.commit()
            self.db.refresh(new_item)
            return new_item
        except Exception:
            self.db.rollback()
            raise

    def get_all(self) -> list[Radiography]:
        items = self.db.query(Radiography).all()
        return [self._refresh_public_status(item) for item in items]

    def get_by_id(self, item_id: int) -> Optional[Radiography]:
        item = self.db.query(Radiography).filter(Radiography.id == item_id).first()
        return self._refresh_public_status(item)

    def get_by_patient_code(self, patient_code: str) -> Optional[Radiography]:
        item = (
            self.db.query(Radiography)
            .filter(Radiography.patient_code == patient_code)
            .first()
        )
        return self._refresh_public_status(item)

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
