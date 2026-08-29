"""Hymn display application."""

from __future__ import annotations

import sys
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from hymn_director import database
from hymn_director.add_hymn_window import AddHymnWindow
from hymn_director.display_config import (
    DisplaySettings,
    format_display_html,
    load_display_settings,
)
from hymn_director.icon_utils import apply_app_icon, apply_window_icon
from hymn_director.settings_window import SettingsWindow


class HymnDisplayWindow(QMainWindow):
    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 500

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hymn Director")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        apply_window_icon(self)

        database.init_database()
        self.hymns = database.list_hymns()
        self.current_hymn_id = self.hymns[0]["id"] if self.hymns else None
        self.current_verse = 1
        self.display_settings = load_display_settings()
        self._add_hymn_window: AddHymnWindow | None = None
        self._settings_window: SettingsWindow | None = None

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_controls_panel())
        splitter.addWidget(self._build_display_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([self.DEFAULT_WIDTH // 2, self.DEFAULT_WIDTH // 2])
        self.setCentralWidget(splitter)

        self._refresh_display()

    def _build_controls_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(240)
        panel.setStyleSheet("background-color: #c8c8c8;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        button_font = QFont("Helvetica", 12)
        button_style = (
            "QPushButton {"
            "  padding: 12px 16px;"
            "  background-color: #ececec;"
            "  color: #1a1a1a;"
            "  border: 1px solid #999999;"
            "  border-radius: 4px;"
            "}"
            "QPushButton:hover { background-color: #f5f5f5; }"
            "QPushButton:pressed { background-color: #b0b0b0; }"
            "QPushButton:disabled { color: #666666; background-color: #d8d8d8; }"
        )
        hymn_label = QLabel("Select Hymn")
        hymn_label.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        hymn_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(hymn_label)

        self.hymn_list = QListWidget()
        self.hymn_list.setFont(QFont("Helvetica", 12))
        self.hymn_list.setStyleSheet(
            "QListWidget {"
            "  background-color: #ececec;"
            "  color: #1a1a1a;"
            "  border: 1px solid #999999;"
            "  border-radius: 4px;"
            "  padding: 4px;"
            "}"
            "QListWidget::item { padding: 8px; }"
            "QListWidget::item:selected {"
            "  background-color: #5a7ea2;"
            "  color: #ffffff;"
            "}"
            "QListWidget::item:hover { background-color: #d8d8d8; }"
        )
        for hymn in self.hymns:
            self.hymn_list.addItem(self._make_hymn_item(hymn))
        self.hymn_list.currentItemChanged.connect(self._on_hymn_selected)
        layout.addWidget(self.hymn_list, stretch=1)

        add_hymn_button = QPushButton("Add Hymn...")
        add_hymn_button.setFont(button_font)
        add_hymn_button.setStyleSheet(button_style)
        add_hymn_button.clicked.connect(self._open_add_hymn_window)
        layout.addWidget(add_hymn_button)

        import_button = QPushButton("Import...")
        import_button.setFont(button_font)
        import_button.setStyleSheet(button_style)
        import_button.clicked.connect(self._import_hymns)
        layout.addWidget(import_button)

        export_button = QPushButton("Export...")
        export_button.setFont(button_font)
        export_button.setStyleSheet(button_style)
        export_button.clicked.connect(self._export_hymns)
        layout.addWidget(export_button)

        self.delete_hymn_button = QPushButton("Delete Hymn")
        self.delete_hymn_button.setFont(button_font)
        self.delete_hymn_button.setStyleSheet(button_style)
        self.delete_hymn_button.clicked.connect(self._delete_selected_hymn)
        layout.addWidget(self.delete_hymn_button)

        settings_button = QPushButton("Display Settings...")
        settings_button.setFont(button_font)
        settings_button.setStyleSheet(button_style)
        settings_button.clicked.connect(self._open_settings_window)
        layout.addWidget(settings_button)

        verse_label = QLabel("Verse Navigation")
        verse_label.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        verse_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(verse_label)

        self.first_button = QPushButton("First Verse")
        self.prev_button = QPushButton("Previous Verse")
        self.next_button = QPushButton("Next Verse")
        self.last_button = QPushButton("Last Verse")

        for button in (
            self.first_button,
            self.prev_button,
            self.next_button,
            self.last_button,
        ):
            button.setFont(button_font)
            button.setStyleSheet(button_style)

        self.first_button.clicked.connect(self._go_first)
        self.prev_button.clicked.connect(self._go_previous)
        self.next_button.clicked.connect(self._go_next)
        self.last_button.clicked.connect(self._go_last)

        layout.addWidget(self.first_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.last_button)

        self.verse_info = QLabel()
        self.verse_info.setFont(QFont("Helvetica", 11))
        self.verse_info.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(self.verse_info)

        return panel

    def _build_display_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(240)
        panel.setStyleSheet("background-color: #000000;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)

        display_size_policy = QSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored,
        )

        self.display_title = QLabel()
        self.display_title.setTextFormat(Qt.TextFormat.RichText)
        self.display_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_title.setWordWrap(True)
        self.display_title.setSizePolicy(display_size_policy)
        layout.addWidget(self.display_title)

        self.display_text = QLabel()
        self.display_text.setTextFormat(Qt.TextFormat.RichText)
        self.display_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_text.setWordWrap(True)
        self.display_text.setSizePolicy(display_size_policy)
        layout.addStretch()
        layout.addWidget(self.display_text)
        layout.addStretch()

        return panel

    def _hymn_label(self, hymn: sqlite3.Row) -> str:
        label = hymn["title"]
        if hymn["number"] is not None:
            label = f"{hymn['number']}. {label}"
        return label

    def _make_hymn_item(self, hymn: sqlite3.Row) -> QListWidgetItem:
        item = QListWidgetItem(self._hymn_label(hymn))
        item.setData(Qt.ItemDataRole.UserRole, hymn["id"])
        return item

    def _reload_hymn_list(self, select_hymn_id: int | None = None) -> None:
        self.hymns = database.list_hymns()
        self.hymn_list.blockSignals(True)
        self.hymn_list.clear()
        for hymn in self.hymns:
            self.hymn_list.addItem(self._make_hymn_item(hymn))
        self.hymn_list.blockSignals(False)

        if select_hymn_id is not None and any(
            hymn["id"] == select_hymn_id for hymn in self.hymns
        ):
            self._select_hymn(select_hymn_id)
        elif self.hymns:
            self._select_hymn(self.hymns[0]["id"])
        else:
            self.current_hymn_id = None
            self.current_verse = 1
            self._refresh_display()

    def _open_add_hymn_window(self) -> None:
        if self._add_hymn_window is None:
            self._add_hymn_window = AddHymnWindow()
            self._add_hymn_window.hymn_saved.connect(self._on_hymn_added)
            self._add_hymn_window.destroyed.connect(
                lambda: setattr(self, "_add_hymn_window", None)
            )
        self._add_hymn_window.show()
        self._add_hymn_window.raise_()
        self._add_hymn_window.activateWindow()

    def _open_settings_window(self) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self.display_settings)
            self._settings_window.settings_saved.connect(self._on_settings_saved)
            self._settings_window.destroyed.connect(
                lambda: setattr(self, "_settings_window", None)
            )
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _on_settings_saved(self, settings: DisplaySettings) -> None:
        self.display_settings = settings
        self._refresh_display()

    def _set_display_title(self, text: str) -> None:
        self.display_title.setText(
            format_display_html(text, self.display_settings, bold=True)
        )

    def _set_display_text(self, text: str) -> None:
        self.display_text.setText(format_display_html(text, self.display_settings))

    def _on_hymn_added(self, hymn_id: int) -> None:
        self._reload_hymn_list(select_hymn_id=hymn_id)

    def _import_hymns(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Hymns",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        try:
            hymns = database.load_hymns_from_json(path)
            result = database.import_hymns(hymns)
        except ValueError as error:
            QMessageBox.warning(self, "Import Failed", str(error))
            return

        if result.imported > 0:
            self._reload_hymn_list()

        lines = []
        if result.imported:
            lines.append(
                f"Imported {result.imported} hymn{'s' if result.imported != 1 else ''}."
            )
        if result.skipped_duplicate:
            lines.append(
                f"Skipped {result.skipped_duplicate} with duplicate numbers."
            )
        if result.skipped_empty:
            lines.append(f"Skipped {result.skipped_empty} with no verses.")
        if result.skipped_invalid:
            lines.append(f"Skipped {result.skipped_invalid} with invalid data.")

        if not lines:
            lines.append("No hymns were found in the file.")

        QMessageBox.information(self, "Import Complete", "\n".join(lines))

    def _export_hymns(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Hymns",
            "hymns.json",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        try:
            count = database.export_hymns_to_json(path)
        except ValueError as error:
            QMessageBox.warning(self, "Export Failed", str(error))
            return

        QMessageBox.information(
            self,
            "Export Complete",
            f"Exported {count} hymn{'s' if count != 1 else ''}.",
        )

    def _delete_selected_hymn(self) -> None:
        if self.current_hymn_id is None:
            return

        hymn = database.get_hymn(self.current_hymn_id)
        if hymn is None:
            self._reload_hymn_list()
            return

        reply = QMessageBox.question(
            self,
            "Delete Hymn",
            f'Delete "{self._hymn_label(hymn)}"? This cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        current_index = next(
            (index for index, h in enumerate(self.hymns) if h["id"] == hymn["id"]),
            0,
        )
        database.delete_hymn(hymn["id"])

        remaining = database.list_hymns()
        select_hymn_id = None
        if remaining:
            next_index = min(current_index, len(remaining) - 1)
            select_hymn_id = remaining[next_index]["id"]
        self._reload_hymn_list(select_hymn_id=select_hymn_id)

    def _verse_count(self) -> int:
        if self.current_hymn_id is None:
            return 0
        return database.get_verse_count(self.current_hymn_id)

    def _on_hymn_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            return
        hymn_id = current.data(Qt.ItemDataRole.UserRole)
        if hymn_id != self.current_hymn_id:
            self._select_hymn(hymn_id)

    def _select_hymn(self, hymn_id: int) -> None:
        self.current_hymn_id = hymn_id
        self.current_verse = 1
        self._refresh_display()

    def _go_first(self) -> None:
        self.current_verse = 1
        self._refresh_display()

    def _go_previous(self) -> None:
        if self.current_verse > 1:
            self.current_verse -= 1
            self._refresh_display()

    def _go_next(self) -> None:
        total = self._verse_count()
        if self.current_verse < total:
            self.current_verse += 1
            self._refresh_display()

    def _go_last(self) -> None:
        total = self._verse_count()
        if total > 0:
            self.current_verse = total
            self._refresh_display()

    def _refresh_display(self) -> None:
        total = self._verse_count()
        has_hymn = self.current_hymn_id is not None and total > 0

        for button in (
            self.first_button,
            self.prev_button,
            self.next_button,
            self.last_button,
        ):
            button.setEnabled(has_hymn)

        self.delete_hymn_button.setEnabled(self.current_hymn_id is not None)

        self.hymn_list.blockSignals(True)
        for row in range(self.hymn_list.count()):
            item = self.hymn_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == self.current_hymn_id:
                self.hymn_list.setCurrentRow(row)
                break
        self.hymn_list.blockSignals(False)

        if not has_hymn:
            self._set_display_title("")
            self._set_display_text("No hymn selected.")
            self.verse_info.setText("")
            return

        self.current_verse = max(1, min(self.current_verse, total))
        verse = database.get_verse(self.current_hymn_id, self.current_verse)

        if verse is None:
            self._set_display_title("")
            self._set_display_text("Verse not found.")
            self.verse_info.setText("")
            return

        hymn = database.get_hymn(self.current_hymn_id)
        if hymn is not None:
            self._set_display_title(self._hymn_label(hymn))
        else:
            self._set_display_title(verse["title"])
        self._set_display_text(verse["text"])
        self.verse_info.setText(f"Verse {self.current_verse} of {total}")

        self.first_button.setEnabled(self.current_verse > 1)
        self.prev_button.setEnabled(self.current_verse > 1)
        self.next_button.setEnabled(self.current_verse < total)
        self.last_button.setEnabled(self.current_verse < total)


def main() -> int:
    app = QApplication(sys.argv)
    apply_app_icon(app)
    window = HymnDisplayWindow()
    window.show()
    return app.exec()
