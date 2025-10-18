"""
Main window for Prism application.
Provides the primary UI with tabbed interface for Personal Finances, Investments, and Reports.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QStatusBar,
    QMenuBar,
    QMenu,
    QToolBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon

from ..database.db_manager import DatabaseManager
from ..api.crypto_api import CryptoAPI
from ..api.stock_api import StockAPI
from ..utils.logger import get_logger, log_exception
from .themes import ThemeManager, Theme
from .tooltips import Tooltips
from .personal_tab import PersonalTab
from .investments_tab import InvestmentsTab
from .reports_tab import ReportsTab
from .orders_tab import OrdersTab
from .log_viewer_dialog import LogViewerDialog
from .help_dialog import HelpDialog

# Initialize logger for this module
logger = get_logger("ui.main_window")


class MainWindow(QMainWindow):
    """
    Main application window with tabbed interface.
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        logger.info("Initializing MainWindow")

        # Initialize components
        try:
            self.db = DatabaseManager()
            self.crypto_api = CryptoAPI()
            self.stock_api = StockAPI()
            self.theme_manager = ThemeManager()
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

        # Set up the window
        self.setWindowTitle("Prism - Personal Finance & Investment")
        self.setMinimumSize(1200, 800)

        # Set window icon (prefer prism2.png, fallback to icon.png)
        icon_path = Path(__file__).parent.parent.parent / "assets" / "prism2.png"
        if not icon_path.exists():
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            logger.debug(f"Window icon set: {icon_path}")
        else:
            logger.warning("No window icon found")

        # Create UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()

        # Apply theme
        self._apply_theme()

        # Center window on screen
        self._center_window()

        logger.info("MainWindow initialized successfully")

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Transaction", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setToolTip(Tooltips.MAIN_WINDOW["new_transaction"])
        new_action.triggered.connect(self._on_new_transaction)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Data", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setToolTip(Tooltips.MAIN_WINDOW["export_data"])
        export_action.triggered.connect(self._on_export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.setToolTip(Tooltips.MAIN_WINDOW["quit"])
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_theme_action = QAction("Toggle &Theme", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.setToolTip(Tooltips.MAIN_WINDOW["toggle_theme"])
        toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme_action)

        view_menu.addSeparator()

        refresh_action = QAction("&Refresh Prices", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.setToolTip(Tooltips.MAIN_WINDOW["refresh_prices"])
        refresh_action.triggered.connect(self._on_refresh_prices)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        # Log viewer action
        log_viewer_action = QAction("View &Logs", self)
        log_viewer_action.setShortcut(QKeySequence("Ctrl+L"))
        log_viewer_action.setToolTip(Tooltips.MAIN_WINDOW["view_logs"])
        log_viewer_action.triggered.connect(self._show_log_viewer)
        view_menu.addAction(log_viewer_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        help_action = QAction("&Help Topics", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.setToolTip("View comprehensive help and tutorials")
        help_action.triggered.connect(lambda: HelpDialog.show_help("welcome", self))
        help_menu.addAction(help_action)

        help_menu.addSeparator()

        help_personal_action = QAction("Personal Finances Help", self)
        help_personal_action.triggered.connect(
            lambda: HelpDialog.show_help("personal_finances", self)
        )
        help_menu.addAction(help_personal_action)

        help_investments_action = QAction("Investments Help", self)
        help_investments_action.triggered.connect(
            lambda: HelpDialog.show_help("investments", self)
        )
        help_menu.addAction(help_investments_action)

        help_reports_action = QAction("Reports Help", self)
        help_reports_action.triggered.connect(
            lambda: HelpDialog.show_help("reports", self)
        )
        help_menu.addAction(help_reports_action)

        help_orders_action = QAction("Order Book Help", self)
        help_orders_action.triggered.connect(
            lambda: HelpDialog.show_help("orders", self)
        )
        help_menu.addAction(help_orders_action)

        help_menu.addSeparator()

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(
            lambda: HelpDialog.show_help("shortcuts", self)
        )
        help_menu.addAction(shortcuts_action)

        faq_action = QAction("FAQ", self)
        faq_action.triggered.connect(lambda: HelpDialog.show_help("faq", self))
        help_menu.addAction(faq_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        logger.debug("Menu bar created")

    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add Transaction button
        add_transaction_btn = QPushButton("+ Transaction")
        add_transaction_btn.setToolTip(Tooltips.MAIN_WINDOW["new_transaction"])
        add_transaction_btn.clicked.connect(self._on_new_transaction)
        toolbar.addWidget(add_transaction_btn)

        # Add Asset button
        add_asset_btn = QPushButton("+ Asset")
        add_asset_btn.setToolTip(Tooltips.MAIN_WINDOW["new_asset"])
        add_asset_btn.clicked.connect(self._on_new_asset)
        toolbar.addWidget(add_asset_btn)

        toolbar.addSeparator()

        # Refresh Prices button
        refresh_btn = QPushButton("Refresh Prices")
        refresh_btn.setToolTip(Tooltips.MAIN_WINDOW["refresh_prices"])
        refresh_btn.clicked.connect(self._on_refresh_prices)
        toolbar.addWidget(refresh_btn)

        toolbar.addSeparator()

        # Theme toggle button
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setToolTip(Tooltips.MAIN_WINDOW["toggle_theme"])
        theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(theme_btn)

        toolbar.addSeparator()

        # Log viewer button
        log_btn = QPushButton("View Logs")
        log_btn.setToolTip(Tooltips.MAIN_WINDOW["view_logs"])
        log_btn.clicked.connect(self._show_log_viewer)
        toolbar.addWidget(log_btn)

        toolbar.addSeparator()

        # Help button
        help_btn = QPushButton("? Help")
        help_btn.setToolTip("View help and tutorials (F1)")
        help_btn.clicked.connect(lambda: HelpDialog.show_help("welcome", self))
        toolbar.addWidget(help_btn)

        logger.debug("Toolbar created")

    def _create_central_widget(self):
        """Create the central widget with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_personal_tab()
        self._create_investments_tab()
        self._create_orders_tab()
        self._create_reports_tab()

        logger.debug("Central widget created with all tabs")

    def _create_personal_tab(self):
        """Create the Personal Finances tab."""
        try:
            self.personal_tab = PersonalTab(self.db)
            self.personal_tab.data_changed.connect(self._on_data_changed)
            self.tab_widget.addTab(self.personal_tab, "Personal Finances")
            logger.debug("Personal tab created")
        except Exception as e:
            logger.error(f"Failed to create personal tab: {e}")
            raise

    def _create_investments_tab(self):
        """Create the Investments tab."""
        try:
            self.investments_tab = InvestmentsTab(
                self.db, self.crypto_api, self.stock_api
            )
            self.investments_tab.data_changed.connect(self._on_data_changed)
            self.tab_widget.addTab(self.investments_tab, "Investments")
            logger.debug("Investments tab created")
        except Exception as e:
            logger.error(f"Failed to create investments tab: {e}")
            raise

    def _create_orders_tab(self):
        """Create the Orders tab."""
        try:
            self.orders_tab = OrdersTab(self.db)
            self.orders_tab.data_changed.connect(self._on_data_changed)
            self.tab_widget.addTab(self.orders_tab, "Order Book")
            logger.debug("Orders tab created")
        except Exception as e:
            logger.error(f"Failed to create orders tab: {e}")
            raise

    def _create_reports_tab(self):
        """Create the Reports tab."""
        try:
            self.reports_tab = ReportsTab(self.db)
            self.reports_tab.data_changed.connect(self._on_data_changed)
            self.tab_widget.addTab(self.reports_tab, "Reports")
            logger.debug("Reports tab created")
        except Exception as e:
            logger.error(f"Failed to create reports tab: {e}")
            raise

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        logger.debug("Status bar created")

    def _apply_theme(self):
        """Apply the current theme to the application."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        logger.debug("Theme applied")

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = self.theme_manager.toggle_theme()
        self._apply_theme()
        theme_name = "Dark" if new_theme == Theme.DARK else "Light"
        self.status_bar.showMessage(f"Switched to {theme_name} theme", 3000)
        logger.info(f"Theme toggled to {theme_name}")

    def _center_window(self):
        """Center the window on the screen."""
        screen = self.screen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    @log_exception
    def _on_new_transaction(self, checked=False):
        """Handle new transaction action."""
        logger.debug("New transaction action triggered")
        # Trigger the personal tab's add transaction dialog
        self.personal_tab._on_add_transaction()

    @log_exception
    def _on_new_asset(self, checked=False):
        """Handle new asset action."""
        logger.debug("New asset action triggered")
        # Trigger the investments tab's add asset dialog
        self.investments_tab._on_add_asset()

    @log_exception
    def _on_refresh_prices(self, checked=False):
        """Handle refresh prices action."""
        logger.info("Refresh prices action triggered")
        # Trigger the investments tab's refresh prices functionality
        self.investments_tab._on_refresh_prices()

    @log_exception
    def _on_export_data(self, checked=False):
        """Handle export data action."""
        logger.debug("Export data action triggered")
        # Switch to reports tab which has export functionality
        self.tab_widget.setCurrentWidget(self.reports_tab)

    def _show_log_viewer(self, checked=False):
        """Show the log viewer dialog."""
        logger.info("Opening log viewer")
        try:
            log_viewer = LogViewerDialog(self)
            log_viewer.exec()
        except Exception as e:
            logger.error(f"Failed to open log viewer: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open log viewer:\n{str(e)}")

    def _show_about(self, checked=False):
        """Show about dialog."""
        logger.debug("Showing about dialog")
        QMessageBox.about(
            self,
            "About Prism",
            "<h3>Prism</h3>"
            "<p>Personal Finance & Investment Application</p>"
            "<p>Version 1.0.0 (MVP)</p>"
            "<p>A local macOS application for managing personal finances "
            "and investments with real-time data.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Personal finance tracking</li>"
            "<li>Investment portfolio management</li>"
            "<li>Real-time cryptocurrency prices (CoinGecko)</li>"
            "<li>Real-time stock prices (Yahoo Finance)</li>"
            "<li>Interactive charts and reports</li>"
            "<li>CSV data export</li>"
            "<li>Comprehensive logging system</li>"
            "</ul>",
        )

    def _refresh_ui(self):
        """Refresh the UI with updated data."""
        logger.debug("Refreshing all UI tabs")
        # Refresh personal tab
        if hasattr(self, "personal_tab"):
            self.personal_tab.refresh()
        # Refresh investments tab
        if hasattr(self, "investments_tab"):
            self.investments_tab.refresh()
        # Refresh orders tab
        if hasattr(self, "orders_tab"):
            self.orders_tab.refresh()
        # Refresh reports tab
        if hasattr(self, "reports_tab"):
            self.reports_tab.refresh()

    def _on_data_changed(self):
        """Handle data changed signal from tabs."""
        logger.debug("Data changed, refreshing UI")
        # Refresh all tabs when data changes
        self._refresh_ui()
        self.status_bar.showMessage("Data updated", 2000)

    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Application close requested")
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit Prism?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            event.accept()
        else:
            logger.debug("Application close cancelled")
            event.ignore()
