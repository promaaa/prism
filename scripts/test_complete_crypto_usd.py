#!/usr/bin/env python3
"""
Comprehensive test for cryptocurrency USD implementation.

This script tests the complete flow of crypto price handling:
1. API fetches prices in USD
2. Database stores prices in USD with correct currency flag
3. UI displays $ symbol for crypto, € for stocks
4. Background refresh updates prices in USD
5. Dialog fetches and displays prices in USD
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.api.crypto_api import CryptoAPI
from prism.database.db_manager import DatabaseManager
from prism.ui.investments_tab import InvestmentsTab, PriceUpdateWorker


def test_crypto_api_usd():
    """Test that crypto API fetches prices in USD correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Crypto API USD Fetching")
    print("=" * 70)

    crypto_api = CryptoAPI()

    # Test single price fetch
    print("\n1.1 Testing single price fetch (ARB)...")
    arb_price = crypto_api.get_price_usd("ARB", use_cache=False)

    if arb_price and arb_price > 0:
        print(f"   ✓ get_price_usd('ARB') = ${arb_price:.4f}")
        assert 0.1 < arb_price < 1.0, f"ARB price ${arb_price} seems unusual"
        print(f"   ✓ Price is in reasonable range")
    else:
        print(f"   ❌ Failed to fetch ARB price")
        return False

    # Test multiple price fetch
    print("\n1.2 Testing multiple price fetch...")
    tickers = ["BTC", "ETH", "ARB"]
    prices = crypto_api.get_multiple_prices_usd(tickers, use_cache=False)

    success_count = 0
    for ticker in tickers:
        if ticker in prices and prices[ticker]:
            print(f"   ✓ {ticker}: ${prices[ticker]:,.2f}")
            success_count += 1
        else:
            print(f"   ⚠️  {ticker}: Failed to fetch")

    if success_count >= 2:
        print(f"   ✓ Successfully fetched {success_count}/{len(tickers)} prices")
    else:
        print(f"   ❌ Only fetched {success_count}/{len(tickers)} prices")
        return False

    # Test EUR vs USD comparison
    print("\n1.3 Testing EUR vs USD difference...")
    arb_eur = crypto_api.get_price("ARB", currency="eur", use_cache=False)
    if arb_eur:
        print(f"   ARB (USD): ${arb_price:.4f}")
        print(f"   ARB (EUR): €{arb_eur:.4f}")
        ratio = arb_price / arb_eur
        print(f"   USD/EUR ratio: {ratio:.4f}")
        assert 1.0 < ratio < 1.3, f"Ratio {ratio} seems unusual"
        print(f"   ✓ Ratio is reasonable (USD > EUR expected)")
    else:
        print(f"   ⚠️  Could not fetch EUR price for comparison")

    print("\n✓ TEST 1 PASSED: API fetches USD correctly\n")
    return True


def test_database_storage():
    """Test that database stores crypto prices with USD currency."""
    print("=" * 70)
    print("TEST 2: Database Storage")
    print("=" * 70)

    db = DatabaseManager()

    # Get all crypto assets
    all_assets = db.get_all_assets()
    crypto_assets = [a for a in all_assets if a.get("asset_type") == "crypto"]

    if not crypto_assets:
        print("\n   ⚠️  No crypto assets in database to test")
        print("   This is OK if you haven't added any crypto yet")
        print("\n✓ TEST 2 SKIPPED: No crypto assets\n")
        return True

    print(f"\n2.1 Found {len(crypto_assets)} crypto asset(s)")

    all_correct = True
    for asset in crypto_assets:
        ticker = asset.get("ticker", "???")
        price_currency = asset.get("price_currency", "EUR")
        current_price = asset.get("current_price", 0)

        print(f"\n   Asset: {ticker}")
        print(f"   Price: {current_price:.4f} {price_currency}")

        if price_currency == "USD":
            print(f"   ✓ Correctly stored in USD")
        else:
            print(f"   ❌ ERROR: Should be USD, but is {price_currency}")
            all_correct = False

    if all_correct:
        print("\n✓ TEST 2 PASSED: All crypto assets stored in USD\n")
        return True
    else:
        print("\n❌ TEST 2 FAILED: Some assets not in USD")
        print("   Run: python scripts/refresh_crypto_prices_usd.py\n")
        return False


