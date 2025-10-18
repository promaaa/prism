"""
Unit tests for database operations.
Tests CRUD operations for transactions, assets, and orders.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager
from database.schema import initialize_database


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = Path(temp_file.name)
    temp_file.close()

    # Initialize database
    initialize_database(db_path)

    # Create database manager
    db = DatabaseManager(db_path)

    yield db

    # Cleanup
    db_path.unlink()


class TestTransactions:
    """Test transaction operations."""

    def test_add_transaction(self, test_db):
        """Test adding a transaction."""
        transaction_id = test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
            description="Groceries",
        )

        assert transaction_id > 0

        # Verify transaction was added
        transaction = test_db.get_transaction(transaction_id)
        assert transaction is not None
        assert transaction["amount"] == -50.0
        assert transaction["category"] == "Food"
        assert transaction["type"] == "personal"

    def test_get_all_transactions(self, test_db):
        """Test getting all transactions."""
        # Add multiple transactions
        test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-16",
            amount=3000.0,
            category="Salary",
            transaction_type="personal",
        )

        transactions = test_db.get_all_transactions()
        assert len(transactions) == 2

    def test_filter_transactions_by_type(self, test_db):
        """Test filtering transactions by type."""
        test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-16",
            amount=-1000.0,
            category="Investment",
            transaction_type="investment",
        )

        personal = test_db.get_all_transactions(transaction_type="personal")
        assert len(personal) == 1
        assert personal[0]["type"] == "personal"

        investment = test_db.get_all_transactions(transaction_type="investment")
        assert len(investment) == 1
        assert investment[0]["type"] == "investment"

    def test_update_transaction(self, test_db):
        """Test updating a transaction."""
        transaction_id = test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )

        # Update amount
        success = test_db.update_transaction(transaction_id, amount=-75.0)
        assert success

        # Verify update
        transaction = test_db.get_transaction(transaction_id)
        assert transaction["amount"] == -75.0

    def test_delete_transaction(self, test_db):
        """Test deleting a transaction."""
        transaction_id = test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )

        # Delete
        success = test_db.delete_transaction(transaction_id)
        assert success

        # Verify deletion
        transaction = test_db.get_transaction(transaction_id)
        assert transaction is None

    def test_search_transactions(self, test_db):
        """Test searching transactions."""
        test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
            description="Supermarket groceries",
        )
        test_db.add_transaction(
            date="2024-01-16",
            amount=-30.0,
            category="Transport",
            transaction_type="personal",
            description="Gas station",
        )

        # Search by description
        results = test_db.search_transactions("groceries")
        assert len(results) == 1
        assert "groceries" in results[0]["description"].lower()

    def test_get_balance(self, test_db):
        """Test balance calculation."""
        test_db.add_transaction(
            date="2024-01-15",
            amount=3000.0,
            category="Salary",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-16",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-17",
            amount=-30.0,
            category="Transport",
            transaction_type="personal",
        )

        balance = test_db.get_balance()
        assert balance == 2920.0

    def test_get_category_summary(self, test_db):
        """Test category summary."""
        test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-16",
            amount=-75.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_transaction(
            date="2024-01-17",
            amount=-30.0,
            category="Transport",
            transaction_type="personal",
        )

        summary = test_db.get_category_summary()
        assert len(summary) == 2

        # Food should have total of -125 (negative for expenses)
        food_summary = next(s for s in summary if s["category"] == "Food")
        assert food_summary["total"] == -125.0
        assert food_summary["count"] == 2


class TestAssets:
    """Test asset operations."""

    def test_add_asset(self, test_db):
        """Test adding an asset."""
        asset_id = test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
            current_price=52000.0,
        )

        assert asset_id > 0

        # Verify asset was added
        asset = test_db.get_asset(asset_id)
        assert asset is not None
        assert asset["ticker"] == "BTC"
        assert asset["quantity"] == 0.5
        assert asset["asset_type"] == "crypto"

    def test_get_all_assets(self, test_db):
        """Test getting all assets."""
        test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )
        test_db.add_asset(
            ticker="AAPL",
            quantity=10.0,
            price_buy=150.0,
            date_buy="2024-01-16",
            asset_type="stock",
        )

        assets = test_db.get_all_assets()
        assert len(assets) == 2

    def test_filter_assets_by_type(self, test_db):
        """Test filtering assets by type."""
        test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )
        test_db.add_asset(
            ticker="AAPL",
            quantity=10.0,
            price_buy=150.0,
            date_buy="2024-01-16",
            asset_type="stock",
        )

        crypto_assets = test_db.get_all_assets(asset_type="crypto")
        assert len(crypto_assets) == 1
        assert crypto_assets[0]["asset_type"] == "crypto"

    def test_update_asset(self, test_db):
        """Test updating an asset."""
        asset_id = test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )

        # Update quantity
        success = test_db.update_asset(asset_id, quantity=0.75)
        assert success

        # Verify update
        asset = test_db.get_asset(asset_id)
        assert asset["quantity"] == 0.75

    def test_update_asset_price(self, test_db):
        """Test updating asset price."""
        asset_id = test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )

        # Update price
        success = test_db.update_asset_price(asset_id, 55000.0)
        assert success

        # Verify update
        asset = test_db.get_asset(asset_id)
        assert asset["current_price"] == 55000.0

    def test_delete_asset(self, test_db):
        """Test deleting an asset."""
        asset_id = test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )

        # Delete
        success = test_db.delete_asset(asset_id)
        assert success

        # Verify deletion
        asset = test_db.get_asset(asset_id)
        assert asset is None

    def test_get_portfolio_value(self, test_db):
        """Test portfolio value calculation."""
        test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
            current_price=52000.0,
        )
        test_db.add_asset(
            ticker="ETH",
            quantity=2.0,
            price_buy=3000.0,
            date_buy="2024-01-16",
            asset_type="crypto",
            current_price=3200.0,
        )

        portfolio_value = test_db.get_portfolio_value()
        expected_value = (0.5 * 52000.0) + (2.0 * 3200.0)
        assert portfolio_value == expected_value

    def test_get_portfolio_summary(self, test_db):
        """Test portfolio summary."""
        test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
            current_price=52000.0,
        )
        test_db.add_asset(
            ticker="AAPL",
            quantity=10.0,
            price_buy=150.0,
            date_buy="2024-01-16",
            asset_type="stock",
            current_price=160.0,
        )

        summary = test_db.get_portfolio_summary()
        assert "total_value" in summary
        assert "allocation" in summary
        assert len(summary["allocation"]) == 2

    def test_get_asset_performance(self, test_db):
        """Test asset performance calculation."""
        asset_id = test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
            current_price=55000.0,
        )

        performance = test_db.get_asset_performance(asset_id)
        assert performance["total_cost"] == 25000.0
        assert performance["current_value"] == 27500.0
        assert performance["gain_loss"] == 2500.0
        assert performance["gain_loss_percent"] == 10.0


class TestOrders:
    """Test order operations."""

    def test_add_order(self, test_db):
        """Test adding an order."""
        order_id = test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
            status="open",
        )

        assert order_id > 0

        # Verify order was added
        order = test_db.get_order(order_id)
        assert order is not None
        assert order["ticker"] == "BTC"
        assert order["order_type"] == "buy"
        assert order["status"] == "open"

    def test_get_all_orders(self, test_db):
        """Test getting all orders."""
        test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
        )
        test_db.add_order(
            ticker="ETH",
            quantity=2.0,
            price=3000.0,
            order_type="buy",
            date="2024-01-16",
        )

        orders = test_db.get_all_orders()
        assert len(orders) == 2

    def test_filter_orders_by_status(self, test_db):
        """Test filtering orders by status."""
        test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
            status="open",
        )
        test_db.add_order(
            ticker="ETH",
            quantity=2.0,
            price=3000.0,
            order_type="buy",
            date="2024-01-16",
            status="closed",
        )

        open_orders = test_db.get_all_orders(status="open")
        assert len(open_orders) == 1
        assert open_orders[0]["status"] == "open"

    def test_update_order(self, test_db):
        """Test updating an order."""
        order_id = test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
        )

        # Update quantity
        success = test_db.update_order(order_id, quantity=0.75)
        assert success

        # Verify update
        order = test_db.get_order(order_id)
        assert order["quantity"] == 0.75

    def test_close_order(self, test_db):
        """Test closing an order."""
        order_id = test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
            status="open",
        )

        # Close order
        success = test_db.close_order(order_id)
        assert success

        # Verify status change
        order = test_db.get_order(order_id)
        assert order["status"] == "closed"

    def test_delete_order(self, test_db):
        """Test deleting an order."""
        order_id = test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
        )

        # Delete
        success = test_db.delete_order(order_id)
        assert success

        # Verify deletion
        order = test_db.get_order(order_id)
        assert order is None


class TestDatabaseStats:
    """Test database statistics."""

    def test_get_database_stats(self, test_db):
        """Test database statistics."""
        # Add some data
        test_db.add_transaction(
            date="2024-01-15",
            amount=-50.0,
            category="Food",
            transaction_type="personal",
        )
        test_db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=50000.0,
            date_buy="2024-01-15",
            asset_type="crypto",
        )
        test_db.add_order(
            ticker="BTC",
            quantity=0.5,
            price=50000.0,
            order_type="buy",
            date="2024-01-15",
        )

        stats = test_db.get_database_stats()
        assert stats["transactions"] == 1
        assert stats["assets"] == 1
        assert stats["orders"] == 1


class TestValidation:
    """Test input validation."""

    def test_invalid_transaction_type(self, test_db):
        """Test that invalid transaction type raises error."""
        with pytest.raises(ValueError):
            test_db.add_transaction(
                date="2024-01-15",
                amount=-50.0,
                category="Food",
                transaction_type="invalid",
            )

    def test_invalid_asset_type(self, test_db):
        """Test that invalid asset type raises error."""
        with pytest.raises(ValueError):
            test_db.add_asset(
                ticker="BTC",
                quantity=0.5,
                price_buy=50000.0,
                date_buy="2024-01-15",
                asset_type="invalid",
            )

    def test_invalid_order_type(self, test_db):
        """Test that invalid order type raises error."""
        with pytest.raises(ValueError):
            test_db.add_order(
                ticker="BTC",
                quantity=0.5,
                price=50000.0,
                order_type="invalid",
                date="2024-01-15",
            )
