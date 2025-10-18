#!/usr/bin/env python3
"""
Demo script for Prism v1.1.0 new features.
Showcases CSV import, recurring transactions, categories, and PDF reports.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.db_manager import DatabaseManager
from prism.database.schema import initialize_database
from prism.utils.csv_import import CSVImporter
from prism.utils.recurring_manager import RecurringTransactionManager
from prism.utils.category_manager import CategoryManager
from prism.utils.pdf_reports import PDFReportGenerator


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}\n")


def demo_categories():
    """Demo category management features."""
    print_header("📋 DEMO: Category Management")

    db_manager = DatabaseManager()
    category_manager = CategoryManager(db_manager)

    print("✓ Database initialized with default categories\n")

    # Show default categories
    print("📊 Default Categories:")
    print("─" * 70)

    income_cats = category_manager.get_all_categories(category_type="income")
    expense_cats = category_manager.get_all_categories(category_type="expense")

    print("\n💰 INCOME CATEGORIES:")
    for cat in income_cats:
        print(f"   {cat['icon']}  {cat['name']:<20} {cat['color']}")

    print("\n💳 EXPENSE CATEGORIES:")
    for cat in expense_cats:
        budget = (
            f"Budget: €{cat['budget_limit']:,.0f}"
            if cat.get("budget_limit")
            else "No budget set"
        )
        print(f"   {cat['icon']}  {cat['name']:<20} {cat['color']:<12} {budget}")

    # Add custom categories
    print_section("Adding Custom Categories")

    custom_categories = [
        ("Groceries", "expense", "#22c55e", "🥗", 300.0),
        ("Coffee", "expense", "#f59e0b", "☕", 50.0),
        ("Freelance", "income", "#3b82f6", "💻", None),
    ]

    for name, cat_type, color, icon, budget in custom_categories:
        try:
            cat_id = category_manager.add_category(
                name=name,
                category_type=cat_type,
                color=color,
                icon=icon,
                budget_limit=budget,
            )
            budget_str = f"(Budget: €{budget:,.0f})" if budget else ""
            print(f"   ✓ Created: {icon} {name} {budget_str}")
        except Exception as e:
            print(f"   ⚠ {name} already exists")

    # Show statistics
    print_section("Category Statistics")

    stats_list = category_manager.get_all_category_statistics()
    if stats_list:
        print("Category                 Transactions    Total Amount")
        print("─" * 70)
        for stats in stats_list[:5]:
            print(
                f"{stats['icon']} {stats['category_name']:<20} {stats['transaction_count']:>8}      €{stats['total_amount']:>10,.2f}"
            )
    else:
        print("No transactions yet. Add some to see statistics!")

    db_manager.close()


def demo_recurring_transactions():
    """Demo recurring transactions features."""
    print_header("🔄 DEMO: Recurring Transactions")

    db_manager = DatabaseManager()
    recurring_manager = RecurringTransactionManager(db_manager)

    # Add sample recurring transactions
    print("Setting up recurring transactions...\n")

    today = datetime.now().strftime("%Y-%m-%d")
    first_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    recurring_examples = [
        (
            3000.0,
            "Salary",
            "personal",
            "monthly",
            first_of_month,
            "Monthly salary payment",
        ),
        (-1200.0, "Housing", "personal", "monthly", first_of_month, "Monthly rent"),
        (
            -50.0,
            "Entertainment",
            "personal",
            "monthly",
            first_of_month,
            "Netflix subscription",
        ),
        (-100.0, "Food", "personal", "weekly", today, "Weekly groceries budget"),
        (
            500.0,
            "Freelance",
            "personal",
            "monthly",
            first_of_month,
            "Side project income",
        ),
    ]

    created_ids = []
    for (
        amount,
        category,
        trans_type,
        frequency,
        start_date,
        description,
    ) in recurring_examples:
        try:
            recurring_id = recurring_manager.add_recurring_transaction(
                amount=amount,
                category=category,
                trans_type=trans_type,
                frequency=frequency,
                start_date=start_date,
                description=description,
            )
            created_ids.append(recurring_id)

            symbol = "+" if amount > 0 else ""
            print(f"   ✓ {category:<20} {symbol}€{amount:>8,.2f}  ({frequency})")
        except Exception as e:
            print(f"   ⚠ Failed to add {category}: {str(e)}")

    # Show all recurring transactions
    print_section("Active Recurring Transactions")

    recurring_list = recurring_manager.get_all_recurring_transactions()

    print("Category              Amount        Frequency    Next Date     Active")
    print("─" * 70)
    for rec in recurring_list:
        amount_str = f"€{rec['amount']:,.2f}"
        active_str = "✓" if rec["is_active"] == 1 else "✗"
        print(
            f"{rec['category']:<20} {amount_str:>12}  {rec['frequency']:<10}  {rec['next_occurrence']}  {active_str}"
        )

    # Show statistics
    print_section("Recurring Transaction Statistics")

    stats = recurring_manager.get_statistics()
    print(f"Total Recurring Transactions: {stats['total_recurring']}")
    print(f"Active: {stats['active_recurring']}")
    print(f"\nEstimated Monthly Impact:")
    print(f"   Income:   €{stats['estimated_monthly_income']:>10,.2f}")
    print(f"   Expense:  €{stats['estimated_monthly_expense']:>10,.2f}")
    print(f"   ───────────────────────")
    net_color = "+" if stats["estimated_monthly_net"] >= 0 else ""
    print(f"   Net:      {net_color}€{stats['estimated_monthly_net']:>10,.2f}")

    # Show upcoming transactions
    print_section("Upcoming Transactions (Next 30 Days)")

    upcoming = recurring_manager.get_upcoming_transactions(days=30)

    if upcoming:
        for trans in upcoming[:10]:  # Show first 10
            amount_str = f"€{trans['amount']:,.2f}"
            print(
                f"   {trans['date']}  {trans['category']:<20} {amount_str:>12}  ({trans['frequency']})"
            )
        if len(upcoming) > 10:
            print(f"   ... and {len(upcoming) - 10} more upcoming transactions")
    else:
        print("   No upcoming transactions in the next 30 days")

    db_manager.close()


def demo_csv_import():
    """Demo CSV import features."""
    print_header("📥 DEMO: CSV Import")

    db_manager = DatabaseManager()
    importer = CSVImporter(db_manager)

    # Generate sample CSV
    sample_path = Path("/tmp/prism_demo_import.csv")

    print("Generating sample CSV file...\n")
    importer.generate_sample_csv(str(sample_path))

    print(f"✓ Sample CSV created: {sample_path}\n")

    # Show CSV contents
    print("CSV Contents:")
    print("─" * 70)
    with open(sample_path, "r") as f:
        for i, line in enumerate(f, 1):
            print(f"{i:2}. {line.rstrip()}")

    # Validate CSV
    print_section("Validating CSV File")

    is_valid, error_msg = importer.validate_csv_file(str(sample_path))
    if is_valid:
        print("✓ CSV file is valid and ready for import")
    else:
        print(f"✗ Validation failed: {error_msg}")
        return

    # Import CSV
    print_section("Importing Transactions")

    successful, failed, errors = importer.import_from_csv(
        str(sample_path), skip_duplicates=True, default_type="personal"
    )

    print(f"Import Results:")
    print(f"   ✓ Successfully imported: {successful} transactions")
    print(f"   ✗ Failed: {failed} transactions")

    if errors:
        print(f"\nErrors:")
        for error in errors[:5]:
            print(f"   • {error}")

    # Show summary
    summary = importer.get_import_summary(successful, failed, errors)
    print_section("Import Summary")
    print(summary)

    # Clean up
    sample_path.unlink(missing_ok=True)
    db_manager.close()


def demo_pdf_reports():
    """Demo PDF report generation."""
    print_header("📄 DEMO: PDF Report Generation")

    try:
        db_manager = DatabaseManager()
        generator = PDFReportGenerator(db_manager)

        # Generate full report
        print("Generating comprehensive PDF report...\n")

        output_path = Path("/tmp/prism_demo_report.pdf")

        generator.generate_full_report(str(output_path))

        file_size_kb = output_path.stat().st_size / 1024

        print(f"✓ PDF Report Generated Successfully!\n")
        print(f"   Location: {output_path}")
        print(f"   File Size: {file_size_kb:.1f} KB")

        # Report contents
        print_section("Report Contents")

        print("The PDF report includes:")
        print("   📊 Financial Summary")
        print("      • Total Income & Expenses")
        print("      • Net Balance")
        print("      • Investment Portfolio Value")
        print("      • Gains/Losses")
        print()
        print("   📝 Recent Transactions")
        print("      • Up to 50 most recent transactions")
        print("      • Organized by date")
        print("      • Color-coded by type")
        print()
        print("   💼 Investment Portfolio")
        print("      • All assets with current values")
        print("      • Buy vs. Current prices")
        print("      • Performance metrics")
        print()
        print("   📋 Order Book")
        print("      • All buy/sell orders")
        print("      • Status tracking")
        print()

        print(f"\n💡 Open the PDF to view: {output_path}\n")

        # Generate monthly report
        print_section("Generating Monthly Report")

        now = datetime.now()
        monthly_path = Path(f"/tmp/prism_monthly_{now.year}_{now.month:02d}.pdf")

        generator.generate_monthly_report(str(monthly_path), now.year, now.month)

        monthly_size_kb = monthly_path.stat().st_size / 1024

        print(f"✓ Monthly Report Generated!")
        print(f"   Period: {now.strftime('%B %Y')}")
        print(f"   Location: {monthly_path}")
        print(f"   File Size: {monthly_size_kb:.1f} KB")

        db_manager.close()

    except ImportError:
        print("✗ ReportLab library not installed")
        print("   Install it with: pip install reportlab")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  🎨 PRISM v1.1.0 - NEW FEATURES DEMONSTRATION")
    print("=" * 70)
    print("\n  This demo showcases the new features added in version 1.1.0:")
    print("  • CSV Import for bulk transaction entry")
    print("  • Recurring Transactions for automated entries")
    print("  • Custom Categories with budget management")
    print("  • PDF Report Generation for professional reports")
    print("\n" + "=" * 70)

    # Initialize database
    print("\nInitializing database...")
    initialize_database()
    print("✓ Database ready\n")

    input("Press Enter to start the demo...")

    # Run demos
    demo_categories()
    input("\nPress Enter to continue to Recurring Transactions demo...")

    demo_recurring_transactions()
    input("\nPress Enter to continue to CSV Import demo...")

    demo_csv_import()
    input("\nPress Enter to continue to PDF Reports demo...")

    demo_pdf_reports()

    # Final summary
    print_header("✨ DEMO COMPLETE!")

    print("Summary of what was demonstrated:\n")
    print("✓ Categories:")
    print("  - Default categories (14 pre-configured)")
    print("  - Custom category creation with colors and icons")
    print("  - Budget limits and tracking")
    print("  - Category statistics\n")

    print("✓ Recurring Transactions:")
    print("  - Automated transaction scheduling")
    print("  - Multiple frequencies (daily, weekly, monthly, yearly)")
    print("  - Upcoming transaction preview")
    print("  - Monthly impact estimation\n")

    print("✓ CSV Import:")
    print("  - Sample CSV generation")
    print("  - File validation")
    print("  - Bulk transaction import")
    print("  - Duplicate detection\n")

    print("✓ PDF Reports:")
    print("  - Comprehensive financial reports")
    print("  - Monthly and yearly reports")
    print("  - Professional formatting\n")

    print("Generated Files:")
    print("  • /tmp/prism_demo_report.pdf - Full financial report")
    print(
        f"  • /tmp/prism_monthly_{datetime.now().year}_{datetime.now().month:02d}.pdf - Monthly report"
    )

    print("\n" + "=" * 70)
    print("  Thank you for trying Prism v1.1.0!")
    print("  Access these features in the application via:")
    print("    • File → Import from CSV (Cmd+I)")
    print("    • Tools → Recurring Transactions (Cmd+Shift+R)")
    print("    • Tools → Categories & Budgets (Cmd+Shift+C)")
    print("    • Tools → Generate PDF Report (Cmd+P)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
