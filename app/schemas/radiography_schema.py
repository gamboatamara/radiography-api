from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import Form
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RadiographyBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
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
    @classmethod
    def as_form(
        cls,
        full_name: Annotated[
            str,
            Form(description="Full name of the patient"),
        ],
        patient_code: Annotated[
            str,
            Form(description="Patient identification code or medical record number"),
        ],
        clinical_description: Annotated[
            str,
            Form(description="Brief clinical description of the radiography study"),
        ],
        study_date: Annotated[
            date,
            Form(description="Date when the radiography study was performed"),
        ],
    ) -> "RadiographyCreate":
        return cls(
            full_name=full_name,
            patient_code=patient_code,
            clinical_description=clinical_description,
            study_date=study_date,
        )

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
        max_length=150,
        description="Updated full name of the patient"
    )
    patient_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated patient identification code or medical record number"
    )
    clinical_description: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated brief clinical description"
    )
    study_date: Optional[date] = Field(
        None,
        description="Updated date of the radiography study"
    )
    image_url: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated image URL"
    )

    @classmethod
    def as_form(
        cls,
        full_name: Annotated[
            Optional[str],
            Form(description="Updated full name of the patient"),
        ] = None,
        patient_code: Annotated[
            Optional[str],
            Form(description="Updated patient identification code or medical record number"),
        ] = None,
        clinical_description: Annotated[
            Optional[str],
            Form(description="Updated brief clinical description"),
        ] = None,
        study_date: Annotated[
            Optional[date],
            Form(description="Updated date of the radiography study"),
        ] = None,
    ) -> "RadiographyUpdate":
        return cls(
            full_name=full_name,
            patient_code=patient_code,
            clinical_description=clinical_description,
            study_date=study_date,
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
        description="(Hidden) Image is accessed only through secure endpoints"
    )
    created_at: datetime = Field(
        ...,
        description="Date and time when the radiography record was created"
    )

    @field_validator("image_url")
    @classmethod
    def hide_image_url(cls, v):
        return None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "full_name": "Juan Pérez",
                "patient_code": "PAT-001",
                "clinical_description": "Fracture in right arm",
                "study_date": "2026-04-13",
                "image_url": None,
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
                        "image_url": None,
                        "created_at": "2026-04-13T10:30:00"
                    }
                ]
            }
        }
    )


class RadiographyImageTokenResponse(BaseModel):
    image_id: int = Field(..., description="Radiography image identifier")
    access_token: str = Field(..., description="Temporary JWT used to request the signed image URL")
    token_type: str = Field(..., description="Bearer token type")
    expires_in_minutes: int = Field(..., description="Token lifetime in minutes")
    expires_at: datetime = Field(..., description="Token expiration timestamp in UTC")
    image_access_url: str = Field(
        ...,
        description="API endpoint that validates the token and returns a signed image URL",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image_id": 1,
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in_minutes": 1,
                "expires_at": "2026-04-17T06:35:00Z",
                "image_access_url": "https://radiography-api-hf8w.onrender.com/api/v1/radiography/1/image-access?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
    )


class SignedImageUrlResponse(BaseModel):
    image_id: int = Field(..., description="Radiography image identifier")
    signed_url: str = Field(..., description="Temporary signed image URL")
    expires_at: datetime = Field(..., description="Signed URL expiration timestamp in UTC")
    expires_in_seconds: int = Field(..., description="Signed URL lifetime in seconds")
    token_subject_google_id: str = Field(
        ...,
        description="Authenticated user identifier encoded in the image token",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image_id": 1,
                "signed_url": "https://radiography-api-hf8w.onrender.com/api/v1/radiography/image-secure?public_id=radiographies/example&delivery_type=authenticated&exp=1776492463&sig=abcdef123456",
                "expires_at": "2026-04-17T06:31:00Z",
                "expires_in_seconds": 60,
                "token_subject_google_id": "123456789",
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