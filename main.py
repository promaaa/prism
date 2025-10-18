#!/usr/bin/env python3
"""
Prism - Personal Finance & Investment App
Main entry point for the application.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from database.schema import initialize_database
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Initialize database
    print("Initializing database...")
    initialize_database()
    print("Database initialized successfully!")

    # Create Qt application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Prism")
    app.setOrganizationName("Prism")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
