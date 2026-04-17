from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ACCESS_TOKEN_TYPE,
    ALGORITHM,
    IMAGE_ACCESS_TOKEN_EXPIRE_MINUTES,
    IMAGE_ACCESS_TOKEN_TYPE,
    SECRET_KEY,
)
from app.schemas.auth_schema import UserResponse


bearer_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_type": ACCESS_TOKEN_TYPE})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_image_access_token(
    *,
    image_id: int,
    user: UserResponse,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=IMAGE_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "exp": expire,
        "token_type": IMAGE_ACCESS_TOKEN_TYPE,
        "image_id": image_id,
        "email": user.email,
        "name": user.name,
        "google_id": user.google_id,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> UserResponse:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("token_type")
        email = payload.get("email")
        name = payload.get("name")
        google_id = payload.get("google_id")

        if token_type != ACCESS_TOKEN_TYPE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        if not email or not name or not google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return UserResponse(email=email, name=name, google_id=google_id)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )


def verify_image_access_token(
    *,
    token: str,
    image_id: int,
    user: UserResponse,
) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("token_type")
        token_image_id = payload.get("image_id")
        google_id = payload.get("google_id")

        if token_type != IMAGE_ACCESS_TOKEN_TYPE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid image token type",
            )

        if token_image_id != image_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This token is not valid for the requested image",
            )

        if google_id != user.google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This token does not belong to the authenticated user",
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate image token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserResponse:
    return verify_token(credentials.credentials)
