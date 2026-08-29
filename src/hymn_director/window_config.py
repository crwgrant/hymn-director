"""Main window layout persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from hymn_director.paths import window_config_path

CONFIG_PATH = window_config_path()


@dataclass
class WindowSettings:
    splitter_sizes: list[int] | None = None
    is_maximized: bool = False


def load_window_settings() -> WindowSettings:
    if not CONFIG_PATH.exists():
        return WindowSettings()

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        splitter_sizes = data.get("splitter_sizes")
        if splitter_sizes is not None:
            splitter_sizes = [int(size) for size in splitter_sizes]
            if len(splitter_sizes) != 2 or any(size <= 0 for size in splitter_sizes):
                splitter_sizes = None
        return WindowSettings(
            splitter_sizes=splitter_sizes,
            is_maximized=bool(data.get("is_maximized", False)),
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return WindowSettings()


def save_window_settings(settings: WindowSettings) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(settings), indent=2) + "\n",
        encoding="utf-8",
    )
