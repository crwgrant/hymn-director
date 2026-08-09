"""Resolve application paths for development and bundled builds."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def project_root() -> Path:
    if is_frozen():
        return Path(sys._MEIPASS)
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path(__file__).resolve().parents[2]


def user_data_dir() -> Path:
    if is_frozen():
        from platformdirs import user_data_dir as platform_user_data_dir

        path = Path(platform_user_data_dir("hymn-director", appauthor="hymn-director"))
    else:
        path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def bundled_db_path() -> Path:
    return project_root() / "data" / "hymns.db"


def db_path() -> Path:
    user_db = user_data_dir() / "hymns.db"
    if not user_db.exists():
        bundled_db = bundled_db_path()
        if bundled_db.exists():
            shutil.copy2(bundled_db, user_db)
    return user_db


def config_path() -> Path:
    return user_data_dir() / "display_settings.json"
