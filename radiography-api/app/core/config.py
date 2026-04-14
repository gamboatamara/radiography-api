from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    MAX_FILE_SIZE: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"


settings = Settings()