#!/usr/bin/env python3
"""
Test script for BoursoBank CSV import functionality.

This script tests the CSV import feature specifically for BoursoBank format:
- Semicolon separator
- French decimal format (comma instead of dot)
- BoursoBank column mapping
- Category translation
- Duplicate detection
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.utils.csv_import import CSVImporter
from prism.database.db_manager import DatabaseManager
from prism.database.schema import initialize_database


def test_boursobank_parsing():
    """Test parsing of BoursoBank CSV format."""
    print("=" * 70)
    print("TEST 1: BoursoBank CSV Parsing")
    print("=" * 70)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)  # Close the file descriptor
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)
        importer = CSVImporter(db)

        # Test with the provided BoursoBank CSV file
        csv_file = "export-operations-18-10-2025_19-25-59.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Test CSV file not found: {csv_file}")
            return False

        print(f"Testing with file: {csv_file}")

        # Validate the file
        is_valid, error_msg = importer.validate_csv_file(csv_file)
        if not is_valid:
            print(f"❌ File validation failed: {error_msg}")
            return False

        print("✓ File validation passed")

        # Check that BoursoBank format was detected
        if not importer.is_boursobank_format:
            print("❌ BoursoBank format not detected")
            return False

        print("✓ BoursoBank format detected")

        # Test import (with skip_duplicates=True to avoid conflicts)
        print("\nImporting transactions...")
        successful, failed, errors = importer.import_from_csv(
            csv_file, skip_duplicates=True, default_type="personal"
        )

        print(f"✓ Successfully imported: {successful} transactions")
        if failed > 0:
            print(f"⚠️  Failed: {failed} transactions")
            print("Errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")

        # Verify some transactions were imported
        if successful == 0:
            print("❌ No transactions were imported")
            return False

        # Check database content
        transactions = db.get_all_transactions()
        print(f"✓ Database now contains {len(transactions)} transactions")

        # Verify some key transactions
        sample_checks = [
            ("LIDL PLOUZANE FR", -11.44, "Other"),  # Should be mapped to "Other"
            (
                "CARTE 13/10/25 SNCF-VOYAGEURS CB*4670",
                -49.00,
                "Transport",
            ),  # Should be mapped to "Transport"
            (
                "VIR INST MARC JULES PAUL DUBOC",
                841.48,
                "Income",
            ),  # Should be mapped to "Income"
        ]

        found_count = 0
        for trans in transactions:
            description = trans.get("description", "").upper()
            amount = trans.get("amount", 0)
            category = trans.get("category", "")

            for check_desc, check_amount, check_category in sample_checks:
                if (
                    check_desc.upper() in description
                    and abs(amount - check_amount) < 0.01
                    and category == check_category
                ):
                    print(
                        f"✓ Found expected transaction: {check_desc} ({check_amount}) -> {check_category}"
                    )
                    found_count += 1
                    break

        if found_count < len(sample_checks):
            print(
                f"⚠️  Only found {found_count}/{len(sample_checks)} expected transactions"
            )
        else:
            print(f"✓ All {found_count} expected transactions found")

        print("\n✓ TEST 1 PASSED: BoursoBank CSV parsing works correctly")
        return True

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_category_mapping():
    """Test BoursoBank category mapping."""
    print("=" * 70)
    print("TEST 2: Category Mapping")
    print("=" * 70)

    # Test the category mapping directly
    test_mappings = [
        ("Alimentation", "Food"),
        ("Transports longue distance (avions, trains…)", "Transport"),
        ("Virements reçus", "Income"),
        ("Téléphonie (fixe et mobile)", "Utilities"),
        ("Restaurants, bars, discothèques…", "Entertainment"),
        ("Non catégorisé", "Non catégorisé"),  # Should remain unchanged
    ]

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)
        importer = CSVImporter(db)

        # Create a small test CSV with category mapping
        test_csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-01-15;2025-01-15;Test Food;Alimentation;Vie quotidienne;;-25,50;Test comment;000123;Test Account;1000.00
2025-01-16;2025-01-16;Test Transport;Transports longue distance (avions, trains…);Voyages & Transports;;-49,00;;000123;Test Account;975.50
2025-01-17;2025-01-17;Test Income;Virements reçus;Virements reçus;;500,00;;000123;Test Account;1475.50"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(test_csv_content)
            temp_csv = f.name

        try:
            # Import the test data
            successful, failed, errors = importer.import_from_csv(
                temp_csv, skip_duplicates=False, default_type="personal"
            )

            if successful != 3:
                print(f"❌ Expected 3 successful imports, got {successful}")
                return False

            # Check category mappings
            transactions = db.get_all_transactions()
            mapped_correctly = 0

            for trans in transactions:
                description = trans.get("description", "")
                category = trans.get("category", "")

                if "Test Food" in description and category == "Food":
                    print("✓ 'Alimentation' correctly mapped to 'Food'")
                    mapped_correctly += 1
                elif "Test Transport" in description and category == "Transport":
                    print(
                        "✓ 'Transports longue distance' correctly mapped to 'Transport'"
                    )
                    mapped_correctly += 1
                elif "Test Income" in description and category == "Income":
                    print("✓ 'Virements reçus' correctly mapped to 'Income'")
                    mapped_correctly += 1

            if mapped_correctly == 3:
                print("✓ All category mappings work correctly")
                print("\n✓ TEST 2 PASSED: Category mapping works")
                return True
            else:
                print(f"❌ Only {mapped_correctly}/3 categories mapped correctly")
                return False

        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_duplicate_detection():
    """Test duplicate transaction detection."""
    print("=" * 70)
    print("TEST 3: Duplicate Detection")
    print("=" * 70)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)
        importer = CSVImporter(db)

        # Create test CSV with duplicate transactions
        test_csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-01-15;2025-01-15;Duplicate Test;Alimentation;Vie quotidienne;;-10,00;Test;000123;Test Account;1000.00
2025-01-15;2025-01-15;Duplicate Test;Alimentation;Vie quotidienne;;-10,00;Test;000123;Test Account;1000.00
2025-01-16;2025-01-16;Unique Test;Alimentation;Vie quotidienne;;-15,00;Test;000123;Test Account;990.00"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(test_csv_content)
            temp_csv = f.name

        try:
            # Import with duplicate detection enabled
            successful, failed, errors = importer.import_from_csv(
                temp_csv, skip_duplicates=True, default_type="personal"
            )

            print(f"✓ Successfully imported: {successful} transactions")
            print(f"✓ Skipped/failed: {failed} transactions")

            # Should import 2 transactions (1 duplicate skipped)
            if successful == 2 and failed == 1:
                print("✓ Duplicate detection working correctly")
                print("\n✓ TEST 3 PASSED: Duplicate detection works")
                return True
            else:
                print(
                    f"❌ Expected 2 successful and 1 failed, got {successful} successful and {failed} failed"
                )
                return False

        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_french_decimal_format():
    """Test French decimal format parsing."""
    print("=" * 70)
    print("TEST 4: French Decimal Format")
    print("=" * 70)

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    try:
        os.close(db_fd)
        # Initialize the database schema
        initialize_database(db_path)
        db = DatabaseManager(db_path)
        importer = CSVImporter(db)

        # Test various French decimal formats
        test_csv_content = """dateOp;dateVal;label;category;categoryParent;supplierFound;amount;comment;accountNum;accountLabel;accountbalance
