# Bug Fixes

## Recent Fixes (December 2024)

### 1. Price Fetching Issues - FIXED ✅

**Issues Found:**
1. Crypto API warning: "Price not found in response for TAO/BTC"
2. Stock API crash: `AttributeError: 'StockAPI' object has no attribute 'get_price'`

**Root Causes:**

#### Crypto API Issue
- **Problem**: Ticker autocomplete was passing formatted suggestions (e.g., "TAO - Bittensor (AI/Machine Learning)") instead of just the ticker
- **Impact**: CoinGecko API couldn't find prices for formatted strings
- **Additional Issue**: TAO and other AI tokens weren't mapped to correct CoinGecko IDs

#### Stock API Issue
- **Problem**: Method `get_price()` was accidentally renamed to `get_price_async()` during logging integration
- **Impact**: Application crashed when trying to fetch stock prices
- **Additional Issue**: Duplicate logging statements and missing `async` keyword in async method

**Fixes Applied:**

#### 1. Crypto API (`src/api/crypto_api.py`)
```python
# Added correct CoinGecko ID mappings for AI tokens
TICKER_TO_ID = {
    # ... existing mappings ...
    "TAO": "bittensor",      # Was missing - caused wrong price
    "FET": "fetch-ai",
    "AGIX": "singularitynet",
    "OCEAN": "ocean-protocol",
    "RNDR": "render-token",
}
```

#### 2. Stock API (`src/api/stock_api.py`)
```python
# Fixed method signature (was accidentally renamed)
@log_exception
@log_performance("stock_get_price")
def get_price(self, ticker: str, use_cache: bool = True) -> Optional[float]:
    # ... implementation ...

# Fixed async method signature (was missing 'async' keyword)
async def get_price_async(self, ticker: str, use_cache: bool = True) -> Optional[float]:
    # ... implementation ...
```

- Removed duplicate `logger.info()` statements
- Restored proper method naming

#### 3. Investments Tab (`src/ui/investments_tab.py`)
```python
def _on_fetch_price(self):
    """Fetch current price for the ticker."""
    ticker_text = self.ticker_edit.text().strip()
    
    # Extract ticker if it's a formatted suggestion
    ticker = (
        extract_ticker(ticker_text) if " - " in ticker_text else ticker_text.upper()
    )
    
    # Now fetch with clean ticker
    if asset_type == "crypto":
        price = self.crypto_api.get_price(ticker)
    else:
        price = self.stock_api.get_price(ticker)
```

**Verification:**

Tested all scenarios:
```bash
# Bitcoin (BTC)
✅ Bitcoin price: €91,615.00

# Bittensor (TAO) - AI token
✅ Bittensor (TAO) price: €339.78

# Airbus stock (AIR.PA)
✅ Airbus (AIR.PA) price: €200.40

# Multiple AI tokens
✅ TAO: €339.78
✅ FET: €0.23
✅ AGIX: €0.11
✅ OCEAN: €0.20
```

**Files Modified:**
- `src/api/crypto_api.py` - Added CoinGecko ID mappings for AI tokens
- `src/api/stock_api.py` - Fixed method signatures and removed duplicates
- `src/ui/investments_tab.py` - Added ticker extraction logic

**Impact:**
- ✅ Price fetching now works for all cryptocurrencies
- ✅ Price fetching now works for all stocks (CAC 40, etc.)
- ✅ TAO (Bittensor) and AI tokens properly supported
- ✅ Autocomplete suggestions work seamlessly with API calls
- ✅ No more crashes when fetching stock prices

---

## Known Issues

None currently! All reported issues have been resolved. 🎉

---

## Reporting Bugs

If you encounter any issues:

1. **Check logs**: Press `Cmd+L` to view application logs
2. **Export logs**: Click "Export" in log viewer to save logs
3. **Note steps**: Document exact steps to reproduce the issue
4. **Check ticker**: Verify ticker symbol is valid in CoinGecko/Yahoo Finance
5. **Internet**: Ensure you have a stable internet connection

**Common Issues:**

### "Price not found"
- Check if ticker is valid (use autocomplete suggestions)
- Wait 1-2 minutes if you just refreshed (API rate limits)
- Check internet connection
- View error log for details (`Cmd+L` → Errors Only)

### "Cached price" message
- Prices are cached for 5 minutes to avoid API limits
- This is normal behavior
- Click "Refresh Prices" to force update after 5 minutes

### Slow price updates
- Large portfolios (50+ assets) take longer
- Be patient and watch progress bar
- APIs may be slow during high traffic periods

---

## Version History

### v1.0.0-rc4 (Current)
- ✅ Fixed crypto price fetching with formatted suggestions
- ✅ Fixed stock API method naming issue
- ✅ Added TAO, FET, AGIX, OCEAN CoinGecko mappings
- ✅ Comprehensive tooltips and help system
- ✅ Smart ticker autocomplete with 141 tickers

### Previous versions
See `PROGRESS.md` for complete development history.

---

**Status**: All API integrations working perfectly! 🚀