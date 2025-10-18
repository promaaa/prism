"""
Calculation utilities for Prism application.
Provides functions for portfolio calculations, performance metrics, and financial analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


def calculate_portfolio_value(assets: List[Dict[str, Any]]) -> float:
    """
    Calculate total portfolio value based on current prices.

    Args:
        assets: List of asset dictionaries with quantity, current_price, price_buy

    Returns:
        float: Total portfolio value
    """
    total_value = 0.0

    for asset in assets:
        quantity = asset.get("quantity", 0.0)
        current_price = asset.get("current_price") or asset.get("price_buy", 0.0)
        total_value += quantity * current_price

    return total_value


def calculate_asset_performance(asset: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate performance metrics for a single asset.

    Args:
        asset: Asset dictionary with quantity, price_buy, current_price

    Returns:
        Dict: Performance metrics including gain/loss and percentage
    """
    quantity = asset.get("quantity", 0.0)
    price_buy = asset.get("price_buy", 0.0)
    current_price = asset.get("current_price") or price_buy

    total_cost = quantity * price_buy
    current_value = quantity * current_price
    gain_loss = current_value - total_cost
    gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0.0

    return {
        "total_cost": total_cost,
        "current_value": current_value,
        "gain_loss": gain_loss,
        "gain_loss_percent": gain_loss_percent,
    }


