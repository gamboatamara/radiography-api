from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_image_file(file: UploadFile) -> None:
    if not file:
        raise HTTPException(status_code=400, detail="No se recibió archivo")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo no permitido. Solo se aceptan JPG, JPEG, PNG y WEBP"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Archivo demasiado grande. Máximo permitido: 5 MB"
        )