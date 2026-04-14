from typing import Optional


class RadiographyRepository:
    def __init__(self):
        self._items = [
            {
                "id": 1,
                "full_name": "Ana Gómez",
                "patient_code": "RAD-001",
                "clinical_description": "Control de tórax",
                "study_date": "2026-04-10",
                "image_url": None,
            },
            {
                "id": 2,
                "full_name": "Luis Herrera",
                "patient_code": "RAD-002",
                "clinical_description": "Dolor lumbar",
                "study_date": "2026-04-11",
                "image_url": None,
            },
        ]
        self._next_id = 3

    def create(self, data: dict) -> dict:
        new_item = {
            "id": self._next_id,
            **data,
            "image_url": None,
        }
        self._items.append(new_item)
        self._next_id += 1
        return new_item

    def get_all(self) -> list[dict]:
        return self._items.copy()

    def get_by_id(self, item_id: int) -> Optional[dict]:
        return next((item for item in self._items if item["id"] == item_id), None)

    def get_by_patient_code(self, patient_code: str) -> Optional[dict]:
        return next(
            (item for item in self._items if item["patient_code"].lower() == patient_code.lower()),
            None,
        )

    def update(self, item_id: int, data: dict) -> Optional[dict]:
        item = self.get_by_id(item_id)
        if not item:
            return None

        item.update(data)
        return item

    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False

        self._items.remove(item)
        return True