"""
Personal Finances tab for Prism application.
Displays transaction management interface with forms, tables, and charts.
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
    QSplitter,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from ..database.db_manager import DatabaseManager
from .tooltips import Tooltips, EXAMPLES
from .csv_import_dialog import CSVImportDialog
from ..utils.config import get_ui_page_size


class TransactionDialog(QDialog):
    """Dialog for adding/editing transactions."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        transaction: Optional[Dict[str, Any]] = None,
        parent=None,
    ):
        """
        Initialize transaction dialog.

        Args:
            db_manager: Database manager instance
            transaction: Existing transaction data for editing (None for new)
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.transaction = transaction
        self.is_edit = transaction is not None

        self.setWindowTitle("Edit Transaction" if self.is_edit else "New Transaction")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setToolTip(Tooltips.TRANSACTION_FORM["date"])
        if self.is_edit and self.transaction:
            date_str = self.transaction.get("date", "")
            if date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                self.date_edit.setDate(
                    QDate(date_obj.year, date_obj.month, date_obj.day)
                )
        else:
            self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)

        # Amount field
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText(EXAMPLES["transaction_amount"])
        self.amount_edit.setToolTip(Tooltips.TRANSACTION_FORM["amount"])
        if self.is_edit and self.transaction:
            self.amount_edit.setText(str(self.transaction.get("amount", "")))
        form_layout.addRow("Amount (€):", self.amount_edit)

        # Category field
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setToolTip(Tooltips.TRANSACTION_FORM["category"])
        self.category_combo.lineEdit().setPlaceholderText(
            EXAMPLES["transaction_category"]
        )
        categories = self._get_categories()
        self.category_combo.addItems(categories)
        if self.is_edit and self.transaction:
            current_category = self.transaction.get("category", "")
            index = self.category_combo.findText(current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(current_category)
        form_layout.addRow("Category:", self.category_combo)

        # Type field
        self.type_combo = QComboBox()
        self.type_combo.addItems(["personal", "investment"])
        self.type_combo.setToolTip(Tooltips.TRANSACTION_FORM["type_personal"])
        if self.is_edit and self.transaction:
            current_type = self.transaction.get("type", "personal")
            index = self.type_combo.findText(current_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        form_layout.addRow("Type:", self.type_combo)

        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText(EXAMPLES["transaction_description"])
        self.description_edit.setToolTip(Tooltips.TRANSACTION_FORM["description"])
        if self.is_edit and self.transaction:
            self.description_edit.setPlainText(self.transaction.get("description", ""))
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Help text
        help_label = QLabel(
            "💡 Tip: Enter negative amounts for expenses, positive for income"
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

    def _get_categories(self) -> List[str]:
        """Get list of existing categories from database."""
        try:
            transactions = self.db.get_all_transactions()
            categories = set()
            for trans in transactions:
                if trans.get("category"):
                    categories.add(trans["category"])

            # Add common default categories
            default_categories = [
                "Salary",
                "Food",
                "Transport",
                "Housing",
                "Entertainment",
                "Healthcare",
                "Shopping",
                "Utilities",
                "Education",
                "Other",
            ]
            categories.update(default_categories)

            return sorted(list(categories))
        except Exception:
            return ["Salary", "Food", "Transport", "Housing", "Entertainment", "Other"]

    def _on_accept(self):
        """Validate and accept dialog."""
        # Validate amount
        try:
            amount = float(self.amount_edit.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Amount", "Please enter a valid number for the amount."
            )
            self.amount_edit.setFocus()
            return

        # Validate category
        category = self.category_combo.currentText().strip()
        if not category:
            QMessageBox.warning(self, "Missing Category", "Please enter a category.")
            self.category_combo.setFocus()
            return

        self.accept()

    def get_transaction_data(self) -> Dict[str, Any]:
        """
        Get transaction data from form.

        Returns:
            Dictionary with transaction data
        """
        date = self.date_edit.date()
        date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"

        return {
            "date": date_str,
            "amount": float(self.amount_edit.text()),
            "category": self.category_combo.currentText().strip(),
            "type": self.type_combo.currentText(),
            "description": self.description_edit.toPlainText().strip(),
        }


class PersonalTab(QWidget):
    """Personal finances tab widget."""

    # Signal emitted when data changes
    data_changed = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        """
        Initialize personal tab.

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

        title = QLabel("Personal Finances")
        title.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Add transaction button
        self.add_btn = QPushButton("+ Add Transaction")
        self.add_btn.setToolTip(Tooltips.PERSONAL_TAB["add_button"])
        self.add_btn.clicked.connect(self._on_add_transaction)
        header_layout.addWidget(self.add_btn)

        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.setToolTip(Tooltips.PERSONAL_TAB["refresh_button"])
        self.refresh_btn.clicked.connect(self._load_data)
        header_layout.addWidget(self.refresh_btn)

        # CSV Import button
        self.import_csv_btn = QPushButton("📄 Import CSV")
        self.import_csv_btn.setToolTip("Import transactions from CSV file")
        self.import_csv_btn.clicked.connect(self._on_import_csv)
        header_layout.addWidget(self.import_csv_btn)

        # Delete button
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setProperty("class", "danger")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setToolTip(
            "Delete selected transaction(s) (or press Delete/Suppr key)\nShift+Click or Ctrl+Click to select multiple"
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

        # Pagination controls
        self._create_pagination_controls()
        layout.addWidget(self.pagination_widget)

        # Transaction table
        self._create_transaction_table()
        layout.addWidget(self.transaction_table, 1)

        # Initialize pagination state
        self.current_page = 0
        self.page_size = get_ui_page_size("personal")  # Configurable page size
        self.total_transactions = 0

    def _create_summary_section(self) -> QWidget:
        """Create summary cards section."""
        summary = QWidget()
        layout = QHBoxLayout(summary)
        layout.setSpacing(15)

        # Balance card
        self.balance_card = self._create_card("Current Balance", "€0.00", "#4CAF50")
        self.balance_card.setToolTip(Tooltips.PERSONAL_TAB["balance_card"])
        layout.addWidget(self.balance_card)

        # Income card
        self.income_card = self._create_card("Total Income", "€0.00", "#2196F3")
        self.income_card.setToolTip(Tooltips.PERSONAL_TAB["income_card"])
        layout.addWidget(self.income_card)

        # Expenses card
        self.expenses_card = self._create_card("Total Expenses", "€0.00", "#F44336")
        self.expenses_card.setToolTip(Tooltips.PERSONAL_TAB["expenses_card"])
        layout.addWidget(self.expenses_card)

        # Transaction count card
        self.count_card = self._create_card("Transactions", "0", "#9C27B0")
        self.count_card.setToolTip(Tooltips.PERSONAL_TAB["count_card"])
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
        card.setStyleSheet(f"""
            QWidget {{
                background-color: palette(base);
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
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

    def _create_transaction_table(self):
        """Create transaction table widget."""
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setToolTip(Tooltips.PERSONAL_TAB["transaction_table"])
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(
            ["Date", "Amount", "Category", "Type", "Description", "Actions"]
        )

        # Configure table
        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.transaction_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.transaction_table.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection
        )
        self.transaction_table.setAlternatingRowColors(True)
        self.transaction_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Connect selection change to enable/disable delete button
        self.transaction_table.itemSelectionChanged.connect(self._on_selection_changed)

    def _create_pagination_controls(self):
        """Create pagination controls widget."""
        self.pagination_widget = QWidget()
        layout = QHBoxLayout(self.pagination_widget)
        layout.setContentsMargins(0, 10, 0, 10)

        # Page size selector
        layout.addWidget(QLabel("Show:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "All"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        layout.addWidget(self.page_size_combo)

        layout.addStretch()

        # Navigation buttons
        self.first_btn = QPushButton("⏮️ First")
        self.first_btn.clicked.connect(self._on_first_page)
        self.first_btn.setEnabled(False)
        layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("◀️ Previous")
        self.prev_btn.clicked.connect(self._on_prev_page)
        self.prev_btn.setEnabled(False)
        layout.addWidget(self.prev_btn)

        # Page info
        self.page_info_label = QLabel("Page 1 of 1")
        layout.addWidget(self.page_info_label)

        self.next_btn = QPushButton("Next ▶️")
        self.next_btn.clicked.connect(self._on_next_page)
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("Last ⏭️")
        self.last_btn.clicked.connect(self._on_last_page)
        self.last_btn.setEnabled(False)
        layout.addWidget(self.last_btn)

        self.pagination_widget.setVisible(False)  # Hidden by default

    def _load_data(self):
        """Load data from database and update UI."""
        try:
            # Get balance
            balance = self.db.get_balance()
            self._update_card_value(self.balance_card, f"€{balance:,.2f}")

            # Get total transaction count
            self.total_transactions = self.db.get_transaction_count()

            # Calculate income and expenses from all transactions
            all_transactions = self.db.get_all_transactions()
            income = sum(t["amount"] for t in all_transactions if t["amount"] > 0)
            expenses = sum(
                abs(t["amount"]) for t in all_transactions if t["amount"] < 0
            )

            self._update_card_value(self.income_card, f"€{income:,.2f}")
            self._update_card_value(self.expenses_card, f"€{expenses:,.2f}")
            self._update_card_value(self.count_card, str(self.total_transactions))

            # Update pagination controls
            self._update_pagination_controls()

            # Load paginated transactions
            self._load_transactions_page()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Data",
                f"Failed to load transaction data:\n{str(e)}",
            )

    def _update_card_value(self, card: QWidget, value: str):
        """Update the value displayed in a card."""
        value_label = card.findChild(QLabel, "card_value")
        if value_label:
            value_label.setText(value)

    def _load_transactions_page(self):
        """Load transactions for current page."""
        if self.page_size == 0:  # Show all
            transactions = self.db.get_all_transactions()
        else:
            offset = self.current_page * self.page_size
            transactions = self.db.get_all_transactions(
                limit=self.page_size, offset=offset
            )

        self._populate_table(transactions)

    def _update_pagination_controls(self):
        """Update pagination controls based on current state."""
        if self.total_transactions <= self.page_size or self.page_size == 0:
            self.pagination_widget.setVisible(False)
            return

        self.pagination_widget.setVisible(True)

        total_pages = (self.total_transactions + self.page_size - 1) // self.page_size
        current_page_display = self.current_page + 1

        # Update page info
        self.page_info_label.setText(f"Page {current_page_display} of {total_pages}")

        # Update button states
        self.first_btn.setEnabled(self.current_page > 0)
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        self.last_btn.setEnabled(self.current_page < total_pages - 1)

    def _on_page_size_changed(self, size_text: str):
        """Handle page size change."""
        if size_text == "All":
            self.page_size = 0
        else:
            self.page_size = int(size_text)

        self.current_page = 0
        self._load_data()

    def _on_first_page(self):
        """Go to first page."""
        self.current_page = 0
        self._load_transactions_page()
        self._update_pagination_controls()

    def _on_prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_transactions_page()
            self._update_pagination_controls()

    def _on_next_page(self):
        """Go to next page."""
        total_pages = (self.total_transactions + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._load_transactions_page()
            self._update_pagination_controls()

    def _on_last_page(self):
        """Go to last page."""
        total_pages = (self.total_transactions + self.page_size - 1) // self.page_size
        self.current_page = total_pages - 1
        self._load_transactions_page()
        self._update_pagination_controls()

    def _populate_table(self, transactions: List[Dict[str, Any]]):
        """Populate transaction table with data."""
        self.transaction_table.setRowCount(0)

        # Sort by date (newest first)
        transactions_sorted = sorted(
            transactions, key=lambda x: x.get("date", ""), reverse=True
        )

        for trans in transactions_sorted:
            row = self.transaction_table.rowCount()
            self.transaction_table.insertRow(row)

            # Date
            date_item = QTableWidgetItem(trans.get("date", ""))
            # Store transaction ID in the first column for later retrieval
            date_item.setData(Qt.ItemDataRole.UserRole, trans.get("id"))
            self.transaction_table.setItem(row, 0, date_item)

            # Amount
            amount = trans.get("amount", 0)
            amount_item = QTableWidgetItem(f"€{amount:,.2f}")
            if amount >= 0:
                amount_item.setForeground(QColor("#4CAF50"))
            else:
                amount_item.setForeground(QColor("#F44336"))
            amount_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.transaction_table.setItem(row, 1, amount_item)

            # Category
            category_item = QTableWidgetItem(trans.get("category", ""))
            self.transaction_table.setItem(row, 2, category_item)

            # Type
            type_item = QTableWidgetItem(trans.get("type", ""))
            self.transaction_table.setItem(row, 3, type_item)

            # Description
            description_item = QTableWidgetItem(trans.get("description", ""))
            self.transaction_table.setItem(row, 4, description_item)

            # Actions
            actions_widget = self._create_action_buttons(trans)
            self.transaction_table.setCellWidget(row, 5, actions_widget)

    def _create_action_buttons(self, transaction: Dict[str, Any]) -> QWidget:
        """Create action buttons for a transaction row."""
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
        edit_btn.setToolTip("Edit this transaction")
        edit_btn.clicked.connect(lambda: self._on_edit_transaction(transaction))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.setMinimumWidth(80)
        delete_btn.setMaximumWidth(95)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip("Delete this transaction")
        delete_btn.clicked.connect(lambda: self._on_delete_transaction(transaction))
        layout.addWidget(delete_btn)

        return widget

    def _on_add_transaction(self):
        """Handle add transaction button click."""
        dialog = TransactionDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_transaction_data()
                self.db.add_transaction(
                    date=data["date"],
                    amount=data["amount"],
                    category=data["category"],
                    trans_type=data["type"],
                    description=data["description"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(
                    self, "Success", "Transaction added successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to add transaction:\n{str(e)}"
                )

    def _on_edit_transaction(self, transaction: Dict[str, Any]):
        """Handle edit transaction."""
        dialog = TransactionDialog(self.db, transaction=transaction, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_transaction_data()
                self.db.update_transaction(
                    transaction_id=transaction["id"],
                    date=data["date"],
                    amount=data["amount"],
                    category=data["category"],
                    trans_type=data["type"],
                    description=data["description"],
                )
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(
                    self, "Success", "Transaction updated successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update transaction:\n{str(e)}"
                )

    def _on_delete_transaction(self, transaction: Dict[str, Any]):
        """Handle delete transaction."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this transaction?\n\n"
            f"Date: {transaction.get('date', 'N/A')}\n"
            f"Amount: €{transaction.get('amount', 0):,.2f}\n"
            f"Category: {transaction.get('category', 'N/A')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_transaction(transaction["id"])
                self._load_data()
                self.data_changed.emit()
                QMessageBox.information(
                    self, "Success", "Transaction deleted successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete transaction:\n{str(e)}"
                )

    def refresh(self):
        """Public method to refresh the tab data."""
        self.current_page = 0  # Reset to first page on refresh
        self._load_data()

    def _on_selection_changed(self):
        """Handle table selection changes to enable/disable delete button."""
        has_selection = len(self.transaction_table.selectedItems()) > 0
        self.delete_btn.setEnabled(has_selection)

    def _on_delete_selected(self):
        """Delete the currently selected transaction(s)."""
        selected_rows = self.transaction_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Get all transaction IDs from selected rows
        transactions_to_delete = []
        for index in selected_rows:
            row = index.row()
            item = self.transaction_table.item(row, 0)
            if item:
                trans_id = item.data(Qt.ItemDataRole.UserRole)
                if trans_id:
                    date = self.transaction_table.item(row, 0).text()
                    amount = self.transaction_table.item(row, 1).text()
                    category = self.transaction_table.item(row, 2).text()
                    transactions_to_delete.append(
                        {
                            "id": trans_id,
                            "date": date,
                            "amount": amount,
                            "category": category,
                        }
                    )

        if not transactions_to_delete:
            return

        # Confirm deletion
        count = len(transactions_to_delete)
        if count == 1:
            trans = transactions_to_delete[0]
            message = (
                f"Are you sure you want to delete this transaction?\n\n"
                f"Date: {trans['date']}\n"
                f"Amount: {trans['amount']}\n"
                f"Category: {trans['category']}"
            )
        else:
            message = (
                f"Are you sure you want to delete {count} transactions?\n\n"
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

            for trans in transactions_to_delete:
                try:
                    self.db.delete_transaction(trans["id"])
                    deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to delete transaction {trans['id']}: {e}")

            # Reload data
            self._load_data()
            self.data_changed.emit()

            # Show result message
            if failed_count == 0:
                if count == 1:
                    QMessageBox.information(
                        self, "Success", "Transaction deleted successfully!"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"{deleted_count} transactions deleted successfully!",
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Partial Success",
                    f"{deleted_count} transaction(s) deleted, {failed_count} failed.",
                )

    def _on_import_csv(self):
        """Handle CSV import button click."""
        try:
            dialog = CSVImportDialog(self.db, parent=self)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                # Refresh data after successful import
                self._load_data()
                self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to open CSV import dialog:\n{str(e)}"
            )

    def keyPressEvent(self, event):
        """Handle key press events for Delete/Suppr key."""
        # Check if Delete or Backspace key is pressed
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.transaction_table.selectedItems():
                self._on_delete_selected()
        else:
            super().keyPressEvent(event)
