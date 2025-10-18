# Prism - Personal Finance & Investment App

Prism is a macOS desktop application for managing personal finances and investments (PEA, cryptos, financial placements) with a highly visual, intuitive interface. It runs locally with no cloud dependency, prioritizing speed, customizability, and real-time financial data via APIs.

## Features

### Core Features
- **Personal Finance Tracking**: Track expenses and revenues with categorization
- **Investment Management**: Manage PEA, cryptocurrencies, stocks, and bonds
- **Order Book Management**: Track buy/sell orders with status management and filtering
- **Real-Time Pricing**: Automatic price updates via CoinGecko and Yahoo Finance APIs
- **Interactive Charts**: Beautiful Plotly visualizations for financial insights
- **Data Export**: CSV export for transactions, assets, and orders
- **Dark/Light Themes**: Customizable interface themes
- **Local Database**: All data stored locally in SQLite (no cloud)

### New in v1.2.0 🎉
- **USD/EUR Crypto Support**: Track cryptocurrency purchases in USD with portfolio totals in EUR
- **Exchange Rate Conversion**: Real-time USD/EUR conversion with intelligent caching
- **Dual Currency Display**: View crypto prices in native currency (USD or EUR) with automatic conversion

### New in v1.1.0
- **CSV Import**: Bulk import transactions from CSV files with validation and duplicate detection
- **Recurring Transactions**: Automate recurring income and expenses (daily, weekly, monthly, yearly)
- **Custom Categories**: Create unlimited custom categories with colors, icons, and budget limits
- **Budget Management**: Set monthly budget limits and receive alerts when approaching limits
- **PDF Reports**: Generate professional financial reports in PDF format

## Requirements

- macOS 10.15+ (Catalina or later)
- Python 3.11 or higher
- 100MB available memory
- Internet connection (for price updates)

## Installation

### From Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/prism.git
   cd prism
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up application icon** (optional):
   ```bash
   ./scripts/setup_icon.sh
   ```
   Or manually place your `prism2.png` icon in the `assets/` folder.
   See `assets/README.md` for icon specifications.

5. **Run the application**:
   ```bash
   python -m prism
   ```

### From Packaged .app (Coming Soon)

1. Download `Prism.app` from releases
2. Move to Applications folder
3. Double-click to launch

## Project Structure

```
prism/
├── prism/                 # Main application package
│   ├── __main__.py        # Application entry point (run with: python -m prism)
│   ├── database/          # SQLite database logic
│   │   ├── __init__.py
│   │   ├── db_manager.py  # Database operations
│   │   └── schema.py      # Database schema
│   ├── api/               # API integrations
│   │   ├── __init__.py
│   │   ├── crypto_api.py  # CoinGecko API
│   │   └── stock_api.py   # Yahoo Finance API
│   ├── ui/                # PyQt6 UI components
│   │   ├── __init__.py
│   │   ├── main_window.py # Main application window
│   │   ├── personal_tab.py   # Personal finances tab
│   │   ├── investments_tab.py # Investments tab
│   │   ├── orders_tab.py     # Order book tab
│   │   ├── reports_tab.py    # Reports tab
│   │   ├── log_viewer_dialog.py # Log viewer
│   │   ├── help_dialog.py     # Help system
│   │   ├── themes.py      # Theme management
│   │   └── tooltips.py    # UI tooltips
│   └── utils/             # Helper functions
│       ├── __init__.py
│       ├── logger.py      # Logging system
│       ├── ticker_data.py # Ticker suggestions
│       ├── calculations.py # Portfolio calculations
│       └── exports.py     # Export functionality
├── scripts/               # Utility scripts
│   ├── add_sample_data.py # Add sample data to database
│   ├── run.sh            # Run script
│   └── setup_icon.sh     # Icon setup script
├── tests/                 # Unit tests
│   ├── __init__.py
│   └── test_database.py  # Database tests
├── assets/                # Application assets
│   ├── icon.png          # Application icon
│   └── README.md         # Icon specifications
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── QUICKSTART.md         # Quick start guide
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Usage

### Personal Finances Tab

1. **Add Transaction**: Click "+ Add Transaction" to add an expense or revenue
2. **View Balance**: See your current balance and total income/expenses in summary cards
3. **Manage Transactions**: Edit or delete transactions directly from the table
4. **Category Tracking**: Automatic categorization with auto-complete suggestions

### Investments Tab

1. **Add Asset**: Click "+ Add Asset" to add a new investment (crypto, stock, or bond)
   - For crypto: Choose price currency (USD or EUR)
   - Prices fetched in selected currency
2. **Refresh Prices**: Click "🔄 Refresh Prices" to update current market values
   - Also refreshes USD/EUR exchange rate
3. **Portfolio Overview**: View total portfolio value, gains/losses, and allocation
   - Total value always calculated in EUR
   - USD crypto values automatically converted
4. **Exchange Rate**: View current USD/EUR rate in header (with cache age)
5. **Manage Assets**: Edit quantities, view performance metrics, and delete assets

### Order Book Tab

1. **Add Order**: Click "+ Add Order" to track a buy or sell order
2. **Filter Orders**: View all, open, or closed orders
3. **Manage Status**: Toggle orders between open and closed status
4. **Quick Actions**: Bulk close all open orders or delete all closed orders

### Reports Tab

1. **View Charts**: Interactive Plotly charts for financial analysis
   - Balance evolution over time
   - Spending by category
   - Portfolio value evolution
   - Asset allocation breakdown
2. **Export Data**: Export transactions, assets, or orders to CSV
3. **Date Filters**: Filter charts by time range (last 7/30/90 days, year, custom)

## Database Schema

### Transactions Table
- `id`: Primary key
- `date`: Transaction date (YYYY-MM-DD)
- `amount`: Amount (positive for revenue, negative for expense)
- `category`: Category (e.g., "Food", "Salary")
- `type`: "personal" or "investment"
- `description`: Optional description

### Assets Table
- `id`: Primary key
- `ticker`: Asset ticker (e.g., "BTC", "AAPL")
- `quantity`: Number of units held
- `price_buy`: Purchase price per unit
- `date_buy`: Purchase date
- `current_price`: Current market price (updated via API)
- `asset_type`: "crypto", "stock", or "bond"
- `price_currency`: Currency of purchase price ("USD" or "EUR", default: "EUR")

### Orders Table
- `id`: Primary key
- `ticker`: Asset ticker
- `quantity`: Order quantity
- `price`: Order price
- `order_type`: "buy" or "sell"
- `date`: Order date
- `status`: "open" or "closed"

## API Integrations

### CoinGecko (Cryptocurrency Prices)
- **Endpoint**: `https://api.coingecko.com/api/v3/simple/price`
- **No API key required**
- **Rate limit**: ~50 calls/minute (free tier)

