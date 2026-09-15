# SPDX-License-Identifier: AGPL-3.0-or-later
"""Command console widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFrame, QCompleter
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont, QColor, QTextCursor

from chimera.interpreter.interpreter import CommandInterpreter


class ConsoleWidget(QWidget):
    """Console widget with > prompt."""

    command_executed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.interpreter = CommandInterpreter()
        self.history: list[str] = []
        self.history_index = -1
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #252526; padding: 10px;")
        header_layout = QHBoxLayout(header)
        title = QLabel("终端")
        title.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.output)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #1e1e1e;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 5, 10, 5)

        self.prompt_label = QLabel(">")
        self.prompt_label.setStyleSheet("color: #569cd6; font-weight: bold; font-family: Consolas;")
        input_layout.addWidget(self.prompt_label)

        self.input_line = QLineEdit()
        self.input_line.setFont(QFont("Consolas", 10))
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: none;
                padding: 5px;
            }
        """)
        self.input_line.returnPressed.connect(self._execute_command)
        self.input_line.keyPressEvent = self._input_key_press
        input_layout.addWidget(self.input_line)

        layout.addWidget(input_frame)

        # Setup completer
        self._setup_completer()

        self._append_output("Chimera 控制台 v0.9.0", "#569cd6")
        self._append_output("输入 help 查看可用命令\n", "#6a9955")

    def _setup_completer(self):
        """Setup tab completion."""
        commands = [
            "help", "clear", "history", "vars", "plugins",
            "exit", "new", "cr", "cancel", "ui", "sys",
            "net", "data", "plugin", "host", "wait", "log"
        ]
        self.completer = QCompleter(commands)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_line.setCompleter(self.completer)

    def _input_key_press(self, event):
        """Handle key press in input."""
        if event.key() == Qt.Key_Up:
            self._history_up()
        elif event.key() == Qt.Key_Down:
            self._history_down()
        elif event.key() == Qt.Key_Tab:
            self._tab_complete()
        else:
            QLineEdit.keyPressEvent(self.input_line, event)

    def _history_up(self):
        """Navigate history up."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_line.setText(self.history[-(self.history_index + 1)])

    def _history_down(self):
        """Navigate history down."""
        if self.history_index > 0:
            self.history_index -= 1
            self.input_line.setText(self.history[-(self.history_index + 1)])
        else:
            self.history_index = -1
            self.input_line.clear()

    def _tab_complete(self):
        """Handle tab completion."""
        text = self.input_line.text()
        if text:
            matches = [c for c in self.interpreter.get_command_names() if c.startswith(text.lower())]
            if len(matches) == 1:
                self.input_line.setText(matches[0])

    def _execute_command(self):
        """Execute the current command."""
        command = self.input_line.text().strip()
        if not command:
            return

        self.history.append(command)
        self.history_index = -1

        self._append_output(f"{self.prompt_label.text()} {command}", "#e0e0e0")

        result = self.interpreter.execute(command)
        if result.output:
            self._append_output(result.output, "#d4d4d4" if result.success else "#f44747")

        if result.new_prompt:
            self.prompt_label.setText(result.new_prompt)

        self.input_line.clear()
        self.command_executed.emit(command)

    def _append_output(self, text: str, color: str = "#d4d4d4"):
        """Append text to output."""
        self.output.setTextColor(QColor(color))
        self.output.append(text)
        self.output.moveCursor(QTextCursor.End)
