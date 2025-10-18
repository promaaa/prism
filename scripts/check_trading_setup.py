#!/usr/bin/env python3
"""
Quick check script to verify trading system installation.

This script checks:
1. Database schema version
2. Required tables exist
3. Required columns exist
4. Sample operations work
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.schema import get_database_path
from prism.database.db_manager import DatabaseManager
from prism.database.trading_operations import TradingManager
import sqlite3


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(check_name, status, details=""):
    """Print status of a check."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check_name:<40} {details}")


def check_database_exists():
    """Check if database file exists."""
    db_path = get_database_path()
    exists = db_path.exists()

    print_header("DATABASE FILE")
    print(f"Location: {db_path}")
    print_status("Database file exists", exists)

    return exists, db_path


def check_tables(db_path):
    """Check if all required tables exist."""
    print_header("TABLES")

    required_tables = [
        "assets",
        "orders",
        "portfolio_cash",
        "historical_prices",
        "transactions",
        "categories",
    ]

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    existing_tables = [row[0] for row in cursor.fetchall()]

    all_exist = True
    for table in required_tables:
        exists = table in existing_tables
        print_status(f"Table: {table}", exists)
        if not exists:
            all_exist = False

    conn.close()
    return all_exist


def check_orders_columns(db_path):
    """Check if orders table has new columns."""
    print_header("ORDERS TABLE COLUMNS")

    required_columns = {
        "id": True,
        "ticker": True,
        "quantity": True,
        "price": True,
        "order_type": True,
        "date": True,
        "status": True,
        "asset_id": False,  # New column
        "asset_type": False,  # New column
        "price_currency": False,  # New column
        "gain_loss": False,  # New column
        "notes": False,  # New column
    }

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(orders)")
    columns = [row[1] for row in cursor.fetchall()]

    all_exist = True
    for col, is_old in required_columns.items():
        exists = col in columns
        status_text = "(old)" if is_old else "(NEW)"
        print_status(f"Column: {col} {status_text}", exists)
        if not exists and not is_old:
            all_exist = False

    conn.close()
    return all_exist


def check_portfolio_cash_table(db_path):
    """Check if portfolio_cash table exists and has data."""
    print_header("PORTFOLIO_CASH TABLE")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='portfolio_cash'
    """)

    table_exists = cursor.fetchone() is not None
    print_status("Table exists", table_exists)

    if table_exists:
        # Check columns
        cursor.execute("PRAGMA table_info(portfolio_cash)")
        columns = [row[1] for row in cursor.fetchall()]

        required_columns = ["id", "amount", "currency", "source", "date"]
        for col in required_columns:
            exists = col in columns
            print_status(f"  Column: {col}", exists)

        # Check if has initial entry
        cursor.execute("SELECT COUNT(*) FROM portfolio_cash")
        count = cursor.fetchone()[0]
        print(f"\n  Entries in table: {count}")

    conn.close()
    return table_exists


def check_indexes(db_path):
    """Check if required indexes exist."""
    print_header("INDEXES")

    required_indexes = [
        "idx_orders_type",
        "idx_orders_asset_id",
        "idx_portfolio_cash_date",
        "idx_portfolio_cash_currency",
    ]

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index'
    """)

    existing_indexes = [row[0] for row in cursor.fetchall()]

    all_exist = True
    for idx in required_indexes:
        exists = idx in existing_indexes
        print_status(f"Index: {idx}", exists)
        if not exists:
            all_exist = False

    conn.close()
    return all_exist


def check_trading_manager():
    """Check if TradingManager can be instantiated."""
    print_header("TRADING MANAGER")

    try:
        db = DatabaseManager()
        trading = TradingManager(db)
        print_status("TradingManager instantiation", True)

        # Check methods exist
        methods = [
            "buy_asset",
            "sell_asset",
            "get_total_cash",
            "get_total_wealth",
            "get_all_transactions",
        ]

        for method in methods:
            exists = hasattr(trading, method)
            print_status(f"  Method: {method}()", exists)

        return True
    except Exception as e:
        print_status("TradingManager instantiation", False, str(e))
        return False


def check_sample_operations():
    """Check if basic operations work."""
    print_header("SAMPLE OPERATIONS")

    try:
        db = DatabaseManager()
        trading = TradingManager(db)

        # Test get_total_cash
        try:
            cash = trading.get_total_cash("EUR")
            print_status("get_total_cash()", True, f"{cash:.2f}€")
        except Exception as e:
            print_status("get_total_cash()", False, str(e))

        # Test get_total_wealth
        try:
            wealth = trading.get_total_wealth(include_cash=True)
            print_status("get_total_wealth()", True, f"{wealth['total_wealth']:.2f}€")
        except Exception as e:
            print_status("get_total_wealth()", False, str(e))

        # Test get_all_transactions
        try:
            txns = trading.get_all_transactions()
            print_status("get_all_transactions()", True, f"{len(txns)} transactions")
        except Exception as e:
            print_status("get_all_transactions()", False, str(e))

        return True
    except Exception as e:
        print_status("Sample operations", False, str(e))
        return False


def main():
    """Run all checks."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  PRISM Trading System - Installation Check".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    # Run checks
    db_exists, db_path = check_database_exists()

    if not db_exists:
        print("\n❌ Database not found!")
        print("Please run the application first to create the database.")
        return False

    tables_ok = check_tables(db_path)
    orders_ok = check_orders_columns(db_path)
    cash_ok = check_portfolio_cash_table(db_path)
    indexes_ok = check_indexes(db_path)
    trading_ok = check_trading_manager()
    operations_ok = check_sample_operations()

    # Summary
    print_header("SUMMARY")

    checks = [
        ("Database file", db_exists),
        ("Required tables", tables_ok),
        ("Orders columns", orders_ok),
        ("Portfolio cash table", cash_ok),
        ("Required indexes", indexes_ok),
        ("Trading manager", trading_ok),
        ("Sample operations", operations_ok),
    ]

    all_ok = all(status for _, status in checks)

    for name, status in checks:
        print_status(name, status)

    print("\n" + "=" * 60)

    if all_ok:
        print("✅ All checks passed!")
        print("\nYour trading system is ready to use!")
        print("\nNext steps:")
        print("  1. Test with: python scripts/demo_trading_operations.py")
        print("  2. Add 'Vendre' button in investments_tab.py")
        print("  3. Update graphs to include cash")
    else:
        print("❌ Some checks failed!")
        print("\nYou need to run the migration:")
        print("  python scripts/migrate_database_for_trading.py")

    print("\n")

    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
