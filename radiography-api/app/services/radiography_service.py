from fastapi import HTTPException, status

from app.schemas.auth_schema import UserResponse
from app.repositories.radiography_repository import RadiographyRepository
from app.services.auth_service import (
    generate_radiography_image_token,
    validate_radiography_image_token,
)
from app.services.cloudinary_service import generate_signed_image_url


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

    def generate_image_token(
        self,
        item_id: int,
        user: UserResponse,
        image_access_url: str,
    ) -> dict:
        item = self.get_radiography_by_id(item_id)
        if not item.image_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This radiography does not have an image",
            )

        token_data = generate_radiography_image_token(image_id=item.id, user=user)
        token_data["image_access_url"] = (
            f"{image_access_url}?token={token_data['access_token']}"
        )
        return token_data

    def get_signed_image_access(
        self,
        item_id: int,
        token: str,
        user: UserResponse,
    ) -> dict:
        item = self.get_radiography_by_id(item_id)
        if not item.image_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This radiography does not have an image",
            )

        token_payload = validate_radiography_image_token(
            token=token,
            image_id=item.id,
            user=user,
        )
        signed_image_data = generate_signed_image_url(item.image_url)

        return {
            "image_id": item.id,
            "signed_url": signed_image_data["signed_url"],
            "expires_at": signed_image_data["expires_at"],
            "expires_in_seconds": signed_image_data["expires_in_seconds"],
            "token_subject_google_id": token_payload["google_id"],
        }

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
