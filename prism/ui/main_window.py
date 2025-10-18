"""
Main window for Prism application.
Provides the primary UI with Finary-inspired sidebar navigation for Personal Finances, Investments, Reports, and Orders.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QStatusBar,
    QMenuBar,
    QMenu,
    QLineEdit,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QPixmap

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
from .settings_tab import SettingsTab
from .log_viewer_dialog import LogViewerDialog
from .help_dialog import HelpDialog
from .csv_import_dialog import CSVImportDialog
from .recurring_dialog import RecurringDialog
from .categories_dialog import CategoriesDialog

# Initialize logger for this module
logger = get_logger("ui.main_window")


class MainWindow(QMainWindow):
    """
    Main application window with Finary-inspired sidebar navigation.
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

        # Sidebar state
        self.sidebar_collapsed = False

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

        # Import CSV action
        import_action = QAction("&Import from CSV", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.setToolTip("Import transactions from CSV file")
        import_action.triggered.connect(self._on_import_csv)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.setToolTip(Tooltips.MAIN_WINDOW["quit"])
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        recurring_action = QAction("&Recurring Transactions", self)
        recurring_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        recurring_action.setToolTip("Manage recurring transactions")
        recurring_action.triggered.connect(self._on_recurring_transactions)
        tools_menu.addAction(recurring_action)

        categories_action = QAction("&Categories && Budgets", self)
        categories_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        categories_action.setToolTip("Manage categories and budget limits")
        categories_action.triggered.connect(self._on_manage_categories)
        tools_menu.addAction(categories_action)

        tools_menu.addSeparator()

        pdf_report_action = QAction("Generate &PDF Report", self)
        pdf_report_action.setShortcut(QKeySequence("Ctrl+P"))
        pdf_report_action.setToolTip("Generate PDF financial report")
        pdf_report_action.triggered.connect(self._on_generate_pdf_report)
        tools_menu.addAction(pdf_report_action)

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

    def _create_header(self):
        """Create the top header with title, search, and refresh."""
        header = QWidget()
        header.setProperty("class", "header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        # Title
        title = QLabel("Prism")
        title.setProperty("class", "header-title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search transactions, assets...")
        self.search_edit.setMaximumWidth(300)
        header_layout.addWidget(self.search_edit)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Refresh all data")
        refresh_btn.clicked.connect(self._on_refresh_prices)
        header_layout.addWidget(refresh_btn)

        return header

    def _create_central_widget(self):
        """Create the central widget with sidebar and main content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main content area (create BEFORE sidebar)
        main_area = QWidget()
        main_area.setProperty("class", "main-content")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Stacked widget for content (MUST be created before sidebar)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Create content pages
        self._create_personal_page()
        self._create_investments_page()
        self._create_orders_page()
        self._create_reports_page()
        self._create_settings_page()

        # NOW create sidebar (after content_stack exists)
        self.sidebar = self._create_sidebar()
        layout.addWidget(self.sidebar)

        layout.addWidget(main_area)

        logger.debug("Central widget created with sidebar and content")

    def _create_sidebar(self):
        """Create the fixed dark sidebar with Finary-style navigation."""
        sidebar = QWidget()
        sidebar.setProperty("class", "sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 24)
        layout.setSpacing(0)

        # Sidebar header with logo (Finary style)
        header_widget = QWidget()
        header_widget.setProperty("class", "sidebar-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 24, 20, 24)
        header_layout.setSpacing(12)

        # Icon image (icon.png) - 50x50px, aligned left
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(
                50,
                50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setFixedSize(50, 50)
            icon_label.setProperty("class", "sidebar-icon")
            header_layout.addWidget(icon_label)
            logger.debug(f"Sidebar icon loaded: {icon_path}")
        else:
            logger.warning(f"Sidebar icon not found: {icon_path}")

        # Text logo
        logo = QLabel("prism")
        logo.setProperty("class", "sidebar-logo")
        header_layout.addWidget(logo)
        header_layout.addStretch()

        layout.addWidget(header_widget)

        # Sidebar navigation section
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 8, 0, 0)
        nav_layout.setSpacing(2)

        # Sidebar buttons (Finary icons: home, wallet, chart, file)
        self.sidebar_buttons = []

        # Synthèse / Dashboard
        dashboard_btn = QPushButton("🏠  Synthèse")
        dashboard_btn.setProperty("class", "sidebar-button")
        dashboard_btn.setMinimumHeight(48)
        dashboard_btn.clicked.connect(lambda: self._switch_to_page(0))
        nav_layout.addWidget(dashboard_btn)
        self.sidebar_buttons.append(dashboard_btn)

        # Patrimoine / Investments
        investments_btn = QPushButton("💼  Patrimoine")
        investments_btn.setProperty("class", "sidebar-button")
        investments_btn.setMinimumHeight(48)
        investments_btn.clicked.connect(lambda: self._switch_to_page(1))
        nav_layout.addWidget(investments_btn)
        self.sidebar_buttons.append(investments_btn)

        # Investir / Orders
        orders_btn = QPushButton("📈  Investir")
        orders_btn.setProperty("class", "sidebar-button")
        orders_btn.setMinimumHeight(48)
        orders_btn.clicked.connect(lambda: self._switch_to_page(2))
        nav_layout.addWidget(orders_btn)
        self.sidebar_buttons.append(orders_btn)

        # Analyses / Reports
        reports_btn = QPushButton("📊  Analyses")
        reports_btn.setProperty("class", "sidebar-button")
        reports_btn.setMinimumHeight(48)
        reports_btn.clicked.connect(lambda: self._switch_to_page(3))
        nav_layout.addWidget(reports_btn)
        self.sidebar_buttons.append(reports_btn)

        layout.addWidget(nav_container)
        layout.addStretch()

        # Settings/Profile at bottom (Finary style)
        settings_btn = QPushButton("⚙️  Paramètres")
        settings_btn.setProperty("class", "sidebar-button")
        settings_btn.setMinimumHeight(48)
        settings_btn.clicked.connect(lambda: self._switch_to_page(4))
        layout.addWidget(settings_btn)

        # Select first button after sidebar is created
        self._switch_to_page(0)

        return sidebar

    def _create_personal_page(self):
        """Create the Personal Finances page."""
        try:
            self.personal_tab = PersonalTab(self.db)
            self.personal_tab.data_changed.connect(self._on_data_changed)
            self.content_stack.addWidget(self.personal_tab)
            logger.debug("Personal page created")
        except Exception as e:
            logger.error(f"Failed to create personal page: {e}")
            raise

    def _create_investments_page(self):
        """Create the Investments page."""
        try:
            self.investments_tab = InvestmentsTab(
                self.db, self.crypto_api, self.stock_api
            )
            self.investments_tab.data_changed.connect(self._on_data_changed)
            self.content_stack.addWidget(self.investments_tab)
            logger.debug("Investments page created")
        except Exception as e:
            logger.error(f"Failed to create investments page: {e}")
            raise

    def _create_orders_page(self):
        """Create the Orders page."""
        try:
            self.orders_tab = OrdersTab(self.db)
            self.orders_tab.data_changed.connect(self._on_data_changed)
            self.content_stack.addWidget(self.orders_tab)
            logger.debug("Orders page created")
        except Exception as e:
            logger.error(f"Failed to create orders page: {e}")
            raise

    def _create_reports_page(self):
        """Create the Reports page."""
        try:
            self.reports_tab = ReportsTab(self.db)
            self.reports_tab.data_changed.connect(self._on_data_changed)
            self.content_stack.addWidget(self.reports_tab)
            logger.debug("Reports page created")
        except Exception as e:
            logger.error(f"Failed to create reports page: {e}")
            raise

    def _create_settings_page(self):
        """Create the Settings page."""
        try:
            self.settings_tab = SettingsTab(self.db)
            self.settings_tab.settings_changed.connect(self._on_settings_changed)
            self.settings_tab.theme_changed.connect(self._toggle_theme)
            self.content_stack.addWidget(self.settings_tab)
            logger.debug("Settings page created")
        except Exception as e:
            logger.error(f"Failed to create settings page: {e}")
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

    def _switch_to_page(self, index):
        """Switch to the specified page."""
        self.content_stack.setCurrentIndex(index)

        # Update sidebar button styles
        for i, btn in enumerate(self.sidebar_buttons):
            if i == index:
                btn.setProperty("class", "sidebar-button selected")
            else:
                btn.setProperty("class", "sidebar-button")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _toggle_sidebar(self):
        """Toggle sidebar collapse/expand."""
        if self.sidebar_collapsed:
            # Expand
            self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.sidebar_animation.setDuration(300)
            self.sidebar_animation.setStartValue(60)
            self.sidebar_animation.setEndValue(200)
            self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.sidebar_animation.start()
            self.sidebar_collapsed = False
        else:
            # Collapse
            self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.sidebar_animation.setDuration(300)
            self.sidebar_animation.setStartValue(200)
            self.sidebar_animation.setEndValue(60)
            self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.sidebar_animation.start()
            self.sidebar_collapsed = True

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
        # Switch to reports page which has export functionality
        self._switch_to_page(3)

    @log_exception
    def _on_import_csv(self, checked=False):
        """Handle CSV import action."""
        logger.info("CSV import action triggered")
        try:
            dialog = CSVImportDialog(self.db_manager, self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Failed to open CSV import dialog: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to open CSV import dialog:\n{str(e)}"
            )

    @log_exception
    def _on_recurring_transactions(self, checked=False):
        """Handle recurring transactions management."""
        logger.info("Recurring transactions dialog triggered")
        try:
            dialog = RecurringDialog(self.db_manager, self)
            dialog.data_changed.connect(self._refresh_ui)
            dialog.exec()
        except Exception as e:
            logger.error(f"Failed to open recurring transactions dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open recurring transactions dialog:\n{str(e)}",
            )

    @log_exception
    def _on_manage_categories(self, checked=False):
        """Handle categories and budget management."""
        logger.info("Categories management dialog triggered")
        try:
            dialog = CategoriesDialog(self.db_manager, self)
            dialog.data_changed.connect(self._refresh_ui)
            dialog.exec()
        except Exception as e:
            logger.error(f"Failed to open categories dialog: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to open categories dialog:\n{str(e)}"
            )

    @log_exception
    def _on_generate_pdf_report(self, checked=False):
        """Handle PDF report generation."""
        logger.info("PDF report generation triggered")
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        from ..utils.pdf_reports import PDFReportGenerator

        try:
            # Ask user for save location
            default_filename = (
                f"prism_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                str(Path.home() / "Downloads" / default_filename),
                "PDF Files (*.pdf)",
            )

            if file_path:
                # Generate report
                generator = PDFReportGenerator(self.db_manager)
                generator.generate_full_report(file_path)

                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF report generated successfully!\n\nSaved to:\n{file_path}",
                )

                logger.info(f"PDF report generated: {file_path}")

        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "PDF generation requires ReportLab.\n\n"
                "Please install it with:\npip install reportlab",
            )
            logger.error("ReportLab not installed")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to generate PDF report:\n{str(e)}"
            )

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
        logger.debug("Refreshing all UI pages")
        # Refresh personal page
        if hasattr(self, "personal_tab"):
            self.personal_tab.refresh()
        # Refresh investments page
        if hasattr(self, "investments_tab"):
            self.investments_tab.refresh()
        # Refresh orders page
        if hasattr(self, "orders_tab"):
            self.orders_tab.refresh()
        # Refresh reports page
        if hasattr(self, "reports_tab"):
            self.reports_tab.refresh()

    def _on_data_changed(self):
        """Handle data changed signal from tabs."""
        logger.debug("Data changed, refreshing UI")
        # Refresh all tabs when data changes
        self._refresh_ui()
        self.status_bar.showMessage("Data updated", 2000)

    def _on_settings_changed(self):
        """Handle settings changed signal from settings tab."""
        logger.debug("Settings changed")
        self.status_bar.showMessage("Settings saved successfully", 3000)
        # Optionally reload settings-dependent components
        # For example: refresh UI with new font size, currency format, etc.

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
