#!/usr/bin/env python3
"""
Script to refresh all cryptocurrency prices in the database to USD.

This script:
1. Fetches all crypto assets from the database
2. Gets current prices in USD from CoinGecko
3. Updates the database with USD prices
4. Sets price_currency to 'USD' for all crypto assets
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.api.crypto_api import CryptoAPI
from prism.database.db_manager import DatabaseManager


def refresh_crypto_prices():
    """Refresh all cryptocurrency prices to USD."""
    print("=" * 70)
    print("Refreshing Cryptocurrency Prices (USD)")
    print("=" * 70 + "\n")

    # Initialize API and database
    crypto_api = CryptoAPI()
    db = DatabaseManager()

    # Get all assets
    all_assets = db.get_all_assets()
    crypto_assets = [a for a in all_assets if a.get("asset_type") == "crypto"]

    if not crypto_assets:
        print("No cryptocurrency assets found in database.")
        return

    print(f"Found {len(crypto_assets)} cryptocurrency asset(s)\n")

    # Get all tickers
    tickers = list(set([asset["ticker"] for asset in crypto_assets]))
    print(
        f"Fetching prices for {len(tickers)} unique ticker(s): {', '.join(tickers)}\n"
    )

    # Fetch all prices in USD
    prices = crypto_api.get_multiple_prices_usd(tickers, use_cache=False)

    # Update each asset
    updated = 0
    failed = 0

    for asset in crypto_assets:
        ticker = asset["ticker"]
        asset_id = asset["id"]
        old_price = asset.get("current_price", 0)
        old_currency = asset.get("price_currency", "EUR")

        print(f"Processing {ticker} (ID: {asset_id})...")

        if ticker in prices and prices[ticker] is not None:
            new_price = prices[ticker]

            # Update price in database
            try:
                # Update the price
                db.update_asset_price(asset_id, new_price)

                # Update price_currency to USD for crypto assets
                conn = db._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE assets SET price_currency = 'USD' WHERE id = ?",
                    (asset_id,),
                )
                conn.commit()
                conn.close()

                print(f"  ✓ Updated: {old_currency}{old_price:.4f} → ${new_price:.4f}")
                updated += 1
            except Exception as e:
                print(f"  ❌ Failed to update database: {e}")
                failed += 1
        else:
            print(f"  ❌ Could not fetch price for {ticker}")
            failed += 1

    print("\n" + "=" * 70)
    print("Refresh Complete!")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  ✓ Successfully updated: {updated}")
    print(f"  ❌ Failed: {failed}")
    print(f"  Total: {len(crypto_assets)}")

    if updated > 0:
        print("\n✓ All cryptocurrency prices are now in USD!")
        print("  - Prices stored in USD in database")
        print("  - UI will display $ symbol for crypto")
        print("  - Totals converted to EUR for portfolio summary")


def main():
    """Run the refresh script."""
    try:
        refresh_crypto_prices()
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
