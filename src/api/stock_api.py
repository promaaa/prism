"""
Stock API integration for Prism application.
Fetches real-time stock prices using yfinance library.
"""

import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.logger import get_logger, log_exception, log_performance

# Initialize logger for this module
logger = get_logger("api.stock")


class StockAPI:
    """
    Handles stock price fetching using yfinance.
    Supports stocks from multiple exchanges (US, European, etc.).
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the StockAPI.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        self._executor = ThreadPoolExecutor(max_workers=5)
        logger.info("StockAPI initialized with timeout=%s", timeout)

    def _is_cache_valid(self, ticker: str) -> bool:
        """
        Check if cached price is still valid.

        Args:
            ticker: Stock ticker

        Returns:
            bool: True if cache is valid
        """
        if ticker not in self._cache or ticker not in self._cache_timestamp:
            return False

        age = datetime.now() - self._cache_timestamp[ticker]
        return age < self._cache_duration

    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normalize ticker symbol for yfinance.
        Handles European stocks and other formats.

        Args:
            ticker: Stock ticker

        Returns:
            str: Normalized ticker
        """
        ticker = ticker.upper().strip()

        # Common European stock exchanges
        # Paris: .PA (e.g., LVMH.PA)
        # Frankfurt: .F or .DE (e.g., BMW.DE)
        # London: .L (e.g., BP.L)
        # Amsterdam: .AS (e.g., ASML.AS)
        # Milan: .MI (e.g., UCG.MI)

        return ticker

    @log_exception
    @log_performance("stock_get_price")
    def get_price(self, ticker: str, use_cache: bool = True) -> Optional[float]:
        """
        Get current price for a stock (synchronous).

        Args:
            ticker: Stock ticker (e.g., "AAPL", "LVMH.PA")
            use_cache: Whether to use cached prices

        Returns:
            Optional[float]: Current price or None if fetch fails
        """
        logger.debug(f"Fetching price for {ticker} (use_cache={use_cache})")

        # Check cache first
        if use_cache and self._is_cache_valid(ticker):
            cached_data = self._cache.get(ticker, {})
            price = cached_data.get("price")
            logger.debug(f"Returning cached price for {ticker}: {price}")
            return price

        normalized_ticker = self._normalize_ticker(ticker)

        try:
            stock = yf.Ticker(normalized_ticker)
            info = stock.info

            # Try different price fields in order of preference
            price = None
            price_fields = [
                "currentPrice",
                "regularMarketPrice",
                "previousClose",
                "ask",
                "bid",
            ]

            for field in price_fields:
                if field in info and info[field] is not None:
                    price = float(info[field])
                    break

            if price is not None:
                # Update cache
                self._cache[ticker] = {
                    "price": price,
                    "currency": info.get("currency", "EUR"),
                    "name": info.get("shortName", ticker),
                }
                self._cache_timestamp[ticker] = datetime.now()

                logger.info(f"Successfully fetched price for {ticker}: {price}")
                return price

            # Fallback: try to get price from history
            hist = stock.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])

                # Update cache
                self._cache[ticker] = {
                    "price": price,
                    "currency": "EUR",  # Default currency
                    "name": ticker,
                }
                self._cache_timestamp[ticker] = datetime.now()

                logger.info(
                    f"Successfully fetched price (from history) for {ticker}: {price}"
                )
                return price

            logger.warning(f"Price not found for {ticker}")
            return None

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}", exc_info=False)

            # Return cached price if available
            if ticker in self._cache:
                cached_data = self._cache[ticker]
                price = cached_data.get("price")
                logger.info(f"Returning cached price for {ticker} after error: {price}")
                return price

            return None

    @log_exception
    @log_performance("stock_get_multiple_prices")
    def get_multiple_prices(
        self, tickers: List[str], use_cache: bool = True
    ) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple stocks (synchronous).

        Args:
            tickers: List of stock tickers
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
                    results[ticker] = cached_data.get("price")
                else:
                    uncached_tickers.append(ticker)
        else:
            uncached_tickers = tickers

        # Fetch uncached tickers
        if uncached_tickers:
            # Normalize tickers
            normalized_tickers = [self._normalize_ticker(t) for t in uncached_tickers]

            try:
                # Use yfinance download for multiple tickers (faster)
                tickers_str = " ".join(normalized_tickers)
                data = yf.download(
                    tickers_str,
                    period="1d",
                    progress=False,
                    show_errors=False,
                    threads=True,
                )

                # Handle single ticker case
                if len(uncached_tickers) == 1:
                    ticker = uncached_tickers[0]
                    if not data.empty and "Close" in data.columns:
                        price = float(data["Close"].iloc[-1])
                        results[ticker] = price

                        # Update cache
                        self._cache[ticker] = {
                            "price": price,
                            "currency": "EUR",
                            "name": ticker,
                        }
                        self._cache_timestamp[ticker] = datetime.now()
                    else:
                        results[ticker] = None
                else:
                    # Multiple tickers
                    for i, ticker in enumerate(uncached_tickers):
                        try:
                            if not data.empty and "Close" in data.columns:
                                # Extract price for this ticker
                                if isinstance(data["Close"], pd.DataFrame):
                                    normalized = normalized_tickers[i]
                                    if normalized in data["Close"].columns:
                                        price = float(
                                            data["Close"][normalized].iloc[-1]
                                        )
                                    else:
                                        price = None
                                else:
                                    price = float(data["Close"].iloc[-1])

                                if price is not None:
                                    results[ticker] = price

                                    # Update cache
                                    self._cache[ticker] = {
                                        "price": price,
                                        "currency": "EUR",
                                        "name": ticker,
                                    }
                                    self._cache_timestamp[ticker] = datetime.now()
                                else:
                                    results[ticker] = None
                            else:
                                results[ticker] = None
                        except Exception as e:
                            print(f"Error processing {ticker}: {e}")
                            results[ticker] = None

            except Exception as e:
                print(f"Error fetching prices: {e}")

                # Fallback: fetch individually
                for ticker in uncached_tickers:
                    price = self.get_price(ticker, use_cache=False)
                    results[ticker] = price

        return results

    async def get_price_async(
        self, ticker: str, use_cache: bool = True
    ) -> Optional[float]:
        """
        Get current price for a stock (asynchronous).

        Args:
            ticker: Stock ticker
            use_cache: Whether to use cached prices

        Returns:
            Optional[float]: Current price or None if fetch fails
        """
        logger.debug(f"Async fetching price for {ticker}")

        # Check cache first
        if use_cache and self._is_cache_valid(ticker):
            cached_data = self._cache.get(ticker, {})
            price = cached_data.get("price")
            logger.debug(f"Returning cached price for {ticker}: {price}")
            return price

        # Run synchronous yfinance call in executor
        loop = asyncio.get_event_loop()
        price = await loop.run_in_executor(
            self._executor, self.get_price, ticker, False
        )

        return price

    async def get_multiple_prices_async(
        self, tickers: List[str], use_cache: bool = True
    ) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple stocks (asynchronous).

        Args:
            tickers: List of stock tickers
            use_cache: Whether to use cached prices

        Returns:
            Dict[str, Optional[float]]: Dictionary mapping tickers to prices
        """
        # Run synchronous yfinance call in executor
        loop = asyncio.get_event_loop()
        prices = await loop.run_in_executor(
            self._executor, self.get_multiple_prices, tickers, use_cache
        )

        return prices

    @log_exception
    def get_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a stock.

        Args:
            ticker: Stock ticker

        Returns:
            Optional[Dict]: Stock information or None if fetch fails
        """
        logger.debug(f"Fetching stock info for {ticker}")

        normalized_ticker = self._normalize_ticker(ticker)

        try:
            stock = yf.Ticker(normalized_ticker)
            info = stock.info

            # Return relevant information
            return {
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "currency": info.get("currency", "EUR"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
            }

        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {e}", exc_info=False)
            return None

    def get_historical_data(
        self, ticker: str, period: str = "1mo", interval: str = "1d"
    ) -> Optional[Dict[str, List[Any]]]:
        """
        Get historical price data for a stock.

        Args:
            ticker: Stock ticker
            period: Time period (e.g., "1d", "5d", "1mo", "3mo", "1y", "5y")
            interval: Data interval (e.g., "1m", "5m", "1h", "1d", "1wk")

        Returns:
            Optional[Dict]: Historical data or None if fetch fails
        """
        normalized_ticker = self._normalize_ticker(ticker)

        try:
            stock = yf.Ticker(normalized_ticker)
            hist = stock.history(period=period, interval=interval)

            if hist.empty:
                return None

            # Convert to dictionary format
            return {
                "dates": [str(date) for date in hist.index],
                "open": hist["Open"].tolist(),
                "high": hist["High"].tolist(),
                "low": hist["Low"].tolist(),
                "close": hist["Close"].tolist(),
                "volume": hist["Volume"].tolist(),
            }

        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear the price cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info(f"Cache cleared ({cache_size} entries removed)")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached prices.

        Returns:
            Dict: Cache statistics
        """
        valid_count = sum(1 for ticker in self._cache if self._is_cache_valid(ticker))

        return {
            "total_cached": len(self._cache),
            "valid_cached": valid_count,
            "cache_duration_minutes": self._cache_duration.total_seconds() / 60,
        }

    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)


# Example usage
if __name__ == "__main__":
    api = StockAPI()

    # Test single price fetch
    aapl_price = api.get_price("AAPL")
    print(f"Apple stock price: ${aapl_price}")

    # Test European stock
    lvmh_price = api.get_price("LVMH.PA")
    print(f"LVMH stock price: €{lvmh_price}")

    # Test multiple prices fetch
    prices = api.get_multiple_prices(["AAPL", "MSFT", "GOOGL"])
    for ticker, price in prices.items():
        print(f"{ticker}: ${price}")

    # Test stock info
    info = api.get_stock_info("AAPL")
    if info:
        print(f"\nStock info for {info['name']}:")
        print(f"  Sector: {info['sector']}")
        print(
            f"  Market Cap: ${info['market_cap']:,.0f}"
            if info["market_cap"]
            else "  Market Cap: N/A"
        )

    # Test async fetch
    async def test_async():
        price = await api.get_price_async("AAPL")
        print(f"\nApple stock price (async): ${price}")

    asyncio.run(test_async())
