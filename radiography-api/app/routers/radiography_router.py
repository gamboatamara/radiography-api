from datetime import date, datetime, timezone
from urllib.parse import unquote

import cloudinary.utils
import hashlib
import hmac
from fastapi import (
    APIRouter,
    Query,
    Depends,
    status,
    Form,
    UploadFile,
    File,
    Path,
    Request,
    HTTPException,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.schemas.radiography_schema import (
    RadiographyResponse,
    RadiographyListResponse,
    MessageResponse,
    RadiographyImageTokenResponse,
    SignedImageUrlResponse,
)
from app.schemas.auth_schema import UserResponse
from app.repositories.radiography_repository import RadiographyRepository
from app.services.radiography_service import RadiographyService
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.cloudinary_service import upload_image

router = APIRouter(tags=["Radiography"])


@router.post(
    "/",
    response_model=RadiographyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create radiography record with image",
    description="Creates a new radiography record, uploads the image to Cloudinary, and stores the image reference along with the patient data.",
    responses={
        201: {"description": "Radiography record created successfully"},
        400: {"description": "Invalid data or unsupported file type"},
        401: {"description": "Unauthorized"},
        409: {"description": "A record with this patient_code already exists"},
        500: {"description": "Internal error while uploading the image or saving the record"},
    },
)
def create_radiography(
    full_name: str = Form(..., description="Full name of the patient"),
    patient_code: str = Form(..., description="Patient code or medical record number"),
    clinical_description: str = Form(..., description="Brief clinical description"),
    study_date: date = Form(..., description="Radiography study date"),
    file: UploadFile = File(..., description="Radiography image file (JPG or PNG)"),
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
    summary="List radiography records",
    description="Returns a paginated list of radiography records with optional filters and sorting.",
    responses={
        200: {"description": "Radiography records retrieved successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Invalid query parameters"},
    },
)
def list_radiographies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    full_name: str | None = Query(None, description="Filter by patient name"),
    patient_code: str | None = Query(None, description="Filter by patient code"),
    sort_by: str = Query(
        "id",
        description="Sort field: id, full_name, patient_code, study_date",
    ),
    order: str = Query(
        "asc",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc",
    ),
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
    "/image-secure",
    include_in_schema=False,
    summary="Serve secure image with expiration validation",
    description="Validates expiration and signature before serving image. No authentication required here because the URL itself is signed and temporary.",
    responses={
        200: {"description": "Redirects to Cloudinary image"},
        403: {"description": "URL expired or invalid signature"},
    },
)
def serve_secure_image(
    public_id: str = Query(..., description="Cloudinary public_id"),
    delivery_type: str = Query(..., description="Delivery type (upload/authenticated)"),
    exp: int = Query(..., description="Expiration timestamp"),
    sig: str = Query(..., description="HMAC signature"),
):
    public_id = unquote(public_id)

    now = int(datetime.now(timezone.utc).timestamp())
    if now > exp:
        raise HTTPException(
            status_code=403,
            detail="Image URL has expired. Please request a new access token."
        )

    from app.core.config import settings

    data_to_sign = f"{public_id}:{delivery_type}:{exp}:{settings.AUTH_TOKEN_KEY}"
    expected_sig = hmac.new(
        settings.AUTH_TOKEN_KEY.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:32]

    if not hmac.compare_digest(expected_sig, sig):
        raise HTTPException(
            status_code=403,
            detail="Invalid signature"
        )

    cloudinary_url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="image",
        type=delivery_type,
        sign_url=True,
        secure=True
    )

    return RedirectResponse(url=cloudinary_url)


@router.get(
    "/{item_id}",
    response_model=RadiographyResponse,
    summary="Get radiography record by ID",
    description="Retrieves a specific radiography record using its unique identifier. The image is not exposed directly; use the secure image endpoints instead.",
    responses={
        200: {"description": "Radiography record retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Radiography record not found"},
    },
)
def get_radiography(
    item_id: int = Path(..., ge=1, description="Radiography record ID"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.get_radiography_by_id(item_id)


@router.post(
    "/{item_id}/image-token",
    response_model=RadiographyImageTokenResponse,
    summary="Generate image access token",
    description="Creates a short-lived JWT tied to the authenticated user and the requested radiography image.",
    responses={
        200: {"description": "Image token generated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Radiography record or image not found"},
    },
)
def create_radiography_image_token(
    request: Request,
    item_id: int = Path(..., ge=1, description="Radiography record ID"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    image_access_url = str(
        request.url_for("get_radiography_signed_image_url", item_id=item_id)
    )
    return service.generate_image_token(
        item_id=item_id,
        user=current_user,
        image_access_url=image_access_url,
    )


@router.get(
    "/{item_id}/image-access",
    response_model=SignedImageUrlResponse,
    summary="Validate image token and return signed URL",
    description="Validates the image JWT and returns a temporary signed image access URL for the requested radiography.",
    responses={
        200: {"description": "Signed image URL generated successfully"},
        401: {"description": "Invalid or expired image token"},
        404: {"description": "Radiography record or image not found"},
    },
)
def get_radiography_signed_image_url(
    item_id: int = Path(..., ge=1, description="Radiography record ID"),
    token: str = Query(..., min_length=10, description="Short-lived image access token"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.get_signed_image_access(
        item_id=item_id,
        token=token,
        user=current_user,
    )


@router.put(
    "/{item_id}",
    response_model=RadiographyResponse,
    summary="Update radiography record (optional image)",
    description="Updates one or more fields of an existing radiography record. Allows optional image replacement.",
    responses={
        200: {"description": "Radiography record updated successfully"},
        400: {"description": "Invalid data or unsupported file type"},
        401: {"description": "Unauthorized"},
        404: {"description": "Radiography record not found"},
        409: {"description": "Another record with this patient_code already exists"},
        500: {"description": "Internal error while uploading the image or updating the record"},
    },
)
def update_radiography(
    item_id: int = Path(..., ge=1, description="Radiography record ID"),
    full_name: str | None = Form(None, description="Updated full name"),
    patient_code: str | None = Form(None, description="Updated patient code"),
    clinical_description: str | None = Form(None, description="Updated clinical description"),
    study_date: date | None = Form(None, description="Updated study date"),
    file: UploadFile | None = File(None, description="New radiography image (optional)"),
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
    summary="Delete radiography record",
    description="Deletes a radiography record from the system.",
    responses={
        200: {"description": "Radiography record deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Radiography record not found"},
    },
)
def delete_radiography(
    item_id: int = Path(..., ge=1, description="Radiography record ID"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    repository = RadiographyRepository(db)
    service = RadiographyService(repository)
    return service.delete_radiography(item_id)