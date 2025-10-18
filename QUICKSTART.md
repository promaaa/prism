# Prism Quick Start Guide

Get up and running with Prism in minutes!

## Prerequisites

- macOS 10.15+ (Catalina or later)
- Python 3.11 or higher
- pip package manager
- Internet connection (for API price updates)

## Installation

### 1. Clone or Download the Project

```bash
cd /path/to/prism
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyQt6 (GUI framework)
- pandas (data manipulation)
- plotly (interactive charts)
- requests & aiohttp (API calls)
- yfinance (stock prices)
- pytest (testing)
- and more...

### 4. Run the Application

```bash
python main.py
```

The application will:
1. Create a database at `~/Library/Application Support/Prism/prism.db`
2. Launch the main window
3. Display three tabs: Personal Finances, Investments, and Reports

## First Steps

### Adding Your First Transaction

1. Click the "+ Transaction" button in the toolbar
2. Fill in the form:
   - Date: Transaction date
   - Amount: Positive for income, negative for expenses
   - Category: e.g., "Salary", "Food", "Transport"
   - Type: "personal"
   - Description: Optional notes

### Adding Your First Investment

1. Click the "+ Asset" button in the toolbar
2. Fill in the form:
   - Ticker: e.g., "BTC", "AAPL", "LVMH.PA"
   - Quantity: Number of units
   - Buy Price: Purchase price per unit
   - Date: Purchase date
   - Asset Type: "crypto", "stock", or "bond"

### Updating Prices

1. Click "Refresh Prices" in the toolbar or menu
2. The app will fetch current prices from:
   - CoinGecko API (for cryptocurrencies)
   - Yahoo Finance (for stocks)
3. Portfolio values will update automatically

### Exporting Data

1. Go to the "Reports" tab
2. Click one of the export buttons:
   - Export Orders to CSV
   - Export Transactions to CSV
   - Export Assets to CSV
3. Files are saved to your Downloads folder with timestamps

## Features Overview

### Personal Finances Tab
- View current balance
- Track income and expenses
- Category-based analytics
- Transaction history
- Balance evolution charts (coming soon)

### Investments Tab
- Portfolio overview
- Asset allocation
- Real-time price updates
- Performance metrics
- Order book management

### Reports Tab
- Data exports (CSV)
- Interactive charts (coming soon)
- Financial reports (coming soon)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+N` | New transaction |
| `Cmd+R` | Refresh prices |
| `Cmd+E` | Export data |
| `Cmd+T` | Toggle theme |
| `Cmd+F` | Search (coming soon) |
| `Cmd+Q` | Quit application |

## Themes

Prism supports light and dark themes:

- **Light Theme**: Clean, minimal design with light backgrounds
- **Dark Theme**: Easy on the eyes for low-light environments

Toggle between themes:
1. Click "Toggle Theme" in the toolbar
2. Or use `Cmd+T` keyboard shortcut
3. Or use View → Toggle Theme menu

## Database Location

Your data is stored locally at:
```
~/Library/Application Support/Prism/prism.db
```

### Backup Your Data

To backup your data:
```bash
cp ~/Library/Application\ Support/Prism/prism.db ~/backup_prism.db
```

### Reset Database

To start fresh (⚠️ deletes all data):
```bash
rm ~/Library/Application\ Support/Prism/prism.db
```

Then restart the app to create a new database.

## Running Tests

Run the test suite:

```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_database.py
```

Run with verbose output:
```bash
pytest -v tests/
```

## Supported Assets

### Cryptocurrencies
Use standard ticker symbols:
- BTC (Bitcoin)
- ETH (Ethereum)
- SOL (Solana)
- ADA (Cardano)
- And many more...

### Stocks

**US Stocks:**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- etc.

**European Stocks:**
Add exchange suffix:
- LVMH.PA (LVMH - Paris)
- BMW.DE (BMW - Frankfurt)
- BP.L (BP - London)
- ASML.AS (ASML - Amsterdam)

## Troubleshooting

### Application Won't Start

1. Check Python version: `python --version` (must be 3.11+)
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

### Price Updates Failing

1. Check internet connection
2. Verify firewall allows Python network access
3. Some APIs may have rate limits (wait a few minutes)
4. App will use cached prices if API fails

### Database Errors

1. Check database file exists and is readable
2. Try resetting database (see Database Location section)
3. Check disk space

### UI Not Updating

1. Try toggling theme (`Cmd+T`)
2. Restart the application
3. Check console for error messages

## API Information

### CoinGecko (Cryptocurrency Prices)
- **URL**: https://api.coingecko.com/api/v3
- **Rate Limit**: ~50 calls/minute (free tier)
- **No API key required**
- **Cached**: 5 minutes

### Yahoo Finance (Stock Prices)
- **Library**: yfinance
- **No API key required**
- **Cached**: 5 minutes

## Development Mode

To run in development mode with debug output:

```bash
python main.py --debug
```

To open Python interactive shell with database access:

```bash
python
>>> from src.database.db_manager import DatabaseManager
>>> db = DatabaseManager()
>>> db.get_database_stats()
```

## Next Steps

1. **Add sample data** to test the application
2. **Explore the UI** and try different features
3. **Set up regular backups** of your database
4. **Star the repo** if you find it useful!

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review test files in `tests/` for usage examples
- Open an issue on GitHub for bugs or feature requests

## What's Coming Next?

Future iterations will add:
- CSV import for bulk transactions
- PDF report generation
- Interactive Plotly charts
- Data encryption
- Budget alerts
- Multi-currency support
- Recurring transactions
- Tax reports

---

**Enjoy using Prism!** 🎨💰

For more information, see the [full README](README.md).