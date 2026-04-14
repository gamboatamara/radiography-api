from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.auth_schema import GoogleTokenRequest, TokenResponse, UserResponse
from app.services.auth_service import login_with_google_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: GoogleTokenRequest):
    return login_with_google_token(payload.token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
