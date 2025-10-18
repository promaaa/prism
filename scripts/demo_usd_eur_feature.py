#!/usr/bin/env python3
"""
Interactive demo script for USD/EUR cryptocurrency feature.
Demonstrates the complete workflow with sample data.

Usage:
    python scripts/demo_usd_eur_feature.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.api.currency_converter import get_converter
from prism.api.crypto_api import CryptoAPI
from prism.database.db_manager import DatabaseManager


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num: int, text: str):
    """Print a step number and description."""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 70)


def demo_currency_converter():
    """Demonstrate currency converter functionality."""
    print_header("DEMO: Currency Converter")

    converter = get_converter()

    print_step(1, "Fetching USD to EUR Exchange Rate")
    rate = converter.get_usd_eur_rate()
    print(f"✓ Current rate: 1 USD = {rate:.4f} EUR")
    print(f"  ({converter.get_rate_display_text()})")

    print_step(2, "Converting Sample Amounts")

    usd_amounts = [100, 1000, 50000, 100000]
    print("\nUSD → EUR:")
    for usd in usd_amounts:
        eur = converter.convert_usd_to_eur(usd)
        print(f"  ${usd:>8,} USD  =  €{eur:>10,.2f} EUR")

    print("\nEUR → USD:")
    eur_amounts = [100, 1000, 40000, 85000]
    for eur in eur_amounts:
        usd = converter.convert_eur_to_usd(eur)
        print(f"  €{eur:>8,} EUR  =  ${usd:>10,.2f} USD")

    print("\n✓ Currency conversion working correctly!")


def demo_crypto_api_usd():
    """Demonstrate CryptoAPI USD methods."""
    print_header("DEMO: CryptoAPI USD Price Fetching")

    api = CryptoAPI()

    print_step(1, "Fetching Single Crypto Price in USD")

    ticker = "BTC"
    price_eur = api.get_price(ticker, currency="eur")
    price_usd = api.get_price_usd(ticker)

    if price_eur and price_usd:
        print(f"✓ Bitcoin (BTC):")
        print(f"  EUR price: €{price_eur:>10,.2f}")
        print(f"  USD price: ${price_usd:>10,.2f}")
        print(f"  Ratio:     {price_usd / price_eur:.4f}")
    else:
        print("⚠ Could not fetch prices (API rate limit)")
        print("  Using demo values for illustration:")
        price_usd = 67000.00
        price_eur = 57500.00
        print(f"  BTC (USD): ${price_usd:,.2f}")
        print(f"  BTC (EUR): €{price_eur:,.2f}")

    print_step(2, "Fetching Multiple Crypto Prices in USD")

    tickers = ["BTC", "ETH", "SOL", "USDC"]
    prices = api.get_multiple_prices_usd(tickers)

    print(f"✓ Fetched prices for {len(tickers)} cryptocurrencies:")
    for ticker, price in prices.items():
        if price:
            print(f"  {ticker:6s}: ${price:>12,.2f} USD")
        else:
            print(f"  {ticker:6s}: Price unavailable")


def demo_portfolio_scenario():
    """Demonstrate a complete portfolio scenario."""
    print_header("DEMO: Mixed USD/EUR Crypto Portfolio")

    converter = get_converter()

    print_step(1, "Portfolio Setup")
    print("""
