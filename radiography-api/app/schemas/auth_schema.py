from pydantic import BaseModel, EmailStr


class GoogleTokenRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    email: EmailStr
    name: str
    google_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
