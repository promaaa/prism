#!/usr/bin/env python3
"""
Health check and verification script for USD/EUR cryptocurrency feature.
Verifies that all components are properly installed and functioning.

Usage:
    python scripts/verify_usd_eur_setup.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(name: str, passed: bool, details: str = ""):
    """Print a check result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {name}")
    if details:
        print(f"       {details}")


def check_imports():
    """Check that all required modules can be imported."""
    print_header("Checking Python Imports")

    checks = []

    # Check currency converter
    try:
        from prism.api.currency_converter import CurrencyConverter, get_converter

        checks.append(("CurrencyConverter module", True, ""))
    except ImportError as e:
        checks.append(("CurrencyConverter module", False, str(e)))

    # Check crypto API
    try:
        from prism.api.crypto_api import CryptoAPI

        api = CryptoAPI()
        has_usd_methods = hasattr(api, "get_price_usd") and hasattr(
            api, "get_multiple_prices_usd"
        )
        checks.append(
            (
                "CryptoAPI USD methods",
                has_usd_methods,
                "get_price_usd() and get_multiple_prices_usd()",
            )
        )
    except Exception as e:
        checks.append(("CryptoAPI USD methods", False, str(e)))

    # Check database manager
    try:
        from prism.database.db_manager import DatabaseManager

        checks.append(("DatabaseManager module", True, ""))
    except ImportError as e:
        checks.append(("DatabaseManager module", False, str(e)))

    # Check schema version
    try:
        from prism.database.schema import get_schema_version

        version = get_schema_version()
        is_correct = version == "1.2.0"
        checks.append(
            ("Database schema version", is_correct, f"Expected: 1.2.0, Got: {version}")
        )
    except Exception as e:
        checks.append(("Database schema version", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_database_schema():
    """Check that database has the price_currency column."""
    print_header("Checking Database Schema")

    checks = []

    try:
        from prism.database.db_manager import DatabaseManager
        from prism.database.schema import get_database_path
        import sqlite3

        db_path = get_database_path()

        if not db_path.exists():
            checks.append(
                ("Database exists", False, f"Database not found at {db_path}")
            )
            for check in checks:
                print_check(*check)
            return False

        checks.append(("Database exists", True, str(db_path)))

        # Check for price_currency column
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(assets)")
        columns = [row[1] for row in cursor.fetchall()]

        has_currency_col = "price_currency" in columns
        checks.append(
            ("price_currency column exists", has_currency_col, "In assets table")
        )

        if has_currency_col:
            # Check column properties
            cursor.execute("PRAGMA table_info(assets)")
            for row in cursor.fetchall():
                if row[1] == "price_currency":
                    col_type = row[2]
                    col_default = row[4]
                    checks.append(
                        ("Column type", col_type == "TEXT", f"Type: {col_type}")
                    )
                    checks.append(
                        (
                            "Column default",
                            col_default == "'EUR'",
                            f"Default: {col_default}",
                        )
                    )

        conn.close()

    except Exception as e:
        checks.append(("Database schema check", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_api_connectivity():
    """Check API connectivity and rate fetching."""
    print_header("Checking API Connectivity")

    checks = []

    try:
        from prism.api.currency_converter import get_converter

        converter = get_converter()

        # Try to get exchange rate
        try:
            rate = converter.get_usd_eur_rate()
            is_valid = 0.5 < rate < 1.5  # Reasonable range
            checks.append(
                ("Exchange rate fetch", is_valid, f"Rate: 1 USD = {rate:.4f} EUR")
            )
        except Exception as e:
            checks.append(("Exchange rate fetch", False, str(e)))

        # Try conversion
        try:
            usd_amount = 100
            eur_amount = converter.convert_usd_to_eur(usd_amount)
            is_valid = eur_amount > 0
            checks.append(
                (
                    "USD to EUR conversion",
                    is_valid,
                    f"${usd_amount} USD = €{eur_amount:.2f} EUR",
                )
            )
        except Exception as e:
            checks.append(("USD to EUR conversion", False, str(e)))

        # Try display text
        try:
            display_text = converter.get_rate_display_text()
            is_valid = "USD" in display_text and "EUR" in display_text
            checks.append(("Rate display text", is_valid, display_text))
        except Exception as e:
            checks.append(("Rate display text", False, str(e)))

    except Exception as e:
        checks.append(("API connectivity", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_crypto_api_usd():
    """Check CryptoAPI USD methods."""
    print_header("Checking CryptoAPI USD Methods")

    checks = []

    try:
        from prism.api.crypto_api import CryptoAPI

        api = CryptoAPI()

        # Check method existence
        has_methods = (
            hasattr(api, "get_price_usd")
            and hasattr(api, "get_multiple_prices_usd")
            and hasattr(api, "get_price_usd_async")
            and hasattr(api, "get_multiple_prices_usd_async")
        )
        checks.append(
            (
                "USD methods exist",
                has_methods,
                "get_price_usd(), get_multiple_prices_usd() + async variants",
            )
        )

        if has_methods:
            # Try fetching a price (may fail due to rate limits)
            try:
                price = api.get_price_usd("BTC")
                if price:
                    checks.append(("Fetch BTC price (USD)", True, f"${price:,.2f} USD"))
                else:
                    checks.append(
                        (
                            "Fetch BTC price (USD)",
                            False,
                            "API returned None (rate limit or network issue)",
                        )
                    )
            except Exception as e:
                checks.append(
                    ("Fetch BTC price (USD)", False, f"Exception: {str(e)[:50]}")
                )

    except Exception as e:
        checks.append(("CryptoAPI USD methods", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_database_operations():
    """Check database operations with price_currency."""
    print_header("Checking Database Operations")

    checks = []

    try:
        from prism.database.db_manager import DatabaseManager
        import tempfile

        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name

        db = DatabaseManager(tmp_path)

        # Test adding asset with USD
        try:
            asset_id = db.add_asset(
                ticker="BTC",
                quantity=0.5,
                price_buy=65000.00,
                date_buy="2024-01-01",
                asset_type="crypto",
                current_price=67000.00,
                price_currency="USD",
            )
            checks.append(("Add asset with USD", True, f"Asset ID: {asset_id}"))

            # Verify currency stored correctly
            asset = db.get_asset(asset_id)
            currency_correct = asset.get("price_currency") == "USD"
            checks.append(
                (
                    "Verify USD currency stored",
                    currency_correct,
                    f"Stored as: {asset.get('price_currency')}",
                )
            )

        except Exception as e:
            checks.append(("Add asset with USD", False, str(e)))

        # Test adding asset with EUR (default)
        try:
            asset_id = db.add_asset(
                ticker="ETH",
                quantity=2.0,
                price_buy=2000.00,
                date_buy="2024-01-01",
                asset_type="crypto",
                current_price=2200.00,
                # price_currency not specified, should default to EUR
            )
            asset = db.get_asset(asset_id)
            currency_correct = asset.get("price_currency") == "EUR"
            checks.append(
                (
                    "Default to EUR when not specified",
                    currency_correct,
                    f"Stored as: {asset.get('price_currency')}",
                )
            )
        except Exception as e:
            checks.append(("Default to EUR when not specified", False, str(e)))

        # Test invalid currency rejection
        try:
            db.add_asset(
                ticker="TEST",
                quantity=1.0,
                price_buy=100.00,
                date_buy="2024-01-01",
                asset_type="crypto",
                price_currency="GBP",  # Invalid
            )
            checks.append(
                ("Reject invalid currency", False, "Should have raised ValueError")
            )
        except ValueError:
            checks.append(
                (
                    "Reject invalid currency",
                    True,
                    "Correctly raised ValueError for 'GBP'",
                )
            )
        except Exception as e:
            checks.append(
                (
                    "Reject invalid currency",
                    False,
                    f"Wrong exception type: {type(e).__name__}",
                )
            )

        # Clean up temp database
        Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        checks.append(("Database operations", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_migration_script():
    """Check if migration script exists and is runnable."""
    print_header("Checking Migration Script")

    checks = []

    script_path = Path(__file__).parent / "migrate_add_price_currency.py"

    checks.append(("Migration script exists", script_path.exists(), str(script_path)))

    if script_path.exists():
        try:
            with open(script_path, "r") as f:
                content = f.read()

            has_backup = "backup_database" in content
            has_add_column = (
                "ALTER TABLE assets" in content or "price_currency" in content
            )
            has_verification = (
                "verify_migration" in content or "verify" in content.lower()
            )

            checks.append(
                (
                    "Script has backup function",
                    has_backup,
                    "Creates database backup before migration",
                )
            )
            checks.append(
                ("Script adds column", has_add_column, "Adds price_currency column")
            )
            checks.append(
                (
                    "Script has verification",
                    has_verification,
                    "Verifies migration success",
                )
            )

        except Exception as e:
            checks.append(("Migration script readable", False, str(e)))

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def check_documentation():
    """Check if documentation files exist."""
    print_header("Checking Documentation")

    checks = []

    docs_dir = Path(__file__).parent.parent / "docs"

    doc_files = [
        ("User Guide", "USD_EUR_CRYPTO_GUIDE.md"),
        ("Quick Start", "USD_EUR_QUICKSTART.md"),
        ("Implementation Doc", "USD_EUR_IMPLEMENTATION.md"),
    ]

    for name, filename in doc_files:
        file_path = docs_dir / filename
        exists = file_path.exists()
        checks.append(
            (name, exists, str(file_path) if exists else f"Not found: {filename}")
        )

    for check in checks:
        print_check(*check)

    return all(c[1] for c in checks)


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  PRISM USD/EUR FEATURE - VERIFICATION SCRIPT")
    print("=" * 70)
    print(f"\nVerification started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis script will verify that the USD/EUR crypto feature is")
    print("properly installed and all components are functioning.\n")

    results = {}

    # Run all checks
    results["Imports"] = check_imports()
    results["Database Schema"] = check_database_schema()
    results["API Connectivity"] = check_api_connectivity()
    results["CryptoAPI USD"] = check_crypto_api_usd()
    results["Database Operations"] = check_database_operations()
    results["Migration Script"] = check_migration_script()
    results["Documentation"] = check_documentation()

    # Summary
    print_header("VERIFICATION SUMMARY")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for category, result in results.items():
        print_check(category, result)

    print(f"\nTotal Categories: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n✓ All checks passed! USD/EUR feature is properly installed.")
        print("\nYou can now:")
        print("  1. Run the demo: python scripts/demo_usd_eur_feature.py")
        print("  2. Run tests: python scripts/test_usd_eur_feature.py")
        print("  3. Launch Prism: python -m prism")
        return 0
    else:
        print(f"\n⚠ {failed} category(ies) failed. Please review the issues above.")
        print("\nTroubleshooting:")
        print(
            "  1. Check that you've run: python scripts/migrate_add_price_currency.py"
        )
        print("  2. Verify all dependencies: pip install -r requirements.txt")
        print("  3. Check database location: ~/Library/Application Support/Prism/")
        print("  4. Review docs/USD_EUR_CRYPTO_GUIDE.md for setup help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
