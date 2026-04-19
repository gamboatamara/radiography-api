from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: str = "local"
    DATABASE_URL: str | None = None
    LOCAL_DATABASE_URL: str = "sqlite:///./radiography.db"
    PRODUCTION_DATABASE_URL: str = "sqlite:///./temp/radiography.db"

    SECRET_KEY: str
    AUTH_TOKEN_KEY: str
    GOOGLE_CLIENT_ID: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7
    ACCESS_TOKEN_TYPE: str = "access"
    IMAGE_ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    IMAGE_ACCESS_TOKEN_TYPE: str = "image_access"

    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    SIGNED_IMAGE_URL_EXPIRE_SECONDS: int = 120

    @property
    def resolved_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.APP_ENV.lower() == "production":
            return self.PRODUCTION_DATABASE_URL

        return self.LOCAL_DATABASE_URL


settings = Settings()