from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.auth_schema import GoogleTokenRequest, TokenResponse, UserResponse
from app.services.auth_service import login_with_google_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse,  
    summary="Login with Google",
    description="Authenticates a user using a Google ID token and returns a JWT for accessing protected endpoints.",
    responses={
        200: {"description": "Successful authentication"},
        401: {"description": "Invalid Google token"},
        422: {"description": "Validation error"}
    })
def login(payload: GoogleTokenRequest):
    return login_with_google_token(payload.token)


@router.get("/me", response_model=UserResponse, 
    summary="Get current authenticated user",
    description="Returns the information of the currently authenticated user based on the provided JWT token.",
    responses={
        200: {"description": "User retrieved successfully"},
        401: {"description": "Unauthorized - Invalid or missing token"}
    })
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
