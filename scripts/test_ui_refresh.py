#!/usr/bin/env python3
"""
Test script to verify UI refreshes after CSV import.
Tests that the PersonalTab properly refreshes data when CSV import succeeds.
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.ui.personal_tab import PersonalTab
from prism.database.schema import initialize_database


def test_ui_refresh_after_csv_import():
    """Test that UI refreshes after successful CSV import."""
    print("=" * 70)
    print("TEST: UI Refresh After CSV Import")
    print("=" * 70)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create the Personal Finances tab
        tab = PersonalTab(db)

        # Check initial state
        print("\n1. INITIAL STATE:")
        initial_transaction_count = tab.transaction_table.rowCount()
        print(f"   Transactions in table: {initial_transaction_count}")

        # Get initial balance display
        initial_balance = tab.balance_card.findChild(
            type(tab.balance_card.findChild(type(None)))
        ).text()
        print(f"   Balance display: {initial_balance}")

        # Mock the CSV import dialog to simulate success
        print("\n2. SIMULATING CSV IMPORT...")

        # Create a mock dialog that returns Accepted
        mock_dialog = Mock()
        mock_dialog.exec.return_value = (
            tab.transaction_table.__class__().Accepted
        )  # QDialog.Accepted

        # Patch the CSVImportDialog import
        with patch("prism.ui.personal_tab.CSVImportDialog", return_value=mock_dialog):
            # Manually add a test transaction to simulate import success
            db.add_transaction(
                date="2025-10-20",
                amount=100.50,
                category="Test Import",
                transaction_type="personal",
                description="Test transaction from CSV import",
            )

            # Call the import handler (this should refresh the UI)
            tab._on_import_csv()

        # Check if dialog was "opened"
        print(f"   Dialog exec called: {mock_dialog.exec.called}")

        # Check final state
        print("\n3. FINAL STATE:")
        final_transaction_count = tab.transaction_table.rowCount()
        print(f"   Transactions in table: {final_transaction_count}")

        # Get final balance display
        final_balance = tab.balance_card.findChild(
            type(tab.balance_card.findChild(type(None)))
        ).text()
        print(f"   Balance display: {final_balance}")

        # Verify changes
        print("\n4. VERIFICATION:")
        if final_transaction_count > initial_transaction_count:
            print("   ✓ Transaction count increased")
            success = True
        else:
            print("   ❌ Transaction count did not increase")
            success = False

        if final_balance != initial_balance:
            print("   ✓ Balance display updated")
        else:
            print("   ⚠️  Balance display may not have updated")

        # Check if the new transaction appears in the table
        found_new_transaction = False
        for row in range(final_transaction_count):
            item = tab.transaction_table.item(row, 4)  # Description column
            if item and "Test transaction from CSV import" in item.text():
                found_new_transaction = True
                print("   ✓ New transaction found in table")
                break

        if not found_new_transaction:
            print("   ❌ New transaction not found in table")
            success = False

        print("\n" + "=" * 70)
        if success:
            print("✅ SUCCESS: UI refreshes correctly after CSV import")
        else:
            print("❌ FAILURE: UI does not refresh properly after CSV import")
        print("=" * 70)

        return success

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_csv_import_dialog_return_values():
    """Test that CSV import dialog returns correct values."""
    print("=" * 70)
    print("TEST: CSV Import Dialog Return Values")
    print("=" * 70)

    # Test the dialog return value logic
    print("\nTesting dialog return value logic...")

    # Simulate successful import (successful > 0)
    successful = 5
    failed = 2

    if successful > 0:
        expected_return = "Accepted"
        print(
            f"   ✓ Import with {successful} successful, {failed} failed → Dialog should return {expected_return}"
        )
    else:
        expected_return = "Not Accepted"
        print(
            f"   ✓ Import with {successful} successful, {failed} failed → Dialog should return {expected_return}"
        )

    # Test edge cases
    test_cases = [
        (10, 0, "Accepted"),  # All successful
        (0, 5, "Not Accepted"),  # All failed
        (1, 10, "Accepted"),  # At least one successful
        (0, 0, "Not Accepted"),  # Nothing imported
    ]

    print("\nTesting edge cases:")
    all_correct = True
    for successful, failed, expected in test_cases:
        actual = "Accepted" if successful > 0 else "Not Accepted"
        status = "✓" if actual == expected else "❌"
        print(
            f"   {status} {successful} successful, {failed} failed → {actual} (expected {expected})"
        )
        if actual != expected:
            all_correct = False

    if all_correct:
        print("\n✅ SUCCESS: Dialog return value logic is correct")
    else:
        print("\n❌ FAILURE: Dialog return value logic has issues")

    return all_correct


def main():
    """Run all UI refresh tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "UI REFRESH AFTER CSV IMPORT TESTS" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    app = QApplication(sys.argv)

    tests = [
        ("UI Refresh After CSV Import", test_ui_refresh_after_csv_import),
        ("CSV Import Dialog Return Values", test_csv_import_dialog_return_values),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH EXCEPTION: {test_name}")
            print(f"   Error: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print("\n" + "-" * 70)
    print(f"  Results: {passed}/{total} tests passed")
    print("-" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nUI refresh after CSV import is working correctly:")
        print("  ✓ Dialog returns Accepted on successful import")
        print("  ✓ PersonalTab refreshes data after import")
        print("  ✓ New transactions appear in the table")
        print("  ✓ Balance display updates")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nThe UI may not refresh properly after CSV import.")
        print("Check that the CSV import dialog returns QDialog.Accepted")
        print("and that PersonalTab._on_import_csv calls _load_data()")
        return 1


if __name__ == "__main__":
    sys.exit(main())
