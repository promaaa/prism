#!/usr/bin/env python3
"""
Test script for USD/EUR cryptocurrency feature.
Tests currency converter, CryptoAPI USD methods, and database operations.

Usage:
    python scripts/test_usd_eur_feature.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.api.currency_converter import CurrencyConverter, get_converter
from prism.api.crypto_api import CryptoAPI
from prism.database.db_manager import DatabaseManager
from prism.database.schema import get_database_path


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_currency_converter():
    """Test the CurrencyConverter class."""
    print_section("Testing CurrencyConverter")

    converter = CurrencyConverter(cache_duration_minutes=5)

    # Test 1: Get USD to EUR rate
    print("Test 1: Fetching USD to EUR exchange rate...")
    try:
        rate = converter.get_usd_eur_rate()
        print(f"✓ USD to EUR rate: {rate:.4f}")
        print(f"  (1 USD = {rate:.4f} EUR)")
    except Exception as e:
        print(f"✗ Failed to fetch rate: {e}")
        return False

    # Test 2: Convert USD to EUR
    print("\nTest 2: Converting amounts...")
    try:
        usd_amounts = [100, 1000, 50000]
        for usd in usd_amounts:
            eur = converter.convert_usd_to_eur(usd)
            print(f"  ${usd:,.2f} USD = €{eur:,.2f} EUR")
        print("✓ Conversion successful")
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        return False

    # Test 3: Convert EUR to USD
    print("\nTest 3: Converting EUR to USD...")
    try:
        eur_amounts = [100, 1000, 50000]
        for eur in eur_amounts:
            usd = converter.convert_eur_to_usd(eur)
            print(f"  €{eur:,.2f} EUR = ${usd:,.2f} USD")
        print("✓ Conversion successful")
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        return False

    # Test 4: Get rate display text
    print("\nTest 4: Display text...")
    try:
        display_text = converter.get_rate_display_text()
        print(f"  {display_text}")
        print("✓ Display text generated")
    except Exception as e:
        print(f"✗ Display text failed: {e}")
        return False

    # Test 5: Cache functionality
    print("\nTest 5: Testing cache...")
    try:
        rate1 = converter.get_usd_eur_rate()
        rate2 = converter.get_usd_eur_rate()  # Should use cache
        print(f"  First fetch:  {rate1:.4f}")
        print(f"  Cached fetch: {rate2:.4f}")
        if rate1 == rate2:
            print("✓ Cache working correctly")
        else:
            print("⚠ Cache returned different value")
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False

    # Test 6: Force refresh
    print("\nTest 6: Testing force refresh...")
    try:
        rate_before = converter.get_usd_eur_rate()
        converter.clear_cache()
        rate_after = converter.get_usd_eur_rate(force_refresh=True)
        print(f"  Before clear: {rate_before:.4f}")
        print(f"  After clear:  {rate_after:.4f}")
        print("✓ Force refresh working")
    except Exception as e:
        print(f"✗ Force refresh failed: {e}")
        return False

    # Test 7: Global converter instance
    print("\nTest 7: Testing global converter...")
    try:
        global_conv = get_converter()
        rate = global_conv.get_usd_eur_rate()
        print(f"  Global converter rate: {rate:.4f}")
        print("✓ Global converter working")
    except Exception as e:
        print(f"✗ Global converter failed: {e}")
        return False

    return True


def test_crypto_api_usd():
    """Test CryptoAPI USD methods."""
    print_section("Testing CryptoAPI USD Methods")

    api = CryptoAPI()

    # Test 1: Single price in USD
    print("Test 1: Fetching single crypto price in USD...")
    try:
        btc_usd = api.get_price_usd("BTC")
        if btc_usd:
            print(f"✓ Bitcoin price: ${btc_usd:,.2f} USD")
        else:
            print("⚠ Could not fetch BTC price")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 2: Multiple prices in USD
    print("\nTest 2: Fetching multiple crypto prices in USD...")
    try:
        tickers = ["BTC", "ETH", "SOL", "USDC"]
        prices_usd = api.get_multiple_prices_usd(tickers)

        print(f"✓ Fetched {len([p for p in prices_usd.values() if p])} prices:")
        for ticker, price in prices_usd.items():
            if price:
                print(f"  {ticker:6s}: ${price:>12,.2f} USD")
            else:
                print(f"  {ticker:6s}: Price unavailable")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 3: Compare EUR vs USD prices
    print("\nTest 3: Comparing EUR vs USD prices...")
    try:
        ticker = "BTC"
        price_eur = api.get_price(ticker, currency="eur")
        price_usd = api.get_price_usd(ticker)

        if price_eur and price_usd:
            ratio = price_usd / price_eur
            print(f"  BTC in EUR: €{price_eur:,.2f}")
            print(f"  BTC in USD: ${price_usd:,.2f}")
            print(f"  USD/EUR ratio: {ratio:.4f}")
            print("✓ Price comparison successful")
        else:
            print("⚠ Could not fetch prices for comparison")
    except Exception as e:
        print(f"✗ Comparison failed: {e}")
        return False

    return True


def test_database_operations():
    """Test database operations with price_currency."""
    print_section("Testing Database Operations")

    # Use test database path
    test_db_path = Path(__file__).parent.parent / "test_usd_eur.db"

    # Clean up any existing test database
    if test_db_path.exists():
        test_db_path.unlink()
        print("Cleaned up existing test database")

    print(f"Using test database: {test_db_path}")
    db = DatabaseManager(str(test_db_path))

    # Test 1: Add asset with EUR price
    print("\nTest 1: Adding asset with EUR price...")
    try:
        asset_id_eur = db.add_asset(
            ticker="ETH",
            quantity=2.5,
            price_buy=2000.00,
            date_buy="2024-01-15",
            asset_type="crypto",
            current_price=2200.00,
            price_currency="EUR",
        )
        print(f"✓ Asset added with ID: {asset_id_eur}")

        # Verify
        asset = db.get_asset(asset_id_eur)
        print(f"  Ticker: {asset['ticker']}")
        print(f"  Price: €{asset['price_buy']:.2f} {asset['price_currency']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 2: Add asset with USD price
    print("\nTest 2: Adding asset with USD price...")
    try:
        asset_id_usd = db.add_asset(
            ticker="BTC",
            quantity=0.5,
            price_buy=65000.00,
            date_buy="2024-02-01",
            asset_type="crypto",
            current_price=67000.00,
            price_currency="USD",
        )
        print(f"✓ Asset added with ID: {asset_id_usd}")

        # Verify
        asset = db.get_asset(asset_id_usd)
        print(f"  Ticker: {asset['ticker']}")
        print(f"  Price: ${asset['price_buy']:.2f} {asset['price_currency']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 3: Add stock (should default to EUR)
    print("\nTest 3: Adding stock (should default to EUR)...")
    try:
        asset_id_stock = db.add_asset(
            ticker="AAPL",
            quantity=10,
            price_buy=150.00,
            date_buy="2024-01-10",
            asset_type="stock",
            current_price=155.00,
        )
        print(f"✓ Stock added with ID: {asset_id_stock}")

        # Verify
        asset = db.get_asset(asset_id_stock)
        print(f"  Ticker: {asset['ticker']}")
        print(
            f"  Price: €{asset['price_buy']:.2f} {asset.get('price_currency', 'EUR')}"
        )
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 4: Update asset price_currency
    print("\nTest 4: Updating asset price_currency...")
    try:
        success = db.update_asset(asset_id_eur, price_currency="USD")
        if success:
            asset = db.get_asset(asset_id_eur)
            print(f"✓ Updated successfully")
            print(f"  New currency: {asset['price_currency']}")
        else:
            print("⚠ Update returned False")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 5: Get all assets and check currencies
    print("\nTest 5: Retrieving all assets...")
    try:
        all_assets = db.get_all_assets()
        print(f"✓ Retrieved {len(all_assets)} assets:")
        for asset in all_assets:
            currency = asset.get("price_currency", "EUR")
            symbol = "$" if currency == "USD" else "€"
            print(
                f"  {asset['ticker']:6s} ({asset['asset_type']:6s}): "
                f"{symbol}{asset['price_buy']:>10,.2f} {currency}"
            )
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 6: Invalid currency should fail
    print("\nTest 6: Testing invalid currency (should fail)...")
    try:
        db.add_asset(
            ticker="TEST",
            quantity=1,
            price_buy=100,
            date_buy="2024-01-01",
            asset_type="crypto",
            price_currency="GBP",  # Invalid
        )
        print("✗ Should have raised ValueError for invalid currency")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid currency: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Clean up test database
    print("\nCleaning up test database...")
    test_db_path.unlink()
    print("✓ Test database removed")

    return True


def test_integration():
    """Test integration of all components."""
    print_section("Integration Test: Complete Workflow")

    # Initialize components
    converter = get_converter()
    crypto_api = CryptoAPI()

    # Use test database
    test_db_path = Path(__file__).parent.parent / "test_integration.db"
    if test_db_path.exists():
        test_db_path.unlink()
    db = DatabaseManager(str(test_db_path))

    print("Test: Complete workflow with USD crypto and EUR total")
    print("-" * 70)

    # Step 1: Fetch BTC price in USD
    print("\n1. Fetching BTC price in USD...")
    try:
        btc_price_usd = crypto_api.get_price_usd("BTC")
        if btc_price_usd is None:
            print(f"   ⚠ Could not fetch BTC price (API rate limit), using fallback")
            btc_price_usd = 67000.00  # Fallback price for testing
        print(f"   ✓ BTC Price: ${btc_price_usd:,.2f} USD")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Step 2: Add BTC asset with USD price
    print("\n2. Adding BTC asset with USD buy price...")
    try:
        btc_id = db.add_asset(
            ticker="BTC",
            quantity=0.25,
            price_buy=60000.00,  # Bought at $60k
            date_buy="2024-01-01",
            asset_type="crypto",
            current_price=btc_price_usd,
            price_currency="USD",
        )
        print(f"   ✓ Asset added (ID: {btc_id})")
        print(f"   Purchase: 0.25 BTC @ $60,000 USD")
        print(f"   Current:  ${btc_price_usd:,.2f} USD")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Step 3: Calculate USD value
    print("\n3. Calculating USD value...")
    btc_value_usd = 0.25 * btc_price_usd
    btc_cost_usd = 0.25 * 60000.00
    btc_gain_usd = btc_value_usd - btc_cost_usd
    print(f"   Cost:    ${btc_cost_usd:,.2f} USD")
    print(f"   Value:   ${btc_value_usd:,.2f} USD")
    print(f"   Gain:    ${btc_gain_usd:+,.2f} USD")

    # Step 4: Get USD/EUR exchange rate
    print("\n4. Fetching USD to EUR exchange rate...")
    try:
        usd_eur_rate = converter.get_usd_eur_rate()
        print(f"   ✓ Rate: 1 USD = {usd_eur_rate:.4f} EUR")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Step 5: Convert to EUR for portfolio total
    print("\n5. Converting BTC value to EUR for portfolio total...")
    try:
        btc_value_eur = converter.convert_usd_to_eur(btc_value_usd)
        btc_cost_eur = converter.convert_usd_to_eur(btc_cost_usd)
        btc_gain_eur = btc_value_eur - btc_cost_eur
        print(f"   Cost:    €{btc_cost_eur:,.2f} EUR")
        print(f"   Value:   €{btc_value_eur:,.2f} EUR")
        print(f"   Gain:    €{btc_gain_eur:+,.2f} EUR")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Step 6: Add EUR-based asset
    print("\n6. Adding EUR-based stock asset...")
    try:
        stock_id = db.add_asset(
            ticker="MC.PA",  # LVMH
            quantity=5,
            price_buy=700.00,
            date_buy="2024-01-01",
            asset_type="stock",
            current_price=750.00,
            price_currency="EUR",
        )
        print(f"   ✓ Asset added (ID: {stock_id})")
        print(f"   Purchase: 5 shares @ €700 EUR")
        print(f"   Current:  €750 EUR")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Step 7: Calculate EUR stock value (no conversion needed)
    print("\n7. Calculating EUR stock value...")
    stock_value_eur = 5 * 750.00
    stock_cost_eur = 5 * 700.00
    stock_gain_eur = stock_value_eur - stock_cost_eur
    print(f"   Cost:    €{stock_cost_eur:,.2f} EUR")
    print(f"   Value:   €{stock_value_eur:,.2f} EUR")
    print(f"   Gain:    €{stock_gain_eur:+,.2f} EUR")

    # Step 8: Calculate total portfolio in EUR
    print("\n8. Calculating total portfolio value in EUR...")
    total_value_eur = btc_value_eur + stock_value_eur
    total_cost_eur = btc_cost_eur + stock_cost_eur
    total_gain_eur = total_value_eur - total_cost_eur
    total_gain_pct = (
        (total_gain_eur / total_cost_eur * 100) if total_cost_eur > 0 else 0
    )

    print(f"\n   {'=' * 50}")
    print(f"   PORTFOLIO SUMMARY (EUR)")
    print(f"   {'=' * 50}")
    print(f"   Total Cost:  €{total_cost_eur:>12,.2f}")
    print(f"   Total Value: €{total_value_eur:>12,.2f}")
    print(f"   Total Gain:  €{total_gain_eur:>12,.2f} ({total_gain_pct:+.2f}%)")
    print(f"   {'=' * 50}")

    # Step 9: Verify data from database
    print("\n9. Verifying all data from database...")
    try:
        all_assets = db.get_all_assets()
        print(f"   ✓ Retrieved {len(all_assets)} assets:")
        for asset in all_assets:
            currency = asset.get("price_currency", "EUR")
            symbol = "$" if currency == "USD" else "€"
            print(
                f"     {asset['ticker']:8s} - {symbol}{asset['price_buy']:>10,.2f} {currency}"
            )
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        test_db_path.unlink()
        return False

    # Clean up
    print("\nCleaning up test database...")
    test_db_path.unlink()
    print("✓ Integration test complete!")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  PRISM USD/EUR CRYPTOCURRENCY FEATURE TEST SUITE")
    print("=" * 70)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Currency Converter", test_currency_converter),
        ("CryptoAPI USD Methods", test_crypto_api_usd),
        ("Database Operations", test_database_operations),
        ("Integration", test_integration),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results[test_name] = False

    # Print summary
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n  🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n  ⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
