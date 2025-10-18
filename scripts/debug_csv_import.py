#!/usr/bin/env python3
"""
Debug script for CSV import functionality.
Tests if transactions are actually added to the database and displays them.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.database.db_manager import DatabaseManager
from prism.utils.csv_import import CSVImporter
from prism.database.schema import initialize_database


def debug_csv_import():
    """Debug CSV import by checking database before and after import."""
    print("=" * 80)
    print("DEBUG: CSV Import Functionality")
    print("=" * 80)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)

        print(f"Using temporary database: {db_path}")

        # Check initial state
        print("\n1. INITIAL STATE:")
        initial_transactions = db.get_all_transactions()
        print(f"   Transactions in database: {len(initial_transactions)}")
        for trans in initial_transactions[:3]:  # Show first 3
            print(
                f"   - ID {trans['id']}: {trans['date']} | {trans['amount']} | {trans['category']} | {trans['type']}"
            )

        # Create sample CSV data (similar to BoursoBank format)
        sample_csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-10-18;;"TEST TRANSACTION 1";"Alimentation";"Vie quotidienne";;-25,50;"Test import";00040211293;BoursoBank;1000.00
2025-10-17;2025-10-17;"TEST INCOME";"Virements reçus";"Virements reçus";;500,00;"Test income";00040211293;BoursoBank;1025.50"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(sample_csv_content)
            temp_csv = f.name

        print(f"\n2. SAMPLE CSV CREATED: {temp_csv}")
        print("   Content:")
        with open(temp_csv, "r", encoding="utf-8") as f:
            lines = f.readlines()[:3]  # Show first 3 lines
            for i, line in enumerate(lines, 1):
                print(f"   {i}: {line.strip()}")

        # Import the CSV
        print("\n3. IMPORTING CSV...")
        importer = CSVImporter(db)

        # Check if BoursoBank format is detected
        is_valid, error_msg = importer.validate_csv_file(temp_csv)
        print(f"   File validation: {'✓ PASS' if is_valid else '❌ FAIL'}")
        if not is_valid:
            print(f"   Error: {error_msg}")
            return

        print(f"   BoursoBank format detected: {importer.is_boursobank_format}")

        # Perform import
        successful, failed, errors = importer.import_from_csv(
            temp_csv, skip_duplicates=False, default_type="personal"
        )

        print(f"   Import result: {successful} successful, {failed} failed")
        if errors:
            print("   Errors:")
            for error in errors[:3]:
                print(f"   - {error}")

        # Check final state
        print("\n4. FINAL STATE:")
        final_transactions = db.get_all_transactions()
        print(f"   Transactions in database: {len(final_transactions)}")

        if len(final_transactions) > len(initial_transactions):
            print("   ✓ New transactions were added!")
            new_transactions = final_transactions[len(initial_transactions) :]
            print(f"   New transactions ({len(new_transactions)}):")

            for trans in new_transactions:
                print(
                    f"   - ID {trans['id']}: {trans['date']} | €{trans['amount']:.2f} | {trans['category']} | {trans['type']} | {trans['description'][:50]}..."
                )
        else:
            print("   ❌ No new transactions found!")

        # Check balance calculation
        print("\n5. BALANCE CHECK:")
        balance = db.get_balance()
        print(f"   Calculated balance: €{balance:.2f}")

        # Manual balance calculation
        personal_transactions = [
            t for t in final_transactions if t["type"] == "personal"
        ]
        manual_balance = sum(t["amount"] for t in personal_transactions)
        print(f"   Manual balance: €{manual_balance:.2f}")
        print(
            f"   Balance match: {'✓ YES' if abs(balance - manual_balance) < 0.01 else '❌ NO'}"
        )

        # Clean up
        if os.path.exists(temp_csv):
            os.unlink(temp_csv)

        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)

        if successful > 0 and len(final_transactions) > len(initial_transactions):
            print("\n✅ SUCCESS: CSV import is working correctly!")
            print("   - Transactions are added to database")
            print("   - Balance calculation works")
            print("   - Data types are correct")
        else:
            print("\n❌ FAILURE: CSV import has issues")
            print("   - Check the import logic")
            print("   - Verify database connection")
            print("   - Check transaction types")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def debug_real_csv_import():
    """Debug with the real BoursoBank CSV file."""
    print("=" * 80)
    print("DEBUG: Real BoursoBank CSV Import")
    print("=" * 80)

    # Use the real database
    db = DatabaseManager()

    print("Using real database")

    # Check initial state
    print("\n1. INITIAL STATE:")
    initial_transactions = db.get_all_transactions()
    print(f"   Transactions in database: {len(initial_transactions)}")

    # Use the provided CSV file
    csv_file = "export-operations-18-10-2025_19-25-59.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return

    print(f"\n2. IMPORTING REAL CSV: {csv_file}")

    # Import with the real importer
    importer = CSVImporter(db)

    # Perform import
    successful, failed, errors = importer.import_from_csv(
        csv_file, skip_duplicates=True, default_type="personal"
    )

    print(f"   Import result: {successful} successful, {failed} failed")

    # Check final state
    print("\n3. FINAL STATE:")
    final_transactions = db.get_all_transactions()
    print(f"   Transactions in database: {len(final_transactions)}")

    if len(final_transactions) > len(initial_transactions):
        added = len(final_transactions) - len(initial_transactions)
        print(f"   ✓ Added {added} new transactions")
    else:
        print("   ⚠️  No new transactions added (possible duplicates)")

    # Show recent transactions
    print("\n4. RECENT TRANSACTIONS:")
    recent = sorted(final_transactions, key=lambda x: x["date"], reverse=True)[:5]
    for trans in recent:
        print(
            f"   - {trans['date']} | €{trans['amount']:.2f} | {trans['category']} | {trans['description'][:40]}..."
        )

    print("\n" + "=" * 80)
    print("REAL CSV DEBUG COMPLETE")
    print("=" * 80)


def main():
    """Run debug tests."""
    if len(sys.argv) > 1 and sys.argv[1] == "real":
        debug_real_csv_import()
    else:
        debug_csv_import()


if __name__ == "__main__":
    main()
