#!/usr/bin/env python
# coding: utf-8

"""
Utilis pour importer les actifs boursiers initiaux dans Prism.

Ce script importe les données initiales pour les actions boursières depuis la saisie fournie par l'utilisateur.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prism.database.db_manager import DatabaseManager
from prism.api.stock_api import StockAPI


def parse_french_date(date_str):
    """Convert French date format (DD/MM/YYYY) to ISO format (YYYY-MM-DD).

    Args:
        date_str: Date string like "24/06/2025"

    Returns:
        str: Date in ISO format like "2025-06-24"
    """
    day, month, year = date_str.split("/")
    return f"{year}-{month}-{day}"


def parse_french_number(value_str):
    """Parse a French-formatted number (comma as decimal separator, space as thousands).

    Args:
        value_str: String like "14 028,86" or "52,75"

    Returns:
        float: The parsed number
    """
    # Remove spaces and replace comma with period
    cleaned = value_str.strip().replace(" ", "").replace(",", ".")
    return float(cleaned)


def import_initial_stocks():
    """Import initial stock assets from the user's portfolio."""

    # Stock data from user's portfolio (exact data provided)
    # name, quantity, buyingPrice, amount in €, buyingDate
    stocks = [
        {
            "name": "TOTALENERGIES",
            "ticker": "TTE.PA",  # TotalEnergies on Euronext Paris
            "quantity": 266,
            "buy_price": 52.75,  # €
            "amount_eur": 14020.86,  # Total value
            "buy_date": "2025-06-24",  # Converted from 24/06/2025
        },
        {
            "name": "SCHNEIDER ELECTRIC",
            "ticker": "SU.PA",  # Schneider Electric on Euronext Paris
            "quantity": 17,
            "buy_price": 215.42,
            "amount_eur": 4183.70,
            "buy_date": "2025-06-23",  # Converted from 23/06/2025
        },
        {
            "name": "KERING",
            "ticker": "KER.PA",  # Kering on Euronext Paris
            "quantity": 5,
            "buy_price": 171.94,
            "amount_eur": 1547.75,
            "buy_date": "2025-05-20",  # Converted from 20/05/2025
        },
        {
            "name": "AMUNDI PEA S&P 500 UCITS ETF",
            "ticker": "PAEM.PA",  # AMUNDI PEA S&P 500 UCITS ETF on Euronext Paris
            "quantity": 28,
            "buy_price": 44.05,
            "amount_eur": 1385.74,
            "buy_date": "2025-05-06",  # Converted from 06/05/2025
        },
        {
            "name": "SAINT-GOBAIN",
            "ticker": "SGO.PA",  # Saint-Gobain on Euronext Paris
            "quantity": 4,
            "buy_price": 88.85,
            "amount_eur": 358.00,
            "buy_date": "2025-04-03",  # Converted from 03/04/2025
        },
    ]

    # Connect to database
    db_path = os.path.expanduser("~/Library/Application Support/Prism/prism.db")

    # Check if database directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)

    db = DatabaseManager(db_path)

    # Create StockAPI instance for fetching current prices
    stock_api = StockAPI()

    print("\n📈 Importing Initial Stock Assets")
    print("=" * 70)
    print(f"Database: {db_path}")
    print(f"Number of stocks to import: {len(stocks)}\n")

    imported_count = 0
    errors = []

    for i, stock in enumerate(stocks, 1):
        ticker = stock["ticker"]
        name = stock["name"]
        quantity = stock["quantity"]
        buy_price = stock["buy_price"]
        buy_date = stock["buy_date"]

        print(f"\n{i}. 📊 {name} ({ticker})")
        print(f"   Quantity:    {quantity:>10}")
        print(f"   Buy Price:   €{buy_price:>9.2f}")
        print(f"   Total Value: €{stock['amount_eur']:>9.2f}")
        print(f"   Buy Date:    {buy_date}")

        # Try to fetch current market price
        print(f"   Fetching current price...", end=" ", flush=True)
        current_price = stock_api.get_price(ticker)

        if current_price and current_price > 0:
            print(f"✓ €{current_price:.2f}")
            current_value = quantity * current_price
            gain_loss = current_value - stock["amount_eur"]
            gain_pct = (gain_loss / stock["amount_eur"]) * 100
            print(f"   Current Value: €{current_value:,.2f} ({gain_pct:+.2f}%)")
        else:
            # If we can't fetch current price, use buy price
            current_price = buy_price
            print(f"⚠️  Using buy price (€{buy_price:.2f})")

        try:
            # Add asset to database
            db.add_asset(
                ticker=ticker,
                quantity=quantity,
                price_buy=buy_price,
                date_buy=buy_date,
                current_price=current_price,
                asset_type="stock",  # All are stocks
                price_currency="EUR",  # All in Euros
            )
            print(f"   ✅ Successfully imported!")
            imported_count += 1

        except Exception as e:
            error_msg = f"{name} ({ticker}): {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ Error: {str(e)}")

    # Print summary
    print("\n" + "=" * 70)
    print(f"✅ Import Complete!")
    print(f"   Successfully imported: {imported_count}/{len(stocks)} assets")

    # Calculate totals
    total_invested = sum(s["amount_eur"] for s in stocks)
    print(f"   Total amount invested: €{total_invested:,.2f}")

    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors:
            print(f"   - {error}")

    return imported_count, len(stocks), errors


def main():
    """Main function."""
    try:
        print("\n🔐 Prism Stock Import Utility")
        print("=" * 70)
        print("This script will import your initial stock portfolio into Prism.\n")

        imported, total, errors = import_initial_stocks()

        print("\n" + "=" * 70)
        if imported == total:
            print("🎉 All stocks imported successfully!")
        elif imported > 0:
            print(f"⚠️  Partial import: {imported}/{total} stocks imported")
        else:
            print("❌ No stocks were imported")
            return 1

        print("\n💡 Next Steps:")
        print("   1. Launch Prism: python -m prism")
        print("   2. Click on '💼 Patrimoine' in the sidebar")
        print("   3. Your stocks will be displayed with current prices")
        print("\n   You can now:")
        print("   • Add more assets with '+ Add Asset' button")
        print("   • Update prices with '🔀 Refresh Prices' button")
        print("   • Delete assets by selecting rows and pressing Delete key")
        print("   • Edit assets by clicking the ✏️ edit button")

        return 0 if imported > 0 else 1

    except Exception as e:
        print(f"\n❌ Error importing stocks: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
