#!/usr/bin/env python3
"""
Simple test to add a transaction and verify UI refresh.
Tests that PersonalTab properly displays transactions and updates balance.
"""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.ui.personal_tab import PersonalTab
from prism.database.schema import initialize_database


def test_simple_transaction_add_and_ui_refresh():
    """Test adding a transaction and verifying UI refresh."""
    print("=" * 60)
    print("SIMPLE TRANSACTION ADD & UI REFRESH TEST")
    print("=" * 60)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)

        print(f"Using temporary database: {db_path}")

        # Create the Personal Finances tab
        app = QApplication(sys.argv)
        tab = PersonalTab(db)

        # Check initial state
        print("\n1. INITIAL STATE:")
        initial_count = tab.transaction_table.rowCount()
        print(f"   Table rows: {initial_count}")

        # Get initial balance card value
        balance_label = tab.balance_card.findChild(type(None), "card_value")
        initial_balance = balance_label.text() if balance_label else "€0.00"
        print(f"   Balance display: {initial_balance}")

        # Add a test transaction directly to database
        print("\n2. ADDING TEST TRANSACTION...")
        transaction_id = db.add_transaction(
            date="2025-10-20",
            amount=123.45,
            category="Test Category",
            transaction_type="personal",
            description="Test transaction for UI refresh",
        )
        print(f"   Added transaction ID: {transaction_id}")

        # Manually refresh the UI (simulate what _load_data does)
        print("\n3. REFRESHING UI...")
        tab._load_data()

        # Check final state
        print("\n4. FINAL STATE:")
        final_count = tab.transaction_table.rowCount()
        print(f"   Table rows: {final_count}")

        # Get final balance card value
        final_balance = balance_label.text() if balance_label else "€0.00"
        print(f"   Balance display: {final_balance}")

        # Check if transaction appears in table
        print("\n5. VERIFYING TRANSACTION IN TABLE:")
        found_transaction = False
        for row in range(final_count):
            # Check description column (index 4)
            desc_item = tab.transaction_table.item(row, 4)
            if desc_item and "Test transaction for UI refresh" in desc_item.text():
                found_transaction = True
                print("   ✓ Transaction found in table")

                # Check amount column (index 1)
                amount_item = tab.transaction_table.item(row, 1)
                if amount_item and "€123.45" in amount_item.text():
                    print("   ✓ Amount displayed correctly")
                else:
                    print(
                        f"   ⚠️  Amount display: {amount_item.text() if amount_item else 'None'}"
                    )

                # Check category column (index 2)
                cat_item = tab.transaction_table.item(row, 2)
                if cat_item and "Test Category" in cat_item.text():
                    print("   ✓ Category displayed correctly")
                else:
                    print(
                        f"   ⚠️  Category display: {cat_item.text() if cat_item else 'None'}"
                    )

                break

        if not found_transaction:
            print("   ❌ Transaction not found in table")
            # Debug: show all table contents
            print("   Table contents:")
            for row in range(final_count):
                desc = tab.transaction_table.item(row, 4)
                desc_text = desc.text() if desc else "None"
                print(f"     Row {row}: {desc_text}")

        # Verify balance update
        print("\n6. VERIFYING BALANCE UPDATE:")
        if final_balance != initial_balance:
            print(f"   ✓ Balance updated: {initial_balance} → {final_balance}")
        else:
            print(f"   ⚠️  Balance not updated: {final_balance}")

        # Summary
        print("\n" + "=" * 60)
        success = found_transaction and final_count > initial_count
        if success:
            print("✅ SUCCESS: Transaction added and UI refreshed correctly")
        else:
            print("❌ FAILURE: Transaction not displayed in UI")
        print("=" * 60)

        return success

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_csv_import_flow():
    """Test the complete CSV import flow."""
    print("\n" + "=" * 60)
    print("CSV IMPORT FLOW TEST")
    print("=" * 60)

    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create sample CSV content
        csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-10-20;2025-10-20;"CSV TEST";"Alimentation";"Vie quotidienne";;-67,89;"Test CSV import";000123;TestBank;1000.00"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            csv_file = f.name

        print(f"Created test CSV: {csv_file}")

        # Import using CSV importer
        from prism.utils.csv_import import CSVImporter

        importer = CSVImporter(db)

        successful, failed, errors = importer.import_from_csv(
            csv_file, skip_duplicates=False, default_type="personal"
        )

        print(f"Import result: {successful} successful, {failed} failed")

        # Create UI and check if transaction appears
        app = QApplication(sys.argv)
        tab = PersonalTab(db)

        # Refresh UI
        tab._load_data()

        # Check if CSV transaction appears
        found_csv_transaction = False
        for row in range(tab.transaction_table.rowCount()):
            desc_item = tab.transaction_table.item(row, 4)
            if desc_item and "CSV TEST" in desc_item.text():
                found_csv_transaction = True
                amount_item = tab.transaction_table.item(row, 1)
                amount_text = amount_item.text() if amount_item else "None"
                print(f"✓ CSV transaction found: {amount_text}")
                break

        if not found_csv_transaction:
            print("❌ CSV transaction not found in UI")

        # Clean up
        if os.path.exists(csv_file):
            os.unlink(csv_file)

        return found_csv_transaction

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run tests."""
    print("Testing transaction addition and UI refresh...\n")

    test1_result = test_simple_transaction_add_and_ui_refresh()
    test2_result = test_csv_import_flow()

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Simple transaction test: {'✓ PASS' if test1_result else '❌ FAIL'}")
    print(f"CSV import flow test: {'✓ PASS' if test2_result else '❌ FAIL'}")

    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("UI refresh is working correctly.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("UI refresh may have issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
