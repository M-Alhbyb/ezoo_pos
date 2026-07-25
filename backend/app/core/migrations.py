import logging

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command
from app.core.config import settings
from app.core.paths import resource_path

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    sync_url = settings.sync_database_url
    cfg = Config(resource_path("alembic.ini"))
    cfg.set_main_option("script_location", resource_path("alembic"))
    cfg.set_main_option("sqlalchemy.url", sync_url)

    engine = create_engine(sync_url)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    if tables and "alembic_version" not in tables:
        # Legacy DB built by create_all(): schema exists but is unversioned.
        # Adopt it at head rather than replaying migrations over live tables.
        command.stamp(cfg, "head")

    command.upgrade(cfg, "head")
