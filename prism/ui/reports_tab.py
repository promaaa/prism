"""
Reports tab for Prism application.
Displays interactive charts and data visualization using Plotly.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
    QFrame,
    QScrollArea,
    QDateEdit,
    QSplitter,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

from ..database.db_manager import DatabaseManager
from ..utils.portfolio_evolution import calculate_true_portfolio_evolution
from ..utils.exports import (
    export_transactions_to_csv,
    export_assets_to_csv,
    export_orders_to_csv,
    get_default_export_path,
)
from . import finary_themes  # Import the new theme


class ReportsTab(QWidget):
    """Reports and visualization tab widget."""

    # Signal emitted when data changes
    data_changed = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        """
        Initialize reports tab.

        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Reports & Analytics")
        title.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh Charts")
        self.refresh_btn.clicked.connect(self._refresh_charts)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Control panel
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Splitter for charts (allows resizing)
        self.chart_splitter = QSplitter(Qt.Orientation.Vertical)

        # Stock Charts Section
        self.stock_charts_widget = self._create_stock_charts_section()
        self.chart_splitter.addWidget(self.stock_charts_widget)

        # Crypto Charts Section
        self.crypto_charts_widget = self._create_crypto_charts_section()
        self.chart_splitter.addWidget(self.crypto_charts_widget)

        layout.addWidget(self.chart_splitter, 1)

        # Load initial data
        self._refresh_charts()

    def _create_control_panel(self) -> QWidget:
        """Create control panel with filters and export options."""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(8)

        # Controls title
        controls_title = QLabel("Controls")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        controls_title.setFont(title_font)
        panel_layout.addWidget(controls_title)

        # Controls container
        controls_container = QWidget()
        layout = QHBoxLayout(controls_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Date range filter
        date_label = QLabel("Date Range:")
        layout.addWidget(date_label)

        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(
            [
                "All Time",
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "Last 6 Months",
                "Last Year",
                "This Year",
                "Custom",
            ]
        )
        self.date_range_combo.currentTextChanged.connect(self._on_date_range_changed)
        layout.addWidget(self.date_range_combo)

        # Custom date range (hidden by default)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setVisible(False)
        layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setVisible(False)
        layout.addWidget(self.end_date_edit)

        layout.addStretch()

        # Export buttons
        export_label = QLabel("Export:")
        layout.addWidget(export_label)

        self.export_transactions_btn = QPushButton("📊 Transactions CSV")
        self.export_transactions_btn.clicked.connect(self._export_transactions)
        layout.addWidget(self.export_transactions_btn)

        self.export_assets_btn = QPushButton("💼 Assets CSV")
        self.export_assets_btn.clicked.connect(self._export_assets)
        layout.addWidget(self.export_assets_btn)

        self.export_orders_btn = QPushButton("📋 Orders CSV")
        self.export_orders_btn.clicked.connect(self._export_orders)
        layout.addWidget(self.export_orders_btn)

        panel_layout.addWidget(controls_container)
        return panel

    def _create_stock_charts_section(self) -> QWidget:
        """Create stock investment charts section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Section title
        title_label = QLabel("PEA (Stocks) Analytics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Stock evolution chart
        self.stock_chart_view = QWebEngineView()
        self.stock_chart_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.stock_chart_view.setMinimumHeight(350)
        layout.addWidget(self.stock_chart_view)

        return section

    def _create_crypto_charts_section(self) -> QWidget:
        """Create crypto investment charts section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Section title
        title_label = QLabel("Crypto Investments Analytics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Crypto evolution chart
        self.crypto_chart_view = QWebEngineView()
        self.crypto_chart_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.crypto_chart_view.setMinimumHeight(350)
        layout.addWidget(self.crypto_chart_view)

        return section

    def _on_date_range_changed(self, range_text: str):
        """Handle date range selection change."""
        if range_text == "Custom":
            self.start_date_edit.setVisible(True)
            self.end_date_edit.setVisible(True)
        else:
            self.start_date_edit.setVisible(False)
            self.end_date_edit.setVisible(False)
            self._refresh_charts()

    def _get_date_range(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get date range based on current selection.

        Returns:
            Tuple of (start_date, end_date) as strings or (None, None) for all time
        """
        range_text = self.date_range_combo.currentText()
        end_date = datetime.now()

        if range_text == "All Time":
            return None, None
        elif range_text == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif range_text == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif range_text == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif range_text == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif range_text == "Last Year":
            start_date = end_date - timedelta(days=365)
        elif range_text == "This Year":
            start_date = datetime(end_date.year, 1, 1)
        elif range_text == "Custom":
            start_qdate = self.start_date_edit.date()
            end_qdate = self.end_date_edit.date()
            start_date = datetime(
                start_qdate.year(), start_qdate.month(), start_qdate.day()
            )
            end_date = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day())
        else:
            return None, None

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def _filter_transactions_by_date(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by selected date range."""
        start_date, end_date = self._get_date_range()

        if start_date is None or end_date is None:
            return transactions

        filtered = []
        for trans in transactions:
            trans_date = trans.get("date", "")
            if start_date <= trans_date <= end_date:
                filtered.append(trans)

        return filtered

    def _refresh_charts(self):
        """Refresh all charts with current data."""
        try:
            # Get data from database
            assets = self.db.get_all_assets()

            # Generate charts
            self._create_stock_evolution_chart(assets)
            self._create_crypto_evolution_chart(assets)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate charts:\n{str(e)}")

    def _create_stock_evolution_chart(self, assets: List[Dict[str, Any]]):
        """Create stock investment evolution line chart."""
        stock_assets = [a for a in assets if a["asset_type"] == "stock"]

        if not stock_assets:
            self._show_empty_chart(
                self.stock_chart_view,
                "No stock investment data available",
                "Stock Investment Evolution (PEA)",
            )
            return

        start_date, end_date = self._get_date_range()

        # Calculate TRUE portfolio evolution based on purchase dates
        portfolio_evolution = calculate_true_portfolio_evolution(
            stock_assets, self.db.get_historical_prices, start_date, end_date
        )

        # If no historical data, show current value
        if not portfolio_evolution:
            current_value = sum(
                asset["quantity"]
                * (asset.get("current_price") or asset.get("price_buy", 0))
                for asset in stock_assets
            )

            if current_value > 0:
                from datetime import datetime

                today = datetime.now().strftime("%Y-%m-%d")

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=[today],
                        y=[current_value],
                        mode="markers+text",
                        name="Current Value",
                        marker=dict(color="#007AFF", size=15),
                        text=[f"€{current_value:,.2f}"],
                        textposition="top center",
                        hovertemplate="<b>Today</b><br>€%{y:,.2f}<extra></extra>",
                    )
                )

                fig.update_layout(
                    title="Stock Portfolio Current Value (PEA)<br><sub>💡 Tip: Update prices in Investments tab to see evolution chart</sub>",
                    xaxis_title="Date",
                    yaxis_title="Value (€)",
                    showlegend=False,
                    height=350,
                    margin=dict(t=70, l=10, r=10, b=40),
                )

                html = fig.to_html(
                    include_plotlyjs="cdn", config={"displayModeBar": True}
                )
                self.stock_chart_view.setHtml(html)
            else:
                self._show_empty_chart(
                    self.stock_chart_view,
                    "No historical price data available.<br><br>"
                    "📊 <b>How to fix this:</b><br>"
                    "1. Go to <b>Investments</b> tab<br>"
                    "2. Click <b>Update Prices</b> button<br>"
                    "3. Wait for prices to update<br>"
                    "4. Come back here and click <b>Refresh All</b><br><br>"
                    "Historical prices will be fetched automatically.",
                    "Stock Investment Evolution (PEA)",
                )
            return

        # Sort the dates and create the lists for the chart
        sorted_dates = sorted(portfolio_evolution.keys())
        dates = sorted_dates
        values = [portfolio_evolution[date] for date in sorted_dates]

        # Create line chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name="Stock Value",
                line=dict(color="#007AFF", width=3),
                fill="tozeroy",
                fillcolor="rgba(0, 122, 255, 0.2)",
                hovertemplate="<b>%{x}</b><br>€%{y:,.2f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Stock Investment Evolution (PEA)<br><sub>Shows actual portfolio value based on purchase dates</sub>",
            xaxis_title="Date",
            yaxis_title="Value (€)",
            hovermode="x unified",
            autosize=True,
            height=350,
            margin=dict(t=70, l=10, r=10, b=40),
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.stock_chart_view.setHtml(html)

    def _create_crypto_evolution_chart(self, assets: List[Dict[str, Any]]):
        """Create crypto investment evolution line chart."""
        crypto_assets = [a for a in assets if a["asset_type"] == "crypto"]

        if not crypto_assets:
            self._show_empty_chart(
                self.crypto_chart_view,
                "No crypto investment data available",
                "Crypto Investment Evolution",
            )
            return

        start_date, end_date = self._get_date_range()

        # Calculate TRUE portfolio evolution based on purchase dates
        portfolio_evolution = calculate_true_portfolio_evolution(
            crypto_assets, self.db.get_historical_prices, start_date, end_date
        )

        # If no historical data, show current value
        if not portfolio_evolution:
            current_value = sum(
                asset["quantity"]
                * (asset.get("current_price") or asset.get("price_buy", 0))
                for asset in crypto_assets
            )

            if current_value > 0:
                from datetime import datetime

                today = datetime.now().strftime("%Y-%m-%d")

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=[today],
                        y=[current_value],
                        mode="markers+text",
                        name="Current Value",
                        marker=dict(color="#FF9500", size=15),
                        text=[f"€{current_value:,.2f}"],
                        textposition="top center",
                        hovertemplate="<b>Today</b><br>€%{y:,.2f}<extra></extra>",
                    )
                )

                fig.update_layout(
                    title="Crypto Portfolio Current Value<br><sub>💡 Tip: Update prices in Investments tab to see evolution chart</sub>",
                    xaxis_title="Date",
                    yaxis_title="Value (€)",
                    showlegend=False,
                    height=350,
                    margin=dict(t=70, l=10, r=10, b=40),
                )

                html = fig.to_html(
                    include_plotlyjs="cdn", config={"displayModeBar": True}
                )
                self.crypto_chart_view.setHtml(html)
            else:
                self._show_empty_chart(
                    self.crypto_chart_view,
                    "No historical price data available.<br><br>"
                    "📊 <b>How to fix this:</b><br>"
                    "1. Go to <b>Investments</b> tab<br>"
                    "2. Click <b>Update Prices</b> button<br>"
                    "3. Wait for prices to update<br>"
                    "4. Come back here and click <b>Refresh All</b><br><br>"
                    "Historical prices will be fetched automatically.",
                    "Crypto Investment Evolution",
                )
            return

        # Sort the dates and create the lists for the chart
        sorted_dates = sorted(portfolio_evolution.keys())
        dates = sorted_dates
        values = [portfolio_evolution[date] for date in sorted_dates]

        # Create line chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name="Crypto Value",
                line=dict(color="#FF9500", width=3),
                fill="tozeroy",
                fillcolor="rgba(255, 149, 0, 0.2)",
                hovertemplate="<b>%{x}</b><br>€%{y:,.2f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Crypto Investment Evolution<br><sub>Shows actual portfolio value based on purchase dates</sub>",
            xaxis_title="Date",
            yaxis_title="Value (€)",
            hovermode="x unified",
            autosize=True,
            height=350,
            margin=dict(t=70, l=10, r=10, b=40),
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.crypto_chart_view.setHtml(html)

    def _export_transactions(self):
        """Export transactions to CSV."""
        try:
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

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export error:\n{str(e)}")

    def _export_assets(self):
        """Export assets to CSV."""
        try:
            assets = self.db.get_all_assets()

            if not assets:
                QMessageBox.warning(self, "No Data", "No assets to export.")
                return

            output_path = get_default_export_path("assets.csv")
            success = export_assets_to_csv(assets, output_path)

            if success:
                QMessageBox.information(
                    self, "Export Successful", f"Assets exported to:\n{output_path}"
                )
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to export assets.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export error:\n{str(e)}")

    def _export_orders(self):
        """Export orders to CSV."""
        try:
            orders = self.db.get_all_orders()

            if not orders:
                QMessageBox.warning(self, "No Data", "No orders to export.")
                return

            output_path = get_default_export_path("orders.csv")
            success = export_orders_to_csv(orders, output_path)

            if success:
                QMessageBox.information(
                    self, "Export Successful", f"Orders exported to:\n{output_path}"
                )
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to export orders.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export error:\n{str(e)}")

    def refresh(self):
        """Public method to refresh the tab data."""
        self._refresh_charts()
