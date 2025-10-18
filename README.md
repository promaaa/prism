# Prism - Personal Finance & Investment App

Prism is a macOS desktop application for managing personal finances and investments (PEA, cryptos, financial placements) with a highly visual, intuitive interface. It runs locally with no cloud dependency, prioritizing speed, customizability, and real-time financial data via APIs.

## Features

- **Personal Finance Tracking**: Track expenses and revenues with categorization
- **Investment Management**: Manage PEA, cryptocurrencies, stocks, and bonds
- **Real-Time Pricing**: Automatic price updates via CoinGecko and Yahoo Finance APIs
- **Interactive Graphs**: Visual insights with Plotly charts
- **Order Book**: Track buy/sell orders with CSV export
- **Dark/Light Themes**: Customizable interface themes
- **Local Database**: All data stored locally in SQLite (no cloud)

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

4. **Run the application**:
   ```bash
   python main.py
   ```

### From Packaged .app (Coming Soon)

1. Download `Prism.app` from releases
2. Move to Applications folder
3. Double-click to launch

## Project Structure

```
prism/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── database/          # SQLite database logic
│   │   ├── __init__.py
│   │   ├── db_manager.py  # Database operations
│   │   └── schema.py      # Database schema
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   ├── transaction.py # Transaction model
│   │   ├── asset.py       # Asset model
│   │   └── order.py       # Order model
│   ├── api/               # API integrations
│   │   ├── __init__.py
│   │   ├── crypto_api.py  # CoinGecko API
│   │   └── stock_api.py   # Yahoo Finance API
│   ├── ui/                # PyQt6 UI components
│   │   ├── __init__.py
│   │   ├── main_window.py # Main application window
│   │   ├── personal_tab.py   # Personal finances tab
│   │   ├── investments_tab.py # Investments tab
│   │   ├── reports_tab.py    # Reports tab
│   │   ├── forms.py       # Input forms
│   │   └── themes.py      # Theme management
│   └── utils/             # Helper functions
│       ├── __init__.py
│       ├── calculations.py # Portfolio calculations
│       └── exports.py     # Export functionality
└── tests/                 # Unit tests
    ├── __init__.py
    ├── test_database.py
    ├── test_api.py
    └── test_calculations.py
```

## Usage

### Personal Finances Tab

1. **Add Transaction**: Click the "+" button to add an expense or revenue
2. **View Balance**: See your balance evolution over time in the line chart
3. **Category Breakdown**: View expense/revenue distribution in the pie chart
4. **Search**: Use the search bar to filter transactions by date, category, or description

### Investments Tab

1. **Add Asset**: Click "+" to add a new investment (crypto, stock, or bond)
2. **Refresh Prices**: Click "Refresh Prices" to update current market values
3. **Portfolio Overview**: View total portfolio value and allocation
4. **Order Book**: Manage buy/sell orders and track status

### Reports Tab

1. **View Graphs**: Interactive charts for financial analysis
2. **Export Data**: Export order book to CSV format
3. **Time Range**: Filter data by date range

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

- `Cmd+N`: New transaction/asset
- `Cmd+R`: Refresh prices
- `Cmd+E`: Export data
- `Cmd+T`: Toggle theme
- `Cmd+F`: Search
- `Cmd+Q`: Quit application

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
pylint src/
```

### Building .app Bundle

```bash
pyinstaller --name=Prism --windowed --icon=assets/icon.icns main.py
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

### Future Features (Next Iterations)
- [ ] CSV import for bulk transaction entry
- [ ] PDF report generation
- [ ] Data encryption for security
- [ ] Custom categories and budget alerts
- [ ] Advanced charts (heatmap, waterfall)
- [ ] Multi-currency support
- [ ] Recurring transactions
- [ ] Tax report generation

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

## Acknowledgments

- Inspired by Finary's clean interface design
- Built with PyQt6, Plotly, and Python
- APIs provided by CoinGecko and Yahoo Finance

---

**Note**: This is the initial MVP iteration. Security features (encryption, passwords) will be added in future versions.