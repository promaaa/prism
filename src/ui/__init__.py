"""
UI module for Prism application.
Contains all PyQt6 user interface components including main window, tabs, forms, and themes.
"""

from .main_window import MainWindow
from .themes import ThemeManager, Theme

__all__ = ["MainWindow", "ThemeManager", "Theme"]
