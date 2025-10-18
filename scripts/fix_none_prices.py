#!/usr/bin/env python3
"""
Fix None prices in database.

This script updates assets that have NULL/None current_price by:
1. Setting current_price to price_buy as a fallback
2. Optionally fetching real current prices from API if available

Usage:
    python scripts/fix_none_prices.py [--fetch-real] [--dry-run]

Options:
    --fetch-real    Attempt to fetch real current prices from API
    --dry-run       Show what would be updated without making changes
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.db_manager import DatabaseManager
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI


def fix_none_prices(fetch_real: bool = False, dry_run: bool = False):
    """
    Fix assets with None current_price.

    Args:
        fetch_real: If True, attempt to fetch real prices from API
        dry_run: If True, don't make actual changes
    """
    print("=" * 70)
    print("Fixing None Prices in Database")
    print("=" * 70)
    print(f"Fetch real prices: {fetch_real}")
    print(f"Dry run: {dry_run}")
    print()

    db = DatabaseManager()
    assets = db.get_all_assets()

    if not assets:
        print("No assets found in database.")
        return

    # Find assets with None current_price
    none_price_assets = [a for a in assets if a.get("current_price") is None]

    if not none_price_assets:
        print("✓ All assets have current_price set. Nothing to fix!")
        return

    print(f"Found {len(none_price_assets)} assets with None current_price:\n")

    # Initialize APIs if needed
    crypto_api = CryptoAPI() if fetch_real else None
    stock_api = StockAPI() if fetch_real else None

    updated_count = 0
    failed_count = 0

    for asset in none_price_assets:
        asset_id = asset["id"]
        ticker = asset["ticker"]
        asset_type = asset.get("asset_type", "unknown")
        price_buy = asset.get("price_buy", 0)

        print(f"  {ticker} (ID: {asset_id}, Type: {asset_type})")
        print(f"    Current price: None")
        print(f"    Buy price: €{price_buy:,.2f}")

        new_price = None

        if fetch_real:
            # Try to fetch real current price
            try:
                if asset_type == "crypto":
                    print(f"    Fetching current crypto price...")
                    crypto_data = crypto_api.get_crypto_data(ticker)
                    if crypto_data and "current_price" in crypto_data:
                        new_price = crypto_data["current_price"]
                        print(f"    ✓ Fetched price: €{new_price:,.2f}")
                elif asset_type == "stock":
                    print(f"    Fetching current stock price...")
                    stock_data = stock_api.get_stock_data(ticker)
                    if stock_data and "current_price" in stock_data:
                        new_price = stock_data["current_price"]
                        print(f"    ✓ Fetched price: €{new_price:,.2f}")
                else:
                    print(f"    ⚠ Unknown asset type, using buy price as fallback")
            except Exception as e:
                print(f"    ⚠ Failed to fetch price: {e}")

        # Fallback to buy price if we couldn't fetch real price
        if new_price is None:
            new_price = price_buy
            print(f"    → Using buy price as fallback: €{new_price:,.2f}")

        # Update the database
        if dry_run:
            print(f"    [DRY RUN] Would update current_price to: €{new_price:,.2f}")
            updated_count += 1
        else:
            try:
                success = db.update_asset(asset_id=asset_id, current_price=new_price)
                if success:
                    print(f"    ✓ Updated current_price to: €{new_price:,.2f}")
                    updated_count += 1
                else:
                    print(f"    ✗ Failed to update (unknown reason)")
                    failed_count += 1
            except Exception as e:
                print(f"    ✗ Failed to update: {e}")
                failed_count += 1

        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total assets checked: {len(assets)}")
    print(f"Assets with None price: {len(none_price_assets)}")
    if dry_run:
        print(f"Would update: {updated_count}")
    else:
        print(f"Successfully updated: {updated_count}")
        print(f"Failed to update: {failed_count}")
    print()

    if dry_run:
        print("ℹ This was a dry run. No changes were made.")
        print("Run without --dry-run to apply changes.")
    elif updated_count > 0:
        print("✓ Database updated successfully!")
        print("You can now run the application without price-related errors.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Fix assets with None current_price in database"
    )
    parser.add_argument(
        "--fetch-real",
        action="store_true",
        help="Attempt to fetch real current prices from API (requires API access)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )

    args = parser.parse_args()

    try:
        fix_none_prices(fetch_real=args.fetch_real, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
