"""
Recurring Transactions Dialog for Prism application.
Provides interface for managing recurring transactions.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QMessageBox,
    QCheckBox,
    QWidget,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime
from ..utils.recurring_manager import RecurringTransactionManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RecurringDialog(QDialog):
    """Dialog for managing recurring transactions."""

    data_changed = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.recurring_manager = RecurringTransactionManager(db_manager)

        self.setWindowTitle("Recurring Transactions")
        self.setModal(False)
        self.resize(1000, 700)

        self._setup_ui()
        self._load_recurring_transactions()
        self._apply_styles()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title = QLabel("Recurring Transactions")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        # Statistics summary
        self.stats_widget = self._create_stats_widget()
        layout.addWidget(self.stats_widget)

        # Add new recurring transaction section
        add_group = self._create_add_section()
        layout.addWidget(add_group)

        # Existing recurring transactions table
        table_group = QGroupBox("Active Recurring Transactions")
        table_layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_recurring_transactions)
        toolbar_layout.addWidget(refresh_btn)

        process_btn = QPushButton("▶️ Process Due Transactions")
        process_btn.clicked.connect(self._process_due_transactions)
        process_btn.setToolTip(
            "Create actual transactions from recurring ones that are due"
        )
        toolbar_layout.addWidget(process_btn)

        show_inactive_btn = QPushButton("👁️ Show Inactive")
        show_inactive_btn.setCheckable(True)
        show_inactive_btn.clicked.connect(self._load_recurring_transactions)
        self.show_inactive_btn = show_inactive_btn
        toolbar_layout.addWidget(show_inactive_btn)

        toolbar_layout.addStretch()
        table_layout.addLayout(toolbar_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Category",
                "Amount",
                "Frequency",
                "Next Date",
                "Type",
                "Description",
                "End Date",
                "Active",
                "Actions",
            ]
        )

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(9, 150)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Upcoming transactions preview
        upcoming_group = self._create_upcoming_section()
        layout.addWidget(upcoming_group)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_stats_widget(self) -> QWidget:
        """Create statistics summary widget."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        stats = self.recurring_manager.get_statistics()

        # Total recurring
        total_label = QLabel(f"Total: {stats['total_recurring']}")
        total_label.setStyleSheet("font-weight: bold; color: #1f2937; padding: 8px;")
        layout.addWidget(total_label)

        # Active
        active_label = QLabel(f"Active: {stats['active_recurring']}")
        active_label.setStyleSheet("font-weight: bold; color: #10b981; padding: 8px;")
        layout.addWidget(active_label)

        # Estimated monthly income
        income_label = QLabel(
            f"Est. Monthly Income: €{stats['estimated_monthly_income']:,.2f}"
        )
        income_label.setStyleSheet("color: #059669; padding: 8px;")
        layout.addWidget(income_label)

        # Estimated monthly expense
        expense_label = QLabel(
            f"Est. Monthly Expense: €{stats['estimated_monthly_expense']:,.2f}"
        )
        expense_label.setStyleSheet("color: #dc2626; padding: 8px;")
        layout.addWidget(expense_label)

        # Net
        net_label = QLabel(f"Est. Net: €{stats['estimated_monthly_net']:,.2f}")
        net_color = "#10b981" if stats["estimated_monthly_net"] >= 0 else "#dc2626"
        net_label.setStyleSheet(f"font-weight: bold; color: {net_color}; padding: 8px;")
        layout.addWidget(net_label)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_add_section(self) -> QGroupBox:
        """Create add new recurring transaction section."""
        group = QGroupBox("Add New Recurring Transaction")
        layout = QVBoxLayout()

        # Form layout
        form_layout = QHBoxLayout()

        # Amount
        amount_layout = QVBoxLayout()
        amount_layout.addWidget(QLabel("Amount (€):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("e.g., 3000 or -50")
        amount_layout.addWidget(self.amount_input)
        form_layout.addLayout(amount_layout)

        # Category
        category_layout = QVBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., Salary, Rent")
        category_layout.addWidget(self.category_input)
        form_layout.addLayout(category_layout)

        # Type
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["personal", "investment"])
        type_layout.addWidget(self.type_combo)
        form_layout.addLayout(type_layout)

        # Frequency
        freq_layout = QVBoxLayout()
        freq_layout.addWidget(QLabel("Frequency:"))
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["monthly", "weekly", "daily", "yearly"])
        freq_layout.addWidget(self.frequency_combo)
        form_layout.addLayout(freq_layout)

        # Start date
        start_layout = QVBoxLayout()
        start_layout.addWidget(QLabel("Start Date:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        start_layout.addWidget(self.start_date_input)
        form_layout.addLayout(start_layout)

        layout.addLayout(form_layout)

        # Second row - description and end date
        form_layout2 = QHBoxLayout()

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description (optional):"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Monthly salary payment")
        desc_layout.addWidget(self.description_input)
        form_layout2.addLayout(desc_layout, 3)

        # End date
        end_layout = QVBoxLayout()
        end_layout.addWidget(QLabel("End Date (optional):"))
        end_date_container = QHBoxLayout()
        self.end_date_enabled = QCheckBox()
        end_date_container.addWidget(self.end_date_enabled)
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate().addYears(1))
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setEnabled(False)
        self.end_date_enabled.toggled.connect(self.end_date_input.setEnabled)
        end_date_container.addWidget(self.end_date_input)
        desc_layout.addLayout(end_date_container)
        form_layout2.addLayout(end_layout, 2)

        layout.addLayout(form_layout2)

        # Add button
        add_btn = QPushButton("➕ Add Recurring Transaction")
        add_btn.clicked.connect(self._add_recurring_transaction)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        layout.addWidget(add_btn)

        group.setLayout(layout)
        return group

    def _create_upcoming_section(self) -> QGroupBox:
        """Create upcoming transactions preview section."""
        group = QGroupBox("Upcoming Transactions (Next 30 Days)")
        layout = QVBoxLayout()

        self.upcoming_text = QTextEdit()
        self.upcoming_text.setReadOnly(True)
        self.upcoming_text.setMaximumHeight(150)
        layout.addWidget(self.upcoming_text)

        group.setLayout(layout)
        return group

    def _apply_styles(self):
        """Apply custom styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1f2937;
            }
            QTableWidget {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #1f2937;
            }
        """)

    def _add_recurring_transaction(self):
        """Add a new recurring transaction."""
        try:
            # Validate inputs
            amount_str = self.amount_input.text().strip()
            if not amount_str:
                QMessageBox.warning(self, "Validation Error", "Please enter an amount.")
                return

            try:
                amount = float(amount_str)
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Invalid amount format.")
                return

            category = self.category_input.text().strip()
            if not category:
                QMessageBox.warning(
                    self, "Validation Error", "Please enter a category."
                )
                return

            trans_type = self.type_combo.currentText()
            frequency = self.frequency_combo.currentText()
            start_date = self.start_date_input.date().toString("yyyy-MM-dd")
            description = self.description_input.text().strip()

            end_date = None
            if self.end_date_enabled.isChecked():
                end_date = self.end_date_input.date().toString("yyyy-MM-dd")

            # Add to database
            recurring_id = self.recurring_manager.add_recurring_transaction(
                amount=amount,
                category=category,
                trans_type=trans_type,
                frequency=frequency,
                start_date=start_date,
                description=description,
                end_date=end_date,
            )

            QMessageBox.information(
                self,
                "Success",
                f"Recurring transaction added successfully!\n\n"
                f"Category: {category}\n"
                f"Amount: €{amount:,.2f}\n"
                f"Frequency: {frequency}",
            )

            # Clear form
            self.amount_input.clear()
            self.category_input.clear()
            self.description_input.clear()
            self.start_date_input.setDate(QDate.currentDate())
            self.end_date_enabled.setChecked(False)

            # Reload table
            self._load_recurring_transactions()
            self.data_changed.emit()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to add recurring transaction:\n{str(e)}"
            )
            logger.error(f"Failed to add recurring transaction: {str(e)}")

    def _load_recurring_transactions(self):
        """Load recurring transactions into table."""
        show_inactive = self.show_inactive_btn.isChecked()
        recurring_list = self.recurring_manager.get_all_recurring_transactions(
            active_only=not show_inactive
        )

        self.table.setRowCount(len(recurring_list))

        for row, recurring in enumerate(recurring_list):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(recurring["id"])))

            # Category
            self.table.setItem(row, 1, QTableWidgetItem(recurring["category"]))

            # Amount
            amount = recurring["amount"]
            amount_item = QTableWidgetItem(f"€{amount:,.2f}")
            if amount > 0:
                amount_item.setForeground(QColor("#10b981"))
            else:
                amount_item.setForeground(QColor("#dc2626"))
            self.table.setItem(row, 2, amount_item)

            # Frequency
            self.table.setItem(row, 3, QTableWidgetItem(recurring["frequency"].title()))

            # Next date
            self.table.setItem(row, 4, QTableWidgetItem(recurring["next_occurrence"]))

            # Type
            self.table.setItem(row, 5, QTableWidgetItem(recurring["type"]))

            # Description
            self.table.setItem(
                row, 6, QTableWidgetItem(recurring.get("description", ""))
            )

            # End date
            end_date = recurring.get("end_date", "")
            self.table.setItem(row, 7, QTableWidgetItem(end_date or "None"))

            # Active status
            is_active = recurring["is_active"] == 1
            status_item = QTableWidgetItem("✓" if is_active else "✗")
            status_item.setForeground(
                QColor("#10b981") if is_active else QColor("#6b7280")
            )
            self.table.setItem(row, 8, status_item)

            # Actions
            actions_widget = self._create_action_buttons(recurring["id"])
            self.table.setCellWidget(row, 9, actions_widget)

        # Update statistics
        stats_widget = self._create_stats_widget()
        old_widget = self.stats_widget
        self.layout().replaceWidget(old_widget, stats_widget)
        old_widget.deleteLater()
        self.stats_widget = stats_widget

        # Update upcoming transactions
        self._update_upcoming_preview()

    def _create_action_buttons(self, recurring_id: int) -> QWidget:
        """Create action buttons for a recurring transaction."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Toggle active button
        toggle_btn = QPushButton("⏸️")
        toggle_btn.setToolTip("Toggle active/inactive")
        toggle_btn.setMaximumWidth(40)
        toggle_btn.clicked.connect(lambda: self._toggle_active(recurring_id))
        layout.addWidget(toggle_btn)

        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete recurring transaction")
        delete_btn.setMaximumWidth(40)
        delete_btn.clicked.connect(lambda: self._delete_recurring(recurring_id))
        layout.addWidget(delete_btn)

        widget.setLayout(layout)
        return widget

    def _toggle_active(self, recurring_id: int):
        """Toggle active status of a recurring transaction."""
        try:
            is_active = self.recurring_manager.toggle_active_status(recurring_id)
            status = "activated" if is_active else "deactivated"

            self._load_recurring_transactions()
            self.data_changed.emit()

            logger.info(f"Recurring transaction {recurring_id} {status}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle status:\n{str(e)}")

    def _delete_recurring(self, recurring_id: int):
        """Delete a recurring transaction."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this recurring transaction?\n\n"
            "This will not affect transactions already created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.recurring_manager.delete_recurring_transaction(recurring_id)
                self._load_recurring_transactions()
                self.data_changed.emit()

                QMessageBox.information(
                    self, "Success", "Recurring transaction deleted."
                )

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{str(e)}")

    def _process_due_transactions(self):
        """Process all due recurring transactions."""
        try:
            count = self.recurring_manager.process_due_transactions()

            if count > 0:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Created {count} transaction(s) from recurring entries.",
                )
                self._load_recurring_transactions()
                self.data_changed.emit()
            else:
                QMessageBox.information(
                    self,
                    "No Due Transactions",
                    "No recurring transactions are due at this time.",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to process transactions:\n{str(e)}"
            )

    def _update_upcoming_preview(self):
        """Update the upcoming transactions preview."""
        upcoming = self.recurring_manager.get_upcoming_transactions(days=30)

        if not upcoming:
            self.upcoming_text.setPlainText(
                "No upcoming transactions in the next 30 days."
            )
            return

        text = "Upcoming Transactions:\n\n"
        for trans in upcoming:
            amount_str = f"€{trans['amount']:,.2f}"
            text += f"• {trans['date']} - {trans['category']}: {amount_str} ({trans['frequency']})\n"

        self.upcoming_text.setPlainText(text)
