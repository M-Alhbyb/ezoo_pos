import os
import sys
from pathlib import Path

APP_DIR_NAME = "EZOO POS"


def user_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_DIR_NAME


def default_database_path() -> str:
    return str(user_data_dir() / "ezoo_pos.db")


def ensure_data_dir() -> None:
    (user_data_dir() / "backups").mkdir(parents=True, exist_ok=True)
    (user_data_dir() / "logs").mkdir(parents=True, exist_ok=True)


def resource_path(rel: str) -> str:
    """Resolve a bundled read-only resource, PyInstaller-aware."""
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = Path(__file__).resolve().parents[2]  # backend/
    return str(Path(base) / rel)
