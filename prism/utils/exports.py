"""
Export utilities for Prism application.
Provides functions for exporting data to CSV and other formats.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


def export_orders_to_csv(orders: List[Dict[str, Any]], output_path: Path) -> bool:
    """
    Export orders to CSV file.

    Args:
        orders: List of order dictionaries
        output_path: Path to output CSV file

    Returns:
        bool: True if export was successful, False otherwise
    """
    if not orders:
        print("No orders to export")
        return False

    try:
        # Define CSV columns
        fieldnames = [
            "id",
            "ticker",
            "quantity",
            "price",
            "order_type",
            "date",
            "status",
            "total_value",
            "created_at",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for order in orders:
                # Calculate total value
                total_value = order.get("quantity", 0.0) * order.get("price", 0.0)

                row = {
                    "id": order.get("id", ""),
                    "ticker": order.get("ticker", ""),
                    "quantity": order.get("quantity", 0.0),
                    "price": order.get("price", 0.0),
                    "order_type": order.get("order_type", ""),
                    "date": order.get("date", ""),
                    "status": order.get("status", ""),
                    "total_value": total_value,
                    "created_at": order.get("created_at", ""),
                }

                writer.writerow(row)

        print(f"Orders exported successfully to {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting orders to CSV: {e}")
        return False


def export_transactions_to_csv(
    transactions: List[Dict[str, Any]], output_path: Path
) -> bool:
    """
    Export transactions to CSV file.

    Args:
        transactions: List of transaction dictionaries
        output_path: Path to output CSV file

    Returns:
        bool: True if export was successful, False otherwise
    """
    if not transactions:
        print("No transactions to export")
        return False

    try:
        # Define CSV columns
        fieldnames = [
            "id",
            "date",
            "amount",
            "category",
            "type",
            "description",
            "created_at",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for transaction in transactions:
                row = {
                    "id": transaction.get("id", ""),
                    "date": transaction.get("date", ""),
                    "amount": transaction.get("amount", 0.0),
                    "category": transaction.get("category", ""),
                    "type": transaction.get("type", ""),
                    "description": transaction.get("description", ""),
                    "created_at": transaction.get("created_at", ""),
                }

                writer.writerow(row)

        print(f"Transactions exported successfully to {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting transactions to CSV: {e}")
        return False


def export_assets_to_csv(assets: List[Dict[str, Any]], output_path: Path) -> bool:
    """
    Export assets to CSV file.

    Args:
        assets: List of asset dictionaries
        output_path: Path to output CSV file

    Returns:
        bool: True if export was successful, False otherwise
    """
    if not assets:
        print("No assets to export")
        return False

    try:
        # Define CSV columns
        fieldnames = [
            "id",
            "ticker",
            "quantity",
            "price_buy",
            "date_buy",
            "current_price",
            "asset_type",
            "total_cost",
            "current_value",
            "gain_loss",
            "gain_loss_percent",
            "created_at",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for asset in assets:
                quantity = asset.get("quantity", 0.0)
                price_buy = asset.get("price_buy", 0.0)
                current_price = asset.get("current_price") or price_buy

                total_cost = quantity * price_buy
                current_value = quantity * current_price
                gain_loss = current_value - total_cost
                gain_loss_percent = (
                    (gain_loss / total_cost * 100) if total_cost > 0 else 0.0
                )

                row = {
                    "id": asset.get("id", ""),
                    "ticker": asset.get("ticker", ""),
                    "quantity": quantity,
                    "price_buy": price_buy,
                    "date_buy": asset.get("date_buy", ""),
                    "current_price": current_price,
                    "asset_type": asset.get("asset_type", ""),
                    "total_cost": total_cost,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "gain_loss_percent": gain_loss_percent,
                    "created_at": asset.get("created_at", ""),
                }

                writer.writerow(row)

        print(f"Assets exported successfully to {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting assets to CSV: {e}")
        return False


def export_portfolio_summary_to_csv(
    assets: List[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    output_path: Path,
) -> bool:
    """
    Export a portfolio summary to CSV file.

    Args:
        assets: List of asset dictionaries
        transactions: List of transaction dictionaries
        output_path: Path to output CSV file

    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        # Calculate summary statistics
        total_asset_value = sum(
            asset.get("quantity", 0.0)
            * (asset.get("current_price") or asset.get("price_buy", 0.0))
            for asset in assets
        )

        total_asset_cost = sum(
            asset.get("quantity", 0.0) * asset.get("price_buy", 0.0) for asset in assets
        )

        total_balance = sum(
            trans.get("amount", 0.0)
            for trans in transactions
            if trans.get("type") == "personal"
        )

        total_gain_loss = total_asset_value - total_asset_cost
        total_gain_loss_percent = (
            (total_gain_loss / total_asset_cost * 100) if total_asset_cost > 0 else 0.0
        )

        # Create summary data
        summary_data = [
            {
                "metric": "Export Date",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {"metric": "Total Assets", "value": len(assets)},
            {"metric": "Total Transactions", "value": len(transactions)},
            {"metric": "Cash Balance", "value": f"{total_balance:.2f}"},
            {"metric": "Portfolio Cost", "value": f"{total_asset_cost:.2f}"},
            {"metric": "Portfolio Value", "value": f"{total_asset_value:.2f}"},
            {"metric": "Total Gain/Loss", "value": f"{total_gain_loss:.2f}"},
            {"metric": "Total Gain/Loss %", "value": f"{total_gain_loss_percent:.2f}%"},
            {
                "metric": "Net Worth",
                "value": f"{total_balance + total_asset_value:.2f}",
            },
        ]

        # Write to CSV
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["metric", "value"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in summary_data:
                writer.writerow(row)

        print(f"Portfolio summary exported successfully to {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting portfolio summary to CSV: {e}")
        return False


def export_category_summary_to_csv(
    transactions: List[Dict[str, Any]], output_path: Path
) -> bool:
    """
    Export category summary to CSV file.

    Args:
        transactions: List of transaction dictionaries
        output_path: Path to output CSV file

    Returns:
        bool: True if export was successful, False otherwise
    """
    if not transactions:
        print("No transactions to export")
        return False

    try:
        from collections import defaultdict

        # Calculate category totals
        category_income = defaultdict(float)
        category_expenses = defaultdict(float)

        for trans in transactions:
            amount = trans.get("amount", 0.0)
            category = trans.get("category", "Uncategorized")

            if amount > 0:
                category_income[category] += amount
            else:
                category_expenses[category] += abs(amount)

        # Combine all categories
        all_categories = set(category_income.keys()) | set(category_expenses.keys())

        # Write to CSV
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["category", "income", "expenses", "net"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for category in sorted(all_categories):
                income = category_income.get(category, 0.0)
                expenses = category_expenses.get(category, 0.0)
                net = income - expenses

                row = {
                    "category": category,
                    "income": income,
                    "expenses": expenses,
                    "net": net,
                }

                writer.writerow(row)

        print(f"Category summary exported successfully to {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting category summary to CSV: {e}")
        return False


def get_default_export_path(filename: str) -> Path:
    """
    Get the default export path for a file.

    Args:
        filename: Name of the file to export

    Returns:
        Path: Default export path
    """
    # Use Downloads folder on macOS
    downloads_path = Path.home() / "Downloads"

    # Add timestamp to filename to avoid overwriting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "csv")
    filename_with_timestamp = f"{name}_{timestamp}.{ext}"

    return downloads_path / filename_with_timestamp


# Example usage
if __name__ == "__main__":
    # Test data
    test_orders = [
        {
            "id": 1,
            "ticker": "BTC",
            "quantity": 0.5,
            "price": 50000.0,
            "order_type": "buy",
            "date": "2024-01-15",
            "status": "closed",
            "created_at": "2024-01-15 10:30:00",
        },
        {
            "id": 2,
            "ticker": "ETH",
            "quantity": 2.0,
            "price": 3000.0,
            "order_type": "buy",
            "date": "2024-01-20",
            "status": "open",
            "created_at": "2024-01-20 14:15:00",
        },
    ]

    test_transactions = [
        {
            "id": 1,
            "date": "2024-01-01",
            "amount": 3000.0,
            "category": "Salary",
            "type": "personal",
            "description": "Monthly salary",
            "created_at": "2024-01-01 00:00:00",
        },
        {
            "id": 2,
            "date": "2024-01-05",
            "amount": -50.0,
            "category": "Food",
            "type": "personal",
            "description": "Groceries",
            "created_at": "2024-01-05 18:30:00",
        },
    ]

    # Test exports
    output_dir = Path("/tmp/prism_exports")
    output_dir.mkdir(exist_ok=True)

    print("Testing order export...")
    export_orders_to_csv(test_orders, output_dir / "orders.csv")

    print("\nTesting transaction export...")
    export_transactions_to_csv(test_transactions, output_dir / "transactions.csv")

    print("\nExport tests completed!")
