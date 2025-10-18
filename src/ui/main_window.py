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

from database.db_manager import DatabaseManager
from api.crypto_api import CryptoAPI
from api.stock_api import StockAPI
from ui.themes import ThemeManager, Theme


class MainWindow(QMainWindow):
    """
    Main application window with tabbed interface.
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Initialize components
        self.db = DatabaseManager()
        self.crypto_api = CryptoAPI()
        self.stock_api = StockAPI()
        self.theme_manager = ThemeManager()

        # Set up the window
        self.setWindowTitle("Prism - Personal Finance & Investment")
        self.setMinimumSize(1200, 800)

        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Create UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()

        # Apply theme
        self._apply_theme()

        # Center window on screen
        self._center_window()

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Transaction", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_transaction)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Data", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._on_export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_theme_action = QAction("Toggle &Theme", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme_action)

        view_menu.addSeparator()

        refresh_action = QAction("&Refresh Prices", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._on_refresh_prices)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add Transaction button
        add_transaction_btn = QPushButton("+ Transaction")
        add_transaction_btn.clicked.connect(self._on_new_transaction)
        toolbar.addWidget(add_transaction_btn)

        # Add Asset button
        add_asset_btn = QPushButton("+ Asset")
        add_asset_btn.clicked.connect(self._on_new_asset)
        toolbar.addWidget(add_asset_btn)

        toolbar.addSeparator()

        # Refresh Prices button
        refresh_btn = QPushButton("Refresh Prices")
        refresh_btn.clicked.connect(self._on_refresh_prices)
        toolbar.addWidget(refresh_btn)

        toolbar.addSeparator()

        # Theme toggle button
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(theme_btn)

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
        self._create_reports_tab()

    def _create_personal_tab(self):
        """Create the Personal Finances tab."""
        personal_tab = QWidget()
        layout = QVBoxLayout(personal_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Personal Finances")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Summary section
        summary_widget = self._create_personal_summary()
        layout.addWidget(summary_widget)

        # Placeholder for transaction list
        placeholder = QLabel("Transaction list and charts will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setProperty("class", "caption")
        layout.addWidget(placeholder, 1)

        # Add tab
        self.tab_widget.addTab(personal_tab, "Personal Finances")

    def _create_personal_summary(self):
        """Create summary widget for personal finances."""
        summary = QWidget()
        layout = QHBoxLayout(summary)

        # Get balance
        balance = self.db.get_balance()

        # Balance card
        balance_label = QLabel(f"Current Balance\n€{balance:,.2f}")
        balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        balance_label.setStyleSheet(
            "background-color: palette(base); padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(balance_label)

        # Transactions count
        stats = self.db.get_database_stats()
        trans_label = QLabel(f"Total Transactions\n{stats.get('transactions', 0)}")
        trans_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trans_label.setStyleSheet(
            "background-color: palette(base); padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(trans_label)

        return summary

    def _create_investments_tab(self):
        """Create the Investments tab."""
        investments_tab = QWidget()
        layout = QVBoxLayout(investments_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Investments")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Summary section
        summary_widget = self._create_investments_summary()
        layout.addWidget(summary_widget)

        # Placeholder for assets list
        placeholder = QLabel("Asset portfolio and charts will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setProperty("class", "caption")
        layout.addWidget(placeholder, 1)

        # Add tab
        self.tab_widget.addTab(investments_tab, "Investments")

    def _create_investments_summary(self):
        """Create summary widget for investments."""
        summary = QWidget()
        layout = QHBoxLayout(summary)

        # Get portfolio value
        portfolio_value = self.db.get_portfolio_value()
        portfolio_summary = self.db.get_portfolio_summary()

        # Portfolio value card
        value_label = QLabel(f"Portfolio Value\n€{portfolio_value:,.2f}")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(
            "background-color: palette(base); padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(value_label)

        # Assets count
        stats = self.db.get_database_stats()
        assets_label = QLabel(f"Total Assets\n{stats.get('assets', 0)}")
        assets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        assets_label.setStyleSheet(
            "background-color: palette(base); padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(assets_label)

        # Orders count
        orders_label = QLabel(f"Total Orders\n{stats.get('orders', 0)}")
        orders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orders_label.setStyleSheet(
            "background-color: palette(base); padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(orders_label)

        return summary

    def _create_reports_tab(self):
        """Create the Reports tab."""
        reports_tab = QWidget()
        layout = QVBoxLayout(reports_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Reports")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Export buttons
        export_layout = QHBoxLayout()

        export_orders_btn = QPushButton("Export Orders to CSV")
        export_orders_btn.clicked.connect(self._on_export_orders)
        export_layout.addWidget(export_orders_btn)

        export_transactions_btn = QPushButton("Export Transactions to CSV")
        export_transactions_btn.clicked.connect(self._on_export_transactions)
        export_layout.addWidget(export_transactions_btn)

        export_assets_btn = QPushButton("Export Assets to CSV")
        export_assets_btn.clicked.connect(self._on_export_assets)
        export_layout.addWidget(export_assets_btn)

        layout.addLayout(export_layout)

        # Placeholder for reports
        placeholder = QLabel("Reports and charts will appear here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setProperty("class", "caption")
        layout.addWidget(placeholder, 1)

        # Add tab
        self.tab_widget.addTab(reports_tab, "Reports")

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _apply_theme(self):
        """Apply the current theme to the application."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = self.theme_manager.toggle_theme()
        self._apply_theme()
        theme_name = "Dark" if new_theme == Theme.DARK else "Light"
        self.status_bar.showMessage(f"Switched to {theme_name} theme", 3000)

    def _center_window(self):
        """Center the window on the screen."""
        screen = self.screen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def _on_new_transaction(self):
        """Handle new transaction action."""
        QMessageBox.information(
            self,
            "New Transaction",
            "Transaction form will be implemented in the next step.",
        )

    def _on_new_asset(self):
        """Handle new asset action."""
        QMessageBox.information(
            self,
            "New Asset",
            "Asset form will be implemented in the next step.",
        )

    def _on_refresh_prices(self):
        """Handle refresh prices action."""
        self.status_bar.showMessage("Refreshing prices...")

        # Get all assets
        assets = self.db.get_all_assets()

        if not assets:
            self.status_bar.showMessage("No assets to refresh", 3000)
            return

        # Separate by type
        crypto_tickers = [a["ticker"] for a in assets if a["asset_type"] == "crypto"]
        stock_tickers = [
            a["ticker"] for a in assets if a["asset_type"] in ["stock", "bond"]
        ]

        # Fetch prices
        updated_count = 0

        if crypto_tickers:
            crypto_prices = self.crypto_api.get_multiple_prices(crypto_tickers)
            for asset in assets:
                if asset["asset_type"] == "crypto" and asset["ticker"] in crypto_prices:
                    price = crypto_prices[asset["ticker"]]
                    if price:
                        self.db.update_asset_price(asset["id"], price)
                        updated_count += 1

        if stock_tickers:
            stock_prices = self.stock_api.get_multiple_prices(stock_tickers)
            for asset in assets:
                if (
                    asset["asset_type"] in ["stock", "bond"]
                    and asset["ticker"] in stock_prices
                ):
                    price = stock_prices[asset["ticker"]]
                    if price:
                        self.db.update_asset_price(asset["id"], price)
                        updated_count += 1

        self.status_bar.showMessage(
            f"Refreshed prices for {updated_count} assets", 5000
        )

        # Refresh UI
        self._refresh_ui()

    def _on_export_data(self):
        """Handle export data action."""
        QMessageBox.information(
            self,
            "Export Data",
            "Choose export type from the Reports tab.",
        )

    def _on_export_orders(self):
        """Export orders to CSV."""
        from utils.exports import export_orders_to_csv, get_default_export_path

        orders = self.db.get_all_orders()

        if not orders:
            QMessageBox.warning(self, "No Data", "No orders to export.")
            return

        output_path = get_default_export_path("orders.csv")
        success = export_orders_to_csv(orders, output_path)

        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Orders exported to:\n{output_path}",
            )
        else:
            QMessageBox.critical(self, "Export Failed", "Failed to export orders.")

    def _on_export_transactions(self):
        """Export transactions to CSV."""
        from utils.exports import export_transactions_to_csv, get_default_export_path

        transactions = self.db.get_all_transactions()

        if not transactions:
            QMessageBox.warning(self, "No Data", "No transactions to export.")
            return

        output_path = get_default_export_path("transactions.csv")
        success = export_transactions_to_csv(transactions, output_path)

        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Transactions exported to:\n{output_path}",
            )
        else:
            QMessageBox.critical(
                self, "Export Failed", "Failed to export transactions."
            )

    def _on_export_assets(self):
        """Export assets to CSV."""
        from utils.exports import export_assets_to_csv, get_default_export_path

        assets = self.db.get_all_assets()

        if not assets:
            QMessageBox.warning(self, "No Data", "No assets to export.")
            return

        output_path = get_default_export_path("assets.csv")
        success = export_assets_to_csv(assets, output_path)

        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Assets exported to:\n{output_path}",
            )
        else:
            QMessageBox.critical(self, "Export Failed", "Failed to export assets.")

    def _show_about(self):
        """Show about dialog."""
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
            "</ul>",
        )

    def _refresh_ui(self):
        """Refresh the UI with updated data."""
        # This is a placeholder - in a full implementation,
        # we would refresh all tabs with new data
        pass

    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit Prism?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
