#!/usr/bin/env python3
"""
Check LVMH stock availability and suggest alternatives.

This script tests various ticker formats for LVMH and provides
alternative approaches if the stock is not available through Yahoo Finance.

Usage:
    python scripts/check_lvmh_availability.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.api.stock_api import StockAPI


def check_lvmh_availability():
    """Check LVMH stock availability across different exchanges."""
    print("=" * 60)
    print("LVMH STOCK AVAILABILITY CHECK")
    print("=" * 60)
    print()

    api = StockAPI()

    # Test different LVMH ticker formats
    test_tickers = [
        "LVMH",  # Plain ticker
        "LVMH.PA",  # Euronext Paris
        "LVMH.DE",  # Frankfurt (if available)
        "LVMH.AS",  # Amsterdam (if available)
        "LVMH.L",  # London (if available)
        "LVMH.MI",  # Milan (if available)
        "MC.PA",  # Alternative: LVMH Moët Hennessy (sometimes listed as MC)
    ]

    print("Testing LVMH ticker availability...")
    print("-" * 50)

    results = {}

    for ticker in test_tickers:
        print(f"Testing {ticker}...", end=" ")
        sys.stdout.flush()

        try:
            price = api.get_price(ticker, use_cache=False)
            info = api.get_stock_info(ticker)

            if price is not None:
                results[ticker] = {"price": price, "info": info, "available": True}
                print("✅ SUCCESS")
                print(f"  Price: €{price:.2f}")
                if info and "name" in info:
                    print(f"  Name: {info['name']}")
                if info and "exchange" in info:
                    print(f"  Exchange: {info['exchange']}")
            else:
                results[ticker] = {"available": False}
                print("❌ FAILED")

        except Exception as e:
            results[ticker] = {"available": False, "error": str(e)}
            print(f"❌ ERROR: {e}")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    successful_tickers = [t for t, r in results.items() if r.get("available", False)]

    if successful_tickers:
        print("✅ SUCCESSFUL TICKERS:")
        for ticker in successful_tickers:
            data = results[ticker]
            price = data.get("price", 0)
            info = data.get("info", {})
            name = info.get("name", ticker) if info else ticker
            print(f"  • {ticker}: €{price:.2f} ({name})")

        print()
        print("🎯 RECOMMENDATION:")
        print(f"  Use '{successful_tickers[0]}' for LVMH in your portfolio.")
        print("  This ticker is working correctly with Yahoo Finance.")

    else:
        print("❌ NO WORKING TICKERS FOUND")
        print()
        print("🔍 POSSIBLE REASONS:")
        print("  • LVMH stock data is temporarily unavailable on Yahoo Finance")
        print("  • Yahoo Finance API is experiencing issues")
        print("  • LVMH may be delisted or suspended")
        print()
        print("💡 ALTERNATIVES:")
        print("  1. Try again later (Yahoo Finance data may be delayed)")
        print("  2. Use a different financial data provider")
        print("  3. Check LVMH's official website for current price")
        print("  4. Consider using a different luxury goods stock as proxy")
        print()
        print("📊 OTHER LUXURY STOCKS TO CONSIDER:")
        print("  • Kering (KER.PA) - Gucci, Saint Laurent, Balenciaga")
        print("  • Hermès (RMS.PA) - Hermès luxury goods")
        print("  • L'Oréal (OR.PA) - Beauty and cosmetics")
        print("  • Pernod Ricard (RI.PA) - Spirits and wines")

    print()
    print("=" * 60)
    print("TECHNICAL DETAILS")
    print("=" * 60)

    print("• Yahoo Finance API is used for stock data")
    print("• European stocks typically use .PA suffix for Euronext Paris")
    print("• Data may be delayed or unavailable during market closures")
    print("• Rate limiting may apply for frequent requests")

    if not successful_tickers:
        print()
        print("🔧 DEBUGGING STEPS:")
        print("  1. Check if LVMH is trading normally on Euronext Paris")
        print("  2. Verify internet connection")
        print("  3. Try again during market hours (9:00-17:30 CET)")
        print("  4. Check Yahoo Finance website directly for LVMH.PA")

    return len(successful_tickers) > 0


def check_alternative_luxury_stocks():
    """Check availability of alternative luxury stocks."""
    print()
    print("=" * 60)
    print("CHECKING ALTERNATIVE LUXURY STOCKS")
    print("=" * 60)

    api = StockAPI()

    alternatives = [
        ("KER.PA", "Kering SA"),
        ("RMS.PA", "Hermès International"),
        ("OR.PA", "L'Oréal SA"),
        ("RI.PA", "Pernod Ricard SA"),
        ("MC.PA", "LVMH Moët Hennessy (alternative)"),
    ]

    print("Testing alternative luxury stocks...")
    print("-" * 50)

    working_alternatives = []

    for ticker, name in alternatives:
        print(f"Testing {ticker} ({name})...", end=" ")
        sys.stdout.flush()

        try:
            price = api.get_price(ticker, use_cache=False)
            if price is not None:
                print("✅ SUCCESS")
                print(f"  Price: €{price:.2f}")
                working_alternatives.append((ticker, name, price))
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        time.sleep(0.5)

    if working_alternatives:
        print()
        print("✅ WORKING ALTERNATIVES:")
        for ticker, name, price in working_alternatives:
            print(f"  • {ticker} ({name}): €{price:.2f}")

    return working_alternatives


def main():
    """Main function."""
    try:
        # Check LVMH availability
        lvmh_available = check_lvmh_availability()

        # If LVMH is not available, check alternatives
        if not lvmh_available:
            check_alternative_luxury_stocks()

        print()
        print("=" * 60)
        print("CHECK COMPLETE")
        print("=" * 60)

        if lvmh_available:
            print("✅ LVMH is available! You can use it in your portfolio.")
        else:
            print("❌ LVMH is currently not available through Yahoo Finance.")
            print(
                "   Consider using one of the alternative luxury stocks listed above."
            )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
