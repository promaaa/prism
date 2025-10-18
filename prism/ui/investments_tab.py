"""
Investments tab for Prism application.
Displays investment portfolio management interface with forms, tables, and charts.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QDialogButtonBox,
    QMessageBox,
    QFrame,
    QProgressBar,
    QCompleter,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QThread, QStringListModel
from PyQt6.QtGui import QColor, QFont

from ..database.db_manager import DatabaseManager
from ..api.crypto_api import CryptoAPI
from ..api.stock_api import StockAPI
from ..utils.ticker_data import get_ticker_suggestions, extract_ticker


class PriceUpdateWorker(QThread):
    """Worker thread for updating asset prices."""

    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, str)

    def __init__(self, db_manager, crypto_api, stock_api):
        super().__init__()
        self.db = db_manager
        self.crypto_api = crypto_api
        self.stock_api = stock_api

    def run(self):
        """Update prices in background thread."""
        results = {"updated": 0, "failed": 0, "total": 0}

        try:
            # Get all assets
            assets = self.db.get_all_assets()
            results["total"] = len(assets)

            if not assets:
                self.finished.emit(results)
                return

            # Separate by type
            crypto_tickers = [
                a["ticker"] for a in assets if a["asset_type"] == "crypto"
            ]
            stock_tickers = [
                a["ticker"] for a in assets if a["asset_type"] in ["stock", "bond"]
            ]

            # Update crypto prices
            if crypto_tickers:
                self.progress.emit(30, "Fetching crypto prices...")
                crypto_prices = self.crypto_api.get_multiple_prices(crypto_tickers)
                for asset in assets:
                    if (
                        asset["asset_type"] == "crypto"
                        and asset["ticker"] in crypto_prices
                    ):
                        price = crypto_prices[asset["ticker"]]
                        if price:
                            self.db.update_asset_price(asset["id"], price)
                            results["updated"] += 1
                        else:
                            results["failed"] += 1

            # Update stock prices
            if stock_tickers:
                self.progress.emit(70, "Fetching stock prices...")
                stock_prices = self.stock_api.get_multiple_prices(stock_tickers)
                for asset in assets:
                    if (
                        asset["asset_type"] in ["stock", "bond"]
                        and asset["ticker"] in stock_prices
                    ):
                        price = stock_prices[asset["ticker"]]
                        if price:
                            self.db.update_asset_price(asset["id"], price)
                            results["updated"] += 1
                        else:
                            results["failed"] += 1

            self.progress.emit(100, "Complete")

        except Exception as e:
            print(f"Error updating prices: {e}")

        self.finished.emit(results)


class AssetDialog(QDialog):
    """Dialog for adding/editing assets."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        crypto_api: CryptoAPI,
        stock_api: StockAPI,
        asset: Optional[Dict[str, Any]] = None,
        parent=None,
    ):
        """
        Initialize asset dialog.

        Args:
            db_manager: Database manager instance
            crypto_api: Crypto API instance
            stock_api: Stock API instance
            asset: Existing asset data for editing (None for new)
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.crypto_api = crypto_api
        self.stock_api = stock_api
        self.asset = asset
        self.is_edit = asset is not None

        self.setWindowTitle("Edit Asset" if self.is_edit else "New Asset")
        self.setMinimumWidth(550)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Asset Type field
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems(["crypto", "stock", "bond"])
        if self.is_edit and self.asset:
            current_type = self.asset.get("asset_type", "crypto")
            index = self.asset_type_combo.findText(current_type)
            if index >= 0:
                self.asset_type_combo.setCurrentIndex(index)
        self.asset_type_combo.currentTextChanged.connect(self._on_asset_type_changed)
        form_layout.addRow("Asset Type:", self.asset_type_combo)

        # Ticker field with autocomplete
        self.ticker_edit = QLineEdit()
        self.ticker_edit.setPlaceholderText("Start typing ticker or company name...")

        # Set up autocomplete
        self.ticker_suggestions = get_ticker_suggestions()
        self._setup_ticker_autocomplete()

        if self.is_edit and self.asset:
            self.ticker_edit.setText(self.asset.get("ticker", ""))
            self.ticker_edit.setEnabled(False)  # Don't allow changing ticker

        self.ticker_edit.textChanged.connect(self._on_ticker_changed)
        form_layout.addRow("Ticker:", self.ticker_edit)

        # Add info label for selected ticker
        self.ticker_info_label = QLabel("")
        self.ticker_info_label.setStyleSheet(
            "color: #2196F3; font-size: 11px; font-style: italic;"
        )
        self.ticker_info_label.setWordWrap(True)
        form_layout.addRow("", self.ticker_info_label)

        # Quantity field
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("e.g., 0.5 BTC or 10 shares")
        if self.is_edit and self.asset:
            self.quantity_edit.setText(str(self.asset.get("quantity", "")))
        form_layout.addRow("Quantity:", self.quantity_edit)

        # Buy Price field
        self.buy_price_edit = QLineEdit()
        self.buy_price_edit.setPlaceholderText("Purchase price per unit")
        if self.is_edit and self.asset:
            self.buy_price_edit.setText(str(self.asset.get("price_buy", "")))
        form_layout.addRow("Buy Price (€):", self.buy_price_edit)

        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        if self.is_edit and self.asset:
            date_str = self.asset.get("date_buy", "")
            if date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                self.date_edit.setDate(
                    QDate(date_obj.year, date_obj.month, date_obj.day)
                )
        else:
            self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Purchase Date:", self.date_edit)

        # Current Price field (read-only)
        if self.is_edit and self.asset:
            current_price = self.asset.get("current_price", 0)
            current_price_label = QLabel(f"€{current_price:,.2f}")
            current_price_label.setStyleSheet("font-weight: bold; color: #2196F3;")
            form_layout.addRow("Current Price:", current_price_label)

        layout.addLayout(form_layout)

        # Help text
        stats = self.ticker_suggestions.get_stats()
        help_label = QLabel(
            f"💡 Start typing to see suggestions from {stats['stocks']} CAC 40 stocks "
            f"and {stats['crypto']} top cryptocurrencies. "
            "Suggestions show: TICKER - Company Name (Sector)"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        layout.addWidget(help_label)

        # Fetch price button (only for new assets)
        if not self.is_edit:
            self.fetch_price_btn = QPushButton("🔄 Fetch Current Price")
            self.fetch_price_btn.clicked.connect(self._on_fetch_price)
            layout.addWidget(self.fetch_price_btn)

            self.price_result_label = QLabel("")
            self.price_result_label.setWordWrap(True)
            layout.addWidget(self.price_result_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _setup_ticker_autocomplete(self):
        """Set up autocomplete for ticker field."""
        # Get all formatted suggestions
        all_suggestions = []
        for ticker in self.ticker_suggestions.get_all_tickers():
            ticker_info = self.ticker_suggestions.get_ticker_info(ticker)
            formatted = self.ticker_suggestions.format_suggestion(*ticker_info)
            all_suggestions.append(formatted)

        # Create completer
        self.completer = QCompleter(all_suggestions)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setMaxVisibleItems(10)

        # Set completer on ticker field
        self.ticker_edit.setCompleter(self.completer)

        # Handle selection
        self.completer.activated.connect(self._on_suggestion_selected)

    def _on_asset_type_changed(self, asset_type: str):
        """Handle asset type change to update suggestions."""
        # Update autocomplete suggestions based on asset type
        suggestions = []

        for ticker in self.ticker_suggestions.get_all_tickers():
            ticker_type = self.ticker_suggestions.get_asset_type(ticker)
            # Show all for bonds, filter for crypto/stock
            if asset_type == "bond" or asset_type == ticker_type:
                ticker_info = self.ticker_suggestions.get_ticker_info(ticker)
                formatted = self.ticker_suggestions.format_suggestion(*ticker_info)
                suggestions.append(formatted)

        # Update completer model
        model = QStringListModel(suggestions)
        self.completer.setModel(model)

    def _on_ticker_changed(self, text: str):
        """Handle ticker text change to show info."""
        if not text or self.is_edit:
            self.ticker_info_label.setText("")
            return

        # Try to extract ticker if it's a formatted suggestion
        ticker = extract_ticker(text) if " - " in text else text.strip().upper()

        # Get ticker info
        ticker_info = self.ticker_suggestions.get_ticker_info(ticker)
        if ticker_info[1] != "Unknown":
            _, name, category = ticker_info
            self.ticker_info_label.setText(f"📊 {name} • {category}")

            # Auto-set asset type if we know it
            asset_type = self.ticker_suggestions.get_asset_type(ticker)
            if asset_type != "unknown":
                index = self.asset_type_combo.findText(asset_type)
                if index >= 0:
                    self.asset_type_combo.setCurrentIndex(index)
        else:
            self.ticker_info_label.setText("")

    def _on_suggestion_selected(self, suggestion: str):
        """Handle when user selects a suggestion."""
        # Extract ticker from formatted suggestion
        ticker = extract_ticker(suggestion)
        self.ticker_edit.setText(ticker)

        # Update info label
        ticker_info = self.ticker_suggestions.get_ticker_info(ticker)
        if ticker_info[1] != "Unknown":
            _, name, category = ticker_info
            self.ticker_info_label.setText(f"✅ Selected: {name} • {category}")

    def _on_fetch_price(self):
        """Fetch current price for the ticker."""
        ticker_text = self.ticker_edit.text().strip()
        asset_type = self.asset_type_combo.currentText()

        if not ticker_text:
            self.price_result_label.setText("❌ Please enter a ticker first")
            self.price_result_label.setStyleSheet("color: #F44336;")
            return

        # Extract ticker if it's a formatted suggestion
        ticker = (
            extract_ticker(ticker_text) if " - " in ticker_text else ticker_text.upper()
        )

        self.price_result_label.setText("⏳ Fetching price...")
        self.price_result_label.setStyleSheet("color: #666;")
        self.fetch_price_btn.setEnabled(False)

        # Fetch price based on type
        price = None
        if asset_type == "crypto":
            price = self.crypto_api.get_price(ticker)
        else:
            price = self.stock_api.get_price(ticker)

        self.fetch_price_btn.setEnabled(True)

        if price:
            self.price_result_label.setText(f"✅ Current price: €{price:,.2f}")
            self.price_result_label.setStyleSheet("color: #4CAF50;")
        else:
            self.price_result_label.setText(
                f"❌ Could not fetch price for {ticker}. "
                "Check ticker symbol or try again later."
            )
            self.price_result_label.setStyleSheet("color: #F44336;")

    def _on_accept(self):
        """Validate and accept dialog."""
        # Validate ticker - extract from suggestion if needed
        ticker_text = self.ticker_edit.text().strip()
        if not ticker_text:
            QMessageBox.warning(self, "Missing Ticker", "Please enter a ticker symbol.")
            self.ticker_edit.setFocus()
            return

        # Extract ticker if it's a formatted suggestion
        ticker = (
            extract_ticker(ticker_text) if " - " in ticker_text else ticker_text.upper()
        )

        # Validate quantity
        try:
            quantity = float(self.quantity_edit.text())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Quantity",
                "Please enter a valid positive number for quantity.",
            )
            self.quantity_edit.setFocus()
            return

        # Validate buy price
        try:
            buy_price = float(self.buy_price_edit.text())
            if buy_price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Price",
                "Please enter a valid positive number for buy price.",
            )
            self.buy_price_edit.setFocus()
            return

        self.accept()

    def get_asset_data(self) -> Dict[str, Any]:
        """
        Get asset data from form.

        Returns:
            Dictionary with asset data
        """
        date = self.date_edit.date()
        date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"

        return {
            "ticker": self.ticker_edit.text().strip().upper(),
            "quantity": float(self.quantity_edit.text()),
            "price_buy": float(self.buy_price_edit.text()),
            "date_buy": date_str,
            "asset_type": self.asset_type_combo.currentText(),
        }


class InvestmentsTab(QWidget):
    """Investments tab widget."""

    # Signal emitted when data changes
    data_changed = pyqtSignal()

    def __init__(
        self,
        db_manager: DatabaseManager,
        crypto_api: CryptoAPI,
        stock_api: StockAPI,
        parent=None,
    ):
        """
        Initialize investments tab.

        Args:
            db_manager: Database manager instance
            crypto_api: Crypto API instance
            stock_api: Stock API instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.crypto_api = crypto_api
        self.stock_api = stock_api
        self.price_worker = None
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Investment Portfolio")
        title.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh prices button
        self.refresh_prices_btn = QPushButton("🔄 Refresh Prices")
        self.refresh_prices_btn.clicked.connect(self._on_refresh_prices)
        header_layout.addWidget(self.refresh_prices_btn)

        # Add asset button
        self.add_btn = QPushButton("+ Add Asset")
        self.add_btn.clicked.connect(self._on_add_asset)
        header_layout.addWidget(self.add_btn)

        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.clicked.connect(self._load_data)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Summary cards
        self.summary_widget = self._create_summary_section()
        layout.addWidget(self.summary_widget)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Assets table
        self._create_assets_table()
        layout.addWidget(self.assets_table, 1)

    def _create_summary_section(self) -> QWidget:
        """Create summary cards section."""
        summary = QWidget()
        layout = QHBoxLayout(summary)
        layout.setSpacing(15)

        # Portfolio value card
        self.portfolio_card = self._create_card("Portfolio Value", "€0.00", "#4CAF50")
        layout.addWidget(self.portfolio_card)

        # Investment cost card
        self.cost_card = self._create_card("Total Invested", "€0.00", "#2196F3")
        layout.addWidget(self.cost_card)

        # Gain/Loss card
        self.gain_card = self._create_card("Gain/Loss", "€0.00", "#9C27B0")
        layout.addWidget(self.gain_card)

        # Assets count card
        self.count_card = self._create_card("Total Assets", "0", "#FF9800")
        layout.addWidget(self.count_card)

        return summary

    def _create_card(self, title: str, value: str, color: str) -> QWidget:
        """
        Create a summary card widget.

        Args:
            title: Card title
            value: Card value
            color: Card accent color

        Returns:
            QWidget configured as a card
        """
        card = QWidget()
        card.setStyleSheet(
            f"""
            QWidget {{
                background-color: palette(base);
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """
        )
        card.setMinimumHeight(100)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(title_label)

        # Value
        value_label = QLabel(value)
        value_label.setObjectName("card_value")
        value_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {color};"
        )
        layout.addWidget(value_label)

        layout.addStretch()

        return card

    def _create_assets_table(self):
        """Create assets table widget."""
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(9)
        self.assets_table.setHorizontalHeaderLabels(
            [
                "Type",
                "Ticker",
                "Quantity",
                "Buy Price",
                "Current Price",
                "Value",
                "Gain/Loss",
                "Gain %",
                "Actions",
            ]
        )

        # Configure table
        header = self.assets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)

        self.assets_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.assets_table.setAlternatingRowColors(True)
        self.assets_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def _load_data(self):
        """Load data from database and update UI."""
        try:
            # Get portfolio metrics
            portfolio_value = self.db.get_portfolio_value()
            portfolio_summary = self.db.get_portfolio_summary()

            total_cost = portfolio_summary.get("total_cost", 0)
            total_gain = portfolio_summary.get("total_gain", 0)

            self._update_card_value(self.portfolio_card, f"€{portfolio_value:,.2f}")
            self._update_card_value(self.cost_card, f"€{total_cost:,.2f}")

            # Update gain/loss card with color
            gain_color = "#4CAF50" if total_gain >= 0 else "#F44336"
            gain_symbol = "+" if total_gain >= 0 else ""
            self._update_card_value(
                self.gain_card, f"{gain_symbol}€{total_gain:,.2f}", gain_color
            )

            # Get all assets
            assets = self.db.get_all_assets()
            self._update_card_value(self.count_card, str(len(assets)))

            # Update table
            self._populate_table(assets)

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Data", f"Failed to load investment data:\n{str(e)}"
            )

    def _update_card_value(
        self, card: QWidget, value: str, color: Optional[str] = None
    ):
        """Update the value displayed in a card."""
        value_label = card.findChild(QLabel, "card_value")
        if value_label:
            value_label.setText(value)
            if color:
                current_style = value_label.styleSheet()
                # Replace color in stylesheet
                import re

                new_style = re.sub(
                    r"color:\s*[^;]+;", f"color: {color};", current_style
                )
                value_label.setStyleSheet(new_style)

    def _populate_table(self, assets: List[Dict[str, Any]]):
        """Populate assets table with data."""
        self.assets_table.setRowCount(0)

        # Sort by value (highest first)
        assets_sorted = sorted(
            assets,
            key=lambda x: x.get("quantity", 0) * x.get("current_price", 0),
            reverse=True,
        )

        for asset in assets_sorted:
            row = self.assets_table.rowCount()
            self.assets_table.insertRow(row)

            # Type
            type_item = QTableWidgetItem(asset.get("asset_type", "").upper())
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.assets_table.setItem(row, 0, type_item)

            # Ticker
            ticker_item = QTableWidgetItem(asset.get("ticker", ""))
            ticker_item.setFont(QFont("Monospace", 10, QFont.Weight.Bold))
            self.assets_table.setItem(row, 1, ticker_item)

            # Quantity
            quantity = asset.get("quantity", 0)
            quantity_item = QTableWidgetItem(f"{quantity:,.4f}".rstrip("0").rstrip("."))
            quantity_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.assets_table.setItem(row, 2, quantity_item)

            # Buy Price
            buy_price = asset.get("price_buy", 0)
            buy_price_item = QTableWidgetItem(f"€{buy_price:,.2f}")
            buy_price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.assets_table.setItem(row, 3, buy_price_item)

            # Current Price
            current_price = asset.get("current_price", 0)
            current_price_item = QTableWidgetItem(f"€{current_price:,.2f}")
            current_price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.assets_table.setItem(row, 4, current_price_item)

            # Current Value
            value = quantity * current_price
            value_item = QTableWidgetItem(f"€{value:,.2f}")
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            value_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.assets_table.setItem(row, 5, value_item)

            # Gain/Loss
            cost = quantity * buy_price
            gain = value - cost
            gain_item = QTableWidgetItem(f"{'+' if gain >= 0 else ''}€{gain:,.2f}")
            gain_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            gain_item.setForeground(QColor("#4CAF50" if gain >= 0 else "#F44336"))
            self.assets_table.setItem(row, 6, gain_item)

            # Gain %
            gain_pct = (
                ((current_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
            )
            gain_pct_item = QTableWidgetItem(
                f"{'+' if gain_pct >= 0 else ''}{gain_pct:.2f}%"
            )
            gain_pct_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            gain_pct_item.setForeground(
                QColor("#4CAF50" if gain_pct >= 0 else "#F44336")
            )
            self.assets_table.setItem(row, 7, gain_pct_item)

            # Actions
            actions_widget = self._create_action_buttons(asset)
            self.assets_table.setCellWidget(row, 8, actions_widget)

    def _create_action_buttons(self, asset: Dict[str, Any]) -> QWidget:
        """Create action buttons for an asset row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setMaximumWidth(35)
        edit_btn.setToolTip("Edit asset")
        edit_btn.clicked.connect(lambda: self._on_edit_asset(asset))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setMaximumWidth(35)
        delete_btn.setToolTip("Delete asset")
        delete_btn.clicked.connect(lambda: self._on_delete_asset(asset))
        layout.addWidget(delete_btn)

        return widget

    def _on_add_asset(self):
        """Handle add asset button click."""
        dialog = AssetDialog(self.db, self.crypto_api, self.stock_api, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_asset_data()

                # Fetch current price before adding
                if data["asset_type"] == "crypto":
                    current_price = self.crypto_api.get_price(data["ticker"])
                else:
                    current_price = self.stock_api.get_price(data["ticker"])

                if not current_price:
                    reply = QMessageBox.question(
                        self,
                        "Price Not Available",
                        f"Could not fetch current price for {data['ticker']}. "
                        "Add asset with buy price as current price?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        current_price = data["price_buy"]
                    else:
                        return

                self.db.add_asset(
                    ticker=data["ticker"],
                    quantity=data["quantity"],
                    price_buy=data["price_buy"],
                    date_buy=data["date_buy"],
                    current_price=current_price,
                    asset_type=data["asset_type"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Asset added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add asset:\n{str(e)}")

    def _on_edit_asset(self, asset: Dict[str, Any]):
        """Handle edit asset."""
        dialog = AssetDialog(
            self.db, self.crypto_api, self.stock_api, asset=asset, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_asset_data()
                self.db.update_asset(
                    asset_id=asset["id"],
                    quantity=data["quantity"],
                    price_buy=data["price_buy"],
                    date_buy=data["date_buy"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Asset updated successfully!")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update asset:\n{str(e)}"
                )

    def _on_delete_asset(self, asset: Dict[str, Any]):
        """Handle delete asset."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this asset?\n\n"
            f"Ticker: {asset.get('ticker', 'N/A')}\n"
            f"Quantity: {asset.get('quantity', 0)}\n"
            f"Type: {asset.get('asset_type', 'N/A')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_asset(asset["id"])
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Asset deleted successfully!")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete asset:\n{str(e)}"
                )

    def _on_refresh_prices(self):
        """Handle refresh prices button click."""
        if self.price_worker and self.price_worker.isRunning():
            QMessageBox.information(
                self, "In Progress", "Price update is already in progress."
            )
            return

        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting...")

        # Disable buttons
        self.refresh_prices_btn.setEnabled(False)
        self.add_btn.setEnabled(False)

        # Create and start worker thread
        self.price_worker = PriceUpdateWorker(self.db, self.crypto_api, self.stock_api)
        self.price_worker.progress.connect(self._on_price_update_progress)
        self.price_worker.finished.connect(self._on_price_update_finished)
        self.price_worker.start()

    def _on_price_update_progress(self, value: int, message: str):
        """Handle price update progress."""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)

    def _on_price_update_finished(self, results: Dict[str, int]):
        """Handle price update completion."""
        # Hide progress bar
        self.progress_bar.setVisible(False)

        # Re-enable buttons
        self.refresh_prices_btn.setEnabled(True)
        self.add_btn.setEnabled(True)

        # Reload data
        self._load_data()
        self.data_changed.emit()

        # Show results
        total = results.get("total", 0)
        updated = results.get("updated", 0)
        failed = results.get("failed", 0)

        if total == 0:
            QMessageBox.information(
                self, "No Assets", "No assets found to update prices."
            )
        else:
            message = f"Price update complete!\n\n"
            message += f"Total assets: {total}\n"
            message += f"Successfully updated: {updated}\n"
            if failed > 0:
                message += f"Failed to update: {failed}"

            QMessageBox.information(self, "Prices Updated", message)

    def refresh(self):
        """Public method to refresh the tab data."""
        self._load_data()
