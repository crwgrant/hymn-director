"""Window for configuring hymn display settings."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPolygon
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProxyStyle,
    QPushButton,
    QSpinBox,
    QStyle,
    QStyleFactory,
    QVBoxLayout,
    QWidget,
)

from hymn_director.display_config import DisplaySettings, save_display_settings
from hymn_director.icon_utils import apply_window_icon

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

# Windows 11 draws a smaller increment glyph than decrement. Draw both ourselves.
_SPIN_ARROW_HALF_WIDTH = 4
_SPIN_ARROW_HALF_HEIGHT = 3


class _EqualSpinArrowStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        up_elements = {
            QStyle.PrimitiveElement.PE_IndicatorSpinUp,
            QStyle.PrimitiveElement.PE_IndicatorSpinPlus,
            QStyle.PrimitiveElement.PE_IndicatorArrowUp,
        }
        down_elements = {
            QStyle.PrimitiveElement.PE_IndicatorSpinDown,
            QStyle.PrimitiveElement.PE_IndicatorSpinMinus,
            QStyle.PrimitiveElement.PE_IndicatorArrowDown,
        }
        if element in up_elements | down_elements:
            self._draw_spin_arrow(option, painter, pointing_up=element in up_elements)
            return
        super().drawPrimitive(element, option, painter, widget)

    def _draw_spin_arrow(self, option, painter: QPainter, *, pointing_up: bool) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(Qt.PenStyle.NoPen)
        color = option.palette.color(option.palette.ColorRole.Text)
        if not (option.state & QStyle.StateFlag.State_Enabled):
            color = option.palette.color(option.palette.ColorRole.Mid)
        painter.setBrush(color)
        center = option.rect.center()
        cx, cy = center.x(), center.y()
        if pointing_up:
            points = [
                QPoint(cx, cy - _SPIN_ARROW_HALF_HEIGHT),
                QPoint(cx + _SPIN_ARROW_HALF_WIDTH, cy + _SPIN_ARROW_HALF_HEIGHT),
                QPoint(cx - _SPIN_ARROW_HALF_WIDTH, cy + _SPIN_ARROW_HALF_HEIGHT),
            ]
        else:
            points = [
                QPoint(cx - _SPIN_ARROW_HALF_WIDTH, cy - _SPIN_ARROW_HALF_HEIGHT),
                QPoint(cx + _SPIN_ARROW_HALF_WIDTH, cy - _SPIN_ARROW_HALF_HEIGHT),
                QPoint(cx, cy + _SPIN_ARROW_HALF_HEIGHT),
            ]
        painter.drawPolygon(QPolygon(points))
        painter.restore()


class SettingsWindow(QMainWindow):
    settings_saved = pyqtSignal(DisplaySettings)

    def __init__(self, settings: DisplaySettings) -> None:
        super().__init__()
        self._settings = settings
        self.setWindowTitle("Display Settings")
        self.resize(460, 360)
        self.setStyle(QStyleFactory.create("Fusion"))
        self._spin_arrow_style = _EqualSpinArrowStyle(self.style())
        self._spin_arrow_style.setParent(self)
        apply_window_icon(self)

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
        self.font_size_input.setStyle(self._spin_arrow_style)
        form.addRow("Font size:", self.font_size_input)

        self.line_spacing_input = QSpinBox()
        self.line_spacing_input.setRange(50, 300)
        self.line_spacing_input.setSuffix(" %")
        self.line_spacing_input.setValue(settings.line_spacing)
        self.line_spacing_input.setStyleSheet(INPUT_STYLE)
        self.line_spacing_input.setStyle(self._spin_arrow_style)
        form.addRow("Line spacing:", self.line_spacing_input)

        self.letter_spacing_input = QDoubleSpinBox()
        self.letter_spacing_input.setRange(0.0, 30.0)
        self.letter_spacing_input.setSingleStep(0.5)
        self.letter_spacing_input.setSuffix(" px")
        self.letter_spacing_input.setValue(settings.letter_spacing)
        self.letter_spacing_input.setStyleSheet(INPUT_STYLE)
        self.letter_spacing_input.setStyle(self._spin_arrow_style)
        form.addRow("Letter spacing:", self.letter_spacing_input)

        self.word_spacing_input = QDoubleSpinBox()
        self.word_spacing_input.setRange(0.0, 50.0)
        self.word_spacing_input.setSingleStep(0.5)
        self.word_spacing_input.setSuffix(" px")
        self.word_spacing_input.setValue(settings.word_spacing)
        self.word_spacing_input.setStyleSheet(INPUT_STYLE)
        self.word_spacing_input.setStyle(self._spin_arrow_style)
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