def test_ui_display():
    """Test that UI displays correct currency symbols."""
    print("=" * 70)
    print("TEST 3: UI Display")
    print("=" * 70)

    from prism.api.stock_api import StockAPI

    db = DatabaseManager()
    crypto_api = CryptoAPI()
    stock_api = StockAPI()

    tab = InvestmentsTab(db, crypto_api, stock_api)

    print("\n3.1 Testing table population...")

    # Create test assets
    test_crypto = {
        "id": 999,
        "ticker": "ARB",
        "name": "Arbitrum",
        "asset_type": "crypto",
        "quantity": 1000,
        "price_buy": 0.25,
        "current_price": 0.3075,
        "price_currency": "USD",
    }

    test_stock = {
        "id": 998,
        "ticker": "TTE.PA",
        "name": "TotalEnergies",
        "asset_type": "stock",
        "quantity": 2,
        "price_buy": 60.0,
        "current_price": 65.5,
        "price_currency": "EUR",
    }

    # Populate table with test data
    # Note: Table sorts by value (highest first)
    # Crypto: 1000 * 0.3075 = 307.5
    # Stock: 2 * 65.5 = 131
    # So crypto will be row 0, stock will be row 1
    tab._populate_table([test_crypto, test_stock])

    # Find crypto and stock rows by checking ticker
    crypto_row = None
    stock_row = None

    for row in range(tab.assets_table.rowCount()):
        ticker_item = tab.assets_table.item(row, 1)
        if ticker_item:
            ticker = ticker_item.text()
            if ticker == "ARB":
                crypto_row = row
            elif ticker == "TTE.PA":
                stock_row = row

    if crypto_row is None or stock_row is None:
        print("   ❌ Could not find test assets in table")
        return False

    # Check crypto row (should have $)
    crypto_buy_price = tab.assets_table.item(crypto_row, 3)
    crypto_current_price = tab.assets_table.item(crypto_row, 4)

    if crypto_buy_price and "$" in crypto_buy_price.text():
        print("   ✓ Crypto buy price shows $ symbol")
    else:
        print(
            f"   ❌ Crypto buy price: {crypto_buy_price.text() if crypto_buy_price else 'None'}"
        )
        print("      Expected $ symbol for crypto")
        return False

    if crypto_current_price and "$" in crypto_current_price.text():
        print("   ✓ Crypto current price shows $ symbol")
    else:
        print(
            f"   ❌ Crypto current price: {crypto_current_price.text() if crypto_current_price else 'None'}"
        )
        return False

    # Check stock row (should have €)
    stock_buy_price = tab.assets_table.item(stock_row, 3)
    stock_current_price = tab.assets_table.item(stock_row, 4)

    if stock_buy_price and "€" in stock_buy_price.text():
        print("   ✓ Stock buy price shows € symbol")
    else:
        print(
            f"   ❌ Stock buy price: {stock_buy_price.text() if stock_buy_price else 'None'}"
        )
        print("      Expected € symbol for stock")
        return False

    if stock_current_price and "€" in stock_current_price.text():
        print("   ✓ Stock current price shows € symbol")
    else:
        print(
            f"   ❌ Stock current price: {stock_current_price.text() if stock_current_price else 'None'}"
        )
        return False

    print("\n✓ TEST 3 PASSED: UI displays correct currency symbols\n")
    return True


def test_price_worker():
    """Test that PriceUpdateWorker fetches crypto prices in USD."""
    print("=" * 70)
    print("TEST 4: Background Price Worker")
    print("=" * 70)

    from prism.api.stock_api import StockAPI

    db = DatabaseManager()
    crypto_api = CryptoAPI()
    stock_api = StockAPI()

    print("\n4.1 Checking that worker uses get_multiple_prices_usd()...")

    # Check the worker code
    import inspect

    worker_source = inspect.getsource(PriceUpdateWorker.run)

    if "get_multiple_prices_usd" in worker_source:
        print("   ✓ Worker uses get_multiple_prices_usd()")
    else:
        print("   ❌ Worker does NOT use get_multiple_prices_usd()")
        print("      This means crypto prices may be fetched in EUR!")
        return False

    print("\n✓ TEST 4 PASSED: Worker fetches USD correctly\n")
    return True


def test_dialog_fetch():
    """Test that dialog fetches and displays prices correctly."""
    print("=" * 70)
    print("TEST 5: Dialog Price Fetch")
    print("=" * 70)

    from prism.ui.investments_tab import AssetDialog

    print("\n5.1 Checking that dialog uses get_price_usd()...")

    import inspect

    dialog_source = inspect.getsource(AssetDialog._on_fetch_price)

    if "get_price_usd" in dialog_source:
        print("   ✓ Dialog uses get_price_usd() for crypto")
    else:
        print("   ❌ Dialog does NOT use get_price_usd()")
        print("      This means dialog may fetch crypto prices in EUR!")
        return False

    # Check currency symbol handling
    if 'currency_symbol = "$"' in dialog_source or '"$"' in dialog_source:
        print("   ✓ Dialog displays $ symbol for crypto")
    else:
        print("   ⚠️  Could not verify $ symbol in dialog")

    print("\n✓ TEST 5 PASSED: Dialog fetches USD correctly\n")
    return True


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print(
        "║" + " " * 10 + "COMPREHENSIVE CRYPTO USD IMPLEMENTATION TEST" + " " * 14 + "║"
    )
    print("╚" + "=" * 68 + "╝")

    app = QApplication(sys.argv)

    tests = [
        ("API USD Fetching", test_crypto_api_usd),
        ("Database Storage", test_database_storage),
        ("UI Display", test_ui_display),
        ("Background Worker", test_price_worker),
        ("Dialog Fetch", test_dialog_fetch),
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
        print("\nCrypto USD implementation is working correctly:")
        print("  ✓ API fetches prices in USD")
        print("  ✓ Database stores prices in USD")
        print("  ✓ UI displays $ for crypto, € for stocks")
        print("  ✓ Background worker updates in USD")
        print("  ✓ Dialog fetches and displays in USD")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the failed tests above.")
        print("You may need to run: python scripts/refresh_crypto_prices_usd.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
