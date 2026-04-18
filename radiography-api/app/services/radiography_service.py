from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import hashlib
import hmac

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.repositories.radiography_repository import RadiographyRepository
from app.schemas.auth_schema import UserResponse
from app.schemas.radiography_schema import (
    RadiographyImageTokenResponse,
    SignedImageUrlResponse,
)
from app.core.config import settings


class RadiographyService:
    def __init__(self, repository: RadiographyRepository):
        self.repository = repository

    def create_radiography(self, data: dict):
        existing = self.repository.get_by_patient_code(data["patient_code"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with this patient_code already exists",
            )

        return self.repository.create(data)

    def list_radiographies(
        self,
        page: int = 1,
        limit: int = 10,
        full_name: str | None = None,
        patient_code: str | None = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> dict:
        items = self.repository.get_all()

        if full_name:
            items = [
                item for item in items
                if full_name.lower() in item.full_name.lower()
            ]

        if patient_code:
            items = [
                item for item in items
                if patient_code.lower() in item.patient_code.lower()
            ]

        allowed_sort_fields = {"id", "full_name", "patient_code", "study_date"}
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by. Use one of: {', '.join(sorted(allowed_sort_fields))}",
            )

        reverse = order.lower() == "desc"
        items = sorted(items, key=lambda x: getattr(x, sort_by), reverse=reverse)

        total = len(items)
        start = (page - 1) * limit
        end = start + limit
        paginated_items = items[start:end]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": paginated_items,
        }

    def get_radiography_by_id(self, item_id: int):
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found",
            )
        return item

    def update_radiography(self, item_id: int, data: dict):
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found",
            )

        if "patient_code" in data and data["patient_code"] != item.patient_code:
            existing = self.repository.get_by_patient_code(data["patient_code"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A record with this patient_code already exists",
                )

        updated = self.repository.update(item_id, data)
        return updated

    def delete_radiography(self, item_id: int) -> dict:
        deleted = self.repository.delete(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found",
            )

        return {"message": "Record deleted successfully"}

    def generate_image_token(
        self,
        item_id: int,
        user: UserResponse,
        image_access_url: str,
    ) -> RadiographyImageTokenResponse:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Radiography record not found",
            )

        if not item.image_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Radiography image not found",
            )

        expires_in_minutes = 5
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        payload = {
            "sub": user.google_id,
            "item_id": item.id,
            "image_url": item.image_url,
            "exp": expires_at,
        }

        access_token = jwt.encode(
            payload,
            settings.AUTH_TOKEN_KEY,
            algorithm="HS256",
        )

        return RadiographyImageTokenResponse(
            image_id=item.id,
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=expires_in_minutes,
            expires_at=expires_at,
            image_access_url=f"{image_access_url}?token={access_token}",
        )

    def get_signed_image_access(
        self,
        item_id: int,
        token: str,
        user: UserResponse,
    ) -> SignedImageUrlResponse:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Radiography record not found",
            )

        if not item.image_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Radiography image not found",
            )

        try:
            payload = jwt.decode(
                token,
                settings.AUTH_TOKEN_KEY,
                algorithms=["HS256"],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired image token",
            )

        token_google_id = payload.get("sub")
        token_item_id = payload.get("item_id")
        token_image_url = payload.get("image_url")

        if token_google_id != user.google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Image token does not belong to the current user",
            )

        if token_item_id != item_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Image token does not match the requested radiography",
            )

        if token_image_url != item.image_url:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Image token is not valid for the current image",
            )

        expires_in_seconds = settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        exp = int(expires_at.timestamp())

        parsed = urlparse(item.image_url)
        path_parts = parsed.path.split("/")

        try:
            upload_index = path_parts.index("upload")
            public_id_with_ext = "/".join(path_parts[upload_index + 2 :])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not parse stored image URL",
            )

        if "." in public_id_with_ext:
            public_id = public_id_with_ext.rsplit(".", 1)[0]
        else:
            public_id = public_id_with_ext

        delivery_type = "upload"

        data_to_sign = f"{public_id}:{delivery_type}:{exp}:{settings.AUTH_TOKEN_KEY}"
        sig = hmac.new(
            settings.AUTH_TOKEN_KEY.encode("utf-8"),
            data_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:32]

        signed_url = (
            f"/api/v1/radiography/image-secure"
            f"?public_id={public_id}"
            f"&delivery_type={delivery_type}"
            f"&exp={exp}"
            f"&sig={sig}"
        )

        return SignedImageUrlResponse(
            image_id=item.id,
            signed_url=signed_url,
            expires_at=expires_at,
            expires_in_seconds=expires_in_seconds,
            token_subject_google_id=user.google_id,
        )