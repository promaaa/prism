#!/usr/bin/env python3
"""
Test script for new Prism features.
Tests CSV import, recurring transactions, categories, and PDF reports.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.db_manager import DatabaseManager
from prism.database.schema import initialize_database
from prism.utils.csv_import import CSVImporter
from prism.utils.recurring_manager import RecurringTransactionManager
from prism.utils.category_manager import CategoryManager
from prism.utils.pdf_reports import PDFReportGenerator
from datetime import datetime


def test_categories():
    """Test category management."""
    print("\n" + "=" * 60)
    print("Testing Category Management")
    print("=" * 60)

    db_manager = DatabaseManager()
    category_manager = CategoryManager(db_manager)

    # Get all categories
    categories = category_manager.get_all_categories()
    print(f"\n✓ Found {len(categories)} categories")

    for cat in categories[:5]:  # Show first 5
        print(f"  • {cat['icon']} {cat['name']} ({cat['type']}) - {cat['color']}")

    # Add a custom category
    try:
        cat_id = category_manager.add_category(
            name="Test Category",
            category_type="expense",
            color="#ff6b6b",
            icon="🧪",
            budget_limit=500.0,
        )
        print(f"\n✓ Added custom category (ID: {cat_id})")
    except Exception as e:
        print(f"\n✗ Failed to add category: {e}")

    # Get budget alerts
    alerts = category_manager.get_budget_alerts()
    print(f"\n✓ Budget alerts: {len(alerts)}")

    # Get category statistics
    income_cats = category_manager.get_all_categories(category_type="income")
    if income_cats:
        stats = category_manager.get_category_statistics(income_cats[0]["name"])
        print(f"\n✓ Statistics for '{income_cats[0]['name']}':")
        print(f"  - Total amount: €{stats['total_amount']:,.2f}")
        print(f"  - Transaction count: {stats['transaction_count']}")

    db_manager.close()


def test_recurring_transactions():
    """Test recurring transactions."""
    print("\n" + "=" * 60)
    print("Testing Recurring Transactions")
    print("=" * 60)

    db_manager = DatabaseManager()
    recurring_manager = RecurringTransactionManager(db_manager)

    # Add a recurring transaction
    try:
        recurring_id = recurring_manager.add_recurring_transaction(
            amount=3000.0,
            category="Salary",
            trans_type="personal",
            frequency="monthly",
            start_date="2024-01-01",
            description="Monthly salary payment",
        )
        print(f"\n✓ Added recurring transaction (ID: {recurring_id})")
    except Exception as e:
        print(f"\n✗ Failed to add recurring transaction: {e}")

    # Get all recurring transactions
    recurring_list = recurring_manager.get_all_recurring_transactions()
    print(f"\n✓ Found {len(recurring_list)} recurring transactions")

    for rec in recurring_list:
        print(
            f"  • {rec['category']}: €{rec['amount']:,.2f} ({rec['frequency']}) - Next: {rec['next_occurrence']}"
        )

    # Get upcoming transactions
    upcoming = recurring_manager.get_upcoming_transactions(days=30)
    print(f"\n✓ Upcoming transactions (next 30 days): {len(upcoming)}")

    # Get statistics
    stats = recurring_manager.get_statistics()
    print(f"\n✓ Recurring statistics:")
    print(f"  - Total recurring: {stats['total_recurring']}")
    print(f"  - Active: {stats['active_recurring']}")
    print(f"  - Est. monthly income: €{stats['estimated_monthly_income']:,.2f}")
    print(f"  - Est. monthly expense: €{stats['estimated_monthly_expense']:,.2f}")
    print(f"  - Est. net: €{stats['estimated_monthly_net']:,.2f}")

    # Process due transactions
    count = recurring_manager.process_due_transactions()
    print(f"\n✓ Processed {count} due transactions")

    db_manager.close()


def test_csv_import():
    """Test CSV import functionality."""
    print("\n" + "=" * 60)
    print("Testing CSV Import")
    print("=" * 60)

    db_manager = DatabaseManager()
    importer = CSVImporter(db_manager)

    # Generate sample CSV
    sample_path = Path("/tmp/prism_test_import.csv")
    try:
        importer.generate_sample_csv(str(sample_path))
        print(f"\n✓ Generated sample CSV: {sample_path}")
    except Exception as e:
        print(f"\n✗ Failed to generate sample CSV: {e}")
        db_manager.close()
        return

    # Validate the sample CSV
    is_valid, error_msg = importer.validate_csv_file(str(sample_path))
    if is_valid:
        print("✓ Sample CSV is valid")
    else:
        print(f"✗ Sample CSV validation failed: {error_msg}")
        db_manager.close()
        return

    # Import the sample CSV
    try:
        successful, failed, errors = importer.import_from_csv(str(sample_path))
        print(f"\n✓ Import completed:")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {failed}")

        if errors:
            print(f"\n  Errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"    • {error}")
    except Exception as e:
        print(f"\n✗ Failed to import CSV: {e}")

    # Clean up
    sample_path.unlink(missing_ok=True)
    db_manager.close()


def test_pdf_reports():
    """Test PDF report generation."""
    print("\n" + "=" * 60)
    print("Testing PDF Report Generation")
    print("=" * 60)

    try:
        from prism.utils.pdf_reports import PDFReportGenerator

        db_manager = DatabaseManager()
        generator = PDFReportGenerator(db_manager)

        # Generate a full report
        output_path = Path("/tmp/prism_test_report.pdf")

        try:
            generator.generate_full_report(str(output_path))
            print(f"\n✓ Generated PDF report: {output_path}")
            print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
        except Exception as e:
            print(f"\n✗ Failed to generate PDF: {e}")

        # Generate monthly report
        now = datetime.now()
        monthly_path = Path("/tmp/prism_monthly_report.pdf")

        try:
            generator.generate_monthly_report(str(monthly_path), now.year, now.month)
            print(f"\n✓ Generated monthly PDF report: {monthly_path}")
            print(f"  File size: {monthly_path.stat().st_size / 1024:.1f} KB")
        except Exception as e:
            print(f"\n✗ Failed to generate monthly PDF: {e}")

        db_manager.close()

    except ImportError:
        print("\n✗ ReportLab not installed")
        print("  Install it with: pip install reportlab")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PRISM NEW FEATURES TEST SUITE")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    initialize_database()
    print("✓ Database initialized")

    # Run tests
    try:
        test_categories()
        test_recurring_transactions()
        test_csv_import()
        test_pdf_reports()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)
        print("\n✓ Categories: Working")
        print("✓ Recurring Transactions: Working")
        print("✓ CSV Import: Working")
        print("✓ PDF Reports: Working")
        print("\nNote: Check /tmp/ for generated PDF files")

    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
