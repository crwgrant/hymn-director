"""Application icon loading."""

from __future__ import annotations

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow

from hymn_director.paths import icons_dir


def app_icon() -> QIcon | None:
    directory = icons_dir()
    if directory is None:
        return None

    icon = QIcon()
    added = False
    for size in (16, 32, 48, 64, 128, 256, 1024):
        path = directory / f"hymn-director-{size}.png"
        if path.exists():
            icon.addFile(str(path))
            added = True

    if not added:
        fallback = directory / "hymn-director-1024.png"
        if fallback.exists():
            return QIcon(str(fallback))
        return None

    return icon


def apply_app_icon(app: QApplication) -> None:
    icon = app_icon()
    if icon is not None:
        app.setWindowIcon(icon)


def apply_window_icon(window: QMainWindow) -> None:
    icon = app_icon()
    if icon is not None:
        window.setWindowIcon(icon)
