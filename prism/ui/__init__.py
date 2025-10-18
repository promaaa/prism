"""
UI module for Prism application.
Contains all PyQt6 user interface components including main window, tabs, forms, and themes.
"""

from .main_window import MainWindow
from .theme_manager import theme_manager
from .personal_tab import PersonalTab
from .investments_tab import InvestmentsTab
from .reports_tab import ReportsTab
from .orders_tab import OrdersTab

__all__ = [
    "MainWindow",
    "theme_manager",
    "PersonalTab",
    "InvestmentsTab",
    "ReportsTab",
    "OrdersTab",
]
