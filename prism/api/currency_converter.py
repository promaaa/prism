"""
Currency conversion module for Prism application.
Handles conversion between USD and EUR using CoinGecko API.
"""

import requests
from typing import Optional, Tuple
from datetime import datetime, timedelta


class CurrencyConverter:
    """
    Handles currency conversion between USD and EUR.
    Uses CoinGecko API with caching and fallback mechanisms.
    """

    def __init__(self, cache_duration_minutes: int = 15):
        """
        Initialize the currency converter.

        Args:
            cache_duration_minutes: How long to cache exchange rates (default: 15 minutes)
        """
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self._cached_rate: Optional[float] = None
        self._cache_timestamp: Optional[datetime] = None
        self.base_url = "https://api.coingecko.com/api/v3"

    def _is_cache_valid(self) -> bool:
        """
        Check if the cached exchange rate is still valid.

        Returns:
            bool: True if cache is valid, False otherwise
        """
        if self._cached_rate is None or self._cache_timestamp is None:
            return False

        age = datetime.now() - self._cache_timestamp
        return age < self.cache_duration

    def _fetch_rate_from_usdc(self) -> Optional[float]:
        """
        Fetch USD to EUR rate using USDC as a proxy.
        USDC is pegged to USD at 1:1, so its EUR price gives us the exchange rate.

        Returns:
            Optional[float]: Exchange rate (USD to EUR) or None if failed
        """
        try:
            url = f"{self.base_url}/simple/price"
            params = {"ids": "usd-coin", "vs_currencies": "eur"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "usd-coin" in data and "eur" in data["usd-coin"]:
                return float(data["usd-coin"]["eur"])

            return None
        except Exception as e:
            print(f"Error fetching USD/EUR rate from USDC: {e}")
            return None

    def _fetch_rate_from_btc_ratio(self) -> Optional[float]:
        """
        Fetch USD to EUR rate using BTC price ratio as fallback.
        Gets BTC price in both USD and EUR, then calculates the ratio.

        Returns:
            Optional[float]: Exchange rate (USD to EUR) or None if failed
        """
        try:
            url = f"{self.base_url}/simple/price"
            params = {"ids": "bitcoin", "vs_currencies": "usd,eur"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "bitcoin" in data:
                btc_data = data["bitcoin"]
                if "usd" in btc_data and "eur" in btc_data:
                    btc_usd = float(btc_data["usd"])
                    btc_eur = float(btc_data["eur"])
                    if btc_usd > 0:
                        # EUR/USD ratio from BTC prices
                        return btc_eur / btc_usd

            return None
        except Exception as e:
            print(f"Error fetching USD/EUR rate from BTC ratio: {e}")
            return None

    def _fetch_rate_fallback_static(self) -> float:
        """
        Fallback to a static approximate exchange rate.
        This should rarely be used, only when all API calls fail.

        Returns:
            float: Static fallback exchange rate (~0.92)
        """
        print("Warning: Using static fallback exchange rate (0.92)")
        return 0.92  # Approximate USD to EUR rate

    def get_usd_eur_rate(self, force_refresh: bool = False) -> float:
        """
        Get the current USD to EUR exchange rate.
        Uses cached value if available and valid, otherwise fetches from API.

        Args:
            force_refresh: Force fetching a new rate even if cache is valid

        Returns:
            float: USD to EUR exchange rate
        """
        # Return cached rate if valid and not forcing refresh
        if not force_refresh and self._is_cache_valid():
            return self._cached_rate

        # Try primary method: USDC price
        rate = self._fetch_rate_from_usdc()

        # Try fallback method: BTC price ratio
        if rate is None:
            rate = self._fetch_rate_from_btc_ratio()

        # Use static fallback if all API calls failed
        if rate is None:
            rate = self._fetch_rate_fallback_static()

        # Update cache
        self._cached_rate = rate
        self._cache_timestamp = datetime.now()

        return rate

    def convert_usd_to_eur(
        self, usd_amount: float, force_refresh: bool = False
    ) -> float:
        """
        Convert an amount from USD to EUR.

        Args:
            usd_amount: Amount in USD
            force_refresh: Force fetching a new exchange rate

        Returns:
            float: Amount in EUR
        """
        rate = self.get_usd_eur_rate(force_refresh)
        return usd_amount * rate

    def convert_eur_to_usd(
        self, eur_amount: float, force_refresh: bool = False
    ) -> float:
        """
        Convert an amount from EUR to USD.

        Args:
            eur_amount: Amount in EUR
            force_refresh: Force fetching a new exchange rate

        Returns:
            float: Amount in USD
        """
        rate = self.get_usd_eur_rate(force_refresh)
        if rate > 0:
            return eur_amount / rate
        return eur_amount  # Fallback if rate is invalid

    def get_rate_info(self) -> Tuple[float, datetime, int]:
        """
        Get exchange rate information including cache age.

        Returns:
            Tuple[float, datetime, int]: (rate, timestamp, age_in_seconds)
        """
        if not self._is_cache_valid():
            # Refresh if cache is invalid
            self.get_usd_eur_rate()

        age = 0
        if self._cache_timestamp:
            age = int((datetime.now() - self._cache_timestamp).total_seconds())

        return (
            self._cached_rate if self._cached_rate else 0.0,
            self._cache_timestamp if self._cache_timestamp else datetime.now(),
            age,
        )

    def get_rate_display_text(self) -> str:
        """
        Get a formatted display text for the current exchange rate.

        Returns:
            str: Formatted text like "1 USD = 0.92 EUR (cached 5m ago)"
        """
        rate, timestamp, age_seconds = self.get_rate_info()

        # Format age
        if age_seconds < 60:
            age_text = f"{age_seconds}s ago"
        elif age_seconds < 3600:
            age_text = f"{age_seconds // 60}m ago"
        else:
            age_text = f"{age_seconds // 3600}h ago"

        return f"1 USD = {rate:.4f} EUR (cached {age_text})"

    def clear_cache(self) -> None:
        """
        Clear the cached exchange rate, forcing a refresh on next request.
        """
        self._cached_rate = None
        self._cache_timestamp = None


# Global instance for app-wide use
_global_converter: Optional[CurrencyConverter] = None


def get_converter() -> CurrencyConverter:
    """
    Get the global CurrencyConverter instance.
    Creates one if it doesn't exist.

    Returns:
        CurrencyConverter: The global converter instance
    """
    global _global_converter
    if _global_converter is None:
        _global_converter = CurrencyConverter()
    return _global_converter


def reset_converter() -> None:
    """
    Reset the global converter instance.
    Useful for testing or changing cache duration.
    """
    global _global_converter
    _global_converter = None