We have a portfolio with:
  1. 0.5 BTC bought at $65,000 USD
  2. 2.0 ETH bought at €2,000 EUR
  3. 10 SOL bought at $100 USD
    """)

    print_step(2, "Current Prices (Simulated)")

    # Simulated current prices
    btc_usd = 67000.00
    eth_eur = 2200.00
    sol_usd = 120.00

    print(f"  BTC: ${btc_usd:,.2f} USD")
    print(f"  ETH: €{eth_eur:,.2f} EUR")
    print(f"  SOL: ${sol_usd:,.2f} USD")

    print_step(3, "Exchange Rate")
    rate = converter.get_usd_eur_rate()
    print(f"  1 USD = {rate:.4f} EUR")

    print_step(4, "Portfolio Calculation")

    # BTC (USD)
    btc_quantity = 0.5
    btc_buy_price_usd = 65000.00
    btc_value_usd = btc_quantity * btc_usd
    btc_cost_usd = btc_quantity * btc_buy_price_usd
    btc_value_eur = converter.convert_usd_to_eur(btc_value_usd)
    btc_cost_eur = converter.convert_usd_to_eur(btc_cost_usd)

    print(f"\nBTC (0.5 units, purchased in USD):")
    print(f"  Buy Price:   ${btc_buy_price_usd:>10,.2f} USD")
    print(f"  Current:     ${btc_usd:>10,.2f} USD")
    print(f"  Cost (USD):  ${btc_cost_usd:>10,.2f}")
    print(f"  Value (USD): ${btc_value_usd:>10,.2f}")
    print(f"  Cost (EUR):  €{btc_cost_eur:>10,.2f} ← Converted")
    print(f"  Value (EUR): €{btc_value_eur:>10,.2f} ← Converted")

    # ETH (EUR)
    eth_quantity = 2.0
    eth_buy_price_eur = 2000.00
    eth_value_eur = eth_quantity * eth_eur
    eth_cost_eur = eth_quantity * eth_buy_price_eur

    print(f"\nETH (2.0 units, purchased in EUR):")
    print(f"  Buy Price:   €{eth_buy_price_eur:>10,.2f} EUR")
    print(f"  Current:     €{eth_eur:>10,.2f} EUR")
    print(f"  Cost (EUR):  €{eth_cost_eur:>10,.2f}")
    print(f"  Value (EUR): €{eth_value_eur:>10,.2f}")

    # SOL (USD)
    sol_quantity = 10.0
    sol_buy_price_usd = 100.00
    sol_value_usd = sol_quantity * sol_usd
    sol_cost_usd = sol_quantity * sol_buy_price_usd
    sol_value_eur = converter.convert_usd_to_eur(sol_value_usd)
    sol_cost_eur = converter.convert_usd_to_eur(sol_cost_usd)

    print(f"\nSOL (10.0 units, purchased in USD):")
    print(f"  Buy Price:   ${sol_buy_price_usd:>10,.2f} USD")
    print(f"  Current:     ${sol_usd:>10,.2f} USD")
    print(f"  Cost (USD):  ${sol_cost_usd:>10,.2f}")
    print(f"  Value (USD): ${sol_value_usd:>10,.2f}")
    print(f"  Cost (EUR):  €{sol_cost_eur:>10,.2f} ← Converted")
    print(f"  Value (EUR): €{sol_value_eur:>10,.2f} ← Converted")

    print_step(5, "Portfolio Total (EUR)")

    total_cost_eur = btc_cost_eur + eth_cost_eur + sol_cost_eur
    total_value_eur = btc_value_eur + eth_value_eur + sol_value_eur
    total_gain_eur = total_value_eur - total_cost_eur
    gain_pct = (total_gain_eur / total_cost_eur * 100) if total_cost_eur > 0 else 0

    print(f"\n{'=' * 50}")
    print(f"  PORTFOLIO SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Total Cost:  €{total_cost_eur:>12,.2f}")
    print(f"  Total Value: €{total_value_eur:>12,.2f}")
    print(f"  Total Gain:  €{total_gain_eur:>12,.2f} ({gain_pct:+.2f}%)")
    print(f"{'=' * 50}")

    print("\n✓ All values properly converted to EUR for portfolio total!")


def demo_database_operations():
    """Demonstrate database operations with USD/EUR support."""
    print_header("DEMO: Database Operations with USD/EUR")

    # Use temporary database
    demo_db_path = Path(__file__).parent.parent / "demo_usd_eur.db"

    # Clean up any existing demo database
    if demo_db_path.exists():
        demo_db_path.unlink()

    db = DatabaseManager(str(demo_db_path))
    converter = get_converter()

    print_step(1, "Adding USD Crypto Asset")

    btc_id = db.add_asset(
        ticker="BTC",
        quantity=0.5,
        price_buy=65000.00,
        date_buy="2024-01-15",
        asset_type="crypto",
        current_price=67000.00,
        price_currency="USD",
    )

    print(f"✓ Added BTC asset (ID: {btc_id})")
    print(f"  Ticker: BTC")
    print(f"  Quantity: 0.5")
    print(f"  Buy Price: $65,000.00 USD")
    print(f"  Current Price: $67,000.00 USD")

    print_step(2, "Adding EUR Crypto Asset")

    eth_id = db.add_asset(
        ticker="ETH",
        quantity=2.0,
        price_buy=2000.00,
        date_buy="2024-01-10",
        asset_type="crypto",
        current_price=2200.00,
        price_currency="EUR",
    )

    print(f"✓ Added ETH asset (ID: {eth_id})")
    print(f"  Ticker: ETH")
    print(f"  Quantity: 2.0")
    print(f"  Buy Price: €2,000.00 EUR")
    print(f"  Current Price: €2,200.00 EUR")

    print_step(3, "Adding EUR Stock Asset")

    stock_id = db.add_asset(
        ticker="MC.PA",
        quantity=5.0,
        price_buy=700.00,
        date_buy="2024-01-05",
        asset_type="stock",
        current_price=750.00,
        # price_currency defaults to EUR
    )

    print(f"✓ Added LVMH stock (ID: {stock_id})")
    print(f"  Ticker: MC.PA")
    print(f"  Quantity: 5.0")
    print(f"  Buy Price: €700.00 EUR")
    print(f"  Current Price: €750.00 EUR")

    print_step(4, "Retrieving All Assets")

    assets = db.get_all_assets()
    print(f"\n✓ Retrieved {len(assets)} assets from database:")
    print(
        f"\n{'Ticker':<8} {'Type':<8} {'Qty':<10} {'Currency':<8} {'Buy Price':<15} {'Current Price':<15}"
    )
    print("-" * 70)

    for asset in assets:
        ticker = asset["ticker"]
        asset_type = asset["asset_type"]
        quantity = asset["quantity"]
        currency = asset.get("price_currency", "EUR")
        buy_price = asset["price_buy"]
        current_price = asset["current_price"]
        symbol = "$" if currency == "USD" else "€"

        print(
            f"{ticker:<8} {asset_type:<8} {quantity:<10.2f} {currency:<8} "
            f"{symbol}{buy_price:<14,.2f} {symbol}{current_price:<14,.2f}"
        )

    print_step(5, "Calculating Portfolio Total")

    total_value_eur = 0
    total_cost_eur = 0

    print("\nDetailed Calculation:")
    for asset in assets:
        ticker = asset["ticker"]
        quantity = asset["quantity"]
        buy_price = asset["price_buy"]
        current_price = asset["current_price"]
        currency = asset.get("price_currency", "EUR")

        value = quantity * current_price
        cost = quantity * buy_price

        if currency == "USD" and asset["asset_type"] == "crypto":
            value_eur = converter.convert_usd_to_eur(value)
            cost_eur = converter.convert_usd_to_eur(cost)
            print(f"  {ticker}: ${value:,.2f} USD → €{value_eur:,.2f} EUR")
        else:
            value_eur = value
            cost_eur = cost
            print(f"  {ticker}: €{value:,.2f} EUR (no conversion)")

        total_value_eur += value_eur
        total_cost_eur += cost_eur

    total_gain_eur = total_value_eur - total_cost_eur

    print(f"\n{'=' * 50}")
    print(f"  TOTAL PORTFOLIO (EUR)")
    print(f"{'=' * 50}")
    print(f"  Cost:  €{total_cost_eur:>12,.2f}")
    print(f"  Value: €{total_value_eur:>12,.2f}")
    print(f"  Gain:  €{total_gain_eur:>12,.2f}")
    print(f"{'=' * 50}")

    # Clean up demo database
    print(f"\nCleaning up demo database...")
    demo_db_path.unlink()
    print("✓ Demo database removed")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  PRISM USD/EUR CRYPTOCURRENCY FEATURE - INTERACTIVE DEMO")
    print("=" * 70)
    print(f"\nDemo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis demo will show you how the USD/EUR crypto feature works.")
    print("It includes live API calls (if available) and simulated data.")

    input("\nPress ENTER to start the demo...")

    try:
        # Demo 1: Currency Converter
        demo_currency_converter()
        input("\nPress ENTER to continue to next demo...")

        # Demo 2: CryptoAPI USD Methods
        demo_crypto_api_usd()
        input("\nPress ENTER to continue to next demo...")

        # Demo 3: Portfolio Scenario
        demo_portfolio_scenario()
        input("\nPress ENTER to continue to next demo...")

        # Demo 4: Database Operations
        demo_database_operations()

        # Summary
        print_header("DEMO COMPLETE!")
        print("""
✓ You've seen how the USD/EUR feature works!

Key Takeaways:
  1. Choose USD or EUR when adding crypto assets
  2. Prices fetched and displayed in selected currency
  3. Portfolio totals automatically calculated in EUR
  4. Real-time exchange rate conversion with caching
  5. Database safely stores currency preferences

Next Steps:
  • Try it yourself in the Prism app!
  • Read docs/USD_EUR_QUICKSTART.md for setup
  • Check docs/USD_EUR_CRYPTO_GUIDE.md for full guide

Happy tracking! 🎉
        """)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
