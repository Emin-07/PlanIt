from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    REDIS_URL: str = f"redis://{redis_host}:{redis_port}/{redis_db}"
    redis_limit_global: int = 100
    redis_limit_auth: int = 10
    rate_limit_api: int = 1000
    redis_window: int = 60
    redis_user_window: int = 3600

    # JWT Configuration
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"

    algorithm: str = "RS256"
    access_token_expire: int = 15
    refresh_token_expire_web: int = 7
    refresh_token_expire_trusted: int = 30
    refresh_token_expire_mobile: int = 90

    # Postgres
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # SQLite
    DATABASE_URL: Optional[str] = None
    TESTING: bool = False

    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    APP_PASSWORD_SECRET: str
    MAIL_FROM: str

    @property
    def POSTGRES_url_psycopg(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def POSTGRES_url_asyncpg(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# mypy: ignore-errors
settings = Settings()