### Yahoo Finance (Stock Prices)
- **Library**: `yfinance`
- **No API key required**
- **Supports**: US stocks, European stocks (e.g., LVMH.PA for PEA)

## Keyboard Shortcuts

### Basic Actions
- `Cmd+N`: New transaction/asset
- `Cmd+R`: Refresh prices
- `Cmd+E`: Export data
- `Cmd+T`: Toggle theme
- `Cmd+Q`: Quit application

### New Features (v1.1.0)
- `Cmd+I`: Import from CSV
- `Cmd+P`: Generate PDF Report
- `Cmd+Shift+R`: Recurring Transactions
- `Cmd+Shift+C`: Categories & Budgets
- `Cmd+L`: View Logs

## Development

### Testing New Features

Test the new features with the included test script:

```bash
python scripts/test_new_features.py
```

This will test:
- CSV import functionality
- Recurring transactions
- Category management
- PDF report generation

### Running Unit Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black prism/ tests/
```

### Linting

```bash
pylint prism/
```

### Building .app Bundle

```bash
pyinstaller --name=Prism --windowed --icon=assets/icon.icns -m prism
```

The `.app` bundle will be created in the `dist/` directory.

## Troubleshooting

### API Connection Issues
- Check your internet connection
- Verify firewall settings allow Python to access the network
- API may be temporarily unavailable (app will use last known prices)

### Database Issues
- Database file is created automatically at first launch
- Located at: `~/Library/Application Support/Prism/prism.db`
- Delete this file to reset all data (backup first!)

### UI Issues
- Try toggling between light/dark themes
- Restart the application
- Check console output for error messages

## Roadmap

### Completed Features ✓
- [x] CSV import for bulk transaction entry
- [x] PDF report generation
- [x] Custom categories and budget alerts
- [x] Recurring transactions

### Future Features (Next Iterations)
- [ ] Data encryption for security
- [ ] Advanced charts (heatmap, waterfall, treemap)
- [ ] Multi-currency support
- [ ] Tax report generation
- [ ] Bank integration (read-only)
- [ ] Transaction search and advanced filtering
- [ ] Cloud sync (optional)
- [ ] Mobile app companion

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@prism-app.com

## What's New in v1.2.0

### USD/EUR Cryptocurrency Support
Track cryptocurrency purchases made in USD while maintaining portfolio totals in EUR.

**Key Features:**
- Choose USD or EUR when adding crypto assets
- Crypto prices displayed in native currency
- Portfolio totals automatically calculated in EUR
- Real-time exchange rate conversion
- Exchange rate displayed in Investments tab

**How to use:**
1. Add a crypto asset (e.g., BTC, ETH)
2. Select "USD" from Price Currency dropdown
3. Enter purchase price in USD
4. View prices in USD, portfolio total in EUR

See `docs/USD_EUR_CRYPTO_GUIDE.md` for detailed documentation.

## What's New in v1.1.0

### CSV Import
Import transactions in bulk from CSV files. The system validates data, detects duplicates, and provides detailed error reporting.

**How to use:**
1. Go to `File → Import from CSV` or press `Cmd+I`
2. Download a sample CSV to see the format
3. Prepare your CSV with columns: date, amount, category, type, description
4. Import and review the results

### Recurring Transactions
Set up automated recurring transactions for salaries, rent, subscriptions, and more.

**How to use:**
1. Go to `Tools → Recurring Transactions` or press `Cmd+Shift+R`
2. Add a new recurring transaction with frequency (daily, weekly, monthly, yearly)
3. The system automatically creates transactions on due dates
4. View upcoming transactions and estimated monthly impact

### Categories & Budgets
Create custom categories with visual customization and set monthly budget limits.

**How to use:**
1. Go to `Tools → Categories & Budgets` or press `Cmd+Shift+C`
2. Create custom categories with colors and emoji icons
3. Set monthly budget limits for expense categories
4. Receive alerts when spending approaches limits

### PDF Reports
Generate professional financial reports with comprehensive summaries.

**How to use:**
1. Go to `Tools → Generate PDF Report` or press `Cmd+P`
2. Choose where to save the PDF
3. Review your complete financial overview with charts and tables

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## Acknowledgments

- Inspired by Finary's clean interface design
- Built with PyQt6, Plotly, ReportLab, and Python
- APIs provided by CoinGecko and Yahoo Finance

---

**Current Version**: 1.2.0 - Now with USD/EUR Crypto Support, CSV Import, Recurring Transactions, Categories & Budgets, and PDF Reports!