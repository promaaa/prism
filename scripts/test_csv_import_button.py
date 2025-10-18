#!/usr/bin/env python3
"""
Test script for CSV import button functionality in Personal Finances tab.

This script tests:
1. CSV import button exists and is clickable
2. Button opens CSV import dialog
3. Dialog can handle BoursoBank CSV format
4. Import process works end-to-end
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.ui.personal_tab import PersonalTab
from prism.database.schema import initialize_database


def test_csv_import_button_exists():
    """Test that CSV import button exists in Personal Finances tab."""
    print("=" * 70)
    print("TEST 1: CSV Import Button Existence")
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

        # Check if the import button exists
        import_btn = getattr(tab, "import_csv_btn", None)
        if import_btn is None:
            print("❌ CSV import button not found in PersonalTab")
            return False

        print("✓ CSV import button found")

        # Check button properties
        if import_btn.text() != "📄 Import CSV":
            print(f"❌ Button text is '{import_btn.text()}', expected '📄 Import CSV'")
            return False

        print("✓ Button has correct text")

        # Check button is enabled
        if not import_btn.isEnabled():
            print("❌ Button is disabled")
            return False

        print("✓ Button is enabled")

        print("\n✓ TEST 1 PASSED: CSV import button exists and is properly configured")
        return True

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_csv_import_dialog_opens():
    """Test that clicking the CSV import button opens the dialog."""
    print("=" * 70)
    print("TEST 2: CSV Import Dialog Opens")
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

        # Get the import button
        import_btn = getattr(tab, "import_csv_btn", None)
        if import_btn is None:
            print("❌ CSV import button not found")
            return False

        # Mock the dialog opening (we can't actually open dialogs in headless mode)
        # Instead, we'll check that the button's clicked signal is connected
        connections = import_btn.receivers(import_btn.clicked)
        if connections == 0:
            print("❌ Button click signal not connected")
            return False

        print("✓ Button click signal is connected")

        # Check that the connected method exists
        if not hasattr(tab, "_on_import_csv"):
            print("❌ _on_import_csv method not found")
            return False

        print("✓ _on_import_csv method exists")

        print("\n✓ TEST 2 PASSED: CSV import dialog setup is correct")
        return True

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_boursobank_csv_sample():
    """Test importing a small sample of BoursoBank CSV data."""
    print("=" * 70)
    print("TEST 3: BoursoBank CSV Sample Import")
    print("=" * 70)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)

        # Create sample BoursoBank CSV content
        sample_csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-10-18;;"LIDL PLOUZANE FR";"Alimentation";"Vie quotidienne";;-11,44;;00040211293;BoursoBank;
2025-10-14;2025-10-14;"CARTE 13/10/25 SNCF-VOYAGEURS CB*4670";"Transports longue distance (avions, trains…)";"Voyages & Transports";sncf;-49,00;;00040211293;BoursoBank;1213.97
2025-10-14;2025-10-14;"VIR INST MARC JULES PAUL DUBOC";"Virements reçus";"Virements reçus";"marc jules paul duboc";841,48;;00040211293;BoursoBank;1213.97"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(sample_csv_content)
            temp_csv = f.name

        try:
            # Import using the CSV importer
            from prism.utils.csv_import import CSVImporter

            importer = CSVImporter(db)

            # Import the sample data
            successful, failed, errors = importer.import_from_csv(
                temp_csv, skip_duplicates=False, default_type="personal"
            )

            print(f"✓ Successfully imported: {successful} transactions")
            if failed > 0:
                print(f"⚠️  Failed: {failed} transactions")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  • {error}")

            # Verify the imported data
            transactions = db.get_all_transactions()
            print(f"✓ Database contains {len(transactions)} transactions")

            # Check specific transactions
            expected_transactions = [
                ("LIDL PLOUZANE FR", -11.44, "Food"),
                ("CARTE 13/10/25 SNCF-VOYAGEURS CB*4670", -49.00, "Transport"),
                ("VIR INST MARC JULES PAUL DUBOC", 841.48, "Income"),
            ]

            found_count = 0
            for trans in transactions:
                description = trans.get("description", "")
                amount = trans.get("amount", 0)
                category = trans.get("category", "")

                for (
                    expected_desc,
                    expected_amount,
                    expected_category,
                ) in expected_transactions:
                    if (
                        expected_desc in description
                        and abs(amount - expected_amount) < 0.01
                        and category == expected_category
                    ):
                        print(
                            f"✓ Found: {expected_desc} ({expected_amount}) -> {expected_category}"
                        )
                        found_count += 1
                        break

            if found_count == len(expected_transactions):
                print("✓ All expected transactions imported correctly")
                print("\n✓ TEST 3 PASSED: BoursoBank CSV sample import works")
                return True
            else:
                print(
                    f"❌ Only found {found_count}/{len(expected_transactions)} expected transactions"
                )
                return False

        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all CSV import button tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "CSV IMPORT BUTTON FUNCTIONALITY TESTS" + " " * 10 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    app = QApplication(sys.argv)

    tests = [
        ("CSV Import Button Existence", test_csv_import_button_exists),
        ("CSV Import Dialog Setup", test_csv_import_dialog_opens),
        ("BoursoBank CSV Sample Import", test_boursobank_csv_sample),
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
        print("\nCSV import button functionality is working correctly:")
        print("  ✓ Button exists in Personal Finances tab")
        print("  ✓ Button is properly configured")
        print("  ✓ Dialog setup is correct")
        print("  ✓ BoursoBank CSV format is supported")
        print("  ✓ Sample data imports successfully")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the failed tests above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
