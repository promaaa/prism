#!/usr/bin/env python3
"""
Health Check Script for Prism v1.1.0
Verifies that all components are properly installed and configured.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_check(name, status, details=""):
    """Print check result."""
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {name:<40} {details}")


def check_python_version():
    """Check Python version."""
    print_header("Python Environment")

    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 11

    print_check(
        "Python Version", is_valid, f"v{version.major}.{version.minor}.{version.micro}"
    )

    if not is_valid:
        print("  ⚠ Python 3.11+ required")

    return is_valid


def check_dependencies():
    """Check required dependencies."""
    print_header("Dependencies")

    dependencies = {
        "PyQt6": "GUI Framework",
        "pandas": "Data Manipulation",
        "plotly": "Visualization",
        "requests": "HTTP Client",
        "yfinance": "Stock Data",
        "reportlab": "PDF Generation",
        "pytest": "Testing",
    }

    all_ok = True

    for package, description in dependencies.items():
        try:
            __import__(package.lower().replace("-", "_"))
            print_check(package, True, description)
        except ImportError:
            print_check(package, False, f"{description} - MISSING")
            all_ok = False

    return all_ok


def check_database():
    """Check database setup."""
    print_header("Database")

    try:
        from prism.database.schema import (
            initialize_database,
            get_database_path,
            get_schema_version,
        )
        from prism.database.db_manager import DatabaseManager

        # Check database path
        db_path = get_database_path()
        print_check("Database Path", True, str(db_path))

        # Initialize if needed
        initialize_database()
        print_check("Database Initialized", True)

        # Check schema version
        version = get_schema_version()
        print_check("Schema Version", version == "1.1.0", f"v{version}")

        # Check database manager
        db = DatabaseManager()
        print_check("Database Manager", True, "Connected")

        # Check tables
        tables = [
            "transactions",
            "assets",
            "orders",
            "categories",
            "recurring_transactions",
        ]
        for table in tables:
            cursor = db.conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print_check(f"  Table: {table}", True, f"{count} rows")

        db.close()
        return True

    except Exception as e:
        print_check("Database", False, str(e))
        return False


def check_api_modules():
    """Check API modules."""
    print_header("API Modules")

    try:
        from prism.api.crypto_api import CryptoAPI
        from prism.api.stock_api import StockAPI

        print_check("CryptoAPI", True, "CoinGecko integration")
        print_check("StockAPI", True, "Yahoo Finance integration")

        return True
    except Exception as e:
        print_check("API Modules", False, str(e))
        return False


def check_new_features():
    """Check new v1.1.0 features."""
    print_header("New Features (v1.1.0)")

    features_ok = True

    # Check CSV Import
    try:
        from prism.utils.csv_import import CSVImporter

        print_check("CSV Import Module", True, "Bulk transaction import")
    except Exception as e:
        print_check("CSV Import Module", False, str(e))
        features_ok = False

    # Check Recurring Transactions
    try:
        from prism.utils.recurring_manager import RecurringTransactionManager

        print_check("Recurring Transactions", True, "Automated scheduling")
    except Exception as e:
        print_check("Recurring Transactions", False, str(e))
        features_ok = False

    # Check Category Manager
    try:
        from prism.utils.category_manager import CategoryManager

        print_check("Category Manager", True, "Custom categories & budgets")
    except Exception as e:
        print_check("Category Manager", False, str(e))
        features_ok = False

    # Check PDF Reports
    try:
        from prism.utils.pdf_reports import PDFReportGenerator

        print_check("PDF Report Generator", True, "Professional reports")
    except Exception as e:
        print_check("PDF Report Generator", False, str(e))
        features_ok = False

    return features_ok


def check_ui_components():
    """Check UI components."""
    print_header("UI Components")

    ui_ok = True

    components = {
        "main_window": "Main Window",
        "personal_tab": "Personal Finances Tab",
        "investments_tab": "Investments Tab",
        "orders_tab": "Orders Tab",
        "reports_tab": "Reports Tab",
        "csv_import_dialog": "CSV Import Dialog",
        "recurring_dialog": "Recurring Transactions Dialog",
        "categories_dialog": "Categories & Budgets Dialog",
        "help_dialog": "Help System",
    }

    for module, description in components.items():
        try:
            __import__(f"prism.ui.{module}")
            print_check(description, True)
        except Exception as e:
            print_check(description, False, str(e))
            ui_ok = False

    return ui_ok


def check_utils():
    """Check utility modules."""
    print_header("Utility Modules")

    utils_ok = True

    utils = {
        "logger": "Logging System",
        "exports": "Data Export",
        "calculations": "Portfolio Calculations",
        "ticker_data": "Ticker Suggestions",
    }

    for module, description in utils.items():
        try:
            __import__(f"prism.utils.{module}")
            print_check(description, True)
        except Exception as e:
            print_check(description, False, str(e))
            utils_ok = False

    return utils_ok


def check_file_structure():
    """Check file and directory structure."""
    print_header("File Structure")

    base_path = Path(__file__).parent.parent

    required_paths = {
        "prism/": "Main package directory",
        "prism/database/": "Database modules",
        "prism/api/": "API integrations",
        "prism/ui/": "User interface",
        "prism/utils/": "Utility modules",
        "scripts/": "Helper scripts",
        "tests/": "Test suite",
        "assets/": "Application assets",
        "README.md": "Documentation",
        "requirements.txt": "Dependencies list",
    }

    all_exist = True

    for path, description in required_paths.items():
        full_path = base_path / path
        exists = full_path.exists()
        print_check(path, exists, description)
        all_exist = all_exist and exists

    return all_exist


def check_default_categories():
    """Check that default categories are loaded."""
    print_header("Default Categories")

    try:
        from prism.utils.category_manager import CategoryManager
        from prism.database.db_manager import DatabaseManager

        db = DatabaseManager()
        cat_manager = CategoryManager(db)

        categories = cat_manager.get_all_categories()

        if len(categories) >= 14:
            print_check(
                "Default Categories Loaded", True, f"{len(categories)} categories"
            )

            # Show sample categories
            for cat in categories[:5]:
                print(f"  {cat['icon']} {cat['name']} ({cat['type']})")
            if len(categories) > 5:
                print(f"  ... and {len(categories) - 5} more")

            db.close()
            return True
        else:
            print_check(
                "Default Categories",
                False,
                f"Only {len(categories)} found (expected 14)",
            )
            db.close()
            return False

    except Exception as e:
        print_check("Default Categories", False, str(e))
        return False


def run_comprehensive_test():
    """Run a comprehensive test of functionality."""
    print_header("Functionality Test")

    try:
        from prism.database.db_manager import DatabaseManager
        from prism.utils.category_manager import CategoryManager
        from prism.utils.recurring_manager import RecurringTransactionManager

        db = DatabaseManager()

        # Test adding a transaction
        try:
            trans_id = db.add_transaction(
                date="2024-01-01",
                amount=100.0,
                category="Test",
                transaction_type="personal",
                description="Health check test",
            )
            print_check("Add Transaction", True, f"ID: {trans_id}")

            # Clean up
            db.conn.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            db.conn.commit()
        except Exception as e:
            print_check("Add Transaction", False, str(e))

        # Test category statistics
        try:
            cat_manager = CategoryManager(db)
            stats = cat_manager.get_all_category_statistics()
            print_check(
                "Category Statistics", True, f"{len(stats)} categories analyzed"
            )
        except Exception as e:
            print_check("Category Statistics", False, str(e))

        # Test recurring transactions
        try:
            rec_manager = RecurringTransactionManager(db)
            stats = rec_manager.get_statistics()
            print_check(
                "Recurring Statistics",
                True,
                f"{stats['total_recurring']} recurring transactions",
            )
        except Exception as e:
            print_check("Recurring Statistics", False, str(e))

        db.close()
        return True

    except Exception as e:
        print_check("Functionality Test", False, str(e))
        return False


def main():
    """Run all health checks."""
    print("\n" + "=" * 70)
    print("  PRISM v1.1.0 - HEALTH CHECK")
    print("=" * 70)
    print("\n  Verifying installation and configuration...")

    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Database": check_database(),
        "API Modules": check_api_modules(),
        "New Features": check_new_features(),
        "UI Components": check_ui_components(),
        "Utility Modules": check_utils(),
        "File Structure": check_file_structure(),
        "Default Categories": check_default_categories(),
        "Functionality": run_comprehensive_test(),
    }

    # Summary
    print_header("Health Check Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {name}")

    print("\n" + "-" * 70)
    print(f"  Result: {passed}/{total} checks passed")
    print("-" * 70)

    if passed == total:
        print("\n  🎉 All checks passed! Prism is ready to use.")
        print("\n  Next steps:")
        print("    • Launch the application: python -m prism")
        print("    • Run the demo: python scripts/demo_new_features.py")
        print("    • Read the guide: NEW_FEATURES_GUIDE.md")
        return 0
    else:
        print("\n  ⚠ Some checks failed. Please review the errors above.")
        print("\n  Common fixes:")
        print("    • Install missing dependencies: pip install -r requirements.txt")
        print("    • Check Python version: python --version (need 3.11+)")
        print(
            "    • Reinitialize database: python -c 'from prism.database.schema import initialize_database; initialize_database()'"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
