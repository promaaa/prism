"""
Categories and Budget Management Dialog for Prism application.
Provides interface for managing custom categories, budgets, and viewing budget alerts.
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
    QMessageBox,
    QWidget,
    QTabWidget,
    QProgressBar,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from ..utils.category_manager import CategoryManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CategoriesDialog(QDialog):
    """Dialog for managing categories and budgets."""

    data_changed = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.category_manager = CategoryManager(db_manager)

        self.setWindowTitle("Categories & Budget Management")
        self.setModal(False)
        self.resize(900, 700)

        self._setup_ui()
        self._apply_styles()
        self._load_categories()
        self._check_budget_alerts()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title = QLabel("Categories & Budget Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_categories_tab(), "📋 Categories")
        tabs.addTab(self._create_budget_tab(), "💰 Budgets")
        tabs.addTab(self._create_alerts_tab(), "⚠️ Alerts")
        layout.addWidget(tabs)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_categories_tab(self) -> QWidget:
        """Create categories management tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add new category section
        add_group = QGroupBox("Add New Category")
        add_layout = QVBoxLayout()

        # Form
        form_layout = QHBoxLayout()

        # Name
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Category Name:"))
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("e.g., Groceries, Utilities")
        name_layout.addWidget(self.category_name_input)
        form_layout.addLayout(name_layout, 2)

        # Type
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.category_type_combo = QComboBox()
        self.category_type_combo.addItems(["expense", "income"])
        type_layout.addWidget(self.category_type_combo)
        form_layout.addLayout(type_layout, 1)

        # Color
        color_layout = QVBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.category_color_combo = QComboBox()
        self.category_color_combo.addItems(
            [
                "Red (#ef4444)",
                "Green (#10b981)",
                "Blue (#3b82f6)",
                "Yellow (#eab308)",
                "Purple (#8b5cf6)",
                "Pink (#ec4899)",
                "Teal (#14b8a6)",
                "Orange (#f59e0b)",
                "Gray (#6b7280)",
            ]
        )
        color_layout.addWidget(self.category_color_combo)
        form_layout.addLayout(color_layout, 1)

        # Icon
        icon_layout = QVBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self.category_icon_input = QLineEdit()
        self.category_icon_input.setPlaceholderText("Emoji (e.g., 🍔, 🚗)")
        self.category_icon_input.setMaxLength(2)
        icon_layout.addWidget(self.category_icon_input)
        form_layout.addLayout(icon_layout, 1)

        add_layout.addLayout(form_layout)

        # Add button
        add_btn = QPushButton("➕ Add Category")
        add_btn.clicked.connect(self._add_category)
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
        add_layout.addWidget(add_btn)

        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        # Existing categories table
        table_group = QGroupBox("Existing Categories")
        table_layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_categories)
        toolbar_layout.addWidget(refresh_btn)

        toolbar_layout.addStretch()
        table_layout.addLayout(toolbar_layout)

        # Table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(7)
        self.categories_table.setHorizontalHeaderLabels(
            ["ID", "Icon", "Name", "Type", "Color", "In Use", "Actions"]
        )

        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 100)

        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        table_layout.addWidget(self.categories_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def _create_budget_tab(self) -> QWidget:
        """Create budget management tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel(
            "Set monthly budget limits for expense categories. "
            "You'll receive alerts when spending approaches or exceeds these limits."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #6b7280; padding: 8px; background-color: #f3f4f6; border-radius: 4px;"
        )
        layout.addWidget(info_label)

        # Budget table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(6)
        self.budget_table.setHorizontalHeaderLabels(
            [
                "Category",
                "Budget Limit (€)",
                "Spent This Month (€)",
                "Remaining (€)",
                "Usage %",
                "Update",
            ]
        )

        header = self.budget_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 100)

        self.budget_table.setAlternatingRowColors(True)

        layout.addWidget(self.budget_table)

        widget.setLayout(layout)
        return widget

    def _create_alerts_tab(self) -> QWidget:
        """Create budget alerts tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Alerts area
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        layout.addWidget(self.alerts_text)

        widget.setLayout(layout)
        return widget

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
            QLineEdit, QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
        """)

    def _add_category(self):
        """Add a new category."""
        try:
            name = self.category_name_input.text().strip()
            if not name:
                QMessageBox.warning(
                    self, "Validation Error", "Please enter a category name."
                )
                return

            category_type = self.category_type_combo.currentText()

            # Extract color hex from combo text
            color_text = self.category_color_combo.currentText()
            color = color_text.split("(")[1].rstrip(")")

            icon = self.category_icon_input.text().strip() or None

            # Check if category already exists
            existing = self.category_manager.get_category_by_name(name)
            if existing:
                QMessageBox.warning(
                    self,
                    "Duplicate Category",
                    f"A category named '{name}' already exists.",
                )
                return

            # Add category
            category_id = self.category_manager.add_category(
                name=name, category_type=category_type, color=color, icon=icon
            )

            QMessageBox.information(
                self, "Success", f"Category '{name}' added successfully!"
            )

            # Clear form
            self.category_name_input.clear()
            self.category_icon_input.clear()

            # Reload table
            self._load_categories()
            self.data_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add category:\n{str(e)}")
            logger.error(f"Failed to add category: {str(e)}")

    def _load_categories(self):
        """Load categories into table."""
        categories = self.category_manager.get_all_categories()

        self.categories_table.setRowCount(len(categories))

        for row, category in enumerate(categories):
            # ID
            self.categories_table.setItem(row, 0, QTableWidgetItem(str(category["id"])))

            # Icon
            icon = category.get("icon", "")
            icon_item = QTableWidgetItem(icon)
            icon_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.categories_table.setItem(row, 1, icon_item)

            # Name
            name_item = QTableWidgetItem(category["name"])
            name_item.setForeground(QColor(category.get("color", "#000000")))
            self.categories_table.setItem(row, 2, name_item)

            # Type
            type_item = QTableWidgetItem(category["type"].title())
            self.categories_table.setItem(row, 3, type_item)

            # Color
            color_item = QTableWidgetItem(category.get("color", ""))
            color_item.setBackground(QColor(category.get("color", "#ffffff")))
            self.categories_table.setItem(row, 4, color_item)

            # In use status
            in_use = self.category_manager._is_category_in_use(category["id"])
            in_use_item = QTableWidgetItem("Yes" if in_use else "No")
            in_use_item.setForeground(
                QColor("#10b981") if in_use else QColor("#6b7280")
            )
            self.categories_table.setItem(row, 5, in_use_item)

            # Actions
            actions_widget = self._create_category_action_buttons(category["id"])
            self.categories_table.setCellWidget(row, 6, actions_widget)

        # Load budgets
        self._load_budgets()

    def _load_budgets(self):
        """Load budget information."""
        from datetime import datetime

        # Get current month stats
        now = datetime.now()
        start_date = f"{now.year:04d}-{now.month:02d}-01"

        # Calculate end date
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)

        from datetime import timedelta

        last_day = (next_month - timedelta(days=1)).day
        end_date = f"{now.year:04d}-{now.month:02d}-{last_day:02d}"

        # Get expense categories
        categories = self.category_manager.get_all_categories(category_type="expense")

        self.budget_table.setRowCount(len(categories))

        for row, category in enumerate(categories):
            # Category name
            name_item = QTableWidgetItem(
                f"{category.get('icon', '')} {category['name']}"
            )
            self.budget_table.setItem(row, 0, name_item)

            # Get stats
            stats = self.category_manager.get_category_statistics(
                category["name"], start_date, end_date
            )

            spent = abs(stats["total_amount"])
            budget_limit = category.get("budget_limit", 0) or 0

            # Budget limit
            budget_item = QTableWidgetItem(
                f"{budget_limit:,.2f}" if budget_limit > 0 else "Not set"
            )
            self.budget_table.setItem(row, 1, budget_item)

            # Spent
            spent_item = QTableWidgetItem(f"{spent:,.2f}")
            self.budget_table.setItem(row, 2, spent_item)

            # Remaining
            if budget_limit > 0:
                remaining = budget_limit - spent
                remaining_item = QTableWidgetItem(f"{remaining:,.2f}")
                remaining_item.setForeground(
                    QColor("#10b981") if remaining >= 0 else QColor("#dc2626")
                )
                self.budget_table.setItem(row, 3, remaining_item)
            else:
                self.budget_table.setItem(row, 3, QTableWidgetItem("N/A"))

            # Usage percentage with progress bar
            if budget_limit > 0:
                usage_pct = (spent / budget_limit * 100) if budget_limit > 0 else 0
                progress_widget = QWidget()
                progress_layout = QVBoxLayout()
                progress_layout.setContentsMargins(4, 4, 4, 4)

                progress_bar = QProgressBar()
                progress_bar.setValue(int(min(usage_pct, 100)))
                progress_bar.setFormat(f"{usage_pct:.1f}%")

                # Color based on usage
                if usage_pct >= 100:
                    progress_bar.setStyleSheet(
                        "QProgressBar::chunk { background-color: #dc2626; }"
                    )
                elif usage_pct >= 80:
                    progress_bar.setStyleSheet(
                        "QProgressBar::chunk { background-color: #f59e0b; }"
                    )
                else:
                    progress_bar.setStyleSheet(
                        "QProgressBar::chunk { background-color: #10b981; }"
                    )

                progress_layout.addWidget(progress_bar)
                progress_widget.setLayout(progress_layout)
                self.budget_table.setCellWidget(row, 4, progress_widget)
            else:
                self.budget_table.setItem(row, 4, QTableWidgetItem("N/A"))

            # Update button
            update_widget = self._create_budget_update_button(
                category["id"], budget_limit
            )
            self.budget_table.setCellWidget(row, 5, update_widget)

    def _create_category_action_buttons(self, category_id: int) -> QWidget:
        """Create action buttons for a category."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete category")
        delete_btn.setMaximumWidth(50)
        delete_btn.clicked.connect(lambda: self._delete_category(category_id))
        layout.addWidget(delete_btn)

        widget.setLayout(layout)
        return widget

    def _create_budget_update_button(
        self, category_id: int, current_limit: float
    ) -> QWidget:
        """Create budget update button."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        update_btn = QPushButton("Set")
        update_btn.setMaximumWidth(80)
        update_btn.clicked.connect(
            lambda: self._set_budget_limit(category_id, current_limit)
        )
        layout.addWidget(update_btn)

        widget.setLayout(layout)
        return widget

    def _delete_category(self, category_id: int):
        """Delete a category."""
        category = self.category_manager.get_category(category_id)
        if not category:
            return

        # Check if in use
        if self.category_manager._is_category_in_use(category_id):
            QMessageBox.warning(
                self,
                "Cannot Delete",
                f"Category '{category['name']}' is currently in use by transactions.\n\n"
                "You cannot delete categories that are being used.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the category '{category['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.category_manager.delete_category(category_id)
                self._load_categories()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", "Category deleted.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete category:\n{str(e)}"
                )

    def _set_budget_limit(self, category_id: int, current_limit: float):
        """Set budget limit for a category."""
        from PyQt6.QtWidgets import QInputDialog

        category = self.category_manager.get_category(category_id)
        if not category:
            return

        new_limit, ok = QInputDialog.getDouble(
            self,
            "Set Budget Limit",
            f"Enter monthly budget limit for '{category['name']}' (€):",
            value=current_limit or 0,
            min=0,
            max=1000000,
            decimals=2,
        )

        if ok:
            try:
                self.category_manager.update_category(
                    category_id, budget_limit=new_limit
                )
                self._load_budgets()
                self._check_budget_alerts()
                self.data_changed.emit()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Budget limit for '{category['name']}' set to €{new_limit:,.2f}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update budget:\n{str(e)}"
                )

    def _check_budget_alerts(self):
        """Check and display budget alerts."""
        alerts = self.category_manager.get_budget_alerts()

        if not alerts:
            self.alerts_text.setHtml(
                "<div style='padding: 20px; text-align: center; color: #10b981;'>"
                "<h2>✓ All Good!</h2>"
                "<p>No budget alerts at this time. You're staying within your limits.</p>"
                "</div>"
            )
            return

        html = "<div style='padding: 10px;'>"
        html += "<h2 style='color: #dc2626;'>⚠️ Budget Alerts</h2>"
        html += "<p>The following categories have reached or exceeded 80% of their budget limits:</p>"
        html += (
            "<table style='width: 100%; border-collapse: collapse; margin-top: 10px;'>"
        )
        html += "<tr style='background-color: #f3f4f6; font-weight: bold;'>"
        html += "<th style='padding: 8px; text-align: left;'>Category</th>"
        html += "<th style='padding: 8px; text-align: right;'>Budget</th>"
        html += "<th style='padding: 8px; text-align: right;'>Spent</th>"
        html += "<th style='padding: 8px; text-align: right;'>Remaining</th>"
        html += "<th style='padding: 8px; text-align: right;'>Usage</th>"
        html += "</tr>"

        for alert in alerts:
            bg_color = "#fee2e2" if alert["alert_level"] == "critical" else "#fef3c7"
            html += f"<tr style='background-color: {bg_color};'>"
            html += (
                f"<td style='padding: 8px;'>{alert['icon']} {alert['category']}</td>"
            )
            html += f"<td style='padding: 8px; text-align: right;'>€{alert['budget_limit']:,.2f}</td>"
            html += f"<td style='padding: 8px; text-align: right;'>€{alert['spent']:,.2f}</td>"
            html += f"<td style='padding: 8px; text-align: right;'>€{alert['remaining']:,.2f}</td>"
            html += f"<td style='padding: 8px; text-align: right; font-weight: bold;'>{alert['usage_percent']:.1f}%</td>"
            html += "</tr>"

        html += "</table>"
        html += "</div>"

        self.alerts_text.setHtml(html)
