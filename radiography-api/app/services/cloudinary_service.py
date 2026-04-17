from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import cloudinary
import cloudinary.utils
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.file_validators import validate_image_file

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def _ensure_cloudinary_configured() -> None:
    if not (
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    ):
        raise HTTPException(
            status_code=500,
            detail="Cloudinary is not configured",
        )


def upload_image(file: UploadFile) -> dict:
    validate_image_file(file)
    _ensure_cloudinary_configured()

    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            type="authenticated",
        )
        url = result.get("secure_url")
        public_id = result.get("public_id")

        if not url or not public_id:
            raise HTTPException(
                status_code=500,
                detail="Could not obtain the uploaded image metadata",
            )

        return {
            "image_url": url,
            "cloudinary_public_id": public_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading image to Cloudinary: {str(e)}",
        )


def _extract_cloudinary_asset_data(image_url: str) -> tuple[str, str]:
    parsed = urlparse(image_url)
    path_parts = [part for part in parsed.path.split("/") if part]

    try:
        resource_index = next(
            index for index, part in enumerate(path_parts)
            if part in {"image", "video", "raw"}
        )
    except StopIteration as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid Cloudinary URL format",
        ) from exc

    if len(path_parts) <= resource_index + 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid Cloudinary delivery type",
        )

    delivery_type = path_parts[resource_index + 1]
    asset_parts = path_parts[resource_index + 2 :]

    version_index = next(
        (
            index for index, part in enumerate(asset_parts)
            if part.startswith("v") and part[1:].isdigit()
        ),
        None,
    )
    if version_index is not None:
        asset_parts = asset_parts[version_index + 1 :]

    if not asset_parts:
        raise HTTPException(
            status_code=400,
            detail="Could not determine the Cloudinary public_id",
        )

    last_part = asset_parts[-1]
    if "." in last_part:
        asset_parts[-1] = last_part.rsplit(".", 1)[0]

    public_id = "/".join(asset_parts)
    return public_id, delivery_type


def generate_signed_image_url(image_url: str) -> dict:
    _ensure_cloudinary_configured()

    public_id, delivery_type = _extract_cloudinary_asset_data(image_url)
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS
    )
    signed_url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="image",
        type=delivery_type,
        secure=True,
        sign_url=True,
        expires_at=int(expires_at.timestamp()),
    )

    return {
        "signed_url": signed_url,
        "expires_at": expires_at,
        "expires_in_seconds": settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS,
        "cloudinary_public_id": public_id,
    }
