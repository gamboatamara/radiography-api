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
        raise HTTPException(status_code=400, detail="No file received")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Only JPG, JPEG, PNG and WEBP are accepted"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum allowed: 5 MB"
        )