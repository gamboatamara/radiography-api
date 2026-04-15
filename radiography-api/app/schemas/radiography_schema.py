from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class RadiographyBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Full name of the patient"
    )
    patient_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Patient identification code or medical record number"
    )
    clinical_description: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Brief clinical description of the radiography study"
    )
    study_date: date = Field(
        ...,
        description="Date when the radiography study was performed"
    )
    image_url: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Public URL of the radiography image stored in Cloudinary"
    )


class RadiographyCreate(RadiographyBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Juan Pérez",
                "patient_code": "PAT-001",
                "clinical_description": "Fractura en brazo derecho",
                "study_date": "2026-04-13",
                "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg"
            }
        }
    )


class RadiographyUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150,
        description="Updated full name of the patient"
    )
    patient_code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Updated patient identification code or medical record number"
    )
    clinical_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255,
        description="Updated brief clinical description"
    )
    study_date: Optional[date] = Field(
        None,
        description="Updated date of the radiography study"
    )
    image_url: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated public URL of the radiography image"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Juan Pérez Gómez",
                "clinical_description": "Control radiográfico de seguimiento"
            }
        }
    )


class RadiographyResponse(RadiographyBase):
    id: int = Field(..., description="Unique identifier of the radiography record")
    created_at: datetime = Field(
        ...,
        description="Date and time when the radiography record was created"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "full_name": "Juan Pérez",
                "patient_code": "PAT-001",
                "clinical_description": "Fractura en brazo derecho",
                "study_date": "2026-04-13",
                "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "created_at": "2026-04-13T10:30:00"
            }
        }
    )

