"""
Theme management for Prism application.
Provides light and dark theme stylesheets for PyQt6 UI.
"""

from enum import Enum
from typing import Dict


class Theme(Enum):
    """Theme enumeration."""

    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    """
    Manages application themes and provides stylesheets.
    Supports light and dark themes with a clean, modern macOS-inspired design.
    """

    def __init__(self):
        """Initialize the ThemeManager."""
        self._current_theme = Theme.LIGHT
        self._themes = {
            Theme.LIGHT: self._get_light_theme(),
            Theme.DARK: self._get_dark_theme(),
        }

    def get_current_theme(self) -> Theme:
        """
        Get the current theme.

        Returns:
            Theme: Current theme
        """
        return self._current_theme

    def set_theme(self, theme: Theme) -> None:
        """
        Set the current theme.

        Args:
            theme: Theme to set
        """
        if theme in self._themes:
            self._current_theme = theme

    def toggle_theme(self) -> Theme:
        """
        Toggle between light and dark themes.

        Returns:
            Theme: New current theme
        """
        if self._current_theme == Theme.LIGHT:
            self._current_theme = Theme.DARK
        else:
            self._current_theme = Theme.LIGHT
        return self._current_theme

    def get_stylesheet(self, theme: Theme = None) -> str:
        """
        Get the stylesheet for a theme.

        Args:
            theme: Theme to get stylesheet for (uses current theme if None)

        Returns:
            str: CSS stylesheet string
        """
        if theme is None:
            theme = self._current_theme
        return self._themes.get(theme, self._themes[Theme.LIGHT])

    def _get_light_theme(self) -> str:
        """
        Get the light theme stylesheet (Finary-inspired).

        Returns:
            str: Light theme CSS
        """
        return """
        /* Light Theme for Prism - Finary Inspired */

        QMainWindow {
            background-color: #F5F5F5;
        }

        QWidget {
            background-color: #F5F5F5;
            color: #1d1d1f;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
        }

        /* Sidebar */
        .sidebar {
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
            min-width: 200px;
            max-width: 200px;
        }

        .sidebar-collapsed {
            max-width: 60px;
        }

        /* Sidebar Header (icon.png + prism logo) */
        QWidget[class="sidebar-header"] {
            background-color: #FFFFFF;
            border: none;
        }

        QLabel[class="sidebar-icon"] {
            background-color: transparent;
            border: none;
            padding: 0px;
        }

        QLabel[class="sidebar-logo"] {
            background-color: transparent;
            color: #1A1A1A;
            font-size: 20px;
            font-weight: 400;
            font-style: italic;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            border: none;
            padding: 0px;
        }

        .sidebar-button {
            background-color: transparent;
            color: #2E7D78;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }

        .sidebar-button:hover {
            background-color: #F0F8F7;
        }

        .sidebar-button:selected {
            background-color: #2E7D78;
            color: #FFFFFF;
        }

        /* Main Content */
        .main-content {
            background-color: #F5F5F5;
        }

        /* Header */
        .header {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E0E0E0;
            padding: 16px 24px;
        }

        .header-title {
            font-size: 24px;
            font-weight: 700;
            color: #2E7D78;
        }

        /* Cards */
        .card {
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #2E7D78;
        }

        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: #FF6F61;
        }

        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            background-color: #ffffff;
            top: -1px;
        }

        QTabBar::tab {
            background-color: #e8e8ed;
            color: #1d1d1f;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid #d2d2d7;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #0071e3;
            font-weight: 600;
        }

        QTabBar::tab:hover {
            background-color: #f0f0f5;
        }

        /* Push Buttons */
        QPushButton {
            background-color: #0071e3;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            min-width: 80px;
        }

        QPushButton:hover {
            background-color: #0077ed;
        }

        QPushButton:pressed {
            background-color: #0062cc;
        }

        QPushButton:disabled {
            background-color: #d2d2d7;
            color: #86868b;
        }

        QPushButton.secondary {
            background-color: #e8e8ed;
            color: #1d1d1f;
        }

        QPushButton.secondary:hover {
            background-color: #d2d2d7;
        }

        QPushButton.danger {
            background-color: #ff3b30;
            color: #ffffff;
        }

        QPushButton.danger:hover {
            background-color: #ff453a;
        }

        /* Line Edit */
        QLineEdit {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #0071e3;
        }

        QLineEdit:focus {
            border: 2px solid #0071e3;
            padding: 7px 11px;
        }

        /* Text Edit */
        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #0071e3;
        }

        QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #0071e3;
            padding: 7px 11px;
        }

        /* Combo Box */
        QComboBox {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px 12px;
            min-width: 120px;
        }

        QComboBox:hover {
            border: 1px solid #0071e3;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: url(down_arrow_light.png);
            width: 12px;
            height: 12px;
        }

        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            selection-background-color: #0071e3;
            selection-color: #ffffff;
            padding: 4px;
        }

        /* Spin Box / Double Spin Box */
        QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px 12px;
        }

        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #0071e3;
            padding: 7px 11px;
        }

        /* Date Edit */
        QDateEdit {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px 12px;
        }

        QDateEdit:focus {
            border: 2px solid #0071e3;
            padding: 7px 11px;
        }

        /* Table Widget */
        QTableWidget {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            gridline-color: #e8e8ed;
            selection-background-color: #0071e3;
            selection-color: #ffffff;
        }

        QTableWidget::item {
            padding: 8px;
        }

        QTableWidget::item:hover {
            background-color: #f5f5f7;
        }

        QHeaderView::section {
            background-color: #e8e8ed;
            color: #1d1d1f;
            padding: 8px;
            border: none;
            border-bottom: 1px solid #d2d2d7;
            font-weight: 600;
        }

        /* List Widget */
        QListWidget {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 4px;
        }

        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }

        QListWidget::item:hover {
            background-color: #f5f5f7;
        }

        QListWidget::item:selected {
            background-color: #0071e3;
            color: #ffffff;
        }

        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: #f5f5f7;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #c7c7cc;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #aeaeb2;
        }

        QScrollBar:horizontal {
            background-color: #f5f5f7;
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #c7c7cc;
            border-radius: 6px;
            min-width: 20px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #aeaeb2;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }

        /* Label */
        QLabel {
            color: #1d1d1f;
            background-color: transparent;
        }

        QLabel.title {
            font-size: 24px;
            font-weight: 700;
            color: #1d1d1f;
        }

        QLabel.subtitle {
            font-size: 16px;
            font-weight: 600;
            color: #1d1d1f;
        }

        QLabel.caption {
            font-size: 11px;
            color: #86868b;
        }

        /* Group Box */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 600;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 8px;
            color: #1d1d1f;
        }

        /* Progress Bar */
        QProgressBar {
            background-color: #e8e8ed;
            border: none;
            border-radius: 4px;
            height: 8px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #0071e3;
            border-radius: 4px;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #e8e8ed;
            color: #1d1d1f;
            border-top: 1px solid #d2d2d7;
        }

        /* Menu Bar */
        QMenuBar {
            background-color: #f5f5f7;
            color: #1d1d1f;
            border-bottom: 1px solid #d2d2d7;
        }

        QMenuBar::item {
            padding: 6px 12px;
            background-color: transparent;
        }

        QMenuBar::item:selected {
            background-color: #0071e3;
            color: #ffffff;
            border-radius: 4px;
        }

        /* Menu */
        QMenu {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            padding: 4px;
        }

        QMenu::item {
            padding: 8px 24px;
            border-radius: 4px;
        }

        QMenu::item:selected {
            background-color: #0071e3;
            color: #ffffff;
        }

        /* Tool Tip */
        QToolTip {
            background-color: #1d1d1f;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 6px 10px;
        }

        /* Splitter */
        QSplitter::handle {
            background-color: #d2d2d7;
        }

        QSplitter::handle:horizontal {
            width: 1px;
        }

        QSplitter::handle:vertical {
            height: 1px;
        }
        """

    def _get_dark_theme(self) -> str:
        """
        Get the dark theme stylesheet (Finary-inspired).

        Returns:
            str: Dark theme CSS
        """
        return """
        /* Dark Theme for Prism - Finary Inspired */

        QMainWindow {
            background-color: #1A1A1A;
        }

        QWidget {
            background-color: #1A1A1A;
            color: #F5F5F5;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
        }

        /* Sidebar */
        .sidebar {
            background-color: #2A2A2A;
            border-right: 1px solid #404040;
            min-width: 200px;
            max-width: 200px;
        }

        .sidebar-collapsed {
            max-width: 60px;
        }

        /* Sidebar Header (icon.png + prism logo) */
        QWidget[class="sidebar-header"] {
            background-color: #2A2A2A;
            border: none;
        }

        QLabel[class="sidebar-icon"] {
            background-color: transparent;
            border: none;
            padding: 0px;
        }

        QLabel[class="sidebar-logo"] {
            background-color: transparent;
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 400;
            font-style: italic;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            border: none;
            padding: 0px;
        }

        .sidebar-button {
            background-color: transparent;
            color: #2E7D78;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }

        .sidebar-button:hover {
            background-color: #3A3A3A;
        }

        .sidebar-button:selected {
            background-color: #2E7D78;
            color: #FFFFFF;
        }

        /* Main Content */
        .main-content {
            background-color: #1A1A1A;
        }

        /* Header */
        .header {
            background-color: #2A2A2A;
            border-bottom: 1px solid #404040;
            padding: 16px 24px;
        }

        .header-title {
            font-size: 24px;
            font-weight: 700;
            color: #2E7D78;
        }

        /* Cards */
        .card {
            background-color: #2A2A2A;
            border-radius: 12px;
            border: 1px solid #404040;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #2E7D78;
        }

        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: #FF6F61;
        }

        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #38383a;
            border-radius: 8px;
            background-color: #2c2c2e;
            top: -1px;
        }

        QTabBar::tab {
            background-color: #3a3a3c;
            color: #f5f5f7;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid #38383a;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #2c2c2e;
            color: #0a84ff;
            font-weight: 600;
        }

        QTabBar::tab:hover {
            background-color: #48484a;
        }

        /* Push Buttons */
        QPushButton {
            background-color: #0a84ff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            min-width: 80px;
        }

        QPushButton:hover {
            background-color: #409cff;
        }

        QPushButton:pressed {
            background-color: #0077ed;
        }

        QPushButton:disabled {
            background-color: #3a3a3c;
            color: #636366;
        }

        QPushButton.secondary {
            background-color: #3a3a3c;
            color: #f5f5f7;
        }

        QPushButton.secondary:hover {
            background-color: #48484a;
        }

        QPushButton.danger {
            background-color: #ff453a;
            color: #ffffff;
        }

        QPushButton.danger:hover {
            background-color: #ff6961;
        }

        /* Line Edit */
        QLineEdit {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #0a84ff;
        }

        QLineEdit:focus {
            border: 2px solid #0a84ff;
            padding: 7px 11px;
        }

        /* Text Edit */
        QTextEdit, QPlainTextEdit {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #0a84ff;
        }

        QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #0a84ff;
            padding: 7px 11px;
        }

        /* Combo Box */
        QComboBox {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 8px 12px;
            min-width: 120px;
        }

        QComboBox:hover {
            border: 1px solid #0a84ff;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: url(down_arrow_dark.png);
            width: 12px;
            height: 12px;
        }

        QComboBox QAbstractItemView {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            selection-background-color: #0a84ff;
            selection-color: #ffffff;
            padding: 4px;
        }

        /* Spin Box / Double Spin Box */
        QSpinBox, QDoubleSpinBox {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 8px 12px;
        }

        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #0a84ff;
            padding: 7px 11px;
        }

        /* Date Edit */
        QDateEdit {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 8px 12px;
        }

        QDateEdit:focus {
            border: 2px solid #0a84ff;
            padding: 7px 11px;
        }

        /* Table Widget */
        QTableWidget {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            gridline-color: #3a3a3c;
            selection-background-color: #0a84ff;
            selection-color: #ffffff;
        }

        QTableWidget::item {
            padding: 8px;
        }

        QTableWidget::item:hover {
            background-color: #3a3a3c;
        }

        QHeaderView::section {
            background-color: #3a3a3c;
            color: #f5f5f7;
            padding: 8px;
            border: none;
            border-bottom: 1px solid #38383a;
            font-weight: 600;
        }

        /* List Widget */
        QListWidget {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 6px;
            padding: 4px;
        }

        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }

        QListWidget::item:hover {
            background-color: #3a3a3c;
        }

        QListWidget::item:selected {
            background-color: #0a84ff;
            color: #ffffff;
        }

        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: #1c1c1e;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #48484a;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #636366;
        }

        QScrollBar:horizontal {
            background-color: #1c1c1e;
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #48484a;
            border-radius: 6px;
            min-width: 20px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #636366;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }

        /* Label */
        QLabel {
            color: #f5f5f7;
            background-color: transparent;
        }

        QLabel.title {
            font-size: 24px;
            font-weight: 700;
            color: #f5f5f7;
        }

        QLabel.subtitle {
            font-size: 16px;
            font-weight: 600;
            color: #f5f5f7;
        }

        QLabel.caption {
            font-size: 11px;
            color: #98989d;
        }

        /* Group Box */
        QGroupBox {
            background-color: #2c2c2e;
            border: 1px solid #38383a;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 600;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 8px;
            color: #f5f5f7;
        }

        /* Progress Bar */
        QProgressBar {
            background-color: #3a3a3c;
            border: none;
            border-radius: 4px;
            height: 8px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #0a84ff;
            border-radius: 4px;
        }

        /* Settings Page */
        QWidget[class="settings-header"] {
            background-color: #2A2A2A;
            border-bottom: 1px solid #404040;
        }

        QLabel[class="settings-title"] {
            color: #F5F5F5;
            font-size: 24px;
            font-weight: 700;
        }

        QGroupBox[class="settings-section"] {
            background-color: #2A2A2A;
            border: 1px solid #404040;
            border-radius: 12px;
            margin-top: 20px;
            padding-top: 20px;
            font-weight: 600;
            font-size: 15px;
            color: #F5F5F5;
        }

        QGroupBox[class="settings-section"]::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 12px;
            color: #F5F5F5;
        }

        QLabel[class="settings-label"] {
            color: #F5F5F5;
            font-size: 13px;
            font-weight: 500;
        }

        QLabel[class="settings-path"] {
            color: #A0A0A0;
            font-size: 12px;
            font-family: monospace;
        }

        QLabel[class="danger-label"] {
            color: #EF4444;
            font-size: 14px;
        }

        QLabel[class="about-title"] {
            color: #10B981;
            font-size: 16px;
            font-weight: 700;
        }

        QLabel[class="about-version"] {
            color: #A0A0A0;
            font-size: 13px;
        }

        QLabel[class="about-description"] {
            color: #D0D0D0;
            font-size: 13px;
            line-height: 1.5;
        }

        QLabel[class="about-credits"] {
            color: #808080;
            font-size: 11px;
            font-style: italic;
        }

        QComboBox[class="settings-combo"] {
            background-color: #3A3A3A;
            color: #F5F5F5;
            border: 1px solid #4A4A4A;
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 30px;
        }

        QComboBox[class="settings-combo"]:hover {
            border-color: #10B981;
        }

        QComboBox[class="settings-combo"]::drop-down {
            border: none;
            width: 30px;
        }

        QComboBox[class="settings-combo"]::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #A0A0A0;
            margin-right: 8px;
        }

        QSpinBox[class="settings-spin"] {
            background-color: #3A3A3A;
            color: #F5F5F5;
            border: 1px solid #4A4A4A;
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 30px;
        }

        QSpinBox[class="settings-spin"]:hover {
            border-color: #10B981;
        }

        QCheckBox[class="settings-checkbox"] {
            color: #F5F5F5;
            spacing: 8px;
        }

        QCheckBox[class="settings-checkbox"]::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #4A4A4A;
            border-radius: 4px;
            background-color: #3A3A3A;
        }

        QCheckBox[class="settings-checkbox"]::indicator:checked {
            background-color: #10B981;
            border-color: #10B981;
            image: none;
        }

        QCheckBox[class="settings-checkbox"]::indicator:hover {
            border-color: #10B981;
        }

        QPushButton[class="primary-button"] {
            background-color: #10B981;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 600;
        }

        QPushButton[class="primary-button"]:hover {
            background-color: #0EA572;
        }

        QPushButton[class="secondary-button"] {
            background-color: #3A3A3A;
            color: #F5F5F5;
            border: 1px solid #4A4A4A;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
        }

        QPushButton[class="secondary-button"]:hover {
            background-color: #4A4A4A;
            border-color: #10B981;
        }

        QPushButton[class="danger-button"] {
            background-color: #5A2A2A;
            color: #EF4444;
            border: 1px solid #EF4444;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
        }

        QPushButton[class="danger-button"]:hover {
            background-color: #EF4444;
            color: #FFFFFF;
        }

        QRadioButton {
            color: #F5F5F5;
            spacing: 8px;
        }

        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #4A4A4A;
            border-radius: 9px;
            background-color: #3A3A3A;
        }

        QRadioButton::indicator:checked {
            background-color: #10B981;
            border-color: #10B981;
        }

        QRadioButton::indicator:hover {
            border-color: #10B981;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border-top: 1px solid #38383a;
        }

        /* Menu Bar */
        QMenuBar {
            background-color: #1c1c1e;
            color: #f5f5f7;
            border-bottom: 1px solid #38383a;
        }

        QMenuBar::item {
            padding: 6px 12px;
            background-color: transparent;
        }

        QMenuBar::item:selected {
            background-color: #0a84ff;
            color: #ffffff;
            border-radius: 4px;
        }

        /* Menu */
        QMenu {
            background-color: #2c2c2e;
            color: #f5f5f7;
            border: 1px solid #38383a;
            border-radius: 8px;
            padding: 4px;
        }

        QMenu::item {
            padding: 8px 24px;
            border-radius: 4px;
        }

        QMenu::item:selected {
            background-color: #0a84ff;
            color: #ffffff;
        }

        /* Tool Tip */
        QToolTip {
            background-color: #f5f5f7;
            color: #1d1d1f;
            border: none;
            border-radius: 4px;
            padding: 6px 10px;
        }

        /* Splitter */
        QSplitter::handle {
            background-color: #38383a;
        }

        QSplitter::handle:horizontal {
            width: 1px;
        }

        QSplitter::handle:vertical {
            height: 1px;
        }
        """

    def get_color(self, color_name: str, theme: Theme = None) -> str:
        """
        Get a color value for the current theme (Finary-inspired).

        Args:
            color_name: Name of the color
            theme: Theme to get color for (uses current if None)

        Returns:
            str: Color hex value
        """
        if theme is None:
            theme = self._current_theme

        colors = {
            Theme.LIGHT: {
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "primary": "#2E7D78",
                "accent": "#FF6F61",
                "text": "#1d1d1f",
                "text_secondary": "#86868b",
                "border": "#E0E0E0",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "danger": "#FF6F61",
            },
            Theme.DARK: {
                "background": "#1A1A1A",
                "surface": "#2A2A2A",
                "primary": "#2E7D78",
                "accent": "#FF6F61",
                "text": "#F5F5F5",
                "text_secondary": "#B0B0B0",
                "border": "#404040",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "danger": "#FF6F61",
            },
        }

        return colors.get(theme, colors[Theme.LIGHT]).get(color_name, "#000000")
