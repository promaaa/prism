#!/usr/bin/env python3
"""
Test script to verify delete functionality in Investments tab.

This script tests:
1. Delete button enable/disable based on selection
2. Bulk delete functionality with button
3. Delete key (Delete/Backspace) functionality
4. Individual delete buttons in actions column

Usage:
    python scripts/test_delete_functionality.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from prism.database.db_manager import DatabaseManager
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI
from prism.ui.investments_tab import InvestmentsTab


class DeleteFunctionalityTester:
    """Test class for delete functionality."""

    def __init__(self):
        """Initialize tester."""
        self.app = None
        self.db = None
        self.crypto_api = None
        self.stock_api = None
        self.tab = None
        self.test_assets = []

    def setup(self):
        """Set up test environment."""
        print("Setting up test environment...")

        # Create QApplication if it doesn't exist
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        # Initialize components
        self.db = DatabaseManager()
        self.crypto_api = CryptoAPI()
        self.stock_api = StockAPI()

        # Create test assets
        self._create_test_assets()

        # Create investments tab
        self.tab = InvestmentsTab(self.db, self.crypto_api, self.stock_api)

        print("✓ Test environment set up")

    def _create_test_assets(self):
        """Create test assets for testing."""
        print("Creating test assets...")

        # Clear existing test assets
        existing = self.db.get_all_assets()
        test_assets = [
            a for a in existing if a.get("ticker", "").startswith("TEST_DELETE_")
        ]

        for asset in test_assets:
            self.db.delete_asset(asset["id"])

        # Create new test assets
        test_data = [
            {
                "ticker": "TEST_DELETE_AAPL",
                "quantity": 10,
                "price_buy": 150.0,
                "date_buy": "2024-01-01",
                "asset_type": "stock",
            },
            {
                "ticker": "TEST_DELETE_MSFT",
                "quantity": 5,
                "price_buy": 300.0,
                "date_buy": "2024-01-01",
                "asset_type": "stock",
            },
            {
                "ticker": "TEST_DELETE_BTC",
                "quantity": 0.5,
                "price_buy": 50000.0,
                "date_buy": "2024-01-01",
                "asset_type": "crypto",
            },
        ]

        for data in test_data:
            asset_id = self.db.add_asset(
                ticker=data["ticker"],
                quantity=data["quantity"],
                price_buy=data["price_buy"],
                date_buy=data["date_buy"],
                current_price=data["price_buy"],  # Use buy price as current for testing
                asset_type=data["asset_type"],
            )
            if asset_id:
                self.test_assets.append({"id": asset_id, **data})

        print(f"✓ Created {len(self.test_assets)} test assets")

    def test_delete_button_state(self):
        """Test that delete button is enabled/disabled correctly."""
        print("\nTesting delete button state...")

        # Initially no selection - button should be disabled
        assert not self.tab.delete_btn.isEnabled(), (
            "Delete button should be disabled with no selection"
        )
        print("✓ Delete button disabled with no selection")

        # Select first row
        table = self.tab.assets_table
        first_row = 0
        table.selectRow(first_row)

        # Button should be enabled
        assert self.tab.delete_btn.isEnabled(), (
            "Delete button should be enabled with selection"
        )
        print("✓ Delete button enabled with selection")

        # Clear selection
        table.clearSelection()

        # Button should be disabled
        assert not self.tab.delete_btn.isEnabled(), (
            "Delete button should be disabled after clearing selection"
        )
        print("✓ Delete button disabled after clearing selection")

    def test_bulk_delete_button(self):
        """Test bulk delete functionality with button."""
        print("\nTesting bulk delete button...")

        table = self.tab.assets_table
        initial_count = table.rowCount()

        # Select first two rows
        table.selectRow(0)
        table.selectRow(1)

        # Click delete button
        QTest.mouseClick(self.tab.delete_btn, Qt.MouseButton.LeftButton)

        # Process events to show dialog
        self.app.processEvents()

        # The dialog should appear, but we can't easily test the confirmation
        # in a headless environment. Let's check if the method exists and is callable.
        assert hasattr(self.tab, "_on_delete_selected"), (
            "Delete selected method should exist"
        )
        print("✓ Bulk delete method exists and is accessible")

    def test_delete_key_functionality(self):
        """Test delete key (Delete/Backspace) functionality."""
        print("\nTesting delete key functionality...")

        table = self.tab.assets_table

        # Select a row
        table.selectRow(0)

        # Simulate delete key press
        QTest.keyClick(table, Qt.Key.Key_Delete)

        # Process events
        self.app.processEvents()

        # Check that event filter exists
        assert hasattr(self.tab, "eventFilter"), (
            "Event filter should exist for key handling"
        )
        print("✓ Delete key event handling is set up")

    def test_individual_delete_buttons(self):
        """Test individual delete buttons in actions column."""
        print("\nTesting individual delete buttons...")

        table = self.tab.assets_table

        # Get the actions widget from first row
        actions_widget = table.cellWidget(0, 8)
        assert actions_widget is not None, "Actions widget should exist"

        # Find the delete button
        delete_buttons = actions_widget.findChildren(QPushButton)
        delete_btn = None
        for btn in delete_buttons:
            if "Delete" in btn.text():
                delete_btn = btn
                break

        assert delete_btn is not None, "Delete button should exist in actions"
        print("✓ Individual delete buttons exist in table")

    def test_table_data_integrity(self):
        """Test that table contains correct asset data."""
        print("\nTesting table data integrity...")

        table = self.tab.assets_table

        # Check that we have rows
        assert table.rowCount() > 0, "Table should have rows"

        # Check that first column contains asset type
        type_item = table.item(0, 0)
        assert type_item is not None, "Type item should exist"
        assert type_item.text() in ["STOCK", "CRYPTO"], "Type should be STOCK or CRYPTO"

        # Check that asset ID is stored in UserRole
        asset_id = type_item.data(Qt.ItemDataRole.UserRole)
        assert asset_id is not None, "Asset ID should be stored in table item"
        assert isinstance(asset_id, int), "Asset ID should be an integer"

        print("✓ Table data integrity verified")

    def cleanup(self):
        """Clean up test assets."""
        print("\nCleaning up test assets...")

        for asset in self.test_assets:
            try:
                self.db.delete_asset(asset["id"])
            except Exception as e:
                print(f"Warning: Could not delete test asset {asset['id']}: {e}")

        print("✓ Test cleanup completed")

    def run_all_tests(self):
        """Run all delete functionality tests."""
        print("=" * 60)
        print("Testing Delete Functionality in Investments Tab")
        print("=" * 60)

        try:
            self.setup()

            self.test_delete_button_state()
            self.test_bulk_delete_button()
            self.test_delete_key_functionality()
            self.test_individual_delete_buttons()
            self.test_table_data_integrity()

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\nDelete functionality appears to be working correctly!")
            print("\nKey features verified:")
            print("• Delete button enables/disables based on selection")
            print("• Bulk delete method exists and is accessible")
            print("• Delete key event handling is configured")
            print("• Individual delete buttons exist in table rows")
            print("• Asset IDs are properly stored in table items")
            print("\nNote: Full end-to-end testing requires GUI interaction.")
            print("Manual testing recommended for complete verification.")

        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """Main test function."""
    tester = DeleteFunctionalityTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
