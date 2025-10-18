#!/usr/bin/env python3
"""
Test script to debug price fetching issues for stocks and cryptocurrencies.

This script tests the price fetching functionality for various assets,
particularly focusing on LVMH (stock) and Arbitrum (crypto) as reported issues.

Usage:
    python scripts/test_price_fetching.py [--verbose] [--no-cache]

Options:
    --verbose, -v    Show detailed output
    --no-cache       Disable cache for testing
"""

import sys
import argparse
from pathlib import Path
import time
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.api.stock_api import StockAPI
from prism.api.crypto_api import CryptoAPI


class PriceFetchingTester:
    """Test class for price fetching functionality."""

    def __init__(self, verbose: bool = False, use_cache: bool = True):
        """Initialize tester."""
        self.verbose = verbose
        self.use_cache = use_cache
        self.stock_api = StockAPI()
        self.crypto_api = CryptoAPI()

        if not self.use_cache:
            self.stock_api.clear_cache()
            self.crypto_api.clear_cache()

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def test_stock_price(self, ticker: str, expected_success: bool = True) -> dict:
        """Test stock price fetching."""
        self.log(f"Testing stock price for {ticker}")

        result = {
            "ticker": ticker,
            "type": "stock",
            "success": False,
            "price": None,
            "error": None,
            "details": {},
        }

        try:
            # Test basic price fetch
            price = self.stock_api.get_price(ticker, use_cache=self.use_cache)
            result["price"] = price
            result["success"] = price is not None

            if price is not None:
                self.log(f"✓ Successfully fetched price: €{price}")
            else:
                result["error"] = "Price returned as None"
                self.log(f"✗ Price fetch failed for {ticker}", "ERROR")

            # Get additional info
            info = self.stock_api.get_stock_info(ticker)
            if info:
                result["details"]["info"] = info
                self.log(f"✓ Got stock info: {info.get('name', 'Unknown')}")

            # Test historical data
            hist = self.stock_api.get_historical_data(ticker, "1d")
            if hist:
                result["details"]["has_history"] = True
                self.log(f"✓ Got historical data ({len(hist['dates'])} points)")
            else:
                result["details"]["has_history"] = False
                self.log(f"⚠ No historical data available")

        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
            self.log(f"✗ Exception during stock price fetch: {e}", "ERROR")

        return result

    def test_crypto_price(self, ticker: str, expected_success: bool = True) -> dict:
        """Test cryptocurrency price fetching."""
        self.log(f"Testing crypto price for {ticker}")

        result = {
            "ticker": ticker,
            "type": "crypto",
            "success": False,
            "price": None,
            "error": None,
            "details": {},
        }

        try:
            # Test basic price fetch (EUR)
            price_eur = self.crypto_api.get_price(ticker, use_cache=self.use_cache)
            result["price"] = price_eur
            result["success"] = price_eur is not None

            if price_eur is not None:
                self.log(f"✓ Successfully fetched EUR price: €{price_eur}")
            else:
                result["error"] = "EUR price returned as None"
                self.log(f"✗ EUR price fetch failed for {ticker}", "ERROR")

            # Test USD price
            price_usd = self.crypto_api.get_price_usd(ticker, use_cache=self.use_cache)
            if price_usd is not None:
                result["details"]["usd_price"] = price_usd
                self.log(f"✓ Successfully fetched USD price: ${price_usd}")
            else:
                self.log(f"⚠ USD price fetch failed for {ticker}")

            # Get CoinGecko ID mapping
            coingecko_id = self.crypto_api._get_coingecko_id(ticker)
            result["details"]["coingecko_id"] = coingecko_id
            self.log(f"✓ CoinGecko ID mapping: {ticker} -> {coingecko_id}")

            # Test coin info
            coin_info = self.crypto_api.get_coin_info(ticker)
            if coin_info:
                result["details"]["coin_info"] = {
                    "name": coin_info.get("name"),
                    "symbol": coin_info.get("symbol"),
                    "market_cap_rank": coin_info.get("market_cap_rank"),
                }
                self.log(f"✓ Got coin info: {coin_info.get('name', 'Unknown')}")
            else:
                self.log(f"⚠ No coin info available")

        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
            self.log(f"✗ Exception during crypto price fetch: {e}", "ERROR")

        return result

    def test_multiple_prices(self):
        """Test fetching multiple prices at once."""
        self.log("\nTesting multiple price fetching...")

        # Test stocks
        stock_tickers = ["AAPL", "LVMH.PA", "MSFT"]
        stock_prices = self.stock_api.get_multiple_prices(
            stock_tickers, use_cache=self.use_cache
        )

        self.log("Stock multiple fetch results:")
        for ticker, price in stock_prices.items():
            status = "✓" if price else "✗"
            self.log(f"  {status} {ticker}: €{price}")

        # Test cryptos
        crypto_tickers = ["BTC", "ARB", "ETH"]
        crypto_prices = self.crypto_api.get_multiple_prices(
            crypto_tickers, use_cache=self.use_cache
        )

        self.log("Crypto multiple fetch results:")
        for ticker, price in crypto_prices.items():
            status = "✓" if price else "✗"
            self.log(f"  {status} {ticker}: €{price}")

    def test_network_connectivity(self):
        """Test basic network connectivity to APIs."""
        self.log("\nTesting network connectivity...")

        import requests

        # Test CoinGecko
        try:
            response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=5)
            if response.status_code == 200:
                self.log("✓ CoinGecko API is reachable")
            else:
                self.log(
                    f"⚠ CoinGecko API returned status {response.status_code}", "WARNING"
                )
        except Exception as e:
            self.log(f"✗ CoinGecko API unreachable: {e}", "ERROR")

        # Test Yahoo Finance (basic connectivity)
        try:
            response = requests.get("https://finance.yahoo.com", timeout=5)
            if response.status_code == 200:
                self.log("✓ Yahoo Finance is reachable")
            else:
                self.log(
                    f"⚠ Yahoo Finance returned status {response.status_code}", "WARNING"
                )
        except Exception as e:
            self.log(f"✗ Yahoo Finance unreachable: {e}", "ERROR")

    def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("=" * 70)
        print("PRICE FETCHING DIAGNOSTIC TEST")
        print("=" * 70)
        print(f"Cache enabled: {self.use_cache}")
        print(f"Verbose mode: {self.verbose}")
        print()

        # Test network connectivity first
        self.test_network_connectivity()

        # Test problematic assets
        test_cases = [
            # Stocks
            ("LVMH", "stock", False),  # Should fail - wrong format
            ("LVMH.PA", "stock", True),  # Should work - correct format
            ("AAPL", "stock", True),  # Should work - US stock
            ("MSFT", "stock", True),  # Should work - US stock
            # Cryptos
            ("ARB", "crypto", True),  # Should work - Arbitrum
            ("ARBITRUM", "crypto", False),  # Should fail - wrong ticker
            ("BTC", "crypto", True),  # Should work - Bitcoin
            ("ETH", "crypto", True),  # Should work - Ethereum
        ]

        results = []

        for ticker, asset_type, expected_success in test_cases:
            print(f"\n{'=' * 50}")
            print(f"Testing {asset_type.upper()}: {ticker}")
            print("=" * 50)

            if asset_type == "stock":
                result = self.test_stock_price(ticker, expected_success)
            else:
                result = self.test_crypto_price(ticker, expected_success)

            results.append(result)

            # Show success/failure summary
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            expected = (
                " (expected)"
                if result["success"] == expected_success
                else " (unexpected)"
            )
            print(f"\nResult: {status}{expected}")

            if result["error"]:
                print(f"Error: {result['error']}")

        # Test multiple price fetching
        self.test_multiple_prices()

        # Summary
        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print("=" * 70)

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        print(f"Total tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")

        # Group by type
        stock_results = [r for r in results if r["type"] == "stock"]
        crypto_results = [r for r in results if r["type"] == "crypto"]

        print(f"\nStock tests: {len(stock_results)}")
        print(f"  Successful: {sum(1 for r in stock_results if r['success'])}")

        print(f"\nCrypto tests: {len(crypto_results)}")
        print(f"  Successful: {sum(1 for r in crypto_results if r['success'])}")

        # Show problematic cases
        failed_results = [r for r in results if not r["success"]]
        if failed_results:
            print(f"\n❌ Failed tests:")
            for result in failed_results:
                print(
                    f"  • {result['type'].upper()}: {result['ticker']} - {result['error']}"
                )

        # Show successful cases
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            print(f"\n✅ Successful tests:")
            for result in successful_results:
                price = result["price"]
                currency = "€" if result["type"] == "stock" else "$"
                print(
                    f"  • {result['type'].upper()}: {result['ticker']} - {currency}{price}"
                )

        print(f"\n{'=' * 70}")

        # Recommendations
        print("RECOMMENDATIONS:")
        if any(r["ticker"] == "LVMH.PA" and r["success"] for r in results):
            print("✅ LVMH: Use 'LVMH.PA' format for Euronext Paris stocks")
        else:
            print("❌ LVMH: Check ticker format - should be 'LVMH.PA'")

        if any(r["ticker"] == "ARB" and r["success"] for r in results):
            print("✅ Arbitrum: 'ARB' ticker works correctly")
        else:
            print("❌ Arbitrum: Check CoinGecko API or ticker mapping")

        print("\nFor debugging:")
        print("- Check internet connection")
        print("- Verify ticker symbols on respective exchanges")
        print("- Check API rate limits")
        print("- Try again later if APIs are temporarily down")

        return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test price fetching functionality")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable cache for testing"
    )

    args = parser.parse_args()

    tester = PriceFetchingTester(verbose=args.verbose, use_cache=not args.no_cache)
    results = tester.run_comprehensive_test()

    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r["success"])
    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
