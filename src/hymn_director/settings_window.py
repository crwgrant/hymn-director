"""Window for configuring hymn display settings."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStyleFactory,
    QVBoxLayout,
    QWidget,
)

from hymn_director.display_config import DisplaySettings, save_display_settings

WINDOW_STYLE = (
    "QWidget { background-color: #ffffff; color: #000000; }"
    "QLabel { background-color: transparent; color: #000000; }"
)

BUTTON_STYLE = (
    "QPushButton {"
    "  padding: 10px 16px;"
    "  background-color: #f0f0f0;"
    "  color: #000000;"
    "  border: 1px solid #cccccc;"
    "  border-radius: 4px;"
    "}"
    "QPushButton:hover { background-color: #e8e8e8; }"
    "QPushButton:pressed { background-color: #d0d0d0; }"
)

INPUT_STYLE = (
    "QSpinBox, QDoubleSpinBox, QFontComboBox {"
    "  background-color: #ffffff;"
    "  color: #000000;"
    "  border: 1px solid #cccccc;"
    "  border-radius: 4px;"
    "  padding: 6px;"
    "}"
)


class SettingsWindow(QMainWindow):
    settings_saved = pyqtSignal(DisplaySettings)

    def __init__(self, settings: DisplaySettings) -> None:
        super().__init__()
        self._settings = settings
        self.setWindowTitle("Display Settings")
        self.resize(460, 360)
        self.setStyle(QStyleFactory.create("Fusion"))

        central = QWidget()
        central.setStyleSheet(WINDOW_STYLE)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Display Settings")
        title.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        help_text = QLabel(
            "Adjust how hymn text appears on the display panel."
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        form = QFormLayout()
        form.setSpacing(12)

        self.font_combo = QFontComboBox()
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)
        self.font_combo.setCurrentFont(QFont(settings.font_family))
        self.font_combo.setStyleSheet(INPUT_STYLE)
        form.addRow("Font:", self.font_combo)

        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 144)
        self.font_size_input.setSuffix(" pt")
        self.font_size_input.setValue(settings.font_size)
        self.font_size_input.setStyleSheet(INPUT_STYLE)
        form.addRow("Font size:", self.font_size_input)

        self.line_spacing_input = QSpinBox()
        self.line_spacing_input.setRange(50, 300)
        self.line_spacing_input.setSuffix(" %")
        self.line_spacing_input.setValue(settings.line_spacing)
        self.line_spacing_input.setStyleSheet(INPUT_STYLE)
        form.addRow("Line spacing:", self.line_spacing_input)

        self.letter_spacing_input = QDoubleSpinBox()
        self.letter_spacing_input.setRange(0.0, 30.0)
        self.letter_spacing_input.setSingleStep(0.5)
        self.letter_spacing_input.setSuffix(" px")
        self.letter_spacing_input.setValue(settings.letter_spacing)
        self.letter_spacing_input.setStyleSheet(INPUT_STYLE)
        form.addRow("Letter spacing:", self.letter_spacing_input)

        self.word_spacing_input = QDoubleSpinBox()
        self.word_spacing_input.setRange(0.0, 50.0)
        self.word_spacing_input.setSingleStep(0.5)
        self.word_spacing_input.setSuffix(" px")
        self.word_spacing_input.setValue(settings.word_spacing)
        self.word_spacing_input.setStyleSheet(INPUT_STYLE)
        form.addRow("Word spacing:", self.word_spacing_input)

        layout.addLayout(form)
        layout.addStretch()

        action_row = QHBoxLayout()
        action_row.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Helvetica", 12))
        cancel_button.setStyleSheet(BUTTON_STYLE)
        cancel_button.clicked.connect(self.close)
        action_row.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.setFont(QFont("Helvetica", 12))
        save_button.setStyleSheet(BUTTON_STYLE)
        save_button.clicked.connect(self._save_settings)
        action_row.addWidget(save_button)
        layout.addLayout(action_row)

    def _current_settings(self) -> DisplaySettings:
        return DisplaySettings(
            font_family=self.font_combo.currentFont().family(),
            font_size=self.font_size_input.value(),
            line_spacing=self.line_spacing_input.value(),
            letter_spacing=self.letter_spacing_input.value(),
            word_spacing=self.word_spacing_input.value(),
        )

    def _save_settings(self) -> None:
        settings = self._current_settings()
        save_display_settings(settings)
        self.settings_saved.emit(settings)
        self.close()
