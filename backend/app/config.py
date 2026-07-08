import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # SQLite by default for local dev. Swap to a Postgres URL to go
    # to production, e.g. postgresql://user:password@host:5432/dbname
    DATABASE_URL: str = "sqlite:///./portfolio.db"

    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
