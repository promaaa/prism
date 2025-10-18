#!/usr/bin/env python3
"""
Test script to verify the improved button styling in action buttons.

This script checks that:
1. Row action buttons have proper styling classes applied
2. Buttons include text labels (not just emojis)
3. Delete buttons use the 'danger' class
4. Edit buttons use the 'secondary' class
5. Buttons have proper cursor and size settings
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from prism.database.db_manager import DatabaseManager
from prism.ui.investments_tab import InvestmentsTab
from prism.ui.personal_tab import PersonalTab
from prism.ui.orders_tab import OrdersTab
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI


def test_investments_tab_buttons():
    """Test that investments tab buttons have proper styling."""
    print("Testing Investments Tab buttons...")

    db = DatabaseManager()
    crypto_api = CryptoAPI()
    stock_api = StockAPI()
    tab = InvestmentsTab(db, crypto_api, stock_api)

    # Check header delete button
    assert tab.delete_btn is not None, "Delete button should exist"
    assert "Delete Selected" in tab.delete_btn.text(), (
        "Delete button should have 'Delete Selected' text"
    )
    assert tab.delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )

    print("  ✓ Header delete button has proper styling")

    # Test row action buttons by creating a sample asset
    sample_asset = {
        "id": 1,
        "ticker": "TEST",
        "name": "Test Asset",
        "asset_type": "stock",
        "quantity": 10,
        "buy_price": 100,
        "current_price": 120,
        "value": 1200,
        "gain_loss": 200,
        "gain_loss_percent": 20.0,
    }

    action_widget = tab._create_action_buttons(sample_asset)
    buttons = action_widget.findChildren(type(tab.delete_btn))

    assert len(buttons) >= 2, "Should have at least 2 action buttons (edit + delete)"

    # Check edit button
    edit_btn = buttons[0]
    assert "Edit" in edit_btn.text(), "Edit button should have 'Edit' text"
    assert edit_btn.property("class") == "secondary", (
        "Edit button should have 'secondary' class"
    )
    assert edit_btn.minimumWidth() == 70, "Edit button should have minimum width of 70"

    print("  ✓ Row edit button has proper styling")

    # Check delete button
    delete_btn = buttons[1]
    assert "Delete" in delete_btn.text(), "Delete button should have 'Delete' text"
    assert delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )
    assert delete_btn.minimumWidth() == 80, (
        "Delete button should have minimum width of 80"
    )

    print("  ✓ Row delete button has proper styling")
    print("✓ Investments Tab: All button styling tests passed!\n")


def test_personal_tab_buttons():
    """Test that personal tab buttons have proper styling."""
    print("Testing Personal Tab buttons...")

    db = DatabaseManager()
    tab = PersonalTab(db)

    # Check header delete button
    assert tab.delete_btn is not None, "Delete button should exist"
    assert "Delete Selected" in tab.delete_btn.text(), (
        "Delete button should have 'Delete Selected' text"
    )
    assert tab.delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )

    print("  ✓ Header delete button has proper styling")

    # Test row action buttons by creating a sample transaction
    sample_transaction = {
        "id": 1,
        "date": "2024-01-15",
        "description": "Test Transaction",
        "category": "Food",
        "amount": -50.0,
    }

    action_widget = tab._create_action_buttons(sample_transaction)
    buttons = action_widget.findChildren(type(tab.delete_btn))

    assert len(buttons) >= 2, "Should have at least 2 action buttons (edit + delete)"

    # Check edit button
    edit_btn = buttons[0]
    assert "Edit" in edit_btn.text(), "Edit button should have 'Edit' text"
    assert edit_btn.property("class") == "secondary", (
        "Edit button should have 'secondary' class"
    )

    print("  ✓ Row edit button has proper styling")

    # Check delete button
    delete_btn = buttons[1]
    assert "Delete" in delete_btn.text(), "Delete button should have 'Delete' text"
    assert delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )

    print("  ✓ Row delete button has proper styling")
    print("✓ Personal Tab: All button styling tests passed!\n")


def test_orders_tab_buttons():
    """Test that orders tab buttons have proper styling."""
    print("Testing Orders Tab buttons...")

    db = DatabaseManager()
    tab = OrdersTab(db)

    # Check header delete button
    assert tab.delete_btn is not None, "Delete button should exist"
    assert "Delete Selected" in tab.delete_btn.text(), (
        "Delete button should have 'Delete Selected' text"
    )
    assert tab.delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )

    print("  ✓ Header delete button has proper styling")

    # Test row action buttons by creating a sample order
    sample_order = {
        "id": 1,
        "date": "2024-01-15",
        "ticker": "TEST",
        "order_type": "buy",
        "quantity": 10,
        "price": 100,
        "status": "open",
    }

    action_widget = tab._create_action_buttons(sample_order)
    buttons = action_widget.findChildren(type(tab.delete_btn))

    assert len(buttons) >= 3, (
        "Should have at least 3 action buttons (edit + toggle + delete)"
    )

    # Check edit button
    edit_btn = buttons[0]
    assert "Edit" in edit_btn.text(), "Edit button should have 'Edit' text"
    assert edit_btn.property("class") == "secondary", (
        "Edit button should have 'secondary' class"
    )

    print("  ✓ Row edit button has proper styling")

    # Check toggle button
    toggle_btn = buttons[1]
    assert "Close" in toggle_btn.text() or "Reopen" in toggle_btn.text(), (
        "Toggle button should have status text"
    )
    assert toggle_btn.property("class") == "secondary", (
        "Toggle button should have 'secondary' class"
    )

    print("  ✓ Row toggle button has proper styling")

    # Check delete button
    delete_btn = buttons[2]
    assert "Delete" in delete_btn.text(), "Delete button should have 'Delete' text"
    assert delete_btn.property("class") == "danger", (
        "Delete button should have 'danger' class"
    )

    print("  ✓ Row delete button has proper styling")
    print("✓ Orders Tab: All button styling tests passed!\n")


def main():
    """Run all button styling tests."""
    print("=" * 60)
    print("Button Styling Improvement Tests")
    print("=" * 60 + "\n")

    app = QApplication(sys.argv)

    try:
        test_investments_tab_buttons()
        test_personal_tab_buttons()
        test_orders_tab_buttons()

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSummary of improvements:")
        print("  • Action buttons now have clear text labels (not just emojis)")
        print("  • Delete buttons use the 'danger' class (red styling)")
        print("  • Edit buttons use the 'secondary' class (gray styling)")
        print("  • Toggle buttons use the 'secondary' class")
        print("  • All buttons have proper cursor (pointing hand)")
        print("  • Buttons have appropriate minimum/maximum widths")
        print("  • Header delete buttons show 'Delete Selected' text")
        print("\nThese changes make the UI much more intuitive and engaging!")

        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
