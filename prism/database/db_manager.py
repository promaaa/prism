"""
Database Manager for Prism application.
Provides CRUD operations for transactions, assets, and orders.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date

from .schema import get_database_path
from ..utils.logger import get_logger, log_exception, log_performance, LogContext

# Initialize logger for this module
logger = get_logger("database")


class DatabaseManager:
    """
    Manages all database operations for Prism application.
    Provides methods for CRUD operations on transactions, assets, and orders.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the DatabaseManager.

        Args:
            db_path: Optional custom path to database file.
                    If None, uses default application support directory.
        """
        self.db_path = db_path if db_path else get_database_path()
        logger.info(f"Initializing DatabaseManager with path: {self.db_path}")
        self._ensure_connection()

    def _ensure_connection(self) -> None:
        """Ensure database file exists and is accessible."""
        if not self.db_path.exists():
            logger.info("Database file does not exist, initializing...")
            from .schema import initialize_database

            initialize_database(self.db_path)
            logger.info("Database initialized successfully")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with row factory enabled.

        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    # ==================== TRANSACTIONS ====================

    @log_exception
    @log_performance("add_transaction")
    def add_transaction(
        self,
        date: str,
        amount: float,
        category: str,
        transaction_type: str,
        description: Optional[str] = None,
    ) -> int:
        """
        Add a new transaction to the database.

        Args:
            date: Transaction date in YYYY-MM-DD format
            amount: Transaction amount (positive for revenue, negative for expense)
            category: Transaction category (e.g., "Food", "Salary")
            transaction_type: Type of transaction ("personal" or "investment")
            description: Optional description

        Returns:
            int: ID of the newly created transaction

        Raises:
            ValueError: If transaction_type is not valid
        """
        if transaction_type not in ("personal", "investment"):
            logger.error(f"Invalid transaction_type: {transaction_type}")
            raise ValueError("transaction_type must be 'personal' or 'investment'")

        logger.debug(
            f"Adding transaction: date={date}, amount={amount}, category={category}, type={transaction_type}"
        )

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transactions (date, amount, category, type, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, transaction_type, description),
        )

        transaction_id = cursor.lastrowid
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()

        logger.info(f"Transaction added successfully with ID: {transaction_id}")
        return transaction_id

    def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Optional[Dict]: Transaction data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_all_transactions(
        self,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all transactions with optional filters.

        Args:
            transaction_type: Filter by type ("personal" or "investment")
            category: Filter by category
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)

        Returns:
            List[Dict]: List of transaction dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)

        if category:
            query += " AND category = ?"
            params.append(category)

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        logger.debug(f"Retrieved {len(rows)} transactions")
        return [dict(row) for row in rows]

    def update_transaction(
        self,
        transaction_id: int,
        date: Optional[str] = None,
        amount: Optional[float] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        Update a transaction.

        Args:
            transaction_id: Transaction ID to update
            date: New date (optional)
            amount: New amount (optional)
            category: New category (optional)
            transaction_type: New type (optional)
            description: New description (optional)

        Returns:
            bool: True if update was successful, False otherwise
        """
        if transaction_type and transaction_type not in ("personal", "investment"):
            raise ValueError("transaction_type must be 'personal' or 'investment'")

        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current values
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        current = cursor.fetchone()

        if not current:
            conn.close()
            return False

        # Use new values if provided, otherwise keep current
        new_date = date if date is not None else current["date"]
        new_amount = amount if amount is not None else current["amount"]
        new_category = category if category is not None else current["category"]
        new_type = transaction_type if transaction_type is not None else current["type"]
        new_description = (
            description if description is not None else current["description"]
        )

        cursor.execute(
            """
            UPDATE transactions
            SET date = ?, amount = ?, category = ?, type = ?, description = ?
            WHERE id = ?
            """,
            (
                new_date,
                new_amount,
                new_category,
                new_type,
                new_description,
                transaction_id,
            ),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: Transaction ID to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def search_transactions(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search transactions by description or category.

        Args:
            search_term: Term to search for

        Returns:
            List[Dict]: List of matching transactions
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM transactions
            WHERE category LIKE ? OR description LIKE ?
            ORDER BY date DESC
            """,
            (f"%{search_term}%", f"%{search_term}%"),
        )

        rows = cursor.fetchall()
        conn.close()

        logger.debug(f"Retrieved {len(rows)} assets")
        return [dict(row) for row in rows]

    def get_balance(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> float:
        """
        Calculate total balance from transactions.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            float: Total balance
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT SUM(amount) as total FROM transactions WHERE type = 'personal'"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()

        return result["total"] if result["total"] else 0.0

    def get_category_summary(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get summary of transactions grouped by category.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List[Dict]: List of category summaries with total amounts
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE type = 'personal'
        """
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " GROUP BY category ORDER BY total DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== ASSETS ====================

    def add_asset(
        self,
        ticker: str,
        quantity: float,
        price_buy: float,
        date_buy: str,
        asset_type: str,
        current_price: Optional[float] = None,
    ) -> int:
        """
        Add a new asset to the database.

        Args:
            ticker: Asset ticker symbol (e.g., "BTC", "AAPL")
            quantity: Quantity of units
            price_buy: Purchase price per unit
            date_buy: Purchase date in YYYY-MM-DD format
            asset_type: Type of asset ("crypto", "stock", or "bond")
            current_price: Optional current market price

        Returns:
            int: ID of the newly created asset

        Raises:
            ValueError: If asset_type is not valid
        """
        if asset_type not in ("crypto", "stock", "bond"):
            raise ValueError("asset_type must be 'crypto', 'stock', or 'bond'")

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assets (ticker, quantity, price_buy, date_buy, current_price, asset_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ticker, quantity, price_buy, date_buy, current_price, asset_type),
        )

        asset_id = cursor.lastrowid
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()

        logger.info(f"Order added successfully with ID: {order_id}")
        return order_id
        logger.info(f"Asset added successfully with ID: {asset_id}")
        return asset_id

    def get_asset(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an asset by ID.

        Args:
            asset_id: Asset ID

        Returns:
            Optional[Dict]: Asset data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_all_assets(self, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all assets with optional type filter.

        Args:
            asset_type: Filter by type ("crypto", "stock", or "bond")

        Returns:
            List[Dict]: List of asset dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if asset_type:
            cursor.execute(
                "SELECT * FROM assets WHERE asset_type = ? ORDER BY ticker",
                (asset_type,),
            )
        else:
            cursor.execute("SELECT * FROM assets ORDER BY ticker")

        rows = cursor.fetchall()
        conn.close()

        logger.debug(f"Retrieved {len(rows)} orders")
        return [dict(row) for row in rows]

    def update_asset(
        self,
        asset_id: int,
        ticker: Optional[str] = None,
        quantity: Optional[float] = None,
        price_buy: Optional[float] = None,
        date_buy: Optional[str] = None,
        current_price: Optional[float] = None,
        asset_type: Optional[str] = None,
    ) -> bool:
        """
        Update an asset.

        Args:
            asset_id: Asset ID to update
            ticker: New ticker (optional)
            quantity: New quantity (optional)
            price_buy: New buy price (optional)
            date_buy: New buy date (optional)
            current_price: New current price (optional)
            asset_type: New type (optional)

        Returns:
            bool: True if update was successful, False otherwise
        """
        if asset_type and asset_type not in ("crypto", "stock", "bond"):
            raise ValueError("asset_type must be 'crypto', 'stock', or 'bond'")

        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current values
        cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        current = cursor.fetchone()

        if not current:
            conn.close()
            return False

        # Use new values if provided, otherwise keep current
        new_ticker = ticker if ticker is not None else current["ticker"]
        new_quantity = quantity if quantity is not None else current["quantity"]
        new_price_buy = price_buy if price_buy is not None else current["price_buy"]
        new_date_buy = date_buy if date_buy is not None else current["date_buy"]
        new_current_price = (
            current_price if current_price is not None else current["current_price"]
        )
        new_asset_type = asset_type if asset_type is not None else current["asset_type"]

        cursor.execute(
            """
            UPDATE assets
            SET ticker = ?, quantity = ?, price_buy = ?, date_buy = ?,
                current_price = ?, asset_type = ?
            WHERE id = ?
            """,
            (
                new_ticker,
                new_quantity,
                new_price_buy,
                new_date_buy,
                new_current_price,
                new_asset_type,
                asset_id,
            ),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def update_asset_price(self, asset_id: int, current_price: float) -> bool:
        """
        Update only the current price of an asset.

        Args:
            asset_id: Asset ID
            current_price: New current price

        Returns:
            bool: True if update was successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE assets SET current_price = ? WHERE id = ?",
            (current_price, asset_id),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset.

        Args:
            asset_id: Asset ID to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    @log_exception
    @log_performance("get_portfolio_value")
    def get_portfolio_value(self) -> float:
        """
        Calculate the total portfolio value based on current prices.

        Returns:
            float: Total portfolio value
        """
        logger.debug("Calculating portfolio value")

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT SUM(quantity * COALESCE(current_price, price_buy)) as total
            FROM assets
            """
        )

        result = cursor.fetchone()
        conn.close()

        return result["total"] if result["total"] else 0.0

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio summary with allocation by asset type.

        Returns:
            Dict: Portfolio summary with total value and allocation
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                asset_type,
                SUM(quantity * COALESCE(current_price, price_buy)) as value,
                COUNT(*) as count
            FROM assets
            GROUP BY asset_type
            """
        )

        rows = cursor.fetchall()
        conn.close()

        allocation = [dict(row) for row in rows]
        total_value = sum(item["value"] for item in allocation)

        return {"total_value": total_value, "allocation": allocation}

    def get_asset_performance(self, asset_id: int) -> Dict[str, Any]:
        """
        Calculate performance metrics for an asset.

        Args:
            asset_id: Asset ID

        Returns:
            Dict: Performance metrics (gain/loss, percentage)
        """
        asset = self.get_asset(asset_id)
        if not asset:
            return {}

        current_price = asset["current_price"] or asset["price_buy"]
        total_cost = asset["price_buy"] * asset["quantity"]
        current_value = current_price * asset["quantity"]
        gain_loss = current_value - total_cost
        gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0

        return {
            "asset_id": asset_id,
            "ticker": asset["ticker"],
            "total_cost": total_cost,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_loss_percent": gain_loss_percent,
        }

    # ==================== ORDERS ====================

    @log_exception
    @log_performance("add_order")
    def add_order(
        self,
        ticker: str,
        order_type: str,
        quantity: float,
        price: float,
        order_date: str,
        status: str = "open",
    ) -> int:
        """
        Add a new order to the database.

        Args:
            ticker: Asset ticker symbol
            order_type: Type of order ("buy" or "sell")
            quantity: Quantity to buy/sell
            price: Price per unit
            order_date: Order date in YYYY-MM-DD format
            status: Order status ("open" or "closed")

        Returns:
            int: ID of the newly created order

        Raises:
            ValueError: If order_type or status is not valid
        """
        if order_type not in ("buy", "sell"):
            logger.error(f"Invalid order_type: {order_type}")
            raise ValueError("order_type must be 'buy' or 'sell'")
        if status not in ("open", "closed"):
            logger.error(f"Invalid status: {status}")
            raise ValueError("status must be 'open' or 'closed'")

        logger.debug(
            f"Adding order: ticker={ticker}, type={order_type}, quantity={quantity}, price={price}, status={status}"
        )

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders (ticker, quantity, price, order_type, date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ticker, quantity, price, order_type, date, status),
        )

        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Order ID {order_id} deleted successfully")

        logger.info(f"Order ID {order_id} updated successfully")

        logger.info(f"Asset ID {asset_id} deleted successfully")

        logger.info(f"Asset ID {asset_id} updated successfully")

        return order_id

    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an order by ID.

        Args:
            order_id: Order ID

        Returns:
            Optional[Dict]: Order data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_all_orders(
        self,
        ticker: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all orders with optional filters.

        Args:
            ticker: Filter by ticker
            status: Filter by status ("open" or "closed")
            order_type: Filter by type ("buy" or "sell")

        Returns:
            List[Dict]: List of order dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM orders WHERE 1=1"
        params = []

        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)

        if status:
            query += " AND status = ?"
            params.append(status)

        if order_type:
            query += " AND order_type = ?"
            params.append(order_type)

        query += " ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_order(
        self,
        order_id: int,
        ticker: Optional[str] = None,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        date: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        """
        Update an order.

        Args:
            order_id: Order ID to update
            ticker: New ticker (optional)
            quantity: New quantity (optional)
            price: New price (optional)
            order_type: New type (optional)
            date: New date (optional)
            status: New status (optional)

        Returns:
            bool: True if update was successful, False otherwise
        """
        if order_type and order_type not in ("buy", "sell"):
            raise ValueError("order_type must be 'buy' or 'sell'")

        if status and status not in ("open", "closed"):
            raise ValueError("status must be 'open' or 'closed'")

        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current values
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        current = cursor.fetchone()

        if not current:
            conn.close()
            return False

        # Use new values if provided, otherwise keep current
        new_ticker = ticker if ticker is not None else current["ticker"]
        new_quantity = quantity if quantity is not None else current["quantity"]
        new_price = price if price is not None else current["price"]
        new_order_type = order_type if order_type is not None else current["order_type"]
        new_date = date if date is not None else current["date"]
        new_status = status if status is not None else current["status"]

        cursor.execute(
            """
            UPDATE orders
            SET ticker = ?, quantity = ?, price = ?, order_type = ?, date = ?, status = ?
            WHERE id = ?
            """,
            (
                new_ticker,
                new_quantity,
                new_price,
                new_order_type,
                new_date,
                new_status,
                order_id,
            ),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def close_order(self, order_id: int) -> bool:
        """
        Close an order (set status to 'closed').

        Args:
            order_id: Order ID to close

        Returns:
            bool: True if update was successful, False otherwise
        """
        return self.update_order(order_id, status="closed")

    def delete_order(self, order_id: int) -> bool:
        """
        Delete an order.

        Args:
            order_id: Order ID to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    # ==================== UTILITY METHODS ====================

    @log_exception
    @log_performance("get_database_stats")
    def get_database_stats(self) -> Dict[str, int]:
        """
        Get statistics about the database.

        Returns:
            Dict containing counts of transactions, assets, and orders
        """
        logger.debug("Fetching database statistics")

        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        stats["transactions"] = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM assets")
        stats["assets"] = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM orders")
        stats["orders"] = cursor.fetchone()["count"]

        conn.close()

        logger.debug(f"Database stats: {stats}")
        return stats

    def backup_database(self, backup_path: Path) -> bool:
        """
        Create a backup of the database.

        Args:
            backup_path: Path where backup should be saved

        Returns:
            bool: True if backup was successful
        """
        import shutil

        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def close(self) -> None:
        """
        Close any open connections.
        Note: Connections are closed after each operation, so this is a no-op.
        """
        pass