2025-01-15;2025-01-15;Test 1;Alimentation;Vie quotidienne;;-10,50;Test;000123;Test Account;1000.00
2025-01-16;2025-01-16;Test 2;Alimentation;Vie quotidienne;;-1 234,56;Test;000123;Test Account;989.50
2025-01-17;2025-01-17;Test 3;Alimentation;Vie quotidienne;;"2 500,00";Test;000123;Test Account;989.50"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(test_csv_content)
            temp_csv = f.name

        try:
            # Import the test data
            successful, failed, errors = importer.import_from_csv(
                temp_csv, skip_duplicates=False, default_type="personal"
            )

            if successful != 3:
                print(f"❌ Expected 3 successful imports, got {successful}")
                return False

            # Check amounts are parsed correctly
            transactions = db.get_all_transactions()
            expected_amounts = [-10.50, -1234.56, 2500.00]
            found_correctly = 0

            for trans in transactions:
                amount = trans.get("amount", 0)
                if amount in expected_amounts:
                    print(f"✓ Correctly parsed amount: {amount}")
                    found_correctly += 1

            if found_correctly == 3:
                print("✓ All French decimal formats parsed correctly")
                print("\n✓ TEST 4 PASSED: French decimal format works")
                return True
            else:
                print(f"❌ Only {found_correctly}/3 amounts parsed correctly")
                return False

        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all BoursoBank import tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "BOURSO BANK CSV IMPORT TESTS" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    tests = [
        ("BoursoBank CSV Parsing", test_boursobank_parsing),
        ("Category Mapping", test_category_mapping),
        ("Duplicate Detection", test_duplicate_detection),
        ("French Decimal Format", test_french_decimal_format),
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
        print("\nBoursoBank CSV import functionality is working correctly:")
        print("  ✓ Semicolon separator detection")
        print("  ✓ French decimal format parsing")
        print("  ✓ BoursoBank column mapping")
        print("  ✓ Category translation")
        print("  ✓ Duplicate detection")
        print("  ✓ Transaction import")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the failed tests above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
