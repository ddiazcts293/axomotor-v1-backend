from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "axomotor_v1"
    DATABASE_URL: str
    SECRET_KEY: str
    HASHING_ALGORITHM: str = "argon2"
    TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    USE_ALEMBIC: bool = True
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
    ]

    LINKING_TOKEN_EXPIRE_MINUTES: int = 10
    TELEGRAM_BOT_USERNAME: Optional[str]
    X_BOT_API_KEY: Optional[str]
    X_MQTT_CONSUMER_API_KEY: Optional[str]

    ONLY_API_SERVER: bool = True

    S3_INTERNAL_ENDPOINT: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "axo-bucket"

    DOWNLOAD_URL_EXPIRE_MINUTES: int = 15
    MAXIMUM_FILE_SIZE_MB: int = 5
    ALLOWED_FILE_FORMATS: dict[str, str] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "video/x-msvideo": ".avi"
    }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings() # type: ignore
