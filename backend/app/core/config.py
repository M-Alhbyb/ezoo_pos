from pydantic_settings import BaseSettings
from typing import Optional, List
import os


def get_default_database_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ezoo_pos.db')


class Settings(BaseSettings):
    app_name: str = 'EZOO POS'
    app_version: str = '1.0.0'
    app_description: str = (
        'Core POS system with product catalog, inventory tracking, and sale processing'
    )

    database_path: str = get_default_database_path()

    cors_origins: str = 'http://localhost:3000'

    xlsx_max_rows: int = 50000
    pdf_max_rows: int = 10000

    export_rate_limit_threshold: int = 5000
    export_rate_limit_per_hour: int = 10

    dashboard_max_points: int = 1000

    export_timeout_seconds: int = 30
    dashboard_timeout_seconds: int = 3

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(',')]

    @property
    def async_database_url(self) -> str:
        return f'sqlite+aiosqlite:///{self.database_path}'

    @property
    def sync_database_url(self) -> str:
        return f'sqlite:///{self.database_path}'

    class Config:
        env_file = '.env'
        case_sensitive = False


settings = Settings()