import unittest
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.radiography_model import Radiography
from app.repositories.radiography_repository import RadiographyRepository
from app.schemas.auth_schema import UserResponse
from app.services.radiography_service import RadiographyService


class RadiographyServiceExpirationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()
        self.repository = RadiographyRepository(self.db)
        self.service = RadiographyService(self.repository)
        self.user = UserResponse(
            email="test@example.com",
            name="Test User",
            google_id="google-user-123",
        )

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _create_item(
        self,
        *,
        patient_code: str,
        created_at: datetime,
        is_public: bool = True,
        expires_at: datetime | None = None,
    ) -> Radiography:
        item = Radiography(
            full_name="Paciente Demo",
            patient_code=patient_code,
            clinical_description="Demo radiography",
            study_date=date(2026, 4, 19),
            image_url=(
                "https://res.cloudinary.com/demo/image/upload/"
                "v123/radiographies/example.png"
            ),
            created_at=created_at,
            is_public=is_public,
            expires_at=expires_at or (created_at + timedelta(hours=24)),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def test_generate_image_token_rejects_expired_image(self) -> None:
        now = datetime.now(timezone.utc)
        item = self._create_item(
            patient_code="PAT-EXP-TOKEN",
            created_at=now - timedelta(days=2),
            is_public=False,
            expires_at=now - timedelta(minutes=1),
        )

        with self.assertRaises(HTTPException) as context:
            self.service.generate_image_token(
                item.id,
                self.user,
                "http://testserver/api/v1/radiography/1/image-access",
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_get_signed_image_access_rejects_expired_image(self) -> None:
        now = datetime.now(timezone.utc)
        item = self._create_item(
            patient_code="PAT-EXP-SIGNED",
            created_at=now,
        )
        image_token = self.service.generate_image_token(
            item.id,
            self.user,
            "http://testserver/api/v1/radiography/1/image-access",
        )

        item.is_public = False
        item.expires_at = now - timedelta(minutes=1)
        self.db.commit()
        self.db.refresh(item)

        with self.assertRaises(HTTPException) as context:
            self.service.get_signed_image_access(
                item.id,
                image_token.access_token,
                self.user,
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_get_signed_image_access_caps_short_url_to_daily_expiration(self) -> None:
        now = datetime.now(timezone.utc)
        item = self._create_item(
            patient_code="PAT-CAP-URL",
            created_at=now - timedelta(hours=23, minutes=59, seconds=35),
            expires_at=now + timedelta(seconds=25),
        )
        image_token = self.service.generate_image_token(
            item.id,
            self.user,
            "http://testserver/api/v1/radiography/1/image-access",
        )

        signed = self.service.get_signed_image_access(
            item.id,
            image_token.access_token,
            self.user,
        )

        self.assertGreaterEqual(signed.expires_in_seconds, 1)
        self.assertLessEqual(signed.expires_in_seconds, 25)
        self.assertLessEqual(
            signed.expires_at,
            self.repository._ensure_utc(item.expires_at),
        )


if __name__ == "__main__":
    unittest.main()
