"""
Cryptocurrency API integration for Prism application.
Fetches real-time cryptocurrency prices from CoinGecko API.
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from utils.logger import get_logger, log_exception, log_performance

# Initialize logger for this module
logger = get_logger("api.crypto")


class CryptoAPI:
    """
    Handles cryptocurrency price fetching from CoinGecko API.
    Supports both synchronous and asynchronous requests.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    # Mapping of common ticker symbols to CoinGecko IDs
    TICKER_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "USDC": "usd-coin",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "TRX": "tron",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "LTC": "litecoin",
        "ATOM": "cosmos",
        "XLM": "stellar",
        "ALGO": "algorand",
        "VET": "vechain",
        "TAO": "bittensor",
        "FET": "fetch-ai",
        "AGIX": "singularitynet",
        "OCEAN": "ocean-protocol",
        "RNDR": "render-token",
    }

    def __init__(self, timeout: int = 10):
        """
        Initialize the CryptoAPI.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        logger.info("CryptoAPI initialized with timeout=%s", timeout)

    def _get_coingecko_id(self, ticker: str) -> str:
        """
        Convert ticker symbol to CoinGecko ID.

        Args:
            ticker: Cryptocurrency ticker (e.g., "BTC")

        Returns:
            str: CoinGecko ID (e.g., "bitcoin")
        """
        ticker_upper = ticker.upper()
        return self.TICKER_TO_ID.get(ticker_upper, ticker.lower())

    def _is_cache_valid(self, ticker: str) -> bool:
        """
        Check if cached price is still valid.

        Args:
            ticker: Cryptocurrency ticker

        Returns:
            bool: True if cache is valid
        """
        if ticker not in self._cache or ticker not in self._cache_timestamp:
            return False

        age = datetime.now() - self._cache_timestamp[ticker]
        return age < self._cache_duration

    @log_exception
    @log_performance("crypto_get_price")
    def get_price(
        self, ticker: str, currency: str = "eur", use_cache: bool = True
    ) -> Optional[float]:
        """
        Get current price for a cryptocurrency (synchronous).

        Args:
            ticker: Cryptocurrency ticker (e.g., "BTC", "ETH")
            currency: Target currency (default: "eur")
            use_cache: Whether to use cached prices

        Returns:
            Optional[float]: Current price or None if fetch fails
        """
        logger.debug(
            f"Fetching price for {ticker} in {currency} (use_cache={use_cache})"
        )

        # Check cache first
        if use_cache and self._is_cache_valid(ticker):
            cached_data = self._cache.get(ticker, {})
            price = cached_data.get(currency)
            logger.debug(f"Returning cached price for {ticker}: {price}")
            return price

        coin_id = self._get_coingecko_id(ticker)
        url = f"{self.BASE_URL}/simple/price"
        params = {"ids": coin_id, "vs_currencies": currency}

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if coin_id in data and currency in data[coin_id]:
                price = data[coin_id][currency]

                # Update cache
                self._cache[ticker] = {currency: price}
                self._cache_timestamp[ticker] = datetime.now()

                logger.info(
                    f"Successfully fetched price for {ticker}: {price} {currency.upper()}"
                )
                return price

            logger.warning(f"Price not found in response for {ticker}")
            return None

        except requests.RequestException as e:
            logger.error(f"Error fetching price for {ticker}: {e}", exc_info=False)

            # Return cached price if available
            if ticker in self._cache:
                cached_data = self._cache[ticker]
                price = cached_data.get(currency)
                logger.info(f"Returning cached price for {ticker} after error: {price}")
                return price

            return None

    @log_exception
    @log_performance("crypto_get_multiple_prices")
    def get_multiple_prices(
        self, tickers: List[str], currency: str = "eur", use_cache: bool = True
    ) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple cryptocurrencies (synchronous).

        Args:
            tickers: List of cryptocurrency tickers
            currency: Target currency (default: "eur")
            use_cache: Whether to use cached prices

        Returns:
            Dict[str, Optional[float]]: Dictionary mapping tickers to prices
        """
        logger.debug(f"Fetching prices for {len(tickers)} tickers: {tickers}")

        results = {}
        uncached_tickers = []

        # Check cache first
        if use_cache:
            for ticker in tickers:
                if self._is_cache_valid(ticker):
                    cached_data = self._cache.get(ticker, {})
                    results[ticker] = cached_data.get(currency)
                else:
                    uncached_tickers.append(ticker)
        else:
            uncached_tickers = tickers

        # Fetch uncached tickers
        if uncached_tickers:
            coin_ids = [self._get_coingecko_id(t) for t in uncached_tickers]
            url = f"{self.BASE_URL}/simple/price"
            params = {"ids": ",".join(coin_ids), "vs_currencies": currency}

            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                for ticker in uncached_tickers:
                    coin_id = self._get_coingecko_id(ticker)
                    if coin_id in data and currency in data[coin_id]:
                        price = data[coin_id][currency]
                        results[ticker] = price

                        # Update cache
                        self._cache[ticker] = {currency: price}
                        self._cache_timestamp[ticker] = datetime.now()
                    else:
                        results[ticker] = None

            except requests.RequestException as e:
                logger.error(f"Error fetching multiple prices: {e}", exc_info=False)

                # Use cached prices for failed fetches
                for ticker in uncached_tickers:
                    if ticker in self._cache:
                        cached_data = self._cache[ticker]
                        results[ticker] = cached_data.get(currency)
                        logger.debug(
                            f"Using cached price for {ticker} after batch error"
                        )
                    else:
                        results[ticker] = None

        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"Fetched prices for {successful}/{len(tickers)} tickers")
        return results

    async def get_price_async(
        self, ticker: str, currency: str = "eur", use_cache: bool = True
    ) -> Optional[float]:
        """
        Get current price for a cryptocurrency (asynchronous).

        Args:
            ticker: Cryptocurrency ticker (e.g., "BTC", "ETH")
            currency: Target currency (default: "eur")
            use_cache: Whether to use cached prices

        Returns:
            Optional[float]: Current price or None if fetch fails
        """
        logger.debug(f"Async fetching price for {ticker} in {currency}")

        # Check cache first
        if use_cache and self._is_cache_valid(ticker):
            cached_data = self._cache.get(ticker, {})
            price = cached_data.get(currency)
            logger.debug(f"Returning cached price for {ticker}: {price}")
            return price

        coin_id = self._get_coingecko_id(ticker)
        url = f"{self.BASE_URL}/simple/price"
        params = {"ids": coin_id, "vs_currencies": currency}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if coin_id in data and currency in data[coin_id]:
                        price = data[coin_id][currency]

                        # Update cache
                        self._cache[ticker] = {currency: price}
                        self._cache_timestamp[ticker] = datetime.now()

                        logger.info(
                            f"Successfully fetched price (async) for {ticker}: {price}"
                        )
                        return price

                    logger.warning(f"Price not found in async response for {ticker}")
                    return None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(
                f"Error fetching price (async) for {ticker}: {e}", exc_info=False
            )

            # Return cached price if available
            if ticker in self._cache:
                cached_data = self._cache[ticker]
                price = cached_data.get(currency)
                logger.info(
                    f"Returning cached price for {ticker} after async error: {price}"
                )
                return price

            return None

    async def get_multiple_prices_async(
        self, tickers: List[str], currency: str = "eur", use_cache: bool = True
    ) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple cryptocurrencies (asynchronous).

        Args:
            tickers: List of cryptocurrency tickers
            currency: Target currency (default: "eur")
            use_cache: Whether to use cached prices

        Returns:
            Dict[str, Optional[float]]: Dictionary mapping tickers to prices
        """
        logger.debug(f"Async fetching prices for {len(tickers)} tickers")

        results = {}
        uncached_tickers = []

        # Check cache first
        if use_cache:
            for ticker in tickers:
                if self._is_cache_valid(ticker):
                    cached_data = self._cache.get(ticker, {})
                    results[ticker] = cached_data.get(currency)
                else:
                    uncached_tickers.append(ticker)
        else:
            uncached_tickers = tickers

        # Fetch uncached tickers
        if uncached_tickers:
            coin_ids = [self._get_coingecko_id(t) for t in uncached_tickers]
            url = f"{self.BASE_URL}/simple/price"
            params = {"ids": ",".join(coin_ids), "vs_currencies": currency}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()

                        for ticker in uncached_tickers:
                            coin_id = self._get_coingecko_id(ticker)
                            if coin_id in data and currency in data[coin_id]:
                                price = data[coin_id][currency]
                                results[ticker] = price

                                # Update cache
                                self._cache[ticker] = {currency: price}
                                self._cache_timestamp[ticker] = datetime.now()
                            else:
                                results[ticker] = None

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Error fetching prices (async): {e}", exc_info=False)

                # Use cached prices for failed fetches
                for ticker in uncached_tickers:
                    if ticker in self._cache:
                        cached_data = self._cache[ticker]
                        results[ticker] = cached_data.get(currency)
                        logger.debug(
                            f"Using cached price for {ticker} after async batch error"
                        )
                    else:
                        results[ticker] = None

        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"Async fetched prices for {successful}/{len(tickers)} tickers")
        return results

    @log_exception
    def get_coin_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a cryptocurrency.

        Args:
            ticker: Cryptocurrency ticker

        Returns:
            Optional[Dict]: Coin information or None if fetch fails
        """
        logger.debug(f"Fetching coin info for {ticker}")

        coin_id = self._get_coingecko_id(ticker)
        url = f"{self.BASE_URL}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Successfully fetched coin info for {ticker}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching info for {ticker}: {e}", exc_info=False)
            return None

    def clear_cache(self) -> None:
        """Clear the price cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info(f"Cache cleared ({cache_size} entries removed)")

    def add_custom_mapping(self, ticker: str, coingecko_id: str) -> None:
        """
        Add a custom ticker to CoinGecko ID mapping.

        Args:
            ticker: Ticker symbol
            coingecko_id: CoinGecko ID
        """
        self.TICKER_TO_ID[ticker.upper()] = coingecko_id
        logger.info(f"Added custom mapping: {ticker.upper()} -> {coingecko_id}")


# Example usage
if __name__ == "__main__":
    api = CryptoAPI()

    # Test single price fetch
    btc_price = api.get_price("BTC")
    print(f"Bitcoin price: €{btc_price}")

    # Test multiple prices fetch
    prices = api.get_multiple_prices(["BTC", "ETH", "SOL"])
    for ticker, price in prices.items():
        print(f"{ticker}: €{price}")

    # Test async fetch
    async def test_async():
        price = await api.get_price_async("BTC")
        print(f"Bitcoin price (async): €{price}")

    asyncio.run(test_async())
