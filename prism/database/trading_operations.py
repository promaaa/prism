"""
Trading operations module for managing buy/sell transactions.

This module provides high-level operations for buying and selling assets,
ensuring proper tracking of orders, cash flow, and portfolio positions.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ..utils.logger import get_logger

logger = get_logger("trading_operations")


class TradingManager:
    """
    Manages trading operations including buying, selling, and tracking cash.
    """

    def __init__(self, db_manager):
        """
        Initialize TradingManager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def buy_asset(
        self,
        ticker: str,
        quantity: float,
        price: float,
        date: str,
        asset_type: str,
        price_currency: str = "EUR",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Buy an asset and record the transaction.

        This function:
        1. Creates an order record (buy)
        2. Adds or updates the asset in the portfolio
        3. Deducts cash if tracking cash balance

        Args:
            ticker: Asset ticker symbol
            quantity: Quantity to buy
            price: Price per unit
            date: Purchase date (YYYY-MM-DD)
            asset_type: Type of asset ('crypto', 'stock', 'bond')
            price_currency: Currency of the price ('EUR' or 'USD')
            notes: Optional notes about the purchase

        Returns:
            Dictionary with order_id and asset_id
        """
        logger.info(f"Buying {quantity} {ticker} at {price} {price_currency} on {date}")

        try:
            # Create order record
            order_id = self.db.add_order(
                ticker=ticker,
                order_type="buy",
                quantity=quantity,
                price=price,
                order_date=date,
                status="closed",
            )

            # Update the order with additional info
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE orders
                SET asset_type = ?, price_currency = ?, notes = ?
                WHERE id = ?
                """,
                (asset_type, price_currency, notes, order_id),
            )
            conn.commit()
            conn.close()

            # Add or update asset
            asset_id = self._add_or_update_asset(
                ticker=ticker,
                quantity=quantity,
                price_buy=price,
                date_buy=date,
                asset_type=asset_type,
                price_currency=price_currency,
            )

            # Link order to asset
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET asset_id = ? WHERE id = ?", (asset_id, order_id)
            )
            conn.commit()
            conn.close()

            # Record cash outflow
            total_cost = quantity * price
            self._record_cash_transaction(
                amount=-total_cost,
                currency=price_currency,
                source="buy",
                date=date,
                related_order_id=order_id,
                notes=f"Purchase of {quantity} {ticker}",
            )

            logger.info(
                f"Buy order completed: order_id={order_id}, asset_id={asset_id}"
            )

            return {
                "success": True,
                "order_id": order_id,
                "asset_id": asset_id,
                "total_cost": total_cost,
            }

        except Exception as e:
            logger.error(f"Error buying asset: {e}")
            return {"success": False, "error": str(e)}

    def sell_asset(
        self,
        ticker: str,
        quantity: float,
        price: float,
        date: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sell an asset and record the transaction.

        This function:
        1. Creates an order record (sell)
        2. Reduces or removes the asset from the portfolio
        3. Records cash inflow from the sale
        4. Calculates and records gain/loss

        Args:
            ticker: Asset ticker symbol
            quantity: Quantity to sell
            price: Sale price per unit
            date: Sale date (YYYY-MM-DD)
            notes: Optional notes about the sale

        Returns:
            Dictionary with order_id, gain/loss info, and remaining quantity
        """
        logger.info(f"Selling {quantity} {ticker} at {price} on {date}")

        try:
            # Get current position
            assets = self._get_assets_by_ticker(ticker)
            if not assets:
                return {
                    "success": False,
                    "error": f"No assets found for ticker {ticker}",
                }

            # Calculate total available quantity
            total_quantity = sum(asset["quantity"] for asset in assets)
            if total_quantity < quantity:
                return {
                    "success": False,
                    "error": f"Insufficient quantity. Available: {total_quantity}, Requested: {quantity}",
                }

            # Calculate average cost basis
            total_cost = sum(asset["quantity"] * asset["price_buy"] for asset in assets)
            avg_cost_basis = total_cost / total_quantity if total_quantity > 0 else 0

            # Calculate gain/loss
            sale_proceeds = quantity * price
            cost_basis = quantity * avg_cost_basis
            gain_loss = sale_proceeds - cost_basis

            # Get asset type and currency from first asset
            asset_type = assets[0]["asset_type"]
            price_currency = assets[0].get("price_currency", "EUR")

            # Create sell order
            order_id = self.db.add_order(
                ticker=ticker,
                order_type="sell",
                quantity=quantity,
                price=price,
                order_date=date,
                status="closed",
            )

            # Update order with additional info
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE orders
                SET asset_type = ?, price_currency = ?, gain_loss = ?, notes = ?
                WHERE id = ?
                """,
                (asset_type, price_currency, gain_loss, notes, order_id),
            )
            conn.commit()
            conn.close()

            # Reduce asset quantity (FIFO - First In First Out)
            remaining_to_sell = quantity
            for asset in sorted(assets, key=lambda x: x["date_buy"]):
                if remaining_to_sell <= 0:
                    break

                asset_quantity = asset["quantity"]
                if asset_quantity <= remaining_to_sell:
                    # Sell entire position
                    self.db.delete_asset(asset["id"])
                    remaining_to_sell -= asset_quantity
                else:
                    # Partial sale
                    new_quantity = asset_quantity - remaining_to_sell
                    self.db.update_asset(asset["id"], quantity=new_quantity)
                    remaining_to_sell = 0

            # Record cash inflow
            self._record_cash_transaction(
                amount=sale_proceeds,
                currency=price_currency,
                source="sell",
                date=date,
                related_order_id=order_id,
                notes=f"Sale of {quantity} {ticker} - Gain/Loss: {gain_loss:.2f} {price_currency}",
            )

            remaining_quantity = total_quantity - quantity

            logger.info(
                f"Sell order completed: order_id={order_id}, gain_loss={gain_loss:.2f}"
            )

            return {
                "success": True,
                "order_id": order_id,
                "sale_proceeds": sale_proceeds,
                "cost_basis": cost_basis,
                "gain_loss": gain_loss,
                "gain_loss_percent": (gain_loss / cost_basis * 100)
                if cost_basis > 0
                else 0,
                "remaining_quantity": remaining_quantity,
            }

        except Exception as e:
            import traceback

            logger.error(f"Error selling asset: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_total_cash(self, currency: str = "EUR") -> float:
        """
        Get total cash balance for a given currency.

        Args:
            currency: Currency to get balance for ('EUR' or 'USD')

        Returns:
            Total cash balance
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM portfolio_cash
            WHERE currency = ?
            """,
            (currency,),
        )

        row = cursor.fetchone()
        conn.close()

        return row["total"] if row else 0.0

    def get_cash_history(
        self, currency: Optional[str] = None, start_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get history of cash transactions.

        Args:
            currency: Optional currency filter
            start_date: Optional start date filter

        Returns:
            List of cash transaction records
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM portfolio_cash WHERE 1=1"
        params = []

        if currency:
            query += " AND currency = ?"
            params.append(currency)

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        query += " ORDER BY date DESC, created_at DESC"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_total_wealth(
        self, currency: str = "EUR", include_cash: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total wealth (assets + cash).

        Args:
            currency: Currency for calculation
            include_cash: Whether to include cash balance

        Returns:
            Dictionary with assets_value, cash, and total_wealth
        """
        # Get portfolio value
        summary = self.db.get_portfolio_summary()
        assets_value = summary.get("total_value", 0)

        cash = 0
        if include_cash:
            cash = self.get_total_cash(currency)

        total_wealth = assets_value + cash

        return {
            "assets_value": assets_value,
            "cash": cash,
            "total_wealth": total_wealth,
            "currency": currency,
        }

    def get_all_transactions(
        self, ticker: Optional[str] = None, order_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all trading transactions (orders).

        Args:
            ticker: Optional ticker filter
            order_type: Optional type filter ('buy' or 'sell')

        Returns:
            List of all orders with full details
        """
        orders = self.db.get_all_orders(ticker=ticker, order_type=order_type)

        # Enrich with additional calculated fields
        for order in orders:
            order["total_value"] = order["quantity"] * order["price"]

        return orders

    # Private helper methods

    def _add_or_update_asset(
        self,
        ticker: str,
        quantity: float,
        price_buy: float,
        date_buy: str,
        asset_type: str,
        price_currency: str,
    ) -> int:
        """
        Add a new asset or update existing one.

        For buying, we add a new entry for each purchase to track cost basis properly.
        """
        # Add new asset entry
        asset_id = self.db.add_asset(
            ticker=ticker,
            quantity=quantity,
            price_buy=price_buy,
            date_buy=date_buy,
            asset_type=asset_type,
            price_currency=price_currency,
        )

        return asset_id

    def _get_assets_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Get all asset positions for a given ticker."""
        all_assets = self.db.get_all_assets()
        # Convert Row objects to dicts
        return [dict(asset) for asset in all_assets if asset["ticker"] == ticker]

    def _record_cash_transaction(
        self,
        amount: float,
        currency: str,
        source: str,
        date: str,
        related_order_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Record a cash transaction."""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO portfolio_cash (amount, currency, source, date, related_order_id, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (amount, currency, source, date, related_order_id, notes),
        )

        cash_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.debug(
            f"Cash transaction recorded: {amount} {currency} from {source} on {date}"
        )

        return cash_id
