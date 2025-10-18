#!/usr/bin/env python3
"""
Balance Adjustment Script for Prism Personal Finances.

This script helps adjust the current balance displayed in Personal Finances
by adding an adjustment transaction to account for discrepancies between
calculated balance and actual bank balance.

Usage:
    python scripts/adjust_balance.py

The script will:
1. Show current calculated balance
2. Ask for the correct balance
3. Add an adjustment transaction to fix the difference
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prism.database.db_manager import DatabaseManager


def get_current_balance(db):
    """Get the current calculated balance."""
    return db.get_balance()


def add_adjustment_transaction(db, amount, description="Balance adjustment"):
    """Add an adjustment transaction to fix balance discrepancy."""
    today = datetime.now().strftime("%Y-%m-%d")

    transaction_id = db.add_transaction(
        date=today,
        amount=amount,
        category="Adjustment",
        transaction_type="personal",
        description=description,
    )

    return transaction_id


def main():
    """Main function to adjust balance."""
    print("=" * 60)
    print("PRISM BALANCE ADJUSTMENT TOOL")
    print("=" * 60)
    print()

    # Connect to database
    db = DatabaseManager()

    # Get current balance
    current_balance = get_current_balance(db)
    print(f"Current calculated balance: €{current_balance:.2f}")
    print()

    # Set target balance to 1213.97€
    correct_balance = 1213.97
    print(f"Target balance: €{correct_balance:.2f}")

    print(f"Target balance: €{correct_balance:.2f}")
    print()

    # Calculate adjustment needed
    adjustment_needed = correct_balance - current_balance

    if abs(adjustment_needed) < 0.01:
        print("✅ Balance is already correct - no adjustment needed!")
        return 0

    print(f"Adjustment needed: €{adjustment_needed:.2f}")
    print()

    # Automatically proceed with adjustment
    print("Proceeding with automatic adjustment...")

    # Add adjustment transaction
    try:
        description = (
            f"Balance adjustment: {current_balance:.2f}€ → {correct_balance:.2f}€"
        )

        transaction_id = add_adjustment_transaction(db, adjustment_needed, description)

        print("\n✅ SUCCESS!")
        print(f"   Added adjustment transaction (ID: {transaction_id})")
        print(f"   New balance: €{correct_balance:.2f}")
        print(f"   Adjustment amount: €{adjustment_needed:.2f}")
        print()
        print("The Personal Finances tab will now show the correct balance.")
        print("You can delete this adjustment transaction later if needed.")

        return 0

    except Exception as e:
        print(f"❌ ERROR: Failed to add adjustment transaction: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
