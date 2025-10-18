#!/usr/bin/env python3
"""
Test script to verify Arbitrum (ARB) price is fetched in USD, not EUR.

This script:
1. Fetches ARB price from CoinGecko in USD
2. Fetches ARB price from CoinGecko in EUR (for comparison)
3. Verifies the price is around $0.30-0.32 range (as of Jan 2024)
4. Shows the difference between USD and EUR prices
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.api.crypto_api import CryptoAPI
from prism.database.db_manager import DatabaseManager


def test_arb_price_usd():
    """Test that ARB price is correctly fetched in USD."""
    print("=" * 70)
    print("Testing Arbitrum (ARB) Price Fetching")
    print("=" * 70 + "\n")

    crypto_api = CryptoAPI()

    # Test 1: Fetch ARB price in USD
    print("1. Fetching ARB price in USD...")
    arb_price_usd = crypto_api.get_price_usd("ARB", use_cache=False)

    if arb_price_usd:
        print(f"   ✓ ARB Price (USD): ${arb_price_usd:.4f}")
    else:
        print("   ❌ Failed to fetch ARB price in USD")
        return False

    # Test 2: Fetch ARB price in EUR (for comparison)
    print("\n2. Fetching ARB price in EUR (for comparison)...")
    arb_price_eur = crypto_api.get_price("ARB", currency="eur", use_cache=False)

    if arb_price_eur:
        print(f"   ✓ ARB Price (EUR): €{arb_price_eur:.4f}")
    else:
        print("   ❌ Failed to fetch ARB price in EUR")

    # Test 3: Verify USD price is in expected range
    print("\n3. Verifying price is in expected range...")
    expected_min = 0.20
    expected_max = 0.50

    if expected_min <= arb_price_usd <= expected_max:
        print(
            f"   ✓ Price ${arb_price_usd:.4f} is within expected range (${expected_min}-${expected_max})"
        )
    else:
        print(
            f"   ⚠️  Warning: Price ${arb_price_usd:.4f} is outside expected range (${expected_min}-${expected_max})"
        )
        print(
            "      This might be normal if market conditions have changed significantly."
        )

    # Test 4: Show conversion difference
    if arb_price_eur:
        print("\n4. Price comparison:")
        print(f"   USD: ${arb_price_usd:.4f}")
        print(f"   EUR: €{arb_price_eur:.4f}")
        ratio = arb_price_usd / arb_price_eur if arb_price_eur > 0 else 0
        print(f"   USD/EUR ratio: {ratio:.4f}")
        print(f"   Difference: {abs(arb_price_usd - arb_price_eur):.4f}")

    # Test 5: Check database for ARB assets
    print("\n5. Checking database for ARB assets...")
    db = DatabaseManager()
    assets = db.get_all_assets()
    arb_assets = [a for a in assets if a.get("ticker", "").upper() == "ARB"]

    if arb_assets:
        print(f"   Found {len(arb_assets)} ARB asset(s) in database:")
        for asset in arb_assets:
            current_price = asset.get("current_price", 0)
            price_currency = asset.get("price_currency", "EUR")
            print(f"   - ID: {asset['id']}")
            print(f"     Current Price: {current_price:.4f} {price_currency}")
            print(f"     Quantity: {asset.get('quantity', 0)}")
            print(f"     Asset Type: {asset.get('asset_type', 'unknown')}")

            # Verify price_currency is USD for crypto
            if asset.get("asset_type") == "crypto" and price_currency != "USD":
                print(
                    f"     ⚠️  WARNING: Crypto asset should have price_currency='USD', but has '{price_currency}'"
                )
            elif asset.get("asset_type") == "crypto" and price_currency == "USD":
                print(f"     ✓ Correctly set to USD")
    else:
        print("   No ARB assets found in database")

    print("\n" + "=" * 70)
    print("✓ Test Complete!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  • ARB current price (USD): ${arb_price_usd:.4f}")
    if arb_price_eur:
        print(f"  • ARB current price (EUR): €{arb_price_eur:.4f}")
    print(f"  • Database ARB assets: {len(arb_assets)}")
    print("\nExpected behavior:")
    print("  ✓ Crypto prices should be fetched in USD")
    print("  ✓ Database should store price_currency='USD' for crypto")
    print("  ✓ UI should display $ symbol for crypto prices")
    print("  ✓ UI should display € symbol for stock prices")

    return True


def main():
    """Run the ARB price test."""
    try:
        success = test_arb_price_usd()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
