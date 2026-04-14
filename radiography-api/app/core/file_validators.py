from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024 


async def validate_image_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed types: jpg, jpeg, png, webp."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the maximum allowed limit of 5 MB."
        )

    await file.seek(0)