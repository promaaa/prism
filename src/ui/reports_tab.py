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
    QGroupBox,
    QSplitter,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from database.db_manager import DatabaseManager
from utils.exports import (
    export_transactions_to_csv,
    export_assets_to_csv,
    export_orders_to_csv,
    get_default_export_path,
)


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

        # Personal Finance Charts Section
        self.personal_charts_widget = self._create_personal_charts_section()
        self.chart_splitter.addWidget(self.personal_charts_widget)

        # Investment Charts Section
        self.investment_charts_widget = self._create_investment_charts_section()
        self.chart_splitter.addWidget(self.investment_charts_widget)

        layout.addWidget(self.chart_splitter, 1)

        # Load initial data
        self._refresh_charts()

    def _create_control_panel(self) -> QWidget:
        """Create control panel with filters and export options."""
        panel = QGroupBox("Controls")
        layout = QHBoxLayout(panel)
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

        return panel

    def _create_personal_charts_section(self) -> QWidget:
        """Create personal finance charts section."""
        section = QGroupBox("Personal Finance Analytics")
        layout = QHBoxLayout(section)
        layout.setSpacing(10)

        # Balance evolution chart
        self.balance_chart_view = QWebEngineView()
        self.balance_chart_view.setMinimumHeight(300)
        layout.addWidget(self.balance_chart_view, 2)

        # Category breakdown chart
        self.category_chart_view = QWebEngineView()
        self.category_chart_view.setMinimumHeight(300)
        layout.addWidget(self.category_chart_view, 1)

        return section

    def _create_investment_charts_section(self) -> QWidget:
        """Create investment charts section."""
        section = QGroupBox("Investment Portfolio Analytics")
        layout = QHBoxLayout(section)
        layout.setSpacing(10)

        # Portfolio value evolution chart
        self.portfolio_chart_view = QWebEngineView()
        self.portfolio_chart_view.setMinimumHeight(300)
        layout.addWidget(self.portfolio_chart_view, 2)

        # Asset allocation chart
        self.allocation_chart_view = QWebEngineView()
        self.allocation_chart_view.setMinimumHeight(300)
        layout.addWidget(self.allocation_chart_view, 1)

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
            transactions = self.db.get_all_transactions()
            assets = self.db.get_all_assets()

            # Filter by date range
            transactions = self._filter_transactions_by_date(transactions)

            # Generate charts
            self._create_balance_chart(transactions)
            self._create_category_chart(transactions)
            self._create_portfolio_chart(assets)
            self._create_allocation_chart(assets)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate charts:\n{str(e)}")

    def _create_balance_chart(self, transactions: List[Dict[str, Any]]):
        """Create balance evolution line chart."""
        if not transactions:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No transaction data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(
                title="Balance Evolution",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=300,
            )
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.balance_chart_view.setHtml(html)
            return

        # Sort by date
        sorted_transactions = sorted(transactions, key=lambda x: x.get("date", ""))

        # Calculate cumulative balance
        dates = []
        balances = []
        running_balance = 0

        for trans in sorted_transactions:
            date = trans.get("date", "")
            amount = trans.get("amount", 0)
            running_balance += amount
            dates.append(date)
            balances.append(running_balance)

        # Create line chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=balances,
                mode="lines+markers",
                name="Balance",
                line=dict(color="#4CAF50", width=3),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(76, 175, 80, 0.1)",
            )
        )

        fig.update_layout(
            title="Balance Evolution Over Time",
            xaxis_title="Date",
            yaxis_title="Balance (€)",
            hovermode="x unified",
            height=300,
            template="plotly_white",
            showlegend=False,
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.balance_chart_view.setHtml(html)

    def _create_category_chart(self, transactions: List[Dict[str, Any]]):
        """Create expense/revenue breakdown pie chart."""
        if not transactions:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No transaction data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(
                title="Category Breakdown",
                height=300,
            )
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.category_chart_view.setHtml(html)
            return

        # Group by category
        category_totals = {}
        for trans in transactions:
            category = trans.get("category", "Uncategorized")
            amount = abs(trans.get("amount", 0))  # Use absolute values

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        if not category_totals:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No category data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(title="Category Breakdown", height=300)
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.category_chart_view.setHtml(html)
            return

        # Create pie chart
        labels = list(category_totals.keys())
        values = list(category_totals.values())

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker=dict(
                        colors=px.colors.qualitative.Set3,
                        line=dict(color="white", width=2),
                    ),
                )
            ]
        )

        fig.update_layout(
            title="Spending by Category",
            height=300,
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02
            ),
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.category_chart_view.setHtml(html)

    def _create_portfolio_chart(self, assets: List[Dict[str, Any]]):
        """Create portfolio value evolution chart."""
        if not assets:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No investment data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(
                title="Portfolio Value Over Time",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=300,
            )
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.portfolio_chart_view.setHtml(html)
            return

        # Group assets by purchase date and calculate cumulative value
        date_values = {}

        for asset in assets:
            date = asset.get("date_buy", "")
            quantity = asset.get("quantity", 0)
            current_price = asset.get("current_price", 0)
            value = quantity * current_price

            if date in date_values:
                date_values[date] += value
            else:
                date_values[date] = value

        # Sort by date
        sorted_dates = sorted(date_values.keys())
        dates = []
        values = []
        cumulative_value = 0

        for date in sorted_dates:
            cumulative_value += date_values[date]
            dates.append(date)
            values.append(cumulative_value)

        # Add current date with current total portfolio value
        current_value = sum(
            asset.get("quantity", 0) * asset.get("current_price", 0) for asset in assets
        )
        dates.append(datetime.now().strftime("%Y-%m-%d"))
        values.append(current_value)

        # Create line chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines+markers",
                name="Portfolio Value",
                line=dict(color="#2196F3", width=3),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(33, 150, 243, 0.1)",
            )
        )

        fig.update_layout(
            title="Portfolio Value Evolution",
            xaxis_title="Date",
            yaxis_title="Value (€)",
            hovermode="x unified",
            height=300,
            template="plotly_white",
            showlegend=False,
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.portfolio_chart_view.setHtml(html)

    def _create_allocation_chart(self, assets: List[Dict[str, Any]]):
        """Create asset allocation pie chart."""
        if not assets:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No investment data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(title="Asset Allocation", height=300)
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.allocation_chart_view.setHtml(html)
            return

        # Group by asset type
        type_values = {}

        for asset in assets:
            asset_type = asset.get("asset_type", "Unknown").upper()
            quantity = asset.get("quantity", 0)
            current_price = asset.get("current_price", 0)
            value = quantity * current_price

            if asset_type in type_values:
                type_values[asset_type] += value
            else:
                type_values[asset_type] = value

        if not type_values:
            # Show empty state
            fig = go.Figure()
            fig.add_annotation(
                text="No allocation data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#999"),
            )
            fig.update_layout(title="Asset Allocation", height=300)
            html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": False})
            self.allocation_chart_view.setHtml(html)
            return

        # Create pie chart
        labels = list(type_values.keys())
        values = list(type_values.values())

        colors = {
            "CRYPTO": "#FF9800",
            "STOCK": "#2196F3",
            "BOND": "#4CAF50",
        }
        chart_colors = [colors.get(label, "#9C27B0") for label in labels]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    marker=dict(colors=chart_colors, line=dict(color="white", width=2)),
                    textinfo="label+percent",
                    textfont=dict(size=14),
                )
            ]
        )

        fig.update_layout(
            title="Portfolio Allocation by Asset Type",
            height=300,
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02
            ),
        )

        html = fig.to_html(include_plotlyjs="cdn", config={"displayModeBar": True})
        self.allocation_chart_view.setHtml(html)

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
