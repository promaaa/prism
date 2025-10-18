#!/usr/bin/env python3
"""
Add sample data to Prism database for testing and demonstration.
This script populates the database with realistic sample transactions and assets.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src directory to Python path
src_path = Path(__file__).parent / "prism"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager


def add_sample_transactions(db: DatabaseManager):
    """Add sample personal finance transactions."""
    print("Adding sample transactions...")

    # Get dates for the last 3 months
    today = datetime.now()

    # Sample income transactions
    income_transactions = [
        {
            "date": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
            "amount": 3500.0,
            "category": "Salary",
            "description": "Monthly salary - January",
        },
        {
            "date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "amount": 3500.0,
            "category": "Salary",
            "description": "Monthly salary - February",
        },
        {
            "date": (today - timedelta(days=0)).strftime("%Y-%m-%d"),
            "amount": 3500.0,
            "category": "Salary",
            "description": "Monthly salary - March",
        },
        {
            "date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "amount": 500.0,
            "category": "Bonus",
            "description": "Performance bonus",
        },
    ]

    # Sample expense transactions
    expense_categories = {
        "Food": [
            ("Supermarket - weekly groceries", -85.50),
            ("Restaurant - dinner", -45.00),
            ("Coffee shop", -12.50),
            ("Grocery store", -62.30),
            ("Bakery", -8.75),
        ],
        "Transport": [
            ("Gas station", -65.00),
            ("Public transport monthly pass", -75.00),
            ("Parking", -15.00),
            ("Uber ride", -22.50),
        ],
        "Utilities": [
            ("Electricity bill", -85.00),
            ("Internet service", -45.00),
            ("Water bill", -35.00),
            ("Phone bill", -35.00),
        ],
        "Entertainment": [
            ("Cinema tickets", -28.00),
            ("Streaming service", -15.99),
            ("Concert tickets", -75.00),
            ("Book purchase", -18.50),
        ],
        "Shopping": [
            ("Clothing store", -120.00),
            ("Electronics", -250.00),
            ("Home goods", -65.00),
        ],
        "Health": [
            ("Pharmacy", -35.50),
            ("Gym membership", -45.00),
            ("Doctor visit", -60.00),
        ],
    }

    # Add income transactions
    for trans in income_transactions:
        db.add_transaction(
            date=trans["date"],
            amount=trans["amount"],
            category=trans["category"],
            transaction_type="personal",
            description=trans["description"],
        )

    # Add expense transactions spread over the last 90 days
    for category, expenses in expense_categories.items():
        for description, amount in expenses:
            # Random date in the last 90 days
            days_ago = random.randint(1, 90)
            trans_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            db.add_transaction(
                date=trans_date,
                amount=amount,
                category=category,
                transaction_type="personal",
                description=description,
            )

    print(
        f"✅ Added {len(income_transactions) + sum(len(e) for e in expense_categories.values())} transactions"
    )


def add_sample_assets(db: DatabaseManager):
    """Add sample investment assets."""
    print("\nAdding sample assets...")

    # Sample cryptocurrency assets
    crypto_assets = [
        {
            "ticker": "BTC",
            "quantity": 0.125,
            "price_buy": 42000.0,
            "date_buy": "2023-11-15",
            "asset_type": "crypto",
        },
        {
            "ticker": "ETH",
            "quantity": 2.5,
            "price_buy": 2800.0,
            "date_buy": "2023-12-01",
            "asset_type": "crypto",
        },
        {
            "ticker": "SOL",
            "quantity": 15.0,
            "price_buy": 85.0,
            "date_buy": "2024-01-10",
            "asset_type": "crypto",
        },
    ]

    # Sample stock assets
    stock_assets = [
        {
            "ticker": "AAPL",
            "quantity": 10.0,
            "price_buy": 175.50,
            "date_buy": "2023-10-20",
            "asset_type": "stock",
        },
        {
            "ticker": "MSFT",
            "quantity": 5.0,
            "price_buy": 380.00,
            "date_buy": "2023-11-05",
            "asset_type": "stock",
        },
        {
            "ticker": "GOOGL",
            "quantity": 8.0,
            "price_buy": 140.00,
            "date_buy": "2024-01-15",
            "asset_type": "stock",
        },
    ]

    # Add crypto assets
    for asset in crypto_assets:
        db.add_asset(**asset)

    # Add stock assets
    for asset in stock_assets:
        db.add_asset(**asset)

    print(f"✅ Added {len(crypto_assets) + len(stock_assets)} assets")


def add_sample_orders(db: DatabaseManager):
    """Add sample orders to the order book."""
    print("\nAdding sample orders...")

    # Sample orders
    orders = [
        {
            "ticker": "BTC",
            "quantity": 0.125,
            "price": 42000.0,
            "order_type": "buy",
            "date": "2023-11-15",
            "status": "closed",
        },
        {
            "ticker": "ETH",
            "quantity": 2.5,
            "price": 2800.0,
            "order_type": "buy",
            "date": "2023-12-01",
            "status": "closed",
        },
        {
            "ticker": "SOL",
            "quantity": 15.0,
            "price": 85.0,
            "order_type": "buy",
            "date": "2024-01-10",
            "status": "closed",
        },
        {
            "ticker": "AAPL",
            "quantity": 10.0,
            "price": 175.50,
            "order_type": "buy",
            "date": "2023-10-20",
            "status": "closed",
        },
        {
            "ticker": "MSFT",
            "quantity": 5.0,
            "price": 380.00,
            "order_type": "buy",
            "date": "2023-11-05",
            "status": "closed",
        },
        {
            "ticker": "GOOGL",
            "quantity": 8.0,
            "price": 140.00,
            "order_type": "buy",
            "date": "2024-01-15",
            "status": "closed",
        },
        {
            "ticker": "BTC",
            "quantity": 0.05,
            "price": 55000.0,
            "order_type": "buy",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "open",
        },
        {
            "ticker": "ETH",
            "quantity": 1.0,
            "price": 3500.0,
            "order_type": "buy",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "open",
        },
    ]

    for order in orders:
        db.add_order(**order)

    print(f"✅ Added {len(orders)} orders")


def main():
    """Main function to add all sample data."""
    print("=" * 60)
    print("Prism - Add Sample Data")
    print("=" * 60)
    print()

    # Initialize database manager
    print("Connecting to database...")
    db = DatabaseManager()

    # Check if database already has data
    stats = db.get_database_stats()
    if stats["transactions"] > 0 or stats["assets"] > 0:
        print("\n⚠️  Warning: Database already contains data!")
        print(f"   Transactions: {stats['transactions']}")
        print(f"   Assets: {stats['assets']}")
        print(f"   Orders: {stats['orders']}")
        print()
        response = input("Do you want to add sample data anyway? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("\n❌ Cancelled. No data was added.")
            return
        print()

    # Add sample data
    try:
        add_sample_transactions(db)
        add_sample_assets(db)
        add_sample_orders(db)

        print("\n" + "=" * 60)
        print("✅ Sample data added successfully!")
        print("=" * 60)

        # Show summary
        stats = db.get_database_stats()
        balance = db.get_balance()
        portfolio_value = db.get_portfolio_value()

        print("\n📊 Database Summary:")
        print(f"   Transactions: {stats['transactions']}")
        print(f"   Assets: {stats['assets']}")
        print(f"   Orders: {stats['orders']}")
        print(f"   Current Balance: €{balance:,.2f}")
        print(f"   Portfolio Value: €{portfolio_value:,.2f}")
        print(f"   Net Worth: €{balance + portfolio_value:,.2f}")
        print()
        print("💡 You can now run the application to see the sample data:")
        print("   python main.py")
        print()

    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
