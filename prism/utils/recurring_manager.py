"""
Recurring Transactions Manager for Prism application.
Handles creation, management, and automatic execution of recurring transactions.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RecurringTransactionManager:
    """Manages recurring transactions and their automatic execution."""

    FREQUENCY_MAP = {
        "daily": lambda date: date + timedelta(days=1),
        "weekly": lambda date: date + timedelta(weeks=1),
        "monthly": lambda date: add_months(date, 1),
        "yearly": lambda date: add_months(date, 12),
    }

    def __init__(self, db_manager):
        """
        Initialize recurring transaction manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def add_recurring_transaction(
        self,
        amount: float,
        category: str,
        trans_type: str,
        frequency: str,
        start_date: str,
        description: str = "",
        end_date: Optional[str] = None,
    ) -> int:
        """
        Add a new recurring transaction.

        Args:
            amount: Transaction amount
            category: Transaction category
            trans_type: Transaction type ('personal' or 'investment')
            frequency: Frequency ('daily', 'weekly', 'monthly', 'yearly')
            start_date: Start date (YYYY-MM-DD)
            description: Optional description
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            ID of created recurring transaction
        """
        if frequency not in self.FREQUENCY_MAP:
            raise ValueError(f"Invalid frequency: {frequency}")

        if trans_type not in ["personal", "investment"]:
            raise ValueError(f"Invalid transaction type: {trans_type}")

        # Calculate next occurrence
        next_occurrence = self._calculate_next_occurrence(start_date, frequency)

        query = """
            INSERT INTO recurring_transactions
            (amount, category, type, description, frequency, start_date, end_date, next_occurrence, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """

        cursor = self.db_manager.conn.execute(
            query,
            (
                amount,
                category,
                trans_type,
                description,
                frequency,
                start_date,
                end_date,
                next_occurrence,
            ),
        )
        self.db_manager.conn.commit()

        recurring_id = cursor.lastrowid
        logger.info(
            f"Added recurring transaction: {category} ({frequency}) - ID {recurring_id}"
        )

        return recurring_id

    def get_all_recurring_transactions(
        self, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all recurring transactions.

        Args:
            active_only: If True, only return active recurring transactions

        Returns:
            List of recurring transaction dictionaries
        """
        query = "SELECT * FROM recurring_transactions"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY next_occurrence ASC"

        cursor = self.db_manager.conn.execute(query)
        columns = [description[0] for description in cursor.description]

        recurring_transactions = []
        for row in cursor.fetchall():
            recurring_transactions.append(dict(zip(columns, row)))

        return recurring_transactions

    def get_recurring_transaction(self, recurring_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific recurring transaction by ID.

        Args:
            recurring_id: Recurring transaction ID

        Returns:
            Recurring transaction dictionary or None if not found
        """
        query = "SELECT * FROM recurring_transactions WHERE id = ?"
        cursor = self.db_manager.conn.execute(query, (recurring_id,))
        row = cursor.fetchone()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))

        return None

    def update_recurring_transaction(self, recurring_id: int, **kwargs) -> bool:
        """
        Update a recurring transaction.

        Args:
            recurring_id: Recurring transaction ID
            **kwargs: Fields to update

        Returns:
            True if successful, False otherwise
        """
        allowed_fields = [
            "amount",
            "category",
            "type",
            "description",
            "frequency",
            "end_date",
            "is_active",
        ]

        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            return False

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        query = f"UPDATE recurring_transactions SET {set_clause} WHERE id = ?"

        values = list(update_fields.values()) + [recurring_id]

        self.db_manager.conn.execute(query, values)
        self.db_manager.conn.commit()

        logger.info(f"Updated recurring transaction ID {recurring_id}")
        return True

    def delete_recurring_transaction(self, recurring_id: int) -> bool:
        """
        Delete a recurring transaction.

        Args:
            recurring_id: Recurring transaction ID

        Returns:
            True if successful, False otherwise
        """
        query = "DELETE FROM recurring_transactions WHERE id = ?"
        cursor = self.db_manager.conn.execute(query, (recurring_id,))
        self.db_manager.conn.commit()

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted recurring transaction ID {recurring_id}")

        return deleted

    def toggle_active_status(self, recurring_id: int) -> bool:
        """
        Toggle active status of a recurring transaction.

        Args:
            recurring_id: Recurring transaction ID

        Returns:
            New active status (True/False)
        """
        query = """
            UPDATE recurring_transactions
            SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
            WHERE id = ?
        """
        self.db_manager.conn.execute(query, (recurring_id,))
        self.db_manager.conn.commit()

        # Get new status
        recurring = self.get_recurring_transaction(recurring_id)
        is_active = recurring["is_active"] == 1 if recurring else False

        logger.info(
            f"Toggled recurring transaction ID {recurring_id} to {'active' if is_active else 'inactive'}"
        )

        return is_active

    def process_due_transactions(self) -> int:
        """
        Process all recurring transactions that are due.
        Creates actual transactions from recurring ones.

        Returns:
            Number of transactions created
        """
        today = datetime.now().strftime("%Y-%m-%d")
        created_count = 0

        # Get all active recurring transactions that are due
        query = """
            SELECT * FROM recurring_transactions
            WHERE is_active = 1
            AND next_occurrence <= ?
            AND (end_date IS NULL OR end_date >= ?)
        """

        cursor = self.db_manager.conn.execute(query, (today, today))
        columns = [description[0] for description in cursor.description]

        for row in cursor.fetchall():
            recurring = dict(zip(columns, row))

            try:
                # Create the actual transaction
                self.db_manager.add_transaction(
                    date=recurring["next_occurrence"],
                    amount=recurring["amount"],
                    category=recurring["category"],
                    transaction_type=recurring["type"],
                    description=recurring["description"]
                    or f"Recurring: {recurring['category']}",
                )

                # Update next occurrence
                next_occurrence = self._calculate_next_occurrence(
                    recurring["next_occurrence"], recurring["frequency"]
                )

                # Check if we should deactivate (past end_date)
                should_deactivate = False
                if recurring["end_date"]:
                    if next_occurrence > recurring["end_date"]:
                        should_deactivate = True

                update_query = """
                    UPDATE recurring_transactions
                    SET next_occurrence = ?, is_active = ?
                    WHERE id = ?
                """

                self.db_manager.conn.execute(
                    update_query,
                    (
                        next_occurrence,
                        0 if should_deactivate else 1,
                        recurring["id"],
                    ),
                )

                created_count += 1
                logger.info(
                    f"Processed recurring transaction ID {recurring['id']}: "
                    f"Created transaction for {recurring['next_occurrence']}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to process recurring transaction ID {recurring['id']}: {str(e)}"
                )

        self.db_manager.conn.commit()

        if created_count > 0:
            logger.info(f"Processed {created_count} recurring transactions")

        return created_count

    def get_upcoming_transactions(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming recurring transactions for the next N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of upcoming transaction previews
        """
        today = datetime.now()
        end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")

        query = """
            SELECT * FROM recurring_transactions
            WHERE is_active = 1
            AND next_occurrence <= ?
            AND (end_date IS NULL OR end_date >= ?)
            ORDER BY next_occurrence ASC
        """

        cursor = self.db_manager.conn.execute(query, (end_date, today_str))
        columns = [description[0] for description in cursor.description]

        upcoming = []
        for row in cursor.fetchall():
            recurring = dict(zip(columns, row))
            upcoming.append(
                {
                    "id": recurring["id"],
                    "date": recurring["next_occurrence"],
                    "amount": recurring["amount"],
                    "category": recurring["category"],
                    "type": recurring["type"],
                    "description": recurring["description"],
                    "frequency": recurring["frequency"],
                }
            )

        return upcoming

    def _calculate_next_occurrence(self, current_date: str, frequency: str) -> str:
        """
        Calculate the next occurrence date based on frequency.

        Args:
            current_date: Current date (YYYY-MM-DD)
            frequency: Frequency type

        Returns:
            Next occurrence date (YYYY-MM-DD)
        """
        date_obj = datetime.strptime(current_date, "%Y-%m-%d")
        next_date = self.FREQUENCY_MAP[frequency](date_obj)
        return next_date.strftime("%Y-%m-%d")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recurring transactions.

        Returns:
            Dictionary with statistics
        """
        all_recurring = self.get_all_recurring_transactions(active_only=False)
        active_recurring = [r for r in all_recurring if r["is_active"] == 1]

        # Calculate total monthly impact (estimate)
        monthly_income = 0
        monthly_expense = 0

        for recurring in active_recurring:
            amount = recurring["amount"]
            frequency = recurring["frequency"]

            # Convert to monthly equivalent
            if frequency == "daily":
                monthly_equiv = amount * 30
            elif frequency == "weekly":
                monthly_equiv = amount * 4.33
            elif frequency == "monthly":
                monthly_equiv = amount
            elif frequency == "yearly":
                monthly_equiv = amount / 12
            else:
                monthly_equiv = 0

            if monthly_equiv > 0:
                monthly_income += monthly_equiv
            else:
                monthly_expense += abs(monthly_equiv)

        return {
            "total_recurring": len(all_recurring),
            "active_recurring": len(active_recurring),
            "inactive_recurring": len(all_recurring) - len(active_recurring),
            "estimated_monthly_income": round(monthly_income, 2),
            "estimated_monthly_expense": round(monthly_expense, 2),
            "estimated_monthly_net": round(monthly_income - monthly_expense, 2),
        }


def add_months(source_date: datetime, months: int) -> datetime:
    """
    Add months to a date, handling edge cases properly.

    Args:
        source_date: Source datetime
        months: Number of months to add

    Returns:
        New datetime with months added
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(
        source_date.day,
        [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][month - 1],
    )

    return datetime(
        year, month, day, source_date.hour, source_date.minute, source_date.second
    )
