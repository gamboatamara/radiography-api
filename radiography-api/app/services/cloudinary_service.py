import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

ALLOWED_TYPES = {"image/jpeg", "image/png"}


def validate_image_file(file: UploadFile) -> None:
    if not file:
        raise HTTPException(status_code=400, detail="No se recibió archivo")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo no permitido. Solo se aceptan JPG y PNG"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Archivo demasiado grande. Máximo permitido: 5 MB"
        )


def upload_image(file: UploadFile) -> str:
    validate_image_file(file)

    try:
        result = cloudinary.uploader.upload(file.file)
        url = result.get("secure_url")

        if not url:
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener la URL de la imagen subida"
            )

        return url

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir la imagen a Cloudinary: {str(e)}"
        )