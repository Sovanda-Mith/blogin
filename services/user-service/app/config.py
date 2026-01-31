from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://blogin_user:blogin_pass@postgres:5432/blogin"
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "blogin-avatars"
    S3_AVATAR_EXPIRATION: int = 3600

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
