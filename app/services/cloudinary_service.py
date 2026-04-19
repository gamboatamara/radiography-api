import hashlib
import hmac
import time
from urllib.parse import urlencode

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.file_validators import validate_image_file

_cloudinary_configured = False


def _configure_cloudinary() -> None:
    global _cloudinary_configured

    if _cloudinary_configured:
        return

    missing = []
    if not settings.CLOUDINARY_CLOUD_NAME.strip():
        missing.append("CLOUDINARY_CLOUD_NAME")
    if not settings.CLOUDINARY_API_KEY.strip():
        missing.append("CLOUDINARY_API_KEY")
    if not settings.CLOUDINARY_API_SECRET.strip():
        missing.append("CLOUDINARY_API_SECRET")

    if missing:
        raise HTTPException(
            status_code=500,
            detail="Cloudinary credentials are not configured",
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _cloudinary_configured = True


def upload_image(file: UploadFile) -> str:
    _configure_cloudinary()
    validate_image_file(file)

    try:
        result = cloudinary.uploader.upload(file.file)
        url = result.get("secure_url")

        if not url:
            raise HTTPException(
                status_code=500,
                detail="Could not obtain the uploaded image URL",
            )

        return url

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error uploading image to Cloudinary",
        )


def generate_signed_image_url(image_url: str, user_id: str) -> str:
    exp = int(time.time()) + settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS

    payload = f"{image_url}|{user_id}|{exp}"
    sig = hmac.new(
        settings.AUTH_TOKEN_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    query = urlencode({
        "url": image_url,
        "user_id": user_id,
        "exp": exp,
        "sig": sig,
    })

    base_url = "https://radiography-api-hf8w.onrender.com"
    return f"{base_url}/api/v1/radiography/image-secure?{query}"


def validate_signed_image_url(
    image_url: str,
    user_id: str,
    exp: int,
    sig: str,
) -> None:
    now = int(time.time())
    if now > exp:
        raise HTTPException(status_code=403, detail="Image URL has expired")

    payload = f"{image_url}|{user_id}|{exp}"
    expected_sig = hmac.new(
        settings.AUTH_TOKEN_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(status_code=403, detail="Invalid image signature")