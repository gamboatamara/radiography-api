import unittest
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.radiography_model import Radiography
from app.repositories.radiography_repository import RadiographyRepository


class RadiographyRepositoryExpirationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()
        self.repository = RadiographyRepository(self.db)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_create_sets_public_expiration_for_new_image(self) -> None:
        item = self.repository.create(
            {
                "full_name": "Juan Perez",
                "patient_code": "PAT-001",
                "clinical_description": "Fracture follow-up",
                "study_date": date(2026, 4, 17),
                "image_url": "https://example.com/xray.png",
            }
        )

        self.assertTrue(item.is_public)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.expires_at)
        self.assertGreater(item.expires_at, item.created_at)

    def test_get_by_id_marks_image_as_private_when_it_is_expired(self) -> None:
        now = datetime.now(timezone.utc)
        expired_item = Radiography(
            full_name="Ana Lopez",
            patient_code="PAT-002",
            clinical_description="Chest radiography",
            study_date=date(2026, 4, 17),
            image_url="https://example.com/expired.png",
            created_at=now - timedelta(days=2),
            is_public=True,
            expires_at=now - timedelta(minutes=1),
        )
        self.db.add(expired_item)
        self.db.commit()
        self.db.refresh(expired_item)

        loaded_item = self.repository.get_by_id(expired_item.id)

        self.assertIsNotNone(loaded_item)
        self.assertFalse(loaded_item.is_public)

    def test_update_image_resets_public_window(self) -> None:
        now = datetime.now(timezone.utc)
        item = Radiography(
            full_name="Luis Mora",
            patient_code="PAT-003",
            clinical_description="Control study",
            study_date=date(2026, 4, 17),
            image_url="https://example.com/old-image.png",
            created_at=now - timedelta(days=2),
            is_public=False,
            expires_at=now - timedelta(hours=1),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        updated_item = self.repository.update(
            item.id,
            {"image_url": "https://example.com/new-image.png"},
        )

        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item.image_url, "https://example.com/new-image.png")
        self.assertTrue(updated_item.is_public)
        self.assertGreater(
            self.repository._ensure_utc(updated_item.expires_at),
            self.repository._ensure_utc(now),
        )


if __name__ == "__main__":
    unittest.main()
