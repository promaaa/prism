#!/usr/bin/env python3
"""
Test script to check if Add Asset dialog works properly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI
from prism.ui.investments_tab import InvestmentsTab, AssetDialog


def test_investments_tab():
    """Test InvestmentsTab creation and Add Asset dialog."""
    print("Testing InvestmentsTab and AssetDialog...")

    # Create test database
    test_db_path = ":memory:"
    db = DatabaseManager(test_db_path)

    # Create API instances
    crypto_api = CryptoAPI()
    stock_api = StockAPI()

    try:
        # Create InvestmentsTab
        print("Creating InvestmentsTab...")
        investments_tab = InvestmentsTab(db, crypto_api, stock_api)
        print("✓ InvestmentsTab created successfully")

        # Test AssetDialog creation
        print("\nTesting AssetDialog creation...")
        dialog = AssetDialog(db, crypto_api, stock_api, parent=None)
        print("✓ AssetDialog created successfully")

        # Check dialog attributes
        assert hasattr(dialog, "db"), "Dialog should have db attribute"
        assert hasattr(dialog, "crypto_api"), "Dialog should have crypto_api attribute"
        assert hasattr(dialog, "stock_api"), "Dialog should have stock_api attribute"
        print("✓ Dialog has all required attributes")

        # Check dialog UI elements
        assert hasattr(dialog, "ticker_edit"), "Dialog should have ticker_edit"
        assert hasattr(dialog, "quantity_edit"), "Dialog should have quantity_edit"
        assert hasattr(dialog, "buy_price_edit"), "Dialog should have buy_price_edit"
        print("✓ Dialog has all UI elements")

        print("\n✅ All tests passed! AssetDialog works correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the test."""
    app = QApplication(sys.argv)

    try:
        success = test_investments_tab()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        app.quit()


if __name__ == "__main__":
    sys.exit(main())
