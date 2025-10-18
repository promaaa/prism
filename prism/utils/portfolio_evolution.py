"""
Portfolio evolution calculation utilities.

This module provides functions to calculate the true historical value of a portfolio
by taking into account the actual purchase dates of assets, sales, and cash positions,
rather than assuming all assets were held throughout the entire period.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import sqlite3


def calculate_true_portfolio_evolution(
    assets: List[Dict[str, Any]],
    get_historical_prices_func: Callable,
    db_manager=None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_cash: bool = True,
) -> Dict[str, float]:
    """
    Calculate the true evolution of portfolio value over time, including sales and cash.

    This function calculates the portfolio value at each date by:
    1. Determining which assets were owned at each date (based on purchase and sale dates)
    2. Calculating the value of owned assets using historical prices
    3. Adding cash accumulated from sales
    4. Summing up the values to get total wealth

    Args:
        assets: List of asset dictionaries with keys:
                - id: Asset ID
                - ticker: Asset ticker symbol
                - quantity: Number of shares/coins held
                - date_buy: Purchase date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
                - asset_type: Type of asset (stock, crypto, etc.)
        get_historical_prices_func: Function to get historical prices for an asset
                                   Signature: func(asset_id, start_date, end_date) -> List[Dict]
                                   Returns list with 'date' and 'price' keys
        db_manager: Optional DatabaseManager instance to fetch orders and cash data
        start_date: Optional start date (YYYY-MM-DD). If None, uses earliest purchase date
        end_date: Optional end date (YYYY-MM-DD). If None, uses today
        include_cash: Whether to include cash from sales in wealth calculation

    Returns:
        Dictionary mapping date strings (YYYY-MM-DD) to portfolio values (float)

    Example:
        >>> assets = [
        ...     {'id': 1, 'ticker': 'AAPL', 'quantity': 10, 'date_buy': '2024-01-01'},
        ...     {'id': 2, 'ticker': 'BTC', 'quantity': 0.5, 'date_buy': '2024-06-01'},
        ... ]
        >>> evolution = calculate_true_portfolio_evolution(assets, get_prices_func, db_manager)
        >>> print(evolution['2024-06-15'])  # Value on June 15, 2024
        15234.56
    """
    if not assets and not db_manager:
        return {}

    # Get orders data if db_manager is provided
    orders = []
    if db_manager:
        try:
            orders = db_manager.get_all_orders()
        except Exception as e:
            print(f"Warning: Could not fetch orders: {e}")
            orders = []

    # Sort assets by purchase date
    if assets:
        assets_sorted = sorted(assets, key=lambda x: _parse_date(x["date_buy"]))
    else:
        assets_sorted = []

    # Determine date range
    if not start_date:
        if assets_sorted:
            # Use the earliest purchase date
            start_date = _parse_date(assets_sorted[0]["date_buy"]).strftime("%Y-%m-%d")
        elif orders:
            # Use earliest order date
            start_date = min(order["date"] for order in orders)
        else:
            start_date = datetime.now().strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Fetch historical prices for all assets
    asset_prices = {}
    for asset in assets:
        try:
            hist_prices = get_historical_prices_func(asset["id"], start_date, end_date)
            if hist_prices:
                # Normalize dates to YYYY-MM-DD format and store prices
                asset_prices[asset["id"]] = {
                    _normalize_date(p["date"]): p["price"] for p in hist_prices
                }
        except Exception as e:
            # Skip this asset if we can't get historical prices
            print(
                f"Warning: Could not get historical prices for {asset.get('ticker', asset['id'])}: {e}"
            )
            continue

    if not asset_prices:
        # No historical data available
        return {}

    # Collect all unique dates from historical prices
    all_dates = set()
    for prices in asset_prices.values():
        all_dates.update(prices.keys())

    # Build a position tracking system that accounts for buys and sells
    position_tracker = _build_position_tracker(assets, orders) if orders else None

    # Calculate portfolio value for each date
    portfolio_evolution = {}

    for date_str in sorted(all_dates):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        assets_value = 0

        if position_tracker:
            # Use position tracker to get accurate holdings at this date
            holdings = _get_holdings_at_date(position_tracker, date_str)

            for ticker, quantity in holdings.items():
                # Find asset info
                asset_info = next((a for a in assets if a["ticker"] == ticker), None)
                if asset_info and asset_info["id"] in asset_prices:
                    if date_str in asset_prices[asset_info["id"]]:
                        price = asset_prices[asset_info["id"]][date_str]
                        assets_value += quantity * price
        else:
            # Fallback to original logic if no orders
            for asset in assets:
                asset_buy_date = _parse_date(asset["date_buy"])

                # Only count the asset if it was purchased on or before this date
                if asset_buy_date <= date_obj:
                    # Get the price of the asset on this date
                    if (
                        asset["id"] in asset_prices
                        and date_str in asset_prices[asset["id"]]
                    ):
                        price = asset_prices[asset["id"]][date_str]
                        assets_value += asset["quantity"] * price

        # Add cash from sales if enabled
        cash_value = 0
        if include_cash and db_manager:
            cash_value = _get_cumulative_cash_at_date(db_manager, date_str)

        total_value = assets_value + cash_value

        # Only store dates where portfolio has value
        if total_value > 0:
            portfolio_evolution[date_str] = total_value

    return portfolio_evolution


def _parse_date(date_str: str) -> datetime:
    """
    Parse a date string in various formats to datetime object.

    Handles:
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM:SS
    - YYYY-MM-DD HH:MM:SS+TZ

    Args:
        date_str: Date string to parse

    Returns:
        datetime object
    """
    # Try to handle dates with timezone info
    if "+" in date_str or date_str.count(":") > 2:
        # Remove timezone info for parsing
        date_str = date_str.split("+")[0].strip()

    # Parse date (handle both date-only and datetime formats)
    if " " in date_str:
        return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d")


def _normalize_date(date_str: str) -> str:
    """
    Normalize a date string to YYYY-MM-DD format.

    Args:
        date_str: Date string in various formats

    Returns:
        Normalized date string (YYYY-MM-DD)
    """
    date_obj = _parse_date(date_str)
    return date_obj.strftime("%Y-%m-%d")


def get_portfolio_value_at_date(
    assets: List[Dict[str, Any]],
    target_date: str,
    get_price_func: Callable,
) -> float:
    """
    Calculate portfolio value at a specific date.

    Args:
        assets: List of asset dictionaries
        target_date: Target date (YYYY-MM-DD)
        get_price_func: Function to get price for an asset at a date
                       Signature: func(asset_id, date) -> float

    Returns:
        Portfolio value at the target date
    """
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    portfolio_value = 0

    for asset in assets:
        asset_buy_date = _parse_date(asset["date_buy"])

        # Only count if asset was owned at target date
        if asset_buy_date <= target_date_obj:
            try:
                price = get_price_func(asset["id"], target_date)
                if price is not None:
                    portfolio_value += asset["quantity"] * price
            except Exception:
                # Skip if price not available
                continue

    return portfolio_value


def get_asset_holding_periods(
    assets: List[Dict[str, Any]],
) -> Dict[str, Dict[str, str]]:
    """
    Get the holding period for each asset.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dictionary mapping ticker to holding period info:
        {
            'AAPL': {'start': '2024-01-01', 'end': '2024-12-31', 'days': 365},
            ...
        }
    """
    holdings = {}
    today = datetime.now()

    for asset in assets:
        ticker = asset["ticker"]
        buy_date = _parse_date(asset["date_buy"])
        days_held = (today - buy_date).days

        holdings[ticker] = {
            "start": buy_date.strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
            "days": days_held,
        }

    return holdings


def _build_position_tracker(
    assets: List[Dict[str, Any]], orders: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Build a position tracker from assets and orders.

    Returns a dictionary mapping ticker to list of transactions (buys/sells).
    """
    tracker = {}

    # Add all orders
    for order in orders:
        ticker = order["ticker"]
        if ticker not in tracker:
            tracker[ticker] = []

        tracker[ticker].append(
            {
                "date": order["date"],
                "type": order["order_type"],
                "quantity": order["quantity"],
                "price": order["price"],
            }
        )

    # Sort transactions by date
    for ticker in tracker:
        tracker[ticker].sort(key=lambda x: x["date"])

    return tracker


def _get_holdings_at_date(
    position_tracker: Dict[str, List[Dict[str, Any]]], target_date: str
) -> Dict[str, float]:
    """
    Calculate holdings at a specific date based on position tracker.

    Returns a dictionary mapping ticker to quantity held.
    """
    holdings = {}

    for ticker, transactions in position_tracker.items():
        quantity = 0

        for txn in transactions:
            if txn["date"] <= target_date:
                if txn["type"] == "buy":
                    quantity += txn["quantity"]
                elif txn["type"] == "sell":
                    quantity -= txn["quantity"]

        if quantity > 0:
            holdings[ticker] = quantity

    return holdings


def _get_cumulative_cash_at_date(db_manager, target_date: str) -> float:
    """
    Get cumulative cash balance up to a specific date.
    """
    try:
        conn = db_manager._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM portfolio_cash
            WHERE date <= ?
            """,
            (target_date,),
        )

        row = cursor.fetchone()
        conn.close()

        return row["total"] if row else 0.0
    except Exception as e:
        print(f"Warning: Could not get cash at date {target_date}: {e}")
        return 0.0
