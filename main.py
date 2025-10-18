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

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from database.schema import initialize_database
from ui.main_window import MainWindow
from utils.logger import get_logger, info, error, exception

# Initialize logger
logger = get_logger("main")


def main():
    """Main application entry point."""
    try:
        info("=" * 80)
        info("Starting Prism Application")
        info("=" * 80)

        # Initialize database
        info("Initializing database...")
        try:
            initialize_database()
            info("Database initialized successfully")
        except Exception as e:
            error(f"Failed to initialize database: {e}")
            raise

        # Create Qt application
        info("Creating Qt application...")
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName("Prism")
        app.setOrganizationName("Prism")
        app.setApplicationVersion("1.0.0")
        info("Application metadata set")

        # Set application icon for dock/taskbar (prefer prism2.png, fallback to icon.png)
        icon_path = Path(__file__).parent / "assets" / "prism2.png"
        if not icon_path.exists():
            icon_path = Path(__file__).parent / "assets" / "icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            info(f"Application icon set: {icon_path}")
        else:
            logger.warning("Application icon not found")

        # Create and show main window
        info("Creating main window...")
        try:
            window = MainWindow()
            window.show()
            info("Main window created and shown")
        except Exception as e:
            error(f"Failed to create main window: {e}")
            raise

        # Start event loop
        info("Starting Qt event loop...")
        exit_code = app.exec()
        info(f"Application exiting with code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        exception(f"Fatal error in main: {e}")

        # Show error dialog if Qt is available
        try:
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Prism encountered a fatal error and must close:\n\n{str(e)}\n\n"
                f"Please check the logs for more details.",
            )
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
