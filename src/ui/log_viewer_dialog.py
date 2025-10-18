"""
Log viewer dialog for viewing application logs.

This module provides a dialog for viewing and filtering application logs
in real-time, with syntax highlighting and search functionality.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from pathlib import Path
import re


class LogViewerDialog(QDialog):
    """Dialog for viewing and filtering application logs."""

    def __init__(self, parent=None):
        """Initialize the log viewer dialog."""
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setModal(False)
        self.resize(1000, 700)

        # Import logger here to avoid circular imports
        from utils.logger import get_log_files

        self.log_files = get_log_files()
        self.current_log_file = self.log_files["main"]
        self.auto_refresh = False
        self.filter_level = "ALL"

        self._setup_ui()
        self._load_log_file()

        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_log_file)

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Top controls
        controls_layout = QHBoxLayout()

        # Log file selector
        controls_layout.addWidget(QLabel("Log File:"))
        self.log_selector = QComboBox()
        self.log_selector.addItem("Main Log", self.log_files["main"])
        self.log_selector.addItem("Errors Only", self.log_files["errors"])
        self.log_selector.addItem("Performance", self.log_files["performance"])
        self.log_selector.currentIndexChanged.connect(self._on_log_file_changed)
        controls_layout.addWidget(self.log_selector)

        # Log level filter
        controls_layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        self.level_filter.currentTextChanged.connect(self._on_filter_changed)
        controls_layout.addWidget(self.level_filter)

        # Search box
        controls_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter text to search...")
        self.search_box.textChanged.connect(self._on_search_changed)
        self.search_box.setClearButtonEnabled(True)
        controls_layout.addWidget(self.search_box)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Log text display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Monaco", 11))
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_text)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.auto_refresh_btn = QPushButton("Auto-Refresh: OFF")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.toggled.connect(self._toggle_auto_refresh)
        button_layout.addWidget(self.auto_refresh_btn)

        refresh_btn = QPushButton("Refresh Now")
        refresh_btn.clicked.connect(self._load_log_file)
        button_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self._clear_logs)
        button_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_logs)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Apply styling
        self._apply_styling()

    def _apply_styling(self):
        """Apply custom styling to the dialog."""
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                padding: 8px;
            }
        """)

    def _load_log_file(self):
        """Load and display the current log file."""
        try:
            # Import here to avoid circular imports
            from utils.logger import get_log_files

            if not self.current_log_file.exists():
                self.log_text.setPlainText("Log file does not exist yet.")
                return

            # Read the log file
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Apply filters
            content = self._apply_filters(content)

            # Apply syntax highlighting
            self._display_with_highlighting(content)

            # Scroll to bottom if auto-refresh is on
            if self.auto_refresh:
                self.log_text.moveCursor(QTextCursor.MoveOperation.End)

        except Exception as e:
            self.log_text.setPlainText(f"Error loading log file: {str(e)}")

    def _apply_filters(self, content: str) -> str:
        """Apply level and search filters to log content."""
        lines = content.split("\n")
        filtered_lines = []

        search_term = self.search_box.text().lower()

        for line in lines:
            # Apply level filter
            if self.filter_level != "ALL":
                if f"| {self.filter_level} " not in line:
                    continue

            # Apply search filter
            if search_term and search_term not in line.lower():
                continue

            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _display_with_highlighting(self, content: str):
        """Display content with syntax highlighting."""
        self.log_text.clear()
        cursor = self.log_text.textCursor()

        # Define formats for different log levels
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor("#00bcd4"))  # Cyan

        info_format = QTextCharFormat()
        info_format.setForeground(QColor("#4caf50"))  # Green

        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor("#ff9800"))  # Orange

        error_format = QTextCharFormat()
        error_format.setForeground(QColor("#f44336"))  # Red

        critical_format = QTextCharFormat()
        critical_format.setForeground(QColor("#e91e63"))  # Pink
        critical_format.setFontWeight(QFont.Weight.Bold)

        default_format = QTextCharFormat()
        default_format.setForeground(QColor("#d4d4d4"))  # Light gray

        # Highlight search terms
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#ffeb3b"))  # Yellow
        highlight_format.setForeground(QColor("#000000"))  # Black

        search_term = self.search_box.text()

        for line in content.split("\n"):
            # Determine format based on log level
            if "| DEBUG " in line:
                fmt = debug_format
            elif "| INFO " in line:
                fmt = info_format
            elif "| WARNING " in line:
                fmt = warning_format
            elif "| ERROR " in line:
                fmt = error_format
            elif "| CRITICAL " in line:
                fmt = critical_format
            else:
                fmt = default_format

            # Insert the line
            cursor.insertText(line + "\n", fmt)

            # Highlight search terms if any
            if search_term and search_term in line:
                # Go back and highlight
                block = cursor.block()
                text = block.text()
                start_pos = block.position()

                # Find all occurrences (case-insensitive)
                pattern = re.escape(search_term)
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    cursor.setPosition(start_pos + match.start())
                    cursor.setPosition(
                        start_pos + match.end(), QTextCursor.MoveMode.KeepAnchor
                    )
                    cursor.mergeCharFormat(highlight_format)

                # Move cursor back to end
                cursor.movePosition(QTextCursor.MoveOperation.End)

    def _on_log_file_changed(self, index):
        """Handle log file selection change."""
        self.current_log_file = Path(self.log_selector.itemData(index))
        self._load_log_file()

    def _on_filter_changed(self, level):
        """Handle log level filter change."""
        self.filter_level = level
        self._load_log_file()

    def _on_search_changed(self, text):
        """Handle search text change."""
        self._load_log_file()

    def _toggle_auto_refresh(self, checked):
        """Toggle auto-refresh on/off."""
        self.auto_refresh = checked
        if checked:
            self.auto_refresh_btn.setText("Auto-Refresh: ON")
            self.refresh_timer.start(2000)  # Refresh every 2 seconds
        else:
            self.auto_refresh_btn.setText("Auto-Refresh: OFF")
            self.refresh_timer.stop()

    def _clear_logs(self):
        """Clear all log files."""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear all log files?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                from utils.logger import clear_logs

                clear_logs()
                self._load_log_file()
                QMessageBox.information(
                    self, "Success", "All log files have been cleared."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to clear log files:\n{str(e)}"
                )

    def _export_logs(self):
        """Export current log view to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            str(
                Path.home()
                / "Downloads"
                / f"prism_logs_{self.log_selector.currentText().replace(' ', '_')}.txt"
            ),
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(
                    self, "Success", f"Logs exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs:\n{str(e)}")

    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop auto-refresh timer
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()
