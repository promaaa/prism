"""
PDF Report Generator for Prism application.
Generates professional financial reports in PDF format using ReportLab.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import os

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        PageBreak,
        Image,
    )
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PDFReportGenerator:
    """Generates PDF financial reports."""

    def __init__(self, db_manager):
        """
        Initialize PDF report generator.

        Args:
            db_manager: DatabaseManager instance
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )

        self.db_manager = db_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f2937"),
                spaceAfter=30,
                alignment=TA_CENTER,
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#4b5563"),
                spaceAfter=12,
                spaceBefore=12,
            )
        )

        # Summary style
        self.styles.add(
            ParagraphStyle(
                name="Summary",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#6b7280"),
                alignment=TA_RIGHT,
            )
        )

    def generate_full_report(
        self,
        output_path: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive financial report.

        Args:
            output_path: Path where PDF should be saved
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating PDF report: {output_path}")

        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Container for the 'Flowable' objects
        elements = []

        # Add title
        title = Paragraph("Prism Financial Report", self.styles["CustomTitle"])
        elements.append(title)

        # Add date range
        if start_date and end_date:
            date_range = f"Period: {start_date} to {end_date}"
        else:
            date_range = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        elements.append(Paragraph(date_range, self.styles["Summary"]))
        elements.append(Spacer(1, 20))

        # Add financial summary
        elements.extend(self._create_financial_summary(start_date, end_date))
        elements.append(Spacer(1, 20))

        # Add transactions section
        elements.extend(self._create_transactions_section(start_date, end_date))
        elements.append(PageBreak())

        # Add investments section
        elements.extend(self._create_investments_section())
        elements.append(PageBreak())

        # Add orders section
        elements.extend(self._create_orders_section(start_date, end_date))

        # Build PDF
        doc.build(elements)

        logger.info(f"PDF report generated successfully: {output_path}")
        return output_path

    def _create_financial_summary(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List:
        """Create financial summary section."""
        elements = []

        # Section title
        elements.append(Paragraph("Financial Summary", self.styles["CustomSubtitle"]))

        # Get transactions
        all_transactions = self.db_manager.get_all_transactions()

        # Filter by date if provided
        if start_date and end_date:
            all_transactions = [
                t for t in all_transactions if start_date <= t["date"] <= end_date
            ]

        # Calculate totals
        total_income = sum(t["amount"] for t in all_transactions if t["amount"] > 0)
        total_expense = sum(
            abs(t["amount"]) for t in all_transactions if t["amount"] < 0
        )
        net_balance = total_income - total_expense

        # Get portfolio value
        all_assets = self.db_manager.get_all_assets()
        total_investment = sum(a["quantity"] * a["price_buy"] for a in all_assets)

        current_portfolio_value = 0
        for asset in all_assets:
            current_price = asset.get("current_price") or asset["price_buy"]
            current_portfolio_value += asset["quantity"] * current_price

        portfolio_gain = current_portfolio_value - total_investment

        # Create summary table
        summary_data = [
            ["Metric", "Amount (€)"],
            ["Total Income", f"{total_income:,.2f}"],
            ["Total Expenses", f"{total_expense:,.2f}"],
            ["Net Balance", f"{net_balance:,.2f}"],
            ["", ""],
            ["Investment Value", f"{total_investment:,.2f}"],
            ["Current Portfolio Value", f"{current_portfolio_value:,.2f}"],
            ["Portfolio Gain/Loss", f"{portfolio_gain:,.2f}"],
        ]

        table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(table)
        return elements

    def _create_transactions_section(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List:
        """Create transactions section."""
        elements = []

        elements.append(Paragraph("Transactions", self.styles["CustomSubtitle"]))

        # Get transactions
        all_transactions = self.db_manager.get_all_transactions()

        # Filter by date if provided
        if start_date and end_date:
            all_transactions = [
                t for t in all_transactions if start_date <= t["date"] <= end_date
            ]

        # Sort by date (newest first)
        all_transactions.sort(key=lambda x: x["date"], reverse=True)

        if not all_transactions:
            elements.append(Paragraph("No transactions found.", self.styles["Normal"]))
            return elements

        # Create transactions table
        table_data = [["Date", "Category", "Amount (€)", "Type", "Description"]]

        for trans in all_transactions[:50]:  # Limit to 50 most recent
            amount_str = f"{trans['amount']:,.2f}"
            if trans["amount"] < 0:
                amount_str = f"({abs(trans['amount']):,.2f})"

            table_data.append(
                [
                    trans["date"],
                    trans["category"],
                    amount_str,
                    trans["type"],
                    trans.get("description", "")[:30],  # Truncate long descriptions
                ]
            )

        table = Table(
            table_data, colWidths=[1 * inch, 1.2 * inch, 1 * inch, 1 * inch, 2.3 * inch]
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.lightgrey],
                    ),
                ]
            )
        )

        elements.append(table)

        if len(all_transactions) > 50:
            elements.append(Spacer(1, 12))
            elements.append(
                Paragraph(
                    f"Showing 50 of {len(all_transactions)} transactions",
                    self.styles["Normal"],
                )
            )

        return elements

    def _create_investments_section(self) -> List:
        """Create investments section."""
        elements = []

        elements.append(
            Paragraph("Investment Portfolio", self.styles["CustomSubtitle"])
        )

        # Get assets
        all_assets = self.db_manager.get_all_assets()

        if not all_assets:
            elements.append(Paragraph("No investments found.", self.styles["Normal"]))
            return elements

        # Create investments table
        table_data = [
            [
                "Ticker",
                "Type",
                "Quantity",
                "Buy Price",
                "Current Price",
                "Value",
                "Gain/Loss",
            ]
        ]

        total_value = 0
        total_invested = 0

        for asset in all_assets:
            current_price = asset.get("current_price") or asset["price_buy"]
            value = asset["quantity"] * current_price
            invested = asset["quantity"] * asset["price_buy"]
            gain_loss = value - invested
            gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0

            total_value += value
            total_invested += invested

            gain_loss_str = f"{gain_loss:,.2f} ({gain_loss_pct:+.1f}%)"

            table_data.append(
                [
                    asset["ticker"],
                    asset["asset_type"],
                    f"{asset['quantity']:.4f}",
                    f"{asset['price_buy']:,.2f}",
                    f"{current_price:,.2f}",
                    f"{value:,.2f}",
                    gain_loss_str,
                ]
            )

        # Add total row
        total_gain_loss = total_value - total_invested
        total_gain_loss_pct = (
            (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        )

        table_data.append(
            [
                "TOTAL",
                "",
                "",
                "",
                "",
                f"{total_value:,.2f}",
                f"{total_gain_loss:,.2f} ({total_gain_loss_pct:+.1f}%)",
            ]
        )

        table = Table(
            table_data,
            colWidths=[
                0.8 * inch,
                0.8 * inch,
                0.8 * inch,
                0.9 * inch,
                1 * inch,
                0.9 * inch,
                1.3 * inch,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -2),
                        [colors.white, colors.lightgrey],
                    ),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )

        elements.append(table)
        return elements

    def _create_orders_section(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List:
        """Create orders section."""
        elements = []

        elements.append(Paragraph("Order Book", self.styles["CustomSubtitle"]))

        # Get orders
        all_orders = self.db_manager.get_all_orders()

        # Filter by date if provided
        if start_date and end_date:
            all_orders = [o for o in all_orders if start_date <= o["date"] <= end_date]

        if not all_orders:
            elements.append(Paragraph("No orders found.", self.styles["Normal"]))
            return elements

        # Sort by date (newest first)
        all_orders.sort(key=lambda x: x["date"], reverse=True)

        # Create orders table
        table_data = [
            ["Date", "Ticker", "Type", "Quantity", "Price", "Total", "Status"]
        ]

        for order in all_orders:
            total = order["quantity"] * order["price"]

            table_data.append(
                [
                    order["date"],
                    order["ticker"],
                    order["order_type"].upper(),
                    f"{order['quantity']:.4f}",
                    f"{order['price']:,.2f}",
                    f"{total:,.2f}",
                    order["status"].upper(),
                ]
            )

        table = Table(
            table_data,
            colWidths=[
                1 * inch,
                0.9 * inch,
                0.8 * inch,
                1 * inch,
                1 * inch,
                1.1 * inch,
                0.8 * inch,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8b5cf6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.lightgrey],
                    ),
                ]
            )
        )

        elements.append(table)
        return elements

    def generate_monthly_report(self, output_path: str, year: int, month: int) -> str:
        """
        Generate a monthly financial report.

        Args:
            output_path: Path where PDF should be saved
            year: Year
            month: Month (1-12)

        Returns:
            Path to generated PDF file
        """
        # Calculate date range
        start_date = f"{year:04d}-{month:02d}-01"

        # Calculate last day of month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        last_day = (next_month - timedelta(days=1)).day
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"

        return self.generate_full_report(output_path, start_date, end_date)

    def generate_yearly_report(self, output_path: str, year: int) -> str:
        """
        Generate a yearly financial report.

        Args:
            output_path: Path where PDF should be saved
            year: Year

        Returns:
            Path to generated PDF file
        """
        start_date = f"{year:04d}-01-01"
        end_date = f"{year:04d}-12-31"

        return self.generate_full_report(output_path, start_date, end_date)
