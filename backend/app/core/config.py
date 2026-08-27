from typing import List, Union, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "UNT Informatics Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./informatics.db"

    # Deployment scheduler. This has no development default on purpose.
    NEWS_INGESTION_SECRET: Optional[str] = None

    # Security
    JWT_SECRET: str = "super_secret_jwt_dev_key_change_in_production_987654321"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours in dev
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Google OAuth 2.0 PKCE
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"

    # Client URLs & Cookies
    FRONTEND_URL: str = "http://localhost:3000"
    AUTH_COOKIE_DOMAIN: Optional[str] = None
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://*.vercel.app",
        "https://*.railway.app",
    ]

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Union[str, None]) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            return v
        return "sqlite+aiosqlite:///./informatics.db"

    @model_validator(mode="after")
    def require_safe_production_settings(self) -> "Settings":
        if self.ENVIRONMENT != "production":
            return self
        if self.JWT_SECRET == "super_secret_jwt_dev_key_change_in_production_987654321" or len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be a unique, cryptographically random production secret")
        if not self.AUTH_COOKIE_SECURE:
            raise ValueError("AUTH_COOKIE_SECURE must be true in production")
        if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            raise ValueError("Production requires a PostgreSQL DATABASE_URL")
        if not self.FRONTEND_URL.startswith("https://") or not self.GOOGLE_REDIRECT_URI.startswith("https://"):
            raise ValueError("FRONTEND_URL and GOOGLE_REDIRECT_URI must use HTTPS in production")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
