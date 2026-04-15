from pydantic_settings import BaseSettings


SECRET_KEY = "radiography-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
GOOGLE_CLIENT_ID = "96697228689-qrn2tcmbn2fvhqfe3rv0ni3obsi9g1m4.apps.googleusercontent.com"


class Settings(BaseSettings):
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    MAX_FILE_SIZE: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"


settings = Settings()