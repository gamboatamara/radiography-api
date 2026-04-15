from fastapi import APIRouter, UploadFile, File, status
from app.core.file_validators import validate_image_file
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/cloudinary", tags=["Cloudinary"])

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload de imagen a Cloudinary",
    responses={
        201: {"description": "Imagen subida correctamente"},
        400: {"description": "Archivo inválido"},
        500: {"description": "Error interno al subir imagen"},
    },
)
async def upload_cloudinary_image(file: UploadFile = File(...)):
    await validate_image_file(file)
    url = upload_image(file)
    return {"url": url}