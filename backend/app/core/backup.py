import logging
import os
import sqlite3
from datetime import date

from app.core.config import settings
from app.core.paths import user_data_dir

logger = logging.getLogger(__name__)

KEEP = 30


def backup_database() -> None:
    src = settings.database_path
    if not os.path.exists(src):
        return
    dest_dir = user_data_dir() / "backups"
    dest = dest_dir / f"ezoo_pos-{date.today():%Y-%m-%d}.db"
    if dest.exists():
        return  # already backed up today
    con = sqlite3.connect(src)
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        con.execute("VACUUM INTO ?", (str(dest),))
    finally:
        con.close()
    for old in sorted(dest_dir.glob("ezoo_pos-*.db"))[:-KEEP]:
        old.unlink()
