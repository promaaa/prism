#!/usr/bin/env python
# coding: utf-8

"""
Test script to verify crypto prices can be fetched for all supported cryptocurrencies.
Tests both EUR and USD prices for key cryptos to ensure they're ready for Prism.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prism.api.crypto_api import CryptoAPI


def test_crypto_prices():
    """Test fetching prices for all supported cryptocurrencies."""

    # Initialize API
    crypto_api = CryptoAPI()

    print("\n🔍 Test des prix des cryptomonnaies")
    print("=" * 80)
    print(f"Nombre de cryptos supportées: {len(crypto_api.TICKER_TO_ID)}\n")

    # Test categories
    test_cryptos = {
        "🥇 Top Cryptos": ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA"],
        "🔗 Layer 2 & Scaling": ["ARB", "OP", "MATIC"],
        "🏦 DeFi": ["AAVE", "UNI", "LINK", "MKR", "SNX", "CRV"],
        "💰 Stablecoins": ["USDT", "USDC", "DAI", "TUSD"],
        "🎮 Gaming & Metaverse": ["SAND", "MANA", "AXS", "IMX"],
        "🤖 AI & Data": ["FET", "AGIX", "OCEAN", "GRT"],
        "🌐 Layer 1": ["AVAX", "DOT", "ATOM", "NEAR", "APT", "SUI"],
        "🐶 Meme Coins": ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK"],
    }

    results = {
        "success_eur": [],
        "success_usd": [],
        "failed_eur": [],
        "failed_usd": [],
    }

    for category, tickers in test_cryptos.items():
        print(f"\n{category}")
        print("-" * 80)

        for ticker in tickers:
            # Check if ticker is supported
            if ticker not in crypto_api.TICKER_TO_ID:
                print(f"  ❌ {ticker:8} - Non supporté")
                continue

            # Test EUR price
            print(f"  {ticker:8} - ", end="", flush=True)
            price_eur = crypto_api.get_price(ticker)

            if price_eur and price_eur > 0:
                print(f"✅ EUR: €{price_eur:>12,.4f} ", end="")
                results["success_eur"].append(ticker)
            else:
                print(f"❌ EUR: Échec{' ' * 20}", end="")
                results["failed_eur"].append(ticker)

            # Test USD price
            price_usd = crypto_api.get_price_usd(ticker)

            if price_usd and price_usd > 0:
                print(f"| USD: ${price_usd:>12,.4f} ✅")
                results["success_usd"].append(ticker)
            else:
                print(f"| USD: Échec ❌")
                results["failed_usd"].append(ticker)

    # Summary
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS")
    print("=" * 80)

    total_tests = len([t for tickers in test_cryptos.values() for t in tickers])
    success_eur = len(results["success_eur"])
    success_usd = len(results["success_usd"])

    print(
        f"\n✅ Prix EUR récupérés: {success_eur}/{total_tests} ({success_eur / total_tests * 100:.1f}%)"
    )
    print(
        f"✅ Prix USD récupérés: {success_usd}/{total_tests} ({success_usd / total_tests * 100:.1f}%)"
    )

    if results["failed_eur"]:
        print(
            f"\n❌ Échecs EUR ({len(results['failed_eur'])}): {', '.join(results['failed_eur'])}"
        )

    if results["failed_usd"]:
        print(
            f"❌ Échecs USD ({len(results['failed_usd'])}): {', '.join(results['failed_usd'])}"
        )

    # Check specific important cryptos
    print("\n🎯 CRYPTOS CRITIQUES:")
    critical_cryptos = ["BTC", "ETH", "ARB", "USDT", "USDC", "SOL", "XRP"]
    all_critical_ok = True

    for ticker in critical_cryptos:
        status_eur = "✅" if ticker in results["success_eur"] else "❌"
        status_usd = "✅" if ticker in results["success_usd"] else "❌"
        status = (
            "✅"
            if (ticker in results["success_eur"] and ticker in results["success_usd"])
            else "❌"
        )

        if status == "❌":
            all_critical_ok = False

        print(f"  {status} {ticker:8} - EUR: {status_eur} | USD: {status_usd}")

    print("\n" + "=" * 80)

    if all_critical_ok:
        print("🎉 SUCCÈS - Toutes les cryptos critiques sont opérationnelles!")
        print("\n💡 Vous pouvez maintenant:")
        print("   • Ajouter des cryptos dans Prism (💼 Patrimoine)")
        print("   • Les prix seront automatiquement récupérés")
        print("   • Choisir EUR ou USD comme devise")
        return 0
    else:
        print("⚠️  ATTENTION - Certaines cryptos critiques ont échoué!")
        print("   Vérifiez votre connexion internet et les IDs CoinGecko")
        return 1


def test_specific_crypto(ticker: str, verbose: bool = True):
    """Test a specific cryptocurrency ticker.

    Args:
        ticker: Crypto ticker symbol (e.g., 'BTC', 'ARB')
        verbose: Print detailed information

    Returns:
        dict: Price information or None if failed
    """
    crypto_api = CryptoAPI()

    if ticker not in crypto_api.TICKER_TO_ID:
        if verbose:
            print(f"❌ {ticker} n'est pas supporté")
            print(
                f"   ID CoinGecko nécessaire. Les cryptos supportées: {list(crypto_api.TICKER_TO_ID.keys())}"
            )
        return None

    coingecko_id = crypto_api.TICKER_TO_ID[ticker]

    if verbose:
        print(f"\n🔍 Test de {ticker}")
        print(f"   ID CoinGecko: {coingecko_id}")

    # Fetch EUR price
    price_eur = crypto_api.get_price(ticker)

    # Fetch USD price
    price_usd = crypto_api.get_price_usd(ticker)

    result = {
        "ticker": ticker,
        "coingecko_id": coingecko_id,
        "price_eur": price_eur,
        "price_usd": price_usd,
        "success": (price_eur and price_eur > 0) and (price_usd and price_usd > 0),
    }

    if verbose:
        if result["success"]:
            print(f"   ✅ Prix EUR: €{price_eur:,.4f}")
            print(f"   ✅ Prix USD: ${price_usd:,.4f}")

            if price_eur and price_usd and price_usd > 0:
                eur_usd_rate = price_eur / price_usd
                print(f"   📊 Taux EUR/USD: {eur_usd_rate:.4f}")
        else:
            print(f"   ❌ Échec de récupération du prix")
            if not price_eur:
                print(f"      Prix EUR: échec")
            if not price_usd:
                print(f"      Prix USD: échec")

    return result


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test crypto prices for Prism")
    parser.add_argument(
        "--ticker", type=str, help="Test specific ticker (e.g., BTC, ARB, ETH)"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all supported tickers"
    )

    args = parser.parse_args()

    if args.list:
        crypto_api = CryptoAPI()
        print(f"\n📀 Cryptos supportées ({len(crypto_api.TICKER_TO_ID)})")
        print("=" * 80)

        tickers_sorted = sorted(crypto_api.TICKER_TO_ID.items())
        for ticker, coingecko_id in tickers_sorted:
            print(f"  {ticker:8} -> {coingecko_id}")

        return 0

    if args.ticker:
        result = test_specific_crypto(args.ticker.upper())
        return 0 if (result and result["success"]) else 1

    # Run full test suite
    return test_crypto_prices()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
