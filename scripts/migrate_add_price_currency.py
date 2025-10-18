#!/usr/bin/env python3
"""
Database migration script to add price_currency column to assets table.
This allows tracking whether crypto asset purchase prices are in USD or EUR.

Schema change:
- Add 'price_currency' column to assets table
- Default value: 'EUR' (for backward compatibility)
- Check constraint: value must be 'USD' or 'EUR'

Usage:
    python scripts/migrate_add_price_currency.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.schema import get_database_path


def backup_database(db_path: Path) -> Path:
    """
    Create a backup of the database before migration.

    Args:
        db_path: Path to the database file

    Returns:
        Path: Path to the backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"prism_backup_{timestamp}.db"

    # Copy database file
    import shutil

    shutil.copy2(db_path, backup_path)

    print(f"✓ Database backed up to: {backup_path}")
    return backup_path


def check_column_exists(cursor: sqlite3.Cursor) -> bool:
    """
    Check if price_currency column already exists.

    Args:
        cursor: Database cursor

    Returns:
        bool: True if column exists, False otherwise
    """
    cursor.execute("PRAGMA table_info(assets)")
    columns = [row[1] for row in cursor.fetchall()]
    return "price_currency" in columns


def add_price_currency_column(db_path: Path) -> None:
    """
    Add price_currency column to assets table.

    Args:
        db_path: Path to the database file
    """
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if column already exists
        if check_column_exists(cursor):
            print("⚠ Column 'price_currency' already exists in assets table.")
            print("  Migration skipped.")
            conn.close()
            return

        print("Adding 'price_currency' column to assets table...")

        # Add the column with default value 'EUR'
        cursor.execute("""
            ALTER TABLE assets
            ADD COLUMN price_currency TEXT DEFAULT 'EUR'
            CHECK(price_currency IN ('USD', 'EUR'))
        """)

        # Set all existing rows to 'EUR' (for backward compatibility)
        cursor.execute("""
            UPDATE assets
            SET price_currency = 'EUR'
            WHERE price_currency IS NULL
        """)

        conn.commit()
        print("✓ Successfully added 'price_currency' column")

        # Verify the change
        cursor.execute("PRAGMA table_info(assets)")
        columns = cursor.fetchall()

        print("\nUpdated assets table schema:")
        print("-" * 60)
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_notnull = "NOT NULL" if col[3] else "NULL"
            col_default = f"DEFAULT {col[4]}" if col[4] else ""
            print(f"  {col_name:20s} {col_type:10s} {col_notnull:10s} {col_default}")
        print("-" * 60)

        # Show count of assets
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        print(f"\n✓ Migration complete. {count} existing assets set to EUR.")

    except sqlite3.Error as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration(db_path: Path) -> None:
    """
    Verify the migration was successful.

    Args:
        db_path: Path to the database file
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check column exists
        if not check_column_exists(cursor):
            print("✗ Verification failed: Column does not exist")
            return

        # Check all assets have a currency set
        cursor.execute("""
            SELECT COUNT(*) FROM assets
            WHERE price_currency IS NULL OR price_currency = ''
        """)
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            print(f"⚠ Warning: {null_count} assets have NULL/empty price_currency")
        else:
            print("✓ All assets have price_currency set")

        # Show currency distribution
        cursor.execute("""
            SELECT price_currency, COUNT(*) as count
            FROM assets
            GROUP BY price_currency
        """)
        results = cursor.fetchall()

        if results:
            print("\nPrice currency distribution:")
            for currency, count in results:
                print(f"  {currency}: {count} asset(s)")

    except sqlite3.Error as e:
        print(f"✗ Error during verification: {e}")
    finally:
        conn.close()


def main():
    """Main migration function."""
    print("=" * 60)
    print("Prism Database Migration: Add price_currency to assets")
    print("=" * 60)
    print()

    # Get database path
    db_path = get_database_path()

    if not db_path.exists():
        print(f"✗ Database not found at: {db_path}")
        print("  Please run the application first to create the database.")
        sys.exit(1)

    print(f"Database location: {db_path}")
    print()

    # Ask for confirmation
    response = input("Create backup and proceed with migration? [y/N]: ")
    if response.lower() not in ["y", "yes"]:
        print("Migration cancelled.")
        sys.exit(0)

    print()

    # Create backup
    try:
        backup_path = backup_database(db_path)
    except Exception as e:
        print(f"✗ Failed to create backup: {e}")
        sys.exit(1)

    print()

    # Run migration
    try:
        add_price_currency_column(db_path)
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print(f"  Database backup is available at: {backup_path}")
        sys.exit(1)

    print()

    # Verify migration
    verify_migration(db_path)

    print()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. The application now supports USD and EUR purchase prices for crypto")
    print("2. When adding new crypto assets, you can choose the currency")
    print("3. Existing assets will continue to use EUR")
    print("4. Backup is available at:", backup_path)
    print()


if __name__ == "__main__":
    main()
