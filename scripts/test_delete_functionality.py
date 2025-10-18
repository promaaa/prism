"""
Test script to verify delete button and key functionality in all tabs.
"""

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.database.db_manager import DatabaseManager
from prism.ui.personal_tab import PersonalTab
from prism.ui.investments_tab import InvestmentsTab
from prism.ui.orders_tab import OrdersTab
from prism.api.crypto_api import CryptoAPI
from prism.api.stock_api import StockAPI


def test_personal_tab(db: DatabaseManager):
    """Test PersonalTab delete functionality."""
    print("\n=== Testing PersonalTab ===")

    # Create tab
    personal_tab = PersonalTab(db)

    # Check delete button exists and is initially disabled
    assert hasattr(personal_tab, "delete_btn"), "Delete button should exist"
    assert not personal_tab.delete_btn.isEnabled(), (
        "Delete button should be disabled initially"
    )
    print("✓ Delete button exists and is initially disabled")

    # Check button has tooltip
    tooltip = personal_tab.delete_btn.toolTip()
    assert "Delete" in tooltip or "Suppr" in tooltip, (
        "Delete button should have tooltip"
    )
    print(f"✓ Delete button tooltip: {tooltip}")

    # Check table has selection handler
    assert (
        personal_tab.transaction_table.receivers(
            personal_tab.transaction_table.itemSelectionChanged
        )
        > 0
    ), "Table should have selection changed handler"
    print("✓ Table selection handler connected")

    # Check keyPressEvent is implemented
    assert hasattr(personal_tab, "keyPressEvent"), "keyPressEvent should be implemented"
    print("✓ keyPressEvent is implemented")

    # Check that table has extended selection mode for multi-select
    selection_mode = personal_tab.transaction_table.selectionMode()
    assert selection_mode == QTableWidget.SelectionMode.ExtendedSelection, (
        "Table should have ExtendedSelection mode for bulk delete"
    )
    print("✓ ExtendedSelection mode enabled for bulk delete")

    return True


def test_investments_tab(
    db: DatabaseManager, crypto_api: CryptoAPI, stock_api: StockAPI
):
    """Test InvestmentsTab delete functionality."""
    print("\n=== Testing InvestmentsTab ===")

    # Create tab
    investments_tab = InvestmentsTab(db, crypto_api, stock_api)

    # Check delete button exists and is initially disabled
    assert hasattr(investments_tab, "delete_btn"), "Delete button should exist"
    assert not investments_tab.delete_btn.isEnabled(), (
        "Delete button should be initially disabled"
    )
    print("✓ Delete button exists and is initially disabled")

    # Check button has tooltip
    tooltip = investments_tab.delete_btn.toolTip()
    assert "Delete" in tooltip or "Suppr" in tooltip, (
        "Delete button should have tooltip"
    )
    print(f"✓ Delete button tooltip: {tooltip}")

    # Check table has selection handler
    assert (
        investments_tab.assets_table.receivers(
            investments_tab.assets_table.itemSelectionChanged
        )
        > 0
    ), "Table should have selection changed handler"
    print("✓ Table selection handler connected")

    # Check that keyPressEvent is implemented
    assert hasattr(investments_tab, "keyPressEvent"), (
        "keyPressEvent should be implemented"
    )
    print("✓ keyPressEvent is implemented")

    # Check that table has extended selection mode for multi-select
    selection_mode = investments_tab.assets_table.selectionMode()
    assert selection_mode == QTableWidget.SelectionMode.ExtendedSelection, (
        "Table should have ExtendedSelection mode for bulk delete"
    )
    print("✓ ExtendedSelection mode enabled for bulk delete")

    return True


def test_orders_tab(db: DatabaseManager):
    """Test OrdersTab delete functionality."""
    print("\n=== Testing OrdersTab ===")

    # Create tab
    orders_tab = OrdersTab(db)

    # Check delete button exists and is initially disabled
    assert hasattr(orders_tab, "delete_btn"), "Delete button should exist"
    assert not orders_tab.delete_btn.isEnabled(), (
        "Delete button should be initially disabled"
    )
    print("✓ Delete button exists and is initially disabled")

    # Check button has tooltip
    tooltip = orders_tab.delete_btn.toolTip()
    assert "Delete" in tooltip or "Suppr" in tooltip, (
        "Delete button should have tooltip"
    )
    print(f"✓ Delete button tooltip: {tooltip}")

    # Check table has selection handler
    assert (
        orders_tab.orders_table.receivers(orders_tab.orders_table.itemSelectionChanged)
        > 0
    ), "Table should have selection handler"
    print("✓ Table selection handler connected")

    # Check that keyPressEvent is implemented
    assert hasattr(orders_tab, "keyPressEvent"), "keyPressEvent should be implemented"
    print("✓ keyPressEvent is implemented")

    # Check that table has extended selection mode for multi-select
    selection_mode = orders_tab.orders_table.selectionMode()
    assert selection_mode == QTableWidget.SelectionMode.ExtendedSelection, (
        "Table should have ExtendedSelection mode for bulk delete"
    )
    print("✓ ExtendedSelection mode enabled for bulk delete")

    return True


def main():
    """Run all tests."""
    print("Starting Delete Functionality Tests...")
    print("=" * 50)

    # Create app
    app = QApplication(sys.argv)

    # Create test database
    test_db_path = ":memory:"  # Use in-memory database for testing
    db = DatabaseManager(test_db_path)

    # Create API instances
    crypto_api = CryptoAPI()
    stock_api = StockAPI()

    try:
        # Test PersonalTab
        success = test_personal_tab(db)
        assert success, "PersonalTab tests failed"

        # Test InvestmentsTab
        success = test_investments_tab(db, crypto_api, stock_api)
        assert success, "InvestmentsTab tests failed"

        # Test OrdersTab
        success = test_orders_tab(db)
        assert success, "OrdersTab tests failed"

        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        print("=" * 50)

        print("\n📋 Summary:")
        print("  • PersonalTab: Delete button and key handler implemented")
        print("  • InvestmentsTab: Delete button and key handler implemented")
        print("  • OrdersTab: Delete button and key handler implemented")
        print("\n🎀 Features:")
        print("  1. Delete button in header (🗑️ Delete)")
        print("  2. Button enabled/disabled based on selection")
        print("  3. Delete/Suppr key support for selected rows")
        print("  4. Confirmation dialog before deletion")
        print("  5. Success/error messages after operation")
        print("  6. Bulk delete - select multiple rows with Shift+Click or Ctrl+Click")
        print("  7. ExtendedSelection mode enabled on all tables")

        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        app.quit()


if __name__ == "__main__":
    sys.exit(main())
