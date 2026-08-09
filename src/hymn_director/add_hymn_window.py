"""Window for adding new hymns to the database."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIntValidator, QPalette
from PyQt6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyleFactory,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from hymn_director import database

WINDOW_STYLE = (
    "QWidget { background-color: #ffffff; color: #000000; }"
    "QLabel { background-color: transparent; color: #000000; }"
    "QScrollArea { background-color: #ffffff; border: 1px solid #cccccc; }"
)

INPUT_STYLE = (
    "QLineEdit, QTextEdit {"
    "  background: #ffffff;"
    "  background-color: #ffffff;"
    "  color: #000000;"
    "  border: 1px solid #cccccc;"
    "  border-radius: 4px;"
    "  padding: 6px;"
    "}"
)

STEPPER_BUTTON_BASE = (
    "QPushButton {"
    "  border: none;"
    "  border-left: 1px solid #cccccc;"
    "  background-color: #f0f0f0;"
    "  color: #333333;"
    "  padding: 0px;"
    "}"
    "QPushButton:hover { background-color: #e8e8e8; }"
    "QPushButton:pressed { background-color: #d8d8d8; }"
)

NUMBER_LINE_STYLE = (
    "QLineEdit {"
    "  background: #ffffff;"
    "  background-color: #ffffff;"
    "  color: #000000;"
    "  border: 1px solid #cccccc;"
    "  border-radius: 4px;"
    "  padding: 6px;"
    "  padding-right: 26px;"
    "}"
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


def _style_text_input(widget: QLineEdit | QTextEdit) -> None:
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    widget.setPalette(palette)
    widget.setStyleSheet(INPUT_STYLE)


class NumberInput(QWidget):
    def __init__(self, minimum: int = 1, maximum: int = 9999, value: int = 1) -> None:
        super().__init__()
        self._minimum = minimum
        self._maximum = maximum

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.line_edit = QLineEdit(str(value))
        self.line_edit.setFont(QFont("Helvetica", 12))
        self.line_edit.setValidator(QIntValidator(minimum, maximum, self))
        self.line_edit.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.line_edit.editingFinished.connect(self._normalize_value)
        self.line_edit.setAutoFillBackground(True)
        palette = self.line_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.line_edit.setPalette(palette)
        self.line_edit.setStyleSheet(NUMBER_LINE_STYLE)

        stepper = QWidget()
        stepper.setFixedWidth(24)
        stepper.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        stepper_layout = QVBoxLayout(stepper)
        stepper_layout.setContentsMargins(0, 1, 1, 1)
        stepper_layout.setSpacing(0)

        arrow_font = QFont("Helvetica", 7)
        self.up_button = QPushButton("▲")
        self.up_button.setFont(arrow_font)
        self.up_button.setStyleSheet(
            STEPPER_BUTTON_BASE
            + "QPushButton { border-bottom: 1px solid #cccccc; border-top-right-radius: 3px; }"
        )
        self.up_button.clicked.connect(self._increment)

        self.down_button = QPushButton("▼")
        self.down_button.setFont(arrow_font)
        self.down_button.setStyleSheet(
            STEPPER_BUTTON_BASE
            + "QPushButton { border-bottom-right-radius: 3px; }"
        )
        self.down_button.clicked.connect(self._decrement)

        stepper_layout.addWidget(self.up_button, stretch=1)
        stepper_layout.addWidget(self.down_button, stretch=1)

        layout.addWidget(self.line_edit, 0, 0)
        layout.addWidget(
            stepper,
            0,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

    def value(self) -> int:
        text = self.line_edit.text().strip()
        if not text:
            return self._minimum
        return int(text)

    def setValue(self, value: int) -> None:
        clamped = max(self._minimum, min(self._maximum, value))
        self.line_edit.setText(str(clamped))

    def _normalize_value(self) -> None:
        self.setValue(self.value())

    def _increment(self) -> None:
        self.setValue(self.value() + 1)

    def _decrement(self) -> None:
        self.setValue(self.value() - 1)


class AddHymnWindow(QMainWindow):
    hymn_saved = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Add Hymn")
        self.resize(520, 560)
        self.setStyle(QStyleFactory.create("Fusion"))

        central = QWidget()
        central.setStyleSheet(WINDOW_STYLE)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_label = QLabel("Add New Hymn")
        title_label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setFont(QFont("Helvetica", 12))
        self.title_input.setPlaceholderText("Hymn title")
        _style_text_input(self.title_input)
        form.addRow("Title:", self.title_input)

        self.number_input = NumberInput(
            value=database.get_next_hymn_number(),
        )
        form.addRow("Number:", self.number_input)

        layout.addLayout(form)

        verses_label = QLabel("Verses")
        verses_label.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        layout.addWidget(verses_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.verses_container = QWidget()
        self.verses_container.setStyleSheet("background-color: #ffffff;")
        self.verses_layout = QVBoxLayout(self.verses_container)
        self.verses_layout.setContentsMargins(8, 8, 8, 8)
        self.verses_layout.setSpacing(12)
        scroll.setWidget(self.verses_container)
        layout.addWidget(scroll, stretch=1)

        self.verse_fields: list[tuple[QLabel, QTextEdit]] = []
        self._add_verse_field()

        verse_button_row = QHBoxLayout()
        add_verse_button = QPushButton("Add Verse")
        add_verse_button.setFont(QFont("Helvetica", 12))
        add_verse_button.setStyleSheet(BUTTON_STYLE)
        add_verse_button.clicked.connect(self._add_verse_field)
        verse_button_row.addWidget(add_verse_button)

        remove_verse_button = QPushButton("Remove Last Verse")
        remove_verse_button.setFont(QFont("Helvetica", 12))
        remove_verse_button.setStyleSheet(BUTTON_STYLE)
        remove_verse_button.clicked.connect(self._remove_last_verse)
        verse_button_row.addWidget(remove_verse_button)
        verse_button_row.addStretch()
        layout.addLayout(verse_button_row)

        action_row = QHBoxLayout()
        action_row.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Helvetica", 12))
        cancel_button.setStyleSheet(BUTTON_STYLE)
        cancel_button.clicked.connect(self.close)
        action_row.addWidget(cancel_button)

        save_button = QPushButton("Save Hymn")
        save_button.setFont(QFont("Helvetica", 12))
        save_button.setStyleSheet(BUTTON_STYLE)
        save_button.clicked.connect(self._save_hymn)
        action_row.addWidget(save_button)
        layout.addLayout(action_row)

    def _add_verse_field(self) -> None:
        verse_number = len(self.verse_fields) + 1
        label = QLabel(f"Verse {verse_number}")
        label.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))

        text_edit = QTextEdit()
        text_edit.setFont(QFont("Helvetica", 12))
        text_edit.setPlaceholderText("Enter verse text...")
        text_edit.setMinimumHeight(100)
        _style_text_input(text_edit)

        self.verses_layout.addWidget(label)
        self.verses_layout.addWidget(text_edit)
        self.verse_fields.append((label, text_edit))

    def _remove_last_verse(self) -> None:
        if len(self.verse_fields) <= 1:
            return
        label, text_edit = self.verse_fields.pop()
        self.verses_layout.removeWidget(text_edit)
        text_edit.deleteLater()
        self.verses_layout.removeWidget(label)
        label.deleteLater()

    def _reset_form(self) -> None:
        self.title_input.clear()
        self.number_input.setValue(database.get_next_hymn_number())
        while len(self.verse_fields) > 1:
            self._remove_last_verse()
        self.verse_fields[0][1].clear()

    def _save_hymn(self) -> None:
        title = self.title_input.text()
        number = self.number_input.value()
        verses = [text_edit.toPlainText() for _, text_edit in self.verse_fields]

        try:
            hymn_id = database.add_hymn(title, number, verses)
        except ValueError as error:
            QMessageBox.warning(self, "Cannot Save Hymn", str(error))
            return

        self.hymn_saved.emit(hymn_id)
        self._reset_form()
        QMessageBox.information(self, "Hymn Saved", "The hymn was added successfully.")
        self.close()
