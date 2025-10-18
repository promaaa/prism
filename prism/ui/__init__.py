"""
UI module for Prism application.
Contains all PyQt6 user interface components including main window, tabs, forms, and themes.
"""

from .main_window import MainWindow
from .themes import ThemeManager, Theme
from .personal_tab import PersonalTab
from .investments_tab import InvestmentsTab
from .reports_tab import ReportsTab
from .orders_tab import OrdersTab

__all__ = [
    "MainWindow",
    "ThemeManager",
    "Theme",
    "PersonalTab",
    "InvestmentsTab",
    "ReportsTab",
    "OrdersTab",
]
