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

    # Export limits (FR-040)
    xlsx_max_rows: int = 50000
    pdf_max_rows: int = 10000

    # Rate limiting (FR-039)
    export_rate_limit_threshold: int = 5000
    export_rate_limit_per_hour: int = 10

    # Dashboard limits (FR-028)
    dashboard_max_points: int = 1000

    # Performance thresholds (FR-035)
    export_timeout_seconds: int = 30
    dashboard_timeout_seconds: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
