"""
Database schema definition for Prism application.
Creates and manages SQLite database tables for transactions, assets, and orders.
"""

import sqlite3
from pathlib import Path
from typing import Optional


def get_database_path() -> Path:
    """
    Get the path to the database file.
    Creates the directory if it doesn't exist.

    Returns:
        Path: Path to the database file
    """
    # For macOS, use Application Support directory
    app_support = Path.home() / "Library" / "Application Support" / "Prism"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support / "prism.db"


def initialize_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize the database with required tables.

    Args:
        db_path: Optional custom path to database file.
                If None, uses default application support directory.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('personal', 'investment')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Assets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL,
            price_buy REAL NOT NULL,
            date_buy TEXT NOT NULL,
            current_price REAL,
            asset_type TEXT NOT NULL CHECK(asset_type IN ('crypto', 'stock', 'bond')),
            price_currency TEXT DEFAULT 'EUR' CHECK(price_currency IN ('USD', 'EUR')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date_buy)
        )
    """)

    # Create Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            order_type TEXT NOT NULL CHECK(order_type IN ('buy', 'sell')),
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('open', 'closed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
            color TEXT,
            icon TEXT,
            budget_limit REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Recurring Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('personal', 'investment')),
            description TEXT,
            frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
            start_date TEXT NOT NULL,
            end_date TEXT,
            next_occurrence TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert default categories
    cursor.execute("""
        INSERT OR IGNORE INTO categories (name, type, color, icon) VALUES
        ('Salary', 'income', '#10b981', '💰'),
        ('Investment Income', 'income', '#3b82f6', '📈'),
        ('Bonus', 'income', '#8b5cf6', '🎁'),
        ('Other Income', 'income', '#06b6d4', '💵'),
        ('Food', 'expense', '#ef4444', '🍔'),
        ('Transport', 'expense', '#f59e0b', '🚗'),
        ('Housing', 'expense', '#6366f1', '🏠'),
        ('Entertainment', 'expense', '#ec4899', '🎬'),
        ('Shopping', 'expense', '#14b8a6', '🛍️'),
        ('Healthcare', 'expense', '#f43f5e', '⚕️'),
        ('Education', 'expense', '#8b5cf6', '📚'),
        ('Utilities', 'expense', '#eab308', '⚡'),
        ('Insurance', 'expense', '#06b6d4', '🛡️'),
        ('Other Expense', 'expense', '#6b7280', '📝')
    """)

    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_date
        ON transactions(date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_category
        ON transactions(category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_type
        ON transactions(type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_assets_ticker
        ON assets(ticker)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_assets_type
        ON assets(asset_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_ticker
        ON orders(ticker)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_date
        ON orders(date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_categories_name
        ON categories(name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_categories_type
        ON categories(type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recurring_category
        ON recurring_transactions(category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recurring_next_occurrence
        ON recurring_transactions(next_occurrence)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recurring_active
        ON recurring_transactions(is_active)
    """)

    # Create trigger to update updated_at timestamp for transactions
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
        AFTER UPDATE ON transactions
        FOR EACH ROW
        BEGIN
            UPDATE transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)

    # Create trigger to update updated_at timestamp for assets
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_assets_timestamp
        AFTER UPDATE ON assets
        FOR EACH ROW
        BEGIN
            UPDATE assets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)

    # Create trigger to update updated_at timestamp for orders
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_orders_timestamp
        AFTER UPDATE ON orders
        FOR EACH ROW
        BEGIN
            UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)

    # Create trigger to update updated_at timestamp for categories
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_categories_timestamp
        AFTER UPDATE ON categories
        FOR EACH ROW
        BEGIN
            UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)

    # Create trigger to update updated_at timestamp for recurring_transactions
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_recurring_timestamp
        AFTER UPDATE ON recurring_transactions
        FOR EACH ROW
        BEGIN
            UPDATE recurring_transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)

    conn.commit()
    conn.close()


def drop_all_tables(db_path: Optional[Path] = None) -> None:
    """
    Drop all tables from the database. Use with caution!
    Mainly for testing purposes.

    Args:
        db_path: Optional custom path to database file.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS assets")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute("DROP TABLE IF EXISTS recurring_transactions")

    conn.commit()
    conn.close()


def get_schema_version() -> str:
    """
    Get the current schema version.

    Returns:
        str: Schema version string
    """
    return "1.2.0"


if __name__ == "__main__":
    # Test database creation
    print(f"Creating database at: {get_database_path()}")
    initialize_database()
    print("Database initialized successfully!")
    print(f"Schema version: {get_schema_version()}")
