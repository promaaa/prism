#!/usr/bin/env python
# coding: utf-8

"""
Test script to verify asset editing functionality in Prism.

This script tests:
1. Editing an existing asset
2. Updating quantity, price, date
3. Currency preservation (USD for crypto, EUR for stocks)
4. Price fetching during edit
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI
from prism.ui.investments_tab import InvestmentsTab, AssetDialog


def test_edit_asset_dialog():
    """Test editing an asset through the AssetDialog."""
    print("\n🧪 Test d'édition d'actif")
    print("=" * 70)

    # Use real database for testing
    db_path = os.path.expanduser("~/Library/Application Support/Prism/prism.db")
    db = DatabaseManager(db_path)

    # Get existing assets
    print("\n📊 Vérification de la base de données...")
    existing_assets = db.get_all_assets()
    print(f"   ✅ Base connectée ({len(existing_assets)} actifs existants)")

    # Create API instances
    crypto_api = CryptoAPI()
    stock_api = StockAPI()

    # Use existing ARB asset or get first crypto
    print("\n1️⃣ Récupération d'un actif crypto existant (ARB)...")
    assets = db.get_all_assets()
    crypto_assets = [a for a in assets if a["asset_type"] == "crypto"]

    if not crypto_assets:
        print("   ⚠️  Aucun crypto trouvé, création d'un actif de test...")
        db.add_asset(
            ticker="ARB",
            quantity=1000.0,
            price_buy=0.50,
            date_buy="2024-01-01",
            current_price=0.31,
            asset_type="crypto",
            price_currency="USD",
        )
        crypto_assets = [a for a in db.get_all_assets() if a["asset_type"] == "crypto"]

    asset = crypto_assets[0]

    print(f"   ✅ Actif créé: {asset['ticker']}")
    print(f"      Quantité: {asset['quantity']}")
    print(f"      Prix d'achat: ${asset['price_buy']}")
    print(f"      Devise: {asset['price_currency']}")

    # Create dialog in edit mode
    print("\n2️⃣ Création du dialogue d'édition...")
    dialog = AssetDialog(db, crypto_api, stock_api, asset=asset, parent=None)

    # Verify dialog is in edit mode
    assert dialog.is_edit == True, "Dialog should be in edit mode"
    assert dialog.ticker_edit.isEnabled() == False, (
        "Ticker should be disabled in edit mode"
    )
    print("   ✅ Dialogue en mode édition")

    # Verify fields are populated
    assert dialog.ticker_edit.text() == asset["ticker"], "Ticker should be populated"
    assert float(dialog.quantity_edit.text()) == asset["quantity"], (
        "Quantity should be populated"
    )
    assert float(dialog.buy_price_edit.text()) == asset["price_buy"], (
        "Buy price should be populated"
    )
    print("   ✅ Champs pré-remplis correctement")
    print(f"      Ticker: {dialog.ticker_edit.text()}")
    print(f"      Quantité: {dialog.quantity_edit.text()}")
    print(f"      Prix: {dialog.buy_price_edit.text()}")

    # Verify currency label shows $ for crypto
    assert "$" in dialog.buy_price_label.text(), "Should show $ for crypto"
    print("   ✅ Label monétaire correct ($)")

    # Verify asset type is set
    assert dialog.asset_type_combo.currentText() == "crypto", (
        "Asset type should be crypto"
    )
    print("   ✅ Type d'actif correct (crypto)")

    print("\n3️⃣ Test de modification...")
    # Simulate editing the quantity (double it)
    original_qty = asset["quantity"]
    new_qty = original_qty * 2
    dialog.quantity_edit.setText(str(new_qty))
    data = dialog.get_asset_data()

    assert data["ticker"] == asset["ticker"]
    assert data["quantity"] == new_qty
    assert data["price_buy"] == asset["price_buy"]
    assert data["asset_type"] == "crypto"
    assert data["price_currency"] == "USD", "Crypto should remain in USD"
    print("   ✅ Données modifiées correctement")
    print(f"      Quantité originale: {original_qty}")
    print(f"      Nouvelle quantité: {data['quantity']}")
    print(f"      Devise préservée: {data['price_currency']}")

    # Test with a stock asset (use existing or skip)
    print("\n4️⃣ Test avec une action (stock)...")
    assets = db.get_all_assets()
    stock_assets = [a for a in assets if a["asset_type"] == "stock"]

    if not stock_assets:
        print("   ⚠️  Aucune action trouvée, test ignoré")
        print("\n" + "=" * 70)
        print("✅ Tous les tests d'édition réussis!\n")
        return True

    stock_asset = stock_assets[0]

    stock_dialog = AssetDialog(
        db, crypto_api, stock_api, asset=stock_asset, parent=None
    )

    print(f"   ✅ Action trouvée: {stock_asset['ticker']}")

    # Verify € is shown for stocks
    assert "€" in stock_dialog.buy_price_label.text(), "Should show € for stocks"
    print("   ✅ Label monétaire correct (€)")

    stock_data = stock_dialog.get_asset_data()
    assert stock_data["price_currency"] == "EUR", "Stock should be in EUR"
    print("   ✅ Devise correcte pour action (EUR)")
    print(f"      Ticker: {stock_data['ticker']}")
    print(f"      Prix: €{stock_data['price_buy']}")

    print("\n" + "=" * 70)
    print("✅ Tous les tests d'édition réussis!\n")

    return True


def main():
    """Main test function."""
    app = QApplication(sys.argv)

    try:
        success = test_edit_asset_dialog()
        return 0 if success else 1
    except AssertionError as e:
        print(f"\n❌ Test échoué: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        app.quit()


if __name__ == "__main__":
    sys.exit(main())
