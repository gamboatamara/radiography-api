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


def upload_image(file: UploadFile) -> str:
    if not file:
        raise HTTPException(status_code=400, detail="No se recibió archivo")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo no permitido (solo JPG/PNG)"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Archivo demasiado grande"
        )

    try:
        result = cloudinary.uploader.upload(file.file)
        return result["secure_url"]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )