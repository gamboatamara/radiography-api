import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.file_validators import validate_image_file

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image(file: UploadFile) -> str:
    validate_image_file(file)

    try:
        result = cloudinary.uploader.upload(file.file)
        url = result.get("secure_url")

        if not url:
            raise HTTPException(
                status_code=500,
                detail="Could not obtain the uploaded image URL"
            )

        return url

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading image to Cloudinary: {str(e)}"
        )