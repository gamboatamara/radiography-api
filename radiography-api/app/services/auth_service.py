from fastapi import HTTPException, status

from app.core.config import GOOGLE_CLIENT_ID
from app.core.security import create_access_token
from app.schemas.auth_schema import TokenResponse, UserResponse


def validate_google_user(user_data: dict) -> UserResponse:
    email = user_data.get("email")
    name = user_data.get("name")
    google_id = user_data.get("google_id")

    if not email or not name or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete Google user data",
        )

    return UserResponse(email=email, name=name, google_id=google_id)


def verify_google_token(token: str) -> UserResponse:
    if GOOGLE_CLIENT_ID == "tu-google-client-id":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured",
        )

    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing Google login dependencies: install google-auth and requests",
        ) from exc

    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        ) from exc

    user_data = {
        "email": id_info.get("email"),
        "name": id_info.get("name"),
        "google_id": id_info.get("sub"),
    }
    return validate_google_user(user_data)


def login_with_google_token(token: str) -> TokenResponse:
    user = verify_google_token(token)

    access_token = create_access_token(
        data={
            "email": user.email,
            "name": user.name,
            "google_id": user.google_id,
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )
