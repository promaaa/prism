#!/usr/bin/env python3
"""
This script fixes the cryptocurrency tickers in the database.
It removes the extra information from the ticker string, for example:
'ARB - ARBITRUM (SCALING SOLUTION)' -> 'ARB'
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.database.db_manager import DatabaseManager
from prism.utils.ticker_data import extract_ticker


def fix_tickers():
    """Fixes the crypto tickers in the database."""
    db = DatabaseManager()
    assets = db.get_all_assets()

    print(f"Found {len(assets)} assets to check.")

    fixed_count = 0
    for asset in assets:
        ticker = asset["ticker"]
        if " - " in ticker:
            new_ticker = extract_ticker(ticker)
            print(f"Fixing ticker: '{ticker}' -> '{new_ticker}'")
            db.update_asset_ticker(asset["id"], new_ticker)
            fixed_count += 1

    if fixed_count > 0:
        print(f"\nFixed {fixed_count} tickers.")
    else:
        print("\nNo tickers needed fixing.")


if __name__ == "__main__":
    fix_tickers()
