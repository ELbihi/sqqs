from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Virtual Studio"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = "postgresql+psycopg2://studio:studio@localhost:5432/studio"
    REDIS_URL: str = "redis://localhost:6379/0"
    # When False, generations run inline in the request (no Redis/Celery needed).
    # Set True once a Celery worker + Redis are running.
    USE_CELERY: bool = False

    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str = "studio-media"
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_REGION: str = "us-east-1"
    LOCAL_STORAGE_DIR: str = "./_storage"

    # Image AI: "mock" (dev placeholder), "gemini" (Google), or "replicate".
    IMAGE_AI_PROVIDER: str = "mock"
    IMAGE_AI_API_KEY: str | None = None  # Replicate API token
    # Virtual try-on model (person + garment). Used when both images exist.
    IMAGE_AI_TRYON_MODEL: str = "cuuupid/idm-vton"
    # Text-to-image fallback model (no photos / scene-only generation).
    IMAGE_AI_MODEL: str = "black-forest-labs/flux-schnell"
    IMAGE_AI_TIMEOUT: int = 120

    # Google Gemini (free tier, no card). Composes person + garment + scene.
    GEMINI_API_KEY: str | None = None
    GEMINI_IMAGE_MODEL: str = "gemini-2.5-flash-image"

    VIDEO_AI_PROVIDER: str = "mock"
    VIDEO_AI_API_KEY: str | None = None

    FREE_SIGNUP_CREDITS: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
