"""
Category Manager for Prism application.
Manages custom categories, budget limits, and category analytics.
"""

from typing import List, Dict, Optional, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CategoryManager:
    """Manages custom categories and their properties."""

    DEFAULT_COLORS = {
        "income": "#10b981",
        "expense": "#ef4444",
    }

    DEFAULT_ICONS = {
        "income": "💰",
        "expense": "💳",
    }

    def __init__(self, db_manager):
        """
        Initialize category manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def add_category(
        self,
        name: str,
        category_type: str,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        budget_limit: Optional[float] = None,
    ) -> int:
        """
        Add a new custom category.

        Args:
            name: Category name
            category_type: 'income' or 'expense'
            color: Hex color code (e.g., '#10b981')
            icon: Emoji icon
            budget_limit: Monthly budget limit (for expenses)

        Returns:
            ID of created category
        """
        if category_type not in ["income", "expense"]:
            raise ValueError(f"Invalid category type: {category_type}")

        # Use default color/icon if not provided
        if color is None:
            color = self.DEFAULT_COLORS.get(category_type, "#6b7280")

        if icon is None:
            icon = self.DEFAULT_ICONS.get(category_type, "📝")

        query = """
            INSERT INTO categories (name, type, color, icon, budget_limit)
            VALUES (?, ?, ?, ?, ?)
        """

        try:
            cursor = self.db_manager.conn.execute(
                query, (name, category_type, color, icon, budget_limit)
            )
            self.db_manager.conn.commit()

            category_id = cursor.lastrowid
            logger.info(f"Added category: {name} ({category_type}) - ID {category_id}")

            return category_id

        except Exception as e:
            logger.error(f"Failed to add category: {str(e)}")
            raise

    def get_all_categories(
        self, category_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all categories, optionally filtered by type.

        Args:
            category_type: Optional filter ('income', 'expense', or None for all)

        Returns:
            List of category dictionaries
        """
        if category_type:
            query = "SELECT * FROM categories WHERE type = ? ORDER BY name ASC"
            cursor = self.db_manager.conn.execute(query, (category_type,))
        else:
            query = "SELECT * FROM categories ORDER BY type ASC, name ASC"
            cursor = self.db_manager.conn.execute(query)

        columns = [description[0] for description in cursor.description]

        categories = []
        for row in cursor.fetchall():
            categories.append(dict(zip(columns, row)))

        return categories

    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category dictionary or None if not found
        """
        query = "SELECT * FROM categories WHERE id = ?"
        cursor = self.db_manager.conn.execute(query, (category_id,))
        row = cursor.fetchone()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))

        return None

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by name.

        Args:
            name: Category name

        Returns:
            Category dictionary or None if not found
        """
        query = "SELECT * FROM categories WHERE name = ?"
        cursor = self.db_manager.conn.execute(query, (name,))
        row = cursor.fetchone()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))

        return None

    def update_category(self, category_id: int, **kwargs) -> bool:
        """
        Update a category's properties.

        Args:
            category_id: Category ID
            **kwargs: Fields to update (name, type, color, icon, budget_limit)

        Returns:
            True if successful, False otherwise
        """
        allowed_fields = ["name", "type", "color", "icon", "budget_limit"]
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            return False

        # Validate type if being updated
        if "type" in update_fields and update_fields["type"] not in [
            "income",
            "expense",
        ]:
            raise ValueError(f"Invalid category type: {update_fields['type']}")

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        query = f"UPDATE categories SET {set_clause} WHERE id = ?"

        values = list(update_fields.values()) + [category_id]

        try:
            self.db_manager.conn.execute(query, values)
            self.db_manager.conn.commit()

            logger.info(f"Updated category ID {category_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update category: {str(e)}")
            return False

    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category.

        Args:
            category_id: Category ID

        Returns:
            True if successful, False otherwise
        """
        # Check if category is in use
        if self._is_category_in_use(category_id):
            logger.warning(
                f"Cannot delete category ID {category_id}: Category is in use"
            )
            return False

        query = "DELETE FROM categories WHERE id = ?"

        try:
            cursor = self.db_manager.conn.execute(query, (category_id,))
            self.db_manager.conn.commit()

            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted category ID {category_id}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete category: {str(e)}")
            return False

    def _is_category_in_use(self, category_id: int) -> bool:
        """
        Check if a category is being used by any transactions.

        Args:
            category_id: Category ID

        Returns:
            True if category is in use, False otherwise
        """
        category = self.get_category(category_id)
        if not category:
            return False

        category_name = category["name"]

        # Check transactions
        query = "SELECT COUNT(*) FROM transactions WHERE category = ?"
        cursor = self.db_manager.conn.execute(query, (category_name,))
        count = cursor.fetchone()[0]

        if count > 0:
            return True

        # Check recurring transactions
        query = "SELECT COUNT(*) FROM recurring_transactions WHERE category = ?"
        cursor = self.db_manager.conn.execute(query, (category_name,))
        count = cursor.fetchone()[0]

        return count > 0

    def get_category_statistics(
        self,
        category_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific category.

        Args:
            category_name: Category name
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            Dictionary with category statistics
        """
        # Build query
        query = "SELECT * FROM transactions WHERE category = ?"
        params = [category_name]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        cursor = self.db_manager.conn.execute(query, params)
        columns = [description[0] for description in cursor.description]

        transactions = []
        for row in cursor.fetchall():
            transactions.append(dict(zip(columns, row)))

        # Calculate statistics
        total_amount = sum(t["amount"] for t in transactions)
        transaction_count = len(transactions)
        avg_amount = total_amount / transaction_count if transaction_count > 0 else 0

        # Get category info
        category = self.get_category_by_name(category_name)

        stats = {
            "category_name": category_name,
            "category_type": category["type"] if category else "unknown",
            "total_amount": round(total_amount, 2),
            "transaction_count": transaction_count,
            "average_amount": round(avg_amount, 2),
            "color": category["color"] if category else "#6b7280",
            "icon": category["icon"] if category else "📝",
        }

        # Add budget info for expenses
        if category and category["budget_limit"]:
            stats["budget_limit"] = category["budget_limit"]
            stats["budget_used"] = round(abs(total_amount), 2)
            stats["budget_remaining"] = round(
                category["budget_limit"] - abs(total_amount), 2
            )
            stats["budget_usage_percent"] = round(
                (abs(total_amount) / category["budget_limit"] * 100)
                if category["budget_limit"] > 0
                else 0,
                1,
            )

        return stats

    def get_all_category_statistics(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get statistics for all categories.

        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            List of category statistics
        """
        all_categories = self.get_all_categories()
        stats_list = []

        for category in all_categories:
            stats = self.get_category_statistics(category["name"], start_date, end_date)
            stats_list.append(stats)

        # Sort by total amount (descending for expenses, ascending for income)
        stats_list.sort(key=lambda x: abs(x["total_amount"]), reverse=True)

        return stats_list

    def get_budget_alerts(self) -> List[Dict[str, Any]]:
        """
        Get budget alerts for categories exceeding their limits.

        Returns:
            List of budget alert dictionaries
        """
        alerts = []

        # Get current month date range
        from datetime import datetime

        now = datetime.now()
        start_date = f"{now.year:04d}-{now.month:02d}-01"

        # Calculate last day of month
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)

        from datetime import timedelta

        last_day = (next_month - timedelta(days=1)).day
        end_date = f"{now.year:04d}-{now.month:02d}-{last_day:02d}"

        # Get expense categories with budget limits
        categories = self.get_all_categories(category_type="expense")

        for category in categories:
            if category["budget_limit"] and category["budget_limit"] > 0:
                stats = self.get_category_statistics(
                    category["name"], start_date, end_date
                )

                spent = abs(stats["total_amount"])
                budget = category["budget_limit"]
                usage_percent = (spent / budget * 100) if budget > 0 else 0

                if usage_percent >= 80:  # Alert if 80% or more used
                    alert_level = "critical" if usage_percent >= 100 else "warning"

                    alerts.append(
                        {
                            "category": category["name"],
                            "budget_limit": budget,
                            "spent": spent,
                            "remaining": max(0, budget - spent),
                            "usage_percent": round(usage_percent, 1),
                            "alert_level": alert_level,
                            "color": category["color"],
                            "icon": category["icon"],
                        }
                    )

        # Sort by usage percent (highest first)
        alerts.sort(key=lambda x: x["usage_percent"], reverse=True)

        return alerts

    def get_category_names(self, category_type: Optional[str] = None) -> List[str]:
        """
        Get a list of category names.

        Args:
            category_type: Optional filter ('income', 'expense', or None for all)

        Returns:
            List of category names
        """
        categories = self.get_all_categories(category_type)
        return [c["name"] for c in categories]

    def merge_categories(
        self, source_category_id: int, target_category_id: int
    ) -> bool:
        """
        Merge one category into another (update all transactions to use target category).

        Args:
            source_category_id: Category to merge from
            target_category_id: Category to merge into

        Returns:
            True if successful, False otherwise
        """
        source = self.get_category(source_category_id)
        target = self.get_category(target_category_id)

        if not source or not target:
            logger.error("Source or target category not found")
            return False

        if source["type"] != target["type"]:
            logger.error("Cannot merge categories of different types")
            return False

        try:
            # Update all transactions
            query = "UPDATE transactions SET category = ? WHERE category = ?"
            self.db_manager.conn.execute(query, (target["name"], source["name"]))

            # Update all recurring transactions
            query = "UPDATE recurring_transactions SET category = ? WHERE category = ?"
            self.db_manager.conn.execute(query, (target["name"], source["name"]))

            # Delete source category
            query = "DELETE FROM categories WHERE id = ?"
            self.db_manager.conn.execute(query, (source_category_id,))

            self.db_manager.conn.commit()

            logger.info(f"Merged category '{source['name']}' into '{target['name']}'")
            return True

        except Exception as e:
            logger.error(f"Failed to merge categories: {str(e)}")
            self.db_manager.conn.rollback()
            return False
