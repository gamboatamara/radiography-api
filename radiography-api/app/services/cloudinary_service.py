from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import cloudinary
import cloudinary.utils
import cloudinary.uploader
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.file_validators import validate_image_file

import hmac
import hashlib

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
            access_control=[{
                "access_type": "token"
            }]
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
    """
    Genera URL firmada que apunta a TU endpoint de validación
    """
    _ensure_cloudinary_configured()

    public_id, delivery_type = _extract_cloudinary_asset_data(image_url)
    
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS
    )
    expiration_timestamp = int(expires_at.timestamp())

    data_to_sign = f"{public_id}:{expiration_timestamp}:{settings.AUTH_TOKEN_KEY}"
    signature = hmac.new(
        settings.AUTH_TOKEN_KEY.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()[:32]
    
    from urllib.parse import quote
    base_url = "http://127.0.0.1:8000"
    validation_url = f"{base_url}/api/v1/radiography/image-secure?public_id={quote(public_id)}&delivery_type={delivery_type}&exp={expiration_timestamp}&sig={signature}"

    return {
        "signed_url": validation_url,
        "expires_at": expires_at,
        "expires_in_seconds": settings.SIGNED_IMAGE_URL_EXPIRE_SECONDS,
        "cloudinary_public_id": public_id,
    }


def verify_signed_url(signed_url: str) -> dict:
    """
    Verifica si una URL firmada es válida y no ha expirado
    """
    from urllib.parse import parse_qs
    
    try:
        parsed = urlparse(signed_url)
        params = parse_qs(parsed.query)
        
        exp_list = params.get('exp', [])
        sig_list = params.get('sig', [])
        
        if not exp_list or not sig_list:
            return {
                "valid": False,
                "error": "Missing expiration or signature parameters"
            }
        
        exp = exp_list[0]
        sig = sig_list[0]
        
        try:
            expiration_timestamp = int(exp)
        except ValueError:
            return {
                "valid": False,
                "error": "Invalid expiration timestamp"
            }
        
        now = int(datetime.now(timezone.utc).timestamp())
        
        if now > expiration_timestamp:
            return {
                "valid": False,
                "error": f"URL has expired. Current time: {now}, expiration: {expiration_timestamp}"
            }

        base_url = signed_url.split('?')[0]
        
        try:
            public_id, delivery_type = _extract_cloudinary_asset_data(base_url)
        except Exception as e:
            return {
                "valid": False,
                "error": f"Could not extract public_id: {str(e)}"
            }
        
        data_to_sign = f"{public_id}:{exp}:{settings.AUTH_TOKEN_KEY}"
        expected_sig = hmac.new(
            settings.AUTH_TOKEN_KEY.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:32]
        
        if not hmac.compare_digest(expected_sig, sig):
            return {
                "valid": False,
                "error": "Invalid signature - URL may have been tampered with"
            }
        
        cloudinary_url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type="image",
            type=delivery_type,
            secure=True,
            sign_url=True
        )
        
        return {
            "valid": True,
            "cloudinary_url": cloudinary_url,
            "public_id": public_id
        }
    
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error validating URL: {str(e)}"
        }
