"""
Orders tab for Prism application.
Displays order book management interface for tracking buy/sell orders.
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
    QDialogButtonBox,
    QMessageBox,
    QFrame,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from ..database.db_manager import DatabaseManager


class OrderDialog(QDialog):
    """Dialog for adding/editing orders."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        order: Optional[Dict[str, Any]] = None,
        parent=None,
    ):
        """
        Initialize order dialog.

        Args:
            db_manager: Database manager instance
            order: Existing order data for editing (None for new)
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.order = order
        self.is_edit = order is not None

        self.setWindowTitle("Edit Order" if self.is_edit else "New Order")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Ticker field
        self.ticker_edit = QLineEdit()
        self.ticker_edit.setPlaceholderText("e.g., BTC, AAPL, LVMH.PA")
        if self.is_edit and self.order:
            self.ticker_edit.setText(self.order.get("ticker", ""))
        form_layout.addRow("Ticker:", self.ticker_edit)

        # Order Type field
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["buy", "sell"])
        if self.is_edit and self.order:
            current_type = self.order.get("order_type", "buy")
            index = self.order_type_combo.findText(current_type)
            if index >= 0:
                self.order_type_combo.setCurrentIndex(index)
        form_layout.addRow("Order Type:", self.order_type_combo)

        # Quantity field
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("e.g., 0.5 BTC or 10 shares")
        if self.is_edit and self.order:
            self.quantity_edit.setText(str(self.order.get("quantity", "")))
        form_layout.addRow("Quantity:", self.quantity_edit)

        # Price field
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("Target price per unit")
        if self.is_edit and self.order:
            self.price_edit.setText(str(self.order.get("price", "")))
        form_layout.addRow("Price (€):", self.price_edit)

        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        if self.is_edit and self.order:
            date_str = self.order.get("date", "")
            if date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                self.date_edit.setDate(
                    QDate(date_obj.year, date_obj.month, date_obj.day)
                )
        else:
            self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Order Date:", self.date_edit)

        # Status field
        self.status_combo = QComboBox()
        self.status_combo.addItems(["open", "closed"])
        if self.is_edit and self.order:
            current_status = self.order.get("status", "open")
            index = self.status_combo.findText(current_status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        form_layout.addRow("Status:", self.status_combo)

        layout.addLayout(form_layout)

        # Help text
        help_label = QLabel(
            "💡 Tip: Track your planned trades or record executed orders. "
            "Use 'open' for pending orders and 'closed' for completed ones."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        layout.addWidget(help_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self):
        """Validate and accept dialog."""
        # Validate ticker
        ticker = self.ticker_edit.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Missing Ticker", "Please enter a ticker symbol.")
            self.ticker_edit.setFocus()
            return

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

        # Validate price
        try:
            price = float(self.price_edit.text())
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Price",
                "Please enter a valid positive number for price.",
            )
            self.price_edit.setFocus()
            return

        self.accept()

    def get_order_data(self) -> Dict[str, Any]:
        """
        Get order data from form.

        Returns:
            Dictionary with order data
        """
        date = self.date_edit.date()
        date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"

        return {
            "ticker": self.ticker_edit.text().strip().upper(),
            "order_type": self.order_type_combo.currentText(),
            "quantity": float(self.quantity_edit.text()),
            "price": float(self.price_edit.text()),
            "date": date_str,
            "status": self.status_combo.currentText(),
        }


class OrdersTab(QWidget):
    """Orders management tab widget."""

    # Signal emitted when data changes
    data_changed = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        """
        Initialize orders tab.

        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Order Book")
        title.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Filter by status
        filter_label = QLabel("Filter:")
        header_layout.addWidget(filter_label)

        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["All", "Open", "Closed"])
        self.status_filter_combo.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.status_filter_combo)

        # Add order button
        self.add_btn = QPushButton("+ Add Order")
        self.add_btn.clicked.connect(self._on_add_order)
        header_layout.addWidget(self.add_btn)

        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.clicked.connect(self._load_data)
        header_layout.addWidget(self.refresh_btn)

        # Delete button
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setProperty("class", "danger")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setToolTip(
            "Delete selected order(s) (or press Delete/Suppr key)\n"
            "Shift+Click or Ctrl+Click to select multiple"
        )
        self.delete_btn.clicked.connect(self._on_delete_selected)
        self.delete_btn.setEnabled(False)  # Disabled until a row is selected
        header_layout.addWidget(self.delete_btn)

        layout.addLayout(header_layout)

        # Summary cards
        self.summary_widget = self._create_summary_section()
        layout.addWidget(self.summary_widget)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Quick actions section
        quick_actions = self._create_quick_actions()
        layout.addWidget(quick_actions)

        # Orders table
        self._create_orders_table()
        layout.addWidget(self.orders_table, 1)

    def _create_summary_section(self) -> QWidget:
        """Create summary cards section."""
        summary = QWidget()
        layout = QHBoxLayout(summary)
        layout.setSpacing(15)

        # Total orders card
        self.total_card = self._create_card("Total Orders", "0", "#9C27B0")
        layout.addWidget(self.total_card)

        # Open orders card
        self.open_card = self._create_card("Open Orders", "0", "#FF9800")
        layout.addWidget(self.open_card)

        # Closed orders card
        self.closed_card = self._create_card("Closed Orders", "0", "#4CAF50")
        layout.addWidget(self.closed_card)

        # Total value card
        self.value_card = self._create_card("Total Order Value", "€0.00", "#2196F3")
        layout.addWidget(self.value_card)

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

    def _create_quick_actions(self) -> QWidget:
        """Create quick actions section."""
        group = QGroupBox("Quick Actions")
        layout = QHBoxLayout(group)

        # Close all open orders button
        self.close_all_btn = QPushButton("✓ Close All Open Orders")
        self.close_all_btn.clicked.connect(self._on_close_all_open)
        layout.addWidget(self.close_all_btn)

        # Delete all closed orders button
        self.delete_closed_btn = QPushButton("🗑️ Delete All Closed Orders")
        self.delete_closed_btn.clicked.connect(self._on_delete_all_closed)
        layout.addWidget(self.delete_closed_btn)

        layout.addStretch()

        return group

    def _create_orders_table(self):
        """Create orders table widget."""
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(
            [
                "Ticker",
                "Type",
                "Quantity",
                "Price",
                "Total Value",
                "Date",
                "Status",
                "Actions",
            ]
        )

        # Configure table
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.orders_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.orders_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Connect selection change to enable/disable delete button
        self.orders_table.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_data(self):
        """Load data from database and update UI."""
        try:
            # Get all orders
            all_orders = self.db.get_all_orders()

            # Calculate statistics
            open_orders = [o for o in all_orders if o.get("status") == "open"]
            closed_orders = [o for o in all_orders if o.get("status") == "closed"]

            total_value = sum(
                o.get("quantity", 0) * o.get("price", 0) for o in all_orders
            )

            # Update summary cards
            self._update_card_value(self.total_card, str(len(all_orders)))
            self._update_card_value(self.open_card, str(len(open_orders)))
            self._update_card_value(self.closed_card, str(len(closed_orders)))
            self._update_card_value(self.value_card, f"€{total_value:,.2f}")

            # Update table based on filter
            self._update_table_with_filter()

        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Data", f"Failed to load order data:\n{str(e)}"
            )

    def _update_card_value(self, card: QWidget, value: str):
        """Update the value displayed in a card."""
        value_label = card.findChild(QLabel, "card_value")
        if value_label:
            value_label.setText(value)

    def _on_filter_changed(self, filter_text: str):
        """Handle status filter change."""
        self._update_table_with_filter()

    def _update_table_with_filter(self):
        """Update table based on current filter."""
        filter_text = self.status_filter_combo.currentText()
        all_orders = self.db.get_all_orders()

        # Apply filter
        if filter_text == "Open":
            filtered_orders = [o for o in all_orders if o.get("status") == "open"]
        elif filter_text == "Closed":
            filtered_orders = [o for o in all_orders if o.get("status") == "closed"]
        else:  # All
            filtered_orders = all_orders

        self._populate_table(filtered_orders)

    def _populate_table(self, orders: List[Dict[str, Any]]):
        """Populate orders table with data."""
        self.orders_table.setRowCount(0)

        # Sort by date (newest first)
        orders_sorted = sorted(orders, key=lambda x: x.get("date", ""), reverse=True)

        for order in orders_sorted:
            row = self.orders_table.rowCount()
            self.orders_table.insertRow(row)

            # Ticker
            ticker_item = QTableWidgetItem(order.get("ticker", ""))
            ticker_item.setFont(QFont("Monospace", 10, QFont.Weight.Bold))
            # Store order ID in the first column for later retrieval
            ticker_item.setData(Qt.ItemDataRole.UserRole, order.get("id"))
            self.orders_table.setItem(row, 0, ticker_item)

            # Order Type
            order_type = order.get("order_type", "").upper()
            type_item = QTableWidgetItem(order_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if order_type == "BUY":
                type_item.setForeground(QColor("#4CAF50"))
            else:
                type_item.setForeground(QColor("#F44336"))
            self.orders_table.setItem(row, 1, type_item)

            # Quantity
            quantity = order.get("quantity", 0)
            quantity_item = QTableWidgetItem(f"{quantity:,.4f}".rstrip("0").rstrip("."))
            quantity_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.orders_table.setItem(row, 2, quantity_item)

            # Price
            price = order.get("price", 0)
            price_item = QTableWidgetItem(f"€{price:,.2f}")
            price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.orders_table.setItem(row, 3, price_item)

            # Total Value
            total_value = quantity * price
            value_item = QTableWidgetItem(f"€{total_value:,.2f}")
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            value_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.orders_table.setItem(row, 4, value_item)

            # Date
            date_item = QTableWidgetItem(order.get("date", ""))
            self.orders_table.setItem(row, 5, date_item)

            # Status
            status = order.get("status", "").upper()
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if status == "OPEN":
                status_item.setForeground(QColor("#FF9800"))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            else:
                status_item.setForeground(QColor("#4CAF50"))
            self.orders_table.setItem(row, 6, status_item)

            # Actions
            actions_widget = self._create_action_buttons(order)
            self.orders_table.setCellWidget(row, 7, actions_widget)

    def _create_action_buttons(self, order: Dict[str, Any]) -> QWidget:
        """Create action buttons for an order row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)

        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setProperty("class", "secondary")
        edit_btn.setMinimumWidth(70)
        edit_btn.setMaximumWidth(85)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setToolTip("Edit this order")
        edit_btn.clicked.connect(lambda: self._on_edit_order(order))
        layout.addWidget(edit_btn)

        # Toggle status button
        status = order.get("status", "open")
        if status == "open":
            toggle_btn = QPushButton("✓ Close")
            toggle_btn.setToolTip("Mark as closed")
        else:
            toggle_btn = QPushButton("↻ Reopen")
            toggle_btn.setToolTip("Mark as open")
        toggle_btn.setProperty("class", "secondary")
        toggle_btn.setMinimumWidth(75)
        toggle_btn.setMaximumWidth(90)
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.clicked.connect(lambda: self._on_toggle_status(order))
        layout.addWidget(toggle_btn)

        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.setMinimumWidth(80)
        delete_btn.setMaximumWidth(95)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip("Delete this order")
        delete_btn.clicked.connect(lambda: self._on_delete_order(order))
        layout.addWidget(delete_btn)

        return widget

    def _on_add_order(self):
        """Handle add order button click."""
        dialog = OrderDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_order_data()
                self.db.add_order(
                    ticker=data["ticker"],
                    quantity=data["quantity"],
                    price=data["price"],
                    order_type=data["order_type"],
                    date=data["date"],
                    status=data["status"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Order added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add order:\n{str(e)}")

    def _on_edit_order(self, order: Dict[str, Any]):
        """Handle edit order."""
        dialog = OrderDialog(self.db, order=order, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_order_data()
                self.db.update_order(
                    order_id=order["id"],
                    ticker=data["ticker"],
                    quantity=data["quantity"],
                    price=data["price"],
                    order_type=data["order_type"],
                    date=data["date"],
                    status=data["status"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Order updated successfully!")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update order:\n{str(e)}"
                )

    def _on_toggle_status(self, order: Dict[str, Any]):
        """Toggle order status between open and closed."""
        try:
            current_status = order.get("status", "open")
            new_status = "closed" if current_status == "open" else "open"

            self.db.update_order(
                order_id=order["id"],
                ticker=order["ticker"],
                quantity=order["quantity"],
                price=order["price"],
                order_type=order["order_type"],
                date=order["date"],
                status=new_status,
            )
            self._load_data()
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update order status:\n{str(e)}"
            )

    def _on_delete_order(self, order: Dict[str, Any]):
        """Handle delete order."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this order?\n\n"
            f"Ticker: {order.get('ticker', 'N/A')}\n"
            f"Type: {order.get('order_type', 'N/A')}\n"
            f"Quantity: {order.get('quantity', 0)}\n"
            f"Price: €{order.get('price', 0):,.2f}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_order(order["id"])
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Order deleted successfully!")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete order:\n{str(e)}"
                )

    def _on_close_all_open(self):
        """Close all open orders."""
        reply = QMessageBox.question(
            self,
            "Confirm Close All",
            "Are you sure you want to mark all open orders as closed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                all_orders = self.db.get_all_orders()
                open_orders = [o for o in all_orders if o.get("status") == "open"]

                for order in open_orders:
                    self.db.update_order(
                        order_id=order["id"],
                        ticker=order["ticker"],
                        quantity=order["quantity"],
                        price=order["price"],
                        order_type=order["order_type"],
                        date=order["date"],
                        status="closed",
                    )

                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Closed {len(open_orders)} order(s) successfully!",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to close orders:\n{str(e)}"
                )

    def _on_delete_all_closed(self):
        """Delete all closed orders."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete All Closed",
            "Are you sure you want to delete all closed orders? This cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                all_orders = self.db.get_all_orders()
                closed_orders = [o for o in all_orders if o.get("status") == "closed"]

                for order in closed_orders:
                    self.db.delete_order(order["id"])

                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Deleted {len(closed_orders)} order(s) successfully!",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete orders:\n{str(e)}"
                )

    def refresh(self):
        """Public method to refresh the tab data."""
        self._load_data()

    def _on_selection_changed(self):
        """Handle table selection changes to enable/disable delete button."""
        has_selection = len(self.orders_table.selectedItems()) > 0
        self.delete_btn.setEnabled(has_selection)

    def _on_delete_selected(self):
        """Delete the currently selected order(s)."""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Get all order IDs from selected rows
        orders_to_delete = []
        for index in selected_rows:
            row = index.row()
            ticker_item = self.orders_table.item(row, 0)
            if ticker_item:
                order_id = ticker_item.data(Qt.ItemDataRole.UserRole)
                if order_id:
                    ticker = ticker_item.text()
                    order_type = self.orders_table.item(row, 1).text()
                    quantity = self.orders_table.item(row, 2).text()
                    orders_to_delete.append(
                        {
                            "id": order_id,
                            "ticker": ticker,
                            "type": order_type,
                            "quantity": quantity,
                        }
                    )

        if not orders_to_delete:
            return

        # Confirm deletion
        count = len(orders_to_delete)
        if count == 1:
            order = orders_to_delete[0]
            message = (
                f"Are you sure you want to delete this order?\n\n"
                f"Ticker: {order['ticker']}\n"
                f"Type: {order['type']}\n"
                f"Quantity: {order['quantity']}"
            )
        else:
            message = (
                f"Are you sure you want to delete {count} orders?\n\n"
                f"This action cannot be undone."
            )

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            failed_count = 0

            for order in orders_to_delete:
                try:
                    self.db.delete_order(order["id"])
                    deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to delete order {order['id']}: {e}")

            # Reload data
            self._load_data()
            self.data_changed.emit()

            # Show result message
            if failed_count == 0:
                if count == 1:
                    QMessageBox.information(
                        self, "Success", "Order deleted successfully!"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"{deleted_count} orders deleted successfully!",
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Partial Success",
                    f"{deleted_count} order(s) deleted, {failed_count} failed.",
                )

    def keyPressEvent(self, event):
        """Handle key press events for Delete/Suppr key."""
        # If Delete or Backspace key is pressed (Key_Backspace is often the Mac Delete key)
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.orders_table.selectedItems():
                self._on_delete_selected()
        else:
            super().keyPressEvent(event)
