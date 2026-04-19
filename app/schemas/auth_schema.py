from pydantic import BaseModel, EmailStr, Field, ConfigDict


class GoogleTokenRequest(BaseModel):
    token: str = Field(
        ...,
        description="Google ID token obtained from the client after authentication"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ij..."
            }
        }
    )


class UserResponse(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User email obtained from Google account"
    )
    name: str = Field(
        ...,
        description="Full name of the authenticated user"
    )
    google_id: str = Field(
        ...,
        description="Unique Google identifier for the user"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@gmail.com",
                "name": "Juan Pérez",
                "google_id": "123456789"
            }
        }
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT token used to authenticate requests"
    )
    token_type: str = Field(
        ...,
        description="Type of token (usually 'bearer')"
    )
    user: UserResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "email": "usuario@gmail.com",
                    "name": "Juan Pérez",
                    "google_id": "123456789"
                }
            }
        }
    )