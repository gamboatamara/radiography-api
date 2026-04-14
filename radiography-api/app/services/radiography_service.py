from fastapi import HTTPException, status
from app.repositories.radiography_repository import RadiographyRepository


class RadiographyService:
    def __init__(self, repository: RadiographyRepository):
        self.repository = repository

    def create_radiography(self, data: dict) -> dict:
        existing = self.repository.get_by_patient_code(data["patient_code"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un registro con ese patient_code",
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
                if full_name.lower() in item["full_name"].lower()
            ]

        if patient_code:
            items = [
                item for item in items
                if patient_code.lower() in item["patient_code"].lower()
            ]

        allowed_sort_fields = {"id", "full_name", "patient_code", "study_date"}
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"sort_by inválido. Use uno de: {', '.join(sorted(allowed_sort_fields))}",
            )

        reverse = order.lower() == "desc"
        items = sorted(items, key=lambda x: x[sort_by], reverse=reverse)

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

    def get_radiography_by_id(self, item_id: int) -> dict:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro no encontrado",
            )
        return item

    def update_radiography(self, item_id: int, data: dict) -> dict:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro no encontrado",
            )

        if "patient_code" in data and data["patient_code"] != item["patient_code"]:
            existing = self.repository.get_by_patient_code(data["patient_code"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un registro con ese patient_code",
                )

        updated = self.repository.update(item_id, data)
        return updated

    def delete_radiography(self, item_id: int) -> dict:
        deleted = self.repository.delete(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro no encontrado",
            )

        return {"message": "Registro eliminado correctamente"}