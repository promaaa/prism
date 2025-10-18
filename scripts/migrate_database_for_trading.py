#!/usr/bin/env python3
"""
Database migration script to add trading features.

This script adds:
1. New columns to orders table (asset_id, asset_type, price_currency, gain_loss, notes)
2. New portfolio_cash table for tracking cash from sales
3. New indexes for better performance

Run this script to upgrade your existing database to support buy/sell trading operations.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import prism modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.schema import get_database_path
from prism.utils.logger import get_logger

logger = get_logger("migration")


def migrate_database(db_path: Path = None):
    """
    Migrate the database to add trading features.

    Args:
        db_path: Optional path to database file
    """
    if db_path is None:
        db_path = get_database_path()

    logger.info(f"Starting database migration for: {db_path}")

    if not db_path.exists():
        logger.error(f"Database not found at: {db_path}")
        print(f"❌ Database not found at: {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get current schema version
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]

        print("\n📊 Current database schema analysis:")
        print(f"   Orders table columns: {len(columns)}")

        # Check if migration is needed
        needs_migration = False

        if "asset_id" not in columns:
            print("   ⚠️  Missing: asset_id column")
            needs_migration = True
        else:
            print("   ✓ Has: asset_id column")

        if "gain_loss" not in columns:
            print("   ⚠️  Missing: gain_loss column")
            needs_migration = True
        else:
            print("   ✓ Has: gain_loss column")

        # Check if portfolio_cash table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='portfolio_cash'
        """)
        has_cash_table = cursor.fetchone() is not None

        if not has_cash_table:
            print("   ⚠️  Missing: portfolio_cash table")
            needs_migration = True
        else:
            print("   ✓ Has: portfolio_cash table")

        if not needs_migration:
            print("\n✅ Database is already up to date!")
            conn.close()
            return True

        print("\n🔄 Starting migration...")

        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")

        # Step 1: Add new columns to orders table if they don't exist
        if "asset_id" not in columns:
            print("   Adding asset_id column to orders...")
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN asset_id INTEGER
            """)

        if "asset_type" not in columns:
            print("   Adding asset_type column to orders...")
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN asset_type TEXT
            """)

        if "price_currency" not in columns:
            print("   Adding price_currency column to orders...")
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN price_currency TEXT DEFAULT 'EUR'
            """)

        if "gain_loss" not in columns:
            print("   Adding gain_loss column to orders...")
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN gain_loss REAL
            """)

        if "notes" not in columns:
            print("   Adding notes column to orders...")
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN notes TEXT
            """)

        # Step 2: Create portfolio_cash table if it doesn't exist
        if not has_cash_table:
            print("   Creating portfolio_cash table...")
            cursor.execute("""
                CREATE TABLE portfolio_cash (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'EUR' CHECK(currency IN ('USD', 'EUR')),
                    source TEXT,
                    date TEXT NOT NULL,
                    related_order_id INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (related_order_id) REFERENCES orders (id) ON DELETE SET NULL
                )
            """)

            # Create indexes
            print("   Creating indexes for portfolio_cash...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_cash_date
                ON portfolio_cash(date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_cash_currency
                ON portfolio_cash(currency)
            """)

            # Initialize with zero balance
            cursor.execute("""
                INSERT INTO portfolio_cash (id, amount, currency, source, date)
                VALUES (1, 0, 'EUR', 'Initial', date('now'))
            """)

        # Step 3: Create additional indexes for orders if they don't exist
        print("   Creating additional indexes for orders...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_type
            ON orders(order_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_asset_id
            ON orders(asset_id)
        """)

        # Step 4: Migrate existing orders data if any
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]

        if order_count > 0:
            print(f"   Updating {order_count} existing orders...")

            # Set default price_currency for existing orders
            cursor.execute("""
                UPDATE orders
                SET price_currency = 'EUR'
                WHERE price_currency IS NULL
            """)

            # Try to link orders to assets by ticker and date
            cursor.execute("""
                UPDATE orders
                SET asset_id = (
                    SELECT id FROM assets
                    WHERE assets.ticker = orders.ticker
                    LIMIT 1
                )
                WHERE order_type = 'buy' AND asset_id IS NULL
            """)

            # Set asset_type from linked assets
            cursor.execute("""
                UPDATE orders
                SET asset_type = (
                    SELECT asset_type FROM assets
                    WHERE assets.id = orders.asset_id
                )
                WHERE asset_id IS NOT NULL AND asset_type IS NULL
            """)

        # Commit transaction
        conn.commit()

        print("\n✅ Migration completed successfully!")

        # Display summary
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM portfolio_cash")
        cash_count = cursor.fetchone()[0]

        print("\n📊 Database summary after migration:")
        print(f"   Total orders: {order_count}")
        print(f"   Cash transactions: {cash_count}")

        conn.close()
        logger.info("Migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"\n❌ Migration failed: {e}")

        try:
            conn.rollback()
            conn.close()
            print("   Transaction rolled back")
        except:
            pass

        return False


def backup_database(db_path: Path = None):
    """
    Create a backup of the database before migration.

    Args:
        db_path: Optional path to database file
    """
    if db_path is None:
        db_path = get_database_path()

    if not db_path.exists():
        return None

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"

    print(f"📦 Creating backup: {backup_path.name}")

    import shutil

    shutil.copy2(db_path, backup_path)

    print(f"✅ Backup created successfully")
    logger.info(f"Database backup created at: {backup_path}")

    return backup_path


if __name__ == "__main__":
    print("=" * 70)
    print("🔧 PRISM Database Migration - Trading Features")
    print("=" * 70)

    # Get database path
    db_path = get_database_path()
    print(f"\n📍 Database location: {db_path}")

    # Ask for confirmation
    response = input("\n⚠️  This will modify your database. Continue? (yes/no): ")

    if response.lower() not in ["yes", "y"]:
        print("❌ Migration cancelled")
        sys.exit(0)

    # Create backup
    backup_path = backup_database(db_path)
    if backup_path:
        print(f"   Backup saved to: {backup_path.name}")

    # Run migration
    success = migrate_database(db_path)

    if success:
        print("\n" + "=" * 70)
        print("🎉 Migration completed successfully!")
        print("=" * 70)
        print("\nYou can now use the new trading features:")
        print("  • Buy and sell assets")
        print("  • Track cash from sales")
        print("  • View complete transaction history")
        print("  • Analyze wealth evolution including cash")
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ Migration failed")
        print("=" * 70)
        if backup_path:
            print(f"\nYour original database is backed up at:")
            print(f"  {backup_path}")
        sys.exit(1)
