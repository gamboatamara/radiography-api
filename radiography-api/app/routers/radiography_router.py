from fastapi import APIRouter, Query, Depends, status
from sqlalchemy.orm import Session

from app.schemas.radiography_schema import (
    RadiographyCreate,
    RadiographyUpdate,
    RadiographyResponse,
    RadiographyListResponse,
)
from app.repositories.radiography_repository import RadiographyRepository
from app.services.radiography_service import RadiographyService
from app.db.session import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=RadiographyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear registro radiográfico",
)
def create_radiography(payload: RadiographyCreate, db: Session = Depends(get_db)):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.create_radiography(payload.model_dump())


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
def get_radiography(item_id: int, db: Session = Depends(get_db)):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.get_radiography_by_id(item_id)


@router.put(
    "/{item_id}",
    response_model=RadiographyResponse,
    summary="Actualizar registro radiográfico",
)
def update_radiography(
    item_id: int,
    payload: RadiographyUpdate,
    db: Session = Depends(get_db),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    data = payload.model_dump(exclude_unset=True)
    return service.update_radiography(item_id, data)


@router.delete(
    "/{item_id}",
    summary="Eliminar registro radiográfico",
)
def delete_radiography(item_id: int, db: Session = Depends(get_db)):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.delete_radiography(item_id)