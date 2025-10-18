"""
CSV Import Dialog for Prism application.
Provides a user-friendly interface for importing transactions from CSV files.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from ..utils.csv_import import CSVImporter, CSVImportError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ImportThread(QThread):
    """Thread for handling CSV import in background."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(int, int, list)
    error = pyqtSignal(str)

    def __init__(self, importer, file_path, skip_duplicates, default_type):
        super().__init__()
        self.importer = importer
        self.file_path = file_path
        self.skip_duplicates = skip_duplicates
        self.default_type = default_type

    def run(self):
        """Run the import process."""
        try:
            self.progress.emit("Starting import...")
            successful, failed, errors = self.importer.import_from_csv(
                self.file_path, self.skip_duplicates, self.default_type
            )
            self.finished.emit(successful, failed, errors)
        except Exception as e:
            self.error.emit(str(e))


class CSVImportDialog(QDialog):
    """Dialog for importing transactions from CSV files."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.importer = CSVImporter(db_manager)
        self.selected_file = None
        self.import_thread = None

        self.setWindowTitle("Import Transactions from CSV")
        self.setModal(True)
        self.resize(700, 600)

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title = QLabel("Import Transactions from CSV")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()

        instructions_text = QLabel(
            "CSV file must contain the following columns:\n"
            "• date (required) - Format: YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY\n"
            "• amount (required) - Positive for income, negative for expenses\n"
            "• category (required) - Transaction category\n"
            "• type (optional) - 'personal' or 'investment'\n"
            "• description (optional) - Transaction notes\n\n"
            "Example:\n"
            "date,amount,category,type,description\n"
            '2024-01-15,-45.50,Food,personal,"Grocery shopping"'
        )
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet("color: #4b5563; font-family: monospace;")
        instructions_layout.addWidget(instructions_text)

        # Download sample button
        sample_btn = QPushButton("📥 Download Sample CSV")
        sample_btn.clicked.connect(self._download_sample)
        instructions_layout.addWidget(sample_btn)

        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)

        # File selection
        file_group = QGroupBox("Select CSV File")
        file_layout = QVBoxLayout()

        file_select_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #6b7280; font-style: italic;")
        file_select_layout.addWidget(self.file_label, 1)

        select_btn = QPushButton("Browse...")
        select_btn.clicked.connect(self._select_file)
        file_select_layout.addWidget(select_btn)

        file_layout.addLayout(file_select_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()

        # Skip duplicates checkbox
        self.skip_duplicates_cb = QCheckBox("Skip duplicate transactions")
        self.skip_duplicates_cb.setChecked(True)
        self.skip_duplicates_cb.setToolTip(
            "Skip transactions that already exist in the database "
            "(same date, amount, and category)"
        )
        options_layout.addWidget(self.skip_duplicates_cb)

        # Default type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Default transaction type:")
        type_layout.addWidget(type_label)

        self.default_type_combo = QComboBox()
        self.default_type_combo.addItems(["personal", "investment"])
        self.default_type_combo.setToolTip(
            "Used when the CSV doesn't specify a transaction type"
        )
        type_layout.addWidget(self.default_type_combo)
        type_layout.addStretch()

        options_layout.addLayout(type_layout)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        # Status/Results area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_btn = QPushButton("Import")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._start_import)
        self.import_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """
        )
        button_layout.addWidget(self.import_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _apply_styles(self):
        """Apply custom styles to the dialog."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1f2937;
            }
            QLabel {
                color: #374151;
            }
            QPushButton {
                background-color: #f3f4f6;
                color: #1f2937;
                border: 1px solid #d1d5db;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QCheckBox {
                color: #374151;
            }
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
        """
        )

    def _select_file(self):
        """Open file dialog to select CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            str(Path.home() / "Downloads"),
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"📄 {Path(file_path).name}")
            self.file_label.setStyleSheet("color: #059669; font-weight: bold;")
            self.import_btn.setEnabled(True)

            # Validate file
            is_valid, error_msg = self.importer.validate_csv_file(file_path)
            if not is_valid:
                QMessageBox.warning(
                    self, "Invalid CSV File", f"File validation failed:\n\n{error_msg}"
                )
                self.selected_file = None
                self.file_label.setText("No file selected")
                self.file_label.setStyleSheet("color: #6b7280; font-style: italic;")
                self.import_btn.setEnabled(False)

    def _download_sample(self):
        """Download a sample CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Sample CSV",
            str(Path.home() / "Downloads" / "prism_sample_import.csv"),
            "CSV Files (*.csv)",
        )

        if file_path:
            try:
                self.importer.generate_sample_csv(file_path)
                QMessageBox.information(
                    self,
                    "Sample Downloaded",
                    f"Sample CSV file saved to:\n{file_path}\n\n"
                    "You can use this as a template for your own data.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to generate sample CSV:\n{str(e)}"
                )

    def _start_import(self):
        """Start the import process."""
        if not self.selected_file:
            return

        # Disable buttons during import
        self.import_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_text.clear()
        self.status_text.setVisible(False)

        # Get options
        skip_duplicates = self.skip_duplicates_cb.isChecked()
        default_type = self.default_type_combo.currentText()

        # Create and start import thread
        self.import_thread = ImportThread(
            self.importer, self.selected_file, skip_duplicates, default_type
        )
        self.import_thread.progress.connect(self._on_progress)
        self.import_thread.finished.connect(self._on_import_finished)
        self.import_thread.error.connect(self._on_import_error)
        self.import_thread.start()

    def _on_progress(self, message: str):
        """Handle progress updates."""
        logger.info(message)

    def _on_import_finished(self, successful: int, failed: int, errors: list):
        """Handle import completion."""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.close_btn.setEnabled(True)

        # Show results
        self.status_text.setVisible(True)
        summary = self.importer.get_import_summary(successful, failed, errors)
        self.status_text.setPlainText(summary)

        # Show summary dialog
        if successful > 0:
            QMessageBox.information(
                self,
                "Import Completed",
                f"Successfully imported {successful} transaction(s).\n"
                f"Failed: {failed} transaction(s).\n\n"
                "See details below for any errors.",
            )

            # Accept dialog to signal success to parent
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Import Failed",
                f"No transactions were imported.\n\n"
                f"Failed: {failed} transaction(s).\n\n"
                "See details below for errors.",
            )

    def _on_import_error(self, error_message: str):
        """Handle import errors."""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.close_btn.setEnabled(True)

        QMessageBox.critical(
            self, "Import Error", f"An error occurred during import:\n\n{error_message}"
        )

        logger.error(f"CSV import error: {error_message}")
