#!/usr/bin/env python
# coding: utf-8

"""
Fix Arbitrum ticker et mettre à jour les prix des cryptomonnaies.

Ce script :
1. Corrige le ticker ARB pour qu'il soit au bon format
2. Rafraîchit les prix de toutes les crypto de la base de données
3. Affiche les prix actualisés pour chaque crypto
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prism.database.db_manager import DatabaseManager
from prism.api.crypto_api import CryptoAPI


def main():
    """Fix Arbitrum ticker and refresh all crypto prices."""

    # Initialize database
    db_path = os.path.expanduser("~/Library/Application Support/Prism/prism.db")
    db = DatabaseManager(db_path)

    print("\n🔧 Correction des tickers crypto et mise à jour des prix")
    print("=" * 70)
    print(f"Database: {db_path}\n")

    # Initialize Crypto API
    crypto_api = CryptoAPI()

    # Get all crypto assets
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all crypto assets
    cursor.execute("""
        SELECT id, ticker, quantity, price_buy, current_price, price_currency, date_buy
        FROM assets
        WHERE asset_type = 'crypto'
    """)

    cryptos = cursor.fetchall()

    if not cryptos:
        print("❌ Aucune cryptomonnaie trouvée dans la base de données")
        return 1

    print(f"📊 {len(cryptos)} cryptomonnaie(s) trouvée(s)\n")

    for crypto in cryptos:
        (
            asset_id,
            ticker,
            quantity,
            price_buy,
            current_price,
            price_currency,
            date_buy,
        ) = crypto

        # Clean ticker - remove everything after " - " if present
        original_ticker = ticker
        if " - " in ticker or " (" in ticker:
            # Extract just the ticker symbol
            ticker_clean = ticker.split(" ")[0].strip().upper()
        else:
            ticker_clean = ticker.strip().upper()

        print(f"\n{'=' * 70}")
        print(f"🪙 {original_ticker}")
        print(f"   ID:              {asset_id}")
        print(f"   Ticker original: {original_ticker}")

        if ticker_clean != original_ticker:
            print(f"   ⚠️  Ticker corrigé:  {ticker_clean}")
            # Update ticker in database
            cursor.execute(
                "UPDATE assets SET ticker = ? WHERE id = ?", (ticker_clean, asset_id)
            )
        else:
            print(f"   ✓ Ticker OK:      {ticker_clean}")

        print(f"   Quantité:        {quantity}")
        print(f"   Prix d'achat:    {price_currency}{price_buy:.2f}")
        print(f"   Prix actuel:     {price_currency}{current_price:.2f}")

        # Fetch current price
        print(f"\n   🔄 Récupération du prix actuel...", end=" ", flush=True)

        if price_currency == "USD":
            new_price = crypto_api.get_price_usd(ticker_clean)
        else:
            new_price = crypto_api.get_price(ticker_clean)

        if new_price and new_price > 0:
            print(f"✓")
            print(f"   💹 Nouveau prix:    {price_currency}{new_price:.4f}")

            # Calculate change
            if current_price > 0:
                change = ((new_price - current_price) / current_price) * 100
                change_symbol = "📈" if change >= 0 else "📉"
                print(f"   {change_symbol} Variation:     {change:+.2f}%")

            # Calculate current value and gain/loss
            current_value = quantity * new_price
            invested = quantity * price_buy
            gain_loss = current_value - invested
            gain_pct = (gain_loss / invested * 100) if invested > 0 else 0

            print(f"\n   💰 Valeur actuelle: {price_currency}{current_value:,.2f}")
            print(f"   💵 Investi:         {price_currency}{invested:,.2f}")
            gain_symbol = "📈" if gain_loss >= 0 else "📉"
            print(
                f"   {gain_symbol} Gain/Perte:     {price_currency}{gain_loss:+,.2f} ({gain_pct:+.2f}%)"
            )

            # Update price in database
            cursor.execute(
                "UPDATE assets SET current_price = ? WHERE id = ?",
                (new_price, asset_id),
            )

            print(f"   ✅ Prix mis à jour avec succès!")

        else:
            print(f"❌")
            print(f"   ⚠️  Impossible de récupérer le prix pour {ticker_clean}")
            print(f"   💡 Vérifiez que le ticker est correct dans l'API CoinGecko")

        # Small delay to avoid API rate limits
        time.sleep(0.5)

    # Commit changes
    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ Mise à jour terminée!")
    print("\n💡 Pour voir vos cryptos mises à jour:")
    print("   1. Lancez Prism: python -m prism")
    print("   2. Cliquez sur '💼 Patrimoine'")
    print("   3. Vos cryptos afficheront les nouveaux prix")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
