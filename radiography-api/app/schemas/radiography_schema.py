from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


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

    @field_validator("full_name", "patient_code", "clinical_description")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("study_date")
    @classmethod
    def validate_study_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Study date cannot be in the future")
        return value


class RadiographyCreate(RadiographyBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Juan Pérez",
                "patient_code": "PAT-001",
                "clinical_description": "Fractura en brazo derecho",
                "study_date": "2026-04-13"
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

    @field_validator("full_name", "patient_code", "clinical_description")
    @classmethod
    def validate_optional_text_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("study_date")
    @classmethod
    def validate_optional_study_date(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("Study date cannot be in the future")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Juan Pérez Gómez",
                "clinical_description": "Control radiographic follow-up"
            }
        }
    )


class RadiographyResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the radiography record")
    full_name: str = Field(..., description="Full name of the patient")
    patient_code: str = Field(..., description="Patient identification code or medical record number")
    clinical_description: str = Field(..., description="Brief clinical description of the radiography study")
    study_date: date = Field(..., description="Date when the radiography study was performed")
    image_url: Optional[str] = Field(
        None,
        description="Public URL of the radiography image stored in Cloudinary"
    )
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
                "clinical_description": "Fracture in right arm",
                "study_date": "2026-04-13",
                "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "created_at": "2026-04-13T10:30:00"
            }
        }
    )


class RadiographyListResponse(BaseModel):
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of records per page")
    items: list[RadiographyResponse] = Field(..., description="List of radiography records")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "items": [
                    {
                        "id": 1,
                        "full_name": "Juan Pérez",
                        "patient_code": "PAT-001",
                        "clinical_description": "Fracture in right arm",
                        "study_date": "2026-04-13",
                        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                        "created_at": "2026-04-13T10:30:00"
                    }
                ]
            }
        }
    )


class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="Operation result message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Radiography record deleted successfully"
            }
        }
    )