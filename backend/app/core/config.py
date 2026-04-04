from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "EZOO POS"
    app_version: str = "1.0.0"
    app_description: str = (
        "Core POS system with product catalog, inventory tracking, and sale processing"
    )

    async_database_url: str
    sync_database_url: str

    database_host: Optional[str] = None
    database_port: Optional[int] = None
    database_name: Optional[str] = None

    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
