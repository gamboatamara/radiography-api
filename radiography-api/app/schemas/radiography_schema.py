from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class RadiographyBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100, examples=["María López"])
    patient_code: str = Field(..., min_length=3, max_length=30, examples=["EXP-001"])
    clinical_description: str = Field(..., min_length=5, max_length=255, examples=["Dolor torácico y control"])
    study_date: date = Field(..., examples=["2026-04-13"])


class RadiographyCreate(RadiographyBase):
    pass


class RadiographyUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=100)
    patient_code: str | None = Field(None, min_length=3, max_length=30)
    clinical_description: str | None = Field(None, min_length=5, max_length=255)
    study_date: date | None = None


class RadiographyResponse(RadiographyBase):
    id: int
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RadiographyListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[RadiographyResponse]


class MessageResponse(BaseModel):
    message: str