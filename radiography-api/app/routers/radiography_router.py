from datetime import date

from fastapi import APIRouter, Query, Depends, status, Form, UploadFile, File
from sqlalchemy.orm import Session

from app.schemas.radiography_schema import (
    RadiographyResponse,
    RadiographyListResponse,
    MessageResponse,
)
from app.schemas.auth_schema import UserResponse
from app.repositories.radiography_repository import RadiographyRepository
from app.services.radiography_service import RadiographyService
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.cloudinary_service import upload_image

router = APIRouter()


@router.post(
    "/",
    response_model=RadiographyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear registro radiográfico con imagen",
)
def create_radiography(
    full_name: str = Form(...),
    patient_code: str = Form(...),
    clinical_description: str = Form(...),
    study_date: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    image_url = upload_image(file)

    data = {
        "full_name": full_name,
        "patient_code": patient_code,
        "clinical_description": clinical_description,
        "study_date": study_date,
        "image_url": image_url,
    }

    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.create_radiography(data)


@router.get(
    "/",
    response_model=RadiographyListResponse,
    summary="Listar registros radiográficos",
)
def list_radiographies(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad por página"),
    full_name: str | None = Query(None, description="Filtrar por nombre del paciente"),
    patient_code: str | None = Query(None, description="Filtrar por código del paciente"),
    sort_by: str = Query("id", description="Campo de ordenamiento: id, full_name, patient_code, study_date"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Orden asc o desc"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.list_radiographies(
        page=page,
        limit=limit,
        full_name=full_name,
        patient_code=patient_code,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{item_id}",
    response_model=RadiographyResponse,
    summary="Obtener registro por ID",
)
def get_radiography(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.get_radiography_by_id(item_id)


@router.put(
    "/{item_id}",
    response_model=RadiographyResponse,
    summary="Actualizar registro radiográfico con imagen opcional",
)
def update_radiography(
    item_id: int,
    full_name: str | None = Form(None),
    patient_code: str | None = Form(None),
    clinical_description: str | None = Form(None),
    study_date: date | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    data = {}

    if full_name is not None:
        data["full_name"] = full_name
    if patient_code is not None:
        data["patient_code"] = patient_code
    if clinical_description is not None:
        data["clinical_description"] = clinical_description
    if study_date is not None:
        data["study_date"] = study_date
    if file is not None:
        data["image_url"] = upload_image(file)

    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.update_radiography(item_id, data)


@router.delete(
    "/{item_id}",
    response_model=MessageResponse,
    summary="Eliminar registro radiográfico",
)
def delete_radiography(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.delete_radiography(item_id)