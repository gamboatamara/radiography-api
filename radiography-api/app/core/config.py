from pydantic_settings import BaseSettings

SECRET_KEY = "radiography-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7
ACCESS_TOKEN_TYPE = "access"
IMAGE_ACCESS_TOKEN_EXPIRE_MINUTES = 5
IMAGE_ACCESS_TOKEN_TYPE = "image_access"
GOOGLE_CLIENT_ID = "96697228689-qrn2tcmbn2fvhqfe3rv0ni3obsi9g1m4.apps.googleusercontent.com"


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./radiography.db"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    AUTH_TOKEN_KEY: str = ""
    SIGNED_IMAGE_URL_EXPIRE_SECONDS: int = 120

    class Config:
        env_file = ".env"


settings = Settings()
