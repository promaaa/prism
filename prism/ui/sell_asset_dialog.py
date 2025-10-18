"""
Sell Asset Dialog for Prism application.
Provides interface to sell assets with automatic gain/loss calculation.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QDialogButtonBox,
    QMessageBox,
    QSpinBox,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QDoubleValidator

from ..database.db_manager import DatabaseManager


class SellAssetDialog(QDialog):
    """Dialog for selling assets with gain/loss calculation."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.selected_ticker = None
        self.available_assets = []
        self.setupUI()
        self.load_available_assets()

    def setupUI(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Vendre une Position")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Vendre un Actif")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Form section
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Ticker selection
        self.ticker_combo = QComboBox()
        self.ticker_combo.currentTextChanged.connect(self.on_ticker_changed)
        form_layout.addRow("Ticker:", self.ticker_combo)

        # Available quantity display
        self.available_qty_label = QLabel("0")
        self.available_qty_label.setStyleSheet("color: #666; font-weight: bold;")
        form_layout.addRow("Quantité disponible:", self.available_qty_label)

        # Average cost basis display
        self.avg_cost_label = QLabel("0.00 EUR")
        self.avg_cost_label.setStyleSheet("color: #666; font-weight: bold;")
        form_layout.addRow("Prix moyen d'achat:", self.avg_cost_label)

        # Quantity to sell
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.00000001)
        self.quantity_input.setMaximum(1000000000)
        self.quantity_input.setDecimals(8)
        self.quantity_input.valueChanged.connect(self.calculate_preview)
        form_layout.addRow("Quantité à vendre:", self.quantity_input)

        # Sale price
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.00000001)
        self.price_input.setMaximum(1000000000)
        self.price_input.setDecimals(8)
        self.price_input.setPrefix("€ ")
        self.price_input.valueChanged.connect(self.calculate_preview)
        form_layout.addRow("Prix de vente unitaire:", self.price_input)

        # Sale date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date de vente:", self.date_input)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Notes optionnelles...")
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Preview section
        preview_group = QGroupBox("Aperçu de la Transaction")
        preview_layout = QFormLayout()
        preview_layout.setSpacing(8)

        self.proceeds_label = QLabel("0.00 EUR")
        self.proceeds_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addRow("Produit de la vente:", self.proceeds_label)

        self.cost_basis_label = QLabel("0.00 EUR")
        self.cost_basis_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addRow("Prix d'achat total:", self.cost_basis_label)

        self.gain_loss_label = QLabel("0.00 EUR")
        self.gain_loss_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addRow("Plus/Moins-value:", self.gain_loss_label)

        self.gain_loss_pct_label = QLabel("0.00%")
        self.gain_loss_pct_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addRow("Performance:", self.gain_loss_pct_label)

        self.remaining_qty_label = QLabel("0")
        self.remaining_qty_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addRow("Quantité restante:", self.remaining_qty_label)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Warning label
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet(
            "color: #ef4444; font-weight: bold; padding: 10px; "
            "background-color: #fee2e2; border-radius: 4px;"
        )
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        layout.addWidget(self.warning_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Vendre")
        self.ok_button.setEnabled(False)
        layout.addWidget(button_box)

    def load_available_assets(self):
        """Load available assets from database."""
        try:
            all_assets = self.db.get_all_assets()

            # Group by ticker and sum quantities
            ticker_info = {}
            for asset in all_assets:
                ticker = asset["ticker"]
                if ticker not in ticker_info:
                    ticker_info[ticker] = {
                        "quantity": 0,
                        "assets": [],
                        "type": asset["asset_type"],
                        "currency": asset.get("price_currency", "EUR"),
                    }
                ticker_info[ticker]["quantity"] += asset["quantity"]
                ticker_info[ticker]["assets"].append(asset)

            # Populate combo box
            self.ticker_combo.clear()
            self.available_assets = ticker_info

            for ticker in sorted(ticker_info.keys()):
                info = ticker_info[ticker]
                display_text = f"{ticker} ({info['quantity']:.8g} disponible)"
                self.ticker_combo.addItem(display_text, ticker)

            if self.ticker_combo.count() == 0:
                self.ticker_combo.addItem("Aucun actif disponible", None)
                self.ok_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors du chargement des actifs: {e}"
            )

    def on_ticker_changed(self, text: str):
        """Handle ticker selection change."""
        ticker = self.ticker_combo.currentData()

        if ticker is None or ticker not in self.available_assets:
            self.available_qty_label.setText("0")
            self.avg_cost_label.setText("0.00 EUR")
            self.quantity_input.setMaximum(0)
            self.ok_button.setEnabled(False)
            return

        self.selected_ticker = ticker
        info = self.available_assets[ticker]

        # Update available quantity
        total_qty = info["quantity"]
        self.available_qty_label.setText(f"{total_qty:.8g}")

        # Calculate average cost basis
        total_cost = sum(
            asset["quantity"] * asset["price_buy"] for asset in info["assets"]
        )
        avg_cost = total_cost / total_qty if total_qty > 0 else 0
        currency = info["currency"]
        self.avg_cost_label.setText(f"{avg_cost:.2f} {currency}")

        # Set quantity limits
        self.quantity_input.setMaximum(total_qty)
        self.quantity_input.setValue(min(total_qty, self.quantity_input.value()))

        # Set default sale price to current price if available
        if info["assets"]:
            current_price = info["assets"][0].get("current_price")
            if current_price:
                self.price_input.setValue(current_price)

        self.calculate_preview()
        self.ok_button.setEnabled(True)

    def calculate_preview(self):
        """Calculate and display transaction preview."""
        if self.selected_ticker is None:
            return

        try:
            quantity = self.quantity_input.value()
            price = self.price_input.value()

            if quantity <= 0 or price <= 0:
                return

            info = self.available_assets[self.selected_ticker]
            total_qty = info["quantity"]
            currency = info["currency"]

            # Check if quantity exceeds available
            if quantity > total_qty:
                self.warning_label.setText(
                    f"⚠️ La quantité à vendre ({quantity:.8g}) dépasse la quantité disponible ({total_qty:.8g})"
                )
                self.warning_label.show()
                self.ok_button.setEnabled(False)
                return
            else:
                self.warning_label.hide()
                self.ok_button.setEnabled(True)

            # Calculate average cost basis
            total_cost = sum(
                asset["quantity"] * asset["price_buy"] for asset in info["assets"]
            )
            avg_cost = total_cost / total_qty if total_qty > 0 else 0

            # Calculate transaction values
            proceeds = quantity * price
            cost_basis = quantity * avg_cost
            gain_loss = proceeds - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
            remaining_qty = total_qty - quantity

            # Update labels
            self.proceeds_label.setText(f"{proceeds:.2f} {currency}")
            self.cost_basis_label.setText(f"{cost_basis:.2f} {currency}")

            # Color code gain/loss
            if gain_loss >= 0:
                color = "#10b981"  # green
                sign = "+"
            else:
                color = "#ef4444"  # red
                sign = ""

            self.gain_loss_label.setText(f"{sign}{gain_loss:.2f} {currency}")
            self.gain_loss_label.setStyleSheet(
                f"font-weight: bold; font-size: 12pt; color: {color};"
            )

            self.gain_loss_pct_label.setText(f"{sign}{gain_loss_pct:.2f}%")
            self.gain_loss_pct_label.setStyleSheet(
                f"font-weight: bold; font-size: 12pt; color: {color};"
            )

            self.remaining_qty_label.setText(f"{remaining_qty:.8g}")

        except Exception as e:
            print(f"Error calculating preview: {e}")

    def get_sale_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the sale data from the form.

        Returns:
            Dictionary with sale information or None if invalid
        """
        if self.selected_ticker is None:
            return None

        try:
            ticker = self.selected_ticker
            quantity = self.quantity_input.value()
            price = self.price_input.value()
            date = self.date_input.date().toString("yyyy-MM-dd")
            notes = self.notes_input.toPlainText().strip()

            if quantity <= 0 or price <= 0:
                QMessageBox.warning(
                    self,
                    "Données invalides",
                    "La quantité et le prix doivent être supérieurs à zéro.",
                )
                return None

            info = self.available_assets[ticker]
            if quantity > info["quantity"]:
                QMessageBox.warning(
                    self,
                    "Quantité insuffisante",
                    f"Vous ne pouvez pas vendre {quantity:.8g} {ticker}.\n"
                    f"Quantité disponible: {info['quantity']:.8g}",
                )
                return None

            return {
                "ticker": ticker,
                "quantity": quantity,
                "price": price,
                "date": date,
                "notes": notes if notes else None,
            }

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de la récupération des données: {e}"
            )
            return None

    def accept(self):
        """Handle dialog acceptance."""
        data = self.get_sale_data()
        if data:
            super().accept()
