# SPDX-License-Identifier: AGPL-3.0-or-later
"""Theme manager for Chimera."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject
from PySide6.QtGui import QPalette, QColor

from chimera.host.settings import SettingsManager

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Microsoft YaHei", sans-serif;
}

#sidebar {
    background-color: #252526;
    border-right: 1px solid #3c3c3c;
}

QListWidget {
    background-color: #252526;
    color: #e0e0e0;
    border: none;
    padding: 5px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #37373d;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
}

QStackedWidget {
    background-color: #1e1e1e;
}

QStatusBar {
    background-color: #007acc;
    color: white;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 5px;
}

QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QLabel {
    color: #e0e0e0;
}

QSplitter::handle {
    background-color: #3c3c3c;
}
"""

LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #ffffff;
    color: #333333;
    font-family: "Microsoft YaHei", sans-serif;
}

#sidebar {
    background-color: #f3f3f3;
    border-right: 1px solid #e0e0e0;
}

QListWidget {
    background-color: #f3f3f3;
    color: #333333;
    border: none;
    padding: 5px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #e0e0e0;
}

QListWidget::item:hover {
    background-color: #e8e8e8;
}

QStatusBar {
    background-color: #007acc;
    color: white;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 5px;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #106ebe;
}
"""


class ThemeManager(QObject):
    """Manages application themes."""

    def __init__(self, settings: SettingsManager):
        super().__init__()
        self.settings = settings

    def apply_theme(self, widget: QWidget):
        """Apply the current theme to a widget."""
        theme = self.settings.theme
        if theme == "dark":
            widget.setStyleSheet(DARK_STYLESHEET)
        else:
            widget.setStyleSheet(LIGHT_STYLESHEET)

    def set_theme(self, theme: str):
        """Set the theme."""
        self.settings.theme = theme