def calculate_portfolio_performance(assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate overall portfolio performance metrics.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dict: Portfolio performance summary
    """
    total_cost = 0.0
    total_value = 0.0

    for asset in assets:
        perf = calculate_asset_performance(asset)
        total_cost += perf["total_cost"]
        total_value += perf["current_value"]

    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (
        (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0
    )

    return {
        "total_cost": total_cost,
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_percent": total_gain_loss_percent,
        "number_of_assets": len(assets),
    }


def calculate_balance_over_time(
    transactions: List[Dict[str, Any]], interval: str = "daily"
) -> List[Dict[str, Any]]:
    """
    Calculate balance evolution over time from transactions.

    Args:
        transactions: List of transaction dictionaries with date and amount
        interval: Time interval ("daily", "weekly", "monthly")

    Returns:
        List[Dict]: List of balance points with date and balance
    """
    if not transactions:
        return []

    # Sort transactions by date
    sorted_transactions = sorted(transactions, key=lambda x: x.get("date", ""))

    # Group transactions by interval
    balance_data = []
    current_balance = 0.0
    date_groups = defaultdict(float)

    for trans in sorted_transactions:
        date_str = trans.get("date", "")
        amount = trans.get("amount", 0.0)

        if not date_str:
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        # Group by interval
        if interval == "daily":
            group_key = date_obj.strftime("%Y-%m-%d")
        elif interval == "weekly":
            # Start of week (Monday)
            start_of_week = date_obj - timedelta(days=date_obj.weekday())
            group_key = start_of_week.strftime("%Y-%m-%d")
        elif interval == "monthly":
            group_key = date_obj.strftime("%Y-%m")
        else:
            group_key = date_obj.strftime("%Y-%m-%d")

        date_groups[group_key] += amount

    # Calculate cumulative balance
    for date_key in sorted(date_groups.keys()):
        current_balance += date_groups[date_key]
        balance_data.append({"date": date_key, "balance": current_balance})

    return balance_data


def calculate_category_distribution(
    transactions: List[Dict[str, Any]], expense_only: bool = True
) -> List[Dict[str, Any]]:
    """
    Calculate distribution of transactions by category.

    Args:
        transactions: List of transaction dictionaries
        expense_only: If True, only include expenses (negative amounts)

    Returns:
        List[Dict]: Category distribution with totals and percentages
    """
    category_totals = defaultdict(float)
    total_amount = 0.0

    for trans in transactions:
        amount = trans.get("amount", 0.0)
        category = trans.get("category", "Uncategorized")

        # Filter by expense/revenue
        if expense_only and amount >= 0:
            continue
        elif not expense_only and amount < 0:
            continue

        # Use absolute value for expenses
        abs_amount = abs(amount)
        category_totals[category] += abs_amount
        total_amount += abs_amount

    # Calculate percentages
    distribution = []
    for category, amount in sorted(
        category_totals.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0.0
        distribution.append(
            {"category": category, "amount": amount, "percentage": percentage}
        )

    return distribution


def calculate_portfolio_allocation(
    assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Calculate portfolio allocation by asset type.

    Args:
        assets: List of asset dictionaries with asset_type

    Returns:
        List[Dict]: Allocation by asset type with values and percentages
    """
    type_values = defaultdict(float)
    total_value = 0.0

    for asset in assets:
        asset_type = asset.get("asset_type", "Unknown")
        quantity = asset.get("quantity", 0.0)
        current_price = asset.get("current_price") or asset.get("price_buy", 0.0)

        value = quantity * current_price
        type_values[asset_type] += value
        total_value += value

    # Calculate percentages
    allocation = []
    for asset_type, value in sorted(
        type_values.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (value / total_value * 100) if total_value > 0 else 0.0
        allocation.append(
            {"asset_type": asset_type, "value": value, "percentage": percentage}
        )

    return allocation


def calculate_roi(initial_investment: float, current_value: float) -> float:
    """
    Calculate Return on Investment (ROI).

    Args:
        initial_investment: Initial investment amount
        current_value: Current value

    Returns:
        float: ROI as a percentage
    """
    if initial_investment <= 0:
        return 0.0

    return ((current_value - initial_investment) / initial_investment) * 100


def calculate_annualized_return(
    initial_investment: float,
    current_value: float,
    days_held: int,
) -> float:
    """
    Calculate annualized return rate.

    Args:
        initial_investment: Initial investment amount
        current_value: Current value
        days_held: Number of days investment was held

    Returns:
        float: Annualized return as a percentage
    """
    if initial_investment <= 0 or days_held <= 0:
        return 0.0

    years = days_held / 365.25
    if years <= 0:
        return 0.0

    return (((current_value / initial_investment) ** (1 / years)) - 1) * 100


def calculate_monthly_average(
    transactions: List[Dict[str, Any]], months: int = 3
) -> Dict[str, float]:
    """
    Calculate average monthly income and expenses.

    Args:
        transactions: List of transaction dictionaries
        months: Number of months to average over

    Returns:
        Dict: Average monthly income and expenses
    """
    if not transactions:
        return {"avg_income": 0.0, "avg_expenses": 0.0, "avg_net": 0.0}

    total_income = 0.0
    total_expenses = 0.0

    # Get date range
    dates = [
        datetime.strptime(t.get("date", ""), "%Y-%m-%d")
        for t in transactions
        if t.get("date")
    ]

    if not dates:
        return {"avg_income": 0.0, "avg_expenses": 0.0, "avg_net": 0.0}

    min_date = min(dates)
    max_date = max(dates)
    days_span = (max_date - min_date).days
    actual_months = max(days_span / 30.0, 1.0)

    # Use the smaller of actual months or requested months
    months_to_use = min(actual_months, float(months))

    for trans in transactions:
        amount = trans.get("amount", 0.0)
        if amount > 0:
            total_income += amount
        else:
            total_expenses += abs(amount)

    avg_income = total_income / months_to_use if months_to_use > 0 else 0.0
    avg_expenses = total_expenses / months_to_use if months_to_use > 0 else 0.0
    avg_net = avg_income - avg_expenses

    return {
        "avg_income": avg_income,
        "avg_expenses": avg_expenses,
        "avg_net": avg_net,
        "months": months_to_use,
    }


def calculate_savings_rate(income: float, expenses: float) -> float:
    """
    Calculate savings rate as a percentage of income.

    Args:
        income: Total income
        expenses: Total expenses

    Returns:
        float: Savings rate as a percentage
    """
    if income <= 0:
        return 0.0

    savings = income - expenses
    return (savings / income) * 100


def calculate_diversification_score(assets: List[Dict[str, Any]]) -> float:
    """
    Calculate a simple diversification score based on asset distribution.
    Returns a score from 0 to 100, where 100 is perfectly diversified.

    Args:
        assets: List of asset dictionaries

    Returns:
        float: Diversification score (0-100)
    """
    if not assets:
        return 0.0

    # Calculate value by asset type
    allocation = calculate_portfolio_allocation(assets)

    if not allocation:
        return 0.0

    # Calculate Herfindahl-Hirschman Index (HHI)
    # HHI ranges from 1/n to 1 (where n is number of assets)
    # Lower HHI = more diversified
    hhi = sum((item["percentage"] / 100) ** 2 for item in allocation)

    # Convert to diversification score (inverse of HHI, normalized to 0-100)
    # Perfect diversification (equal weights) = 100
    # All in one asset = 0
    num_types = len(allocation)
    if num_types == 1:
        return 0.0

    min_hhi = 1.0  # All in one asset
    max_hhi = 1.0 / num_types  # Perfectly diversified

    # Normalize to 0-100 scale (inverted so higher is better)
    score = ((min_hhi - hhi) / (min_hhi - max_hhi)) * 100

    return max(0.0, min(100.0, score))


def calculate_profit_loss_by_ticker(
    assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Calculate profit/loss for each ticker.

    Args:
        assets: List of asset dictionaries

    Returns:
        List[Dict]: P/L summary by ticker
    """
    ticker_summary = defaultdict(lambda: {"quantity": 0.0, "cost": 0.0, "value": 0.0})

    for asset in assets:
        ticker = asset.get("ticker", "Unknown")
        quantity = asset.get("quantity", 0.0)
        price_buy = asset.get("price_buy", 0.0)
        current_price = asset.get("current_price") or price_buy

        ticker_summary[ticker]["quantity"] += quantity
        ticker_summary[ticker]["cost"] += quantity * price_buy
        ticker_summary[ticker]["value"] += quantity * current_price

    # Calculate P/L for each ticker
    results = []
    for ticker, data in ticker_summary.items():
        pl = data["value"] - data["cost"]
        pl_percent = (pl / data["cost"] * 100) if data["cost"] > 0 else 0.0

        results.append(
            {
                "ticker": ticker,
                "quantity": data["quantity"],
                "total_cost": data["cost"],
                "current_value": data["value"],
                "profit_loss": pl,
                "profit_loss_percent": pl_percent,
            }
        )

    # Sort by absolute profit/loss (descending)
    results.sort(key=lambda x: abs(x["profit_loss"]), reverse=True)

    return results


def get_date_range_from_transactions(
    transactions: List[Dict[str, Any]],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the date range from a list of transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Tuple[Optional[str], Optional[str]]: (min_date, max_date) or (None, None)
    """
    if not transactions:
        return None, None

    dates = [t.get("date") for t in transactions if t.get("date")]

    if not dates:
        return None, None

    return min(dates), max(dates)
