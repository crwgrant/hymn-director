"""Display settings persistence and text formatting."""

from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class DisplaySettings:
    font_family: str = "Helvetica"
    font_size: int = 24
    line_spacing: int = 100
    letter_spacing: float = 0.0
    word_spacing: float = 0.0


def config_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "display_settings.json"
    return Path(__file__).resolve().parents[2] / "data" / "display_settings.json"


CONFIG_PATH = config_path()


def load_display_settings() -> DisplaySettings:
    if not CONFIG_PATH.exists():
        return DisplaySettings()

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return DisplaySettings(
            font_family=str(data.get("font_family", "Helvetica")),
            font_size=int(data.get("font_size", 24)),
            line_spacing=int(data.get("line_spacing", 100)),
            letter_spacing=float(data.get("letter_spacing", 0.0)),
            word_spacing=float(data.get("word_spacing", 0.0)),
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return DisplaySettings()


def save_display_settings(settings: DisplaySettings) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(settings), indent=2) + "\n",
        encoding="utf-8",
    )


def format_display_html(
    text: str, settings: DisplaySettings, *, bold: bool = False
) -> str:
    escaped = html.escape(text).replace("\n", "<br>")
    family = html.escape(settings.font_family, quote=True)
    weight = "bold" if bold else "normal"
    return (
        f'<div align="center" style="'
        f"font-family:'{family}';"
        f"font-size:{settings.font_size}pt;"
        f"font-weight:{weight};"
        f"line-height:{settings.line_spacing}%;"
        f"letter-spacing:{settings.letter_spacing}px;"
        f"word-spacing:{settings.word_spacing}px;"
        f'color:#ffffff;">{escaped}</div>'
    )
