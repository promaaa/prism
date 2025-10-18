# Prism User Guide

Welcome to **Prism** - your personal finance and investment management application! This guide will help you get the most out of Prism.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Personal Finances](#personal-finances)
3. [Investment Portfolio](#investment-portfolio)
4. [Reports & Analytics](#reports--analytics)
5. [Tips & Best Practices](#tips--best-practices)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Getting Started

### First Launch

When you first launch Prism, the application will:
1. Create a local database at `~/Library/Application Support/Prism/prism.db`
2. Initialize the database with the required tables
3. Open the main window with three tabs

### Understanding the Interface

Prism has three main tabs:

- **Personal Finances**: Track your income and expenses
- **Investments**: Manage your investment portfolio (crypto, stocks, bonds)
- **Reports**: View analytics and export data

### Adding Your First Data

Start by adding a transaction or an asset:
- Click **"+ Add Transaction"** in the toolbar or Personal Finances tab
- Click **"+ Add Asset"** in the toolbar or Investments tab

---

## Personal Finances

The Personal Finances tab helps you track your day-to-day financial transactions.

### Summary Cards

At the top of the tab, you'll see four summary cards:

1. **Current Balance** (Green): Your total balance (income - expenses)
2. **Total Income** (Blue): Sum of all positive transactions
3. **Total Expenses** (Red): Sum of all negative transactions
4. **Transactions** (Purple): Total number of transactions

### Adding a Transaction

1. Click **"+ Add Transaction"** button
2. Fill in the form:
   - **Date**: Select the transaction date (defaults to today)
   - **Amount**: Enter the amount
     - For **income**: Enter positive number (e.g., `2500` for salary)
     - For **expenses**: Enter negative number (e.g., `-50` for groceries)
   - **Category**: Choose or type a category (e.g., "Salary", "Food", "Transport")
   - **Type**: Select "personal" or "investment"
   - **Description**: Optional details about the transaction
3. Click **OK** to save

**Pro Tip**: The category field has auto-complete! Start typing and it will suggest existing categories.

### Managing Transactions

#### Viewing Transactions

The transaction table shows all your transactions sorted by date (newest first):
- **Green amounts**: Income
- **Red amounts**: Expenses
- **Sortable columns**: Click headers to sort

#### Editing a Transaction

1. Find the transaction in the table
2. Click the **✏️ (Edit)** button in the Actions column
3. Modify the fields as needed
4. Click **OK** to save

#### Deleting a Transaction

1. Find the transaction in the table
2. Click the **🗑️ (Delete)** button in the Actions column
3. Confirm deletion in the dialog

⚠️ **Warning**: Deleting a transaction cannot be undone!

### Common Categories

Here are some suggested categories to help you get started:

**Income Categories**:
- Salary
- Bonus
- Freelance
- Investment Returns
- Gifts

**Expense Categories**:
- Food & Dining
- Transport
- Housing (Rent/Mortgage)
- Utilities
- Entertainment
- Healthcare
- Shopping
- Education
- Insurance

---

## Investment Portfolio

The Investments tab helps you track your investment portfolio including cryptocurrencies, stocks, and bonds.

### Summary Cards

At the top of the tab, you'll see four summary cards:

1. **Portfolio Value** (Green): Current total value of all assets
2. **Total Invested** (Blue): Total amount you've invested (cost basis)
3. **Gain/Loss** (Purple/Green/Red): Profit or loss (changes color based on performance)
4. **Total Assets** (Orange): Number of different assets you own

### Adding an Asset

1. Click **"+ Add Asset"** button
2. Fill in the form:
   - **Asset Type**: Choose crypto, stock, or bond
   - **Ticker**: Enter the ticker symbol
     - Crypto: `BTC`, `ETH`, `SOL`, `ADA`, etc.
     - US Stocks: `AAPL`, `MSFT`, `GOOGL`, etc.
     - European Stocks: Add exchange suffix (e.g., `LVMH.PA` for Paris, `BMW.DE` for Frankfurt)
   - **Quantity**: Number of units/shares (e.g., `0.5` for half a Bitcoin)
   - **Buy Price**: Price per unit when you purchased
   - **Purchase Date**: Date of purchase
3. Optional: Click **"🔄 Fetch Current Price"** to verify the ticker and see current price
4. Click **OK** to save

The app will automatically fetch the current price and save it with your asset.

### Understanding the Asset Table

The asset table shows detailed information about each asset:

- **Type**: Asset type (CRYPTO, STOCK, BOND)
- **Ticker**: Symbol in bold monospace font
- **Quantity**: How many units you own
- **Buy Price**: Your purchase price per unit
- **Current Price**: Latest market price (updated when you refresh)
- **Value**: Current total value (Quantity × Current Price)
- **Gain/Loss**: Profit/loss in euros (color-coded: green = profit, red = loss)
- **Gain %**: Percentage gain/loss from your purchase price

### Refreshing Prices

Keep your portfolio up-to-date with current market prices:

1. Click **"🔄 Refresh Prices"** button
2. Watch the progress bar as prices are fetched:
   - Crypto prices from CoinGecko API
   - Stock prices from Yahoo Finance
3. View the results summary showing:
   - Total assets checked
   - Successfully updated
   - Failed updates (if any)

**Note**: Price updates require an internet connection. The app caches prices for 5 minutes to avoid excessive API calls.

### Managing Assets

#### Editing an Asset

1. Find the asset in the table
2. Click the **✏️ (Edit)** button
3. Modify quantity, buy price, or date as needed
4. Click **OK** to save

**Note**: You cannot change the ticker symbol when editing. If you need to change the ticker, delete and recreate the asset.

#### Deleting an Asset

1. Find the asset in the table
2. Click the **🗑️ (Delete)** button
3. Confirm deletion in the dialog

⚠️ **Warning**: Deleting an asset cannot be undone!

### Supported Assets

#### Cryptocurrencies (via CoinGecko)

Popular cryptocurrencies supported:
- BTC (Bitcoin)
- ETH (Ethereum)
- BNB (Binance Coin)
- SOL (Solana)
- ADA (Cardano)
- XRP (Ripple)
- DOT (Polkadot)
- MATIC (Polygon)
- And 10,000+ more!

#### Stocks (via Yahoo Finance)

**US Stocks**: Use standard ticker
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- AMZN (Amazon)
- TSLA (Tesla)

**European Stocks**: Add exchange suffix
- LVMH.PA (LVMH - Paris)
- MC.PA (LVMH - Paris)
- BMW.DE (BMW - Frankfurt)
- SAP.DE (SAP - Frankfurt)
- BP.L (BP - London)
- ASML.AS (ASML - Amsterdam)

**Exchange Suffixes**:
- `.PA` - Euronext Paris
- `.DE` - XETRA (Frankfurt)
- `.L` - London Stock Exchange
- `.AS` - Amsterdam
- `.MI` - Milan
- `.SW` - Swiss Exchange

---

## Reports & Analytics

The Reports tab provides powerful visualizations and data export capabilities.

### Date Range Filters

Control what data is displayed in the charts:

1. **All Time**: Show all data (default)
2. **Last 7 Days**: Last week
3. **Last 30 Days**: Last month
4. **Last 90 Days**: Last quarter
5. **Last 6 Months**: Last half year
6. **Last Year**: Last 365 days
7. **This Year**: January 1st to today
8. **Custom**: Choose your own date range

To use custom dates:
1. Select "Custom" from the dropdown
2. Choose start and end dates from the date pickers
3. Charts will automatically update

### Personal Finance Analytics

#### Balance Evolution Chart

**What it shows**: How your balance has changed over time

- **X-axis**: Date
- **Y-axis**: Balance in euros
- **Line**: Your cumulative balance (income - expenses)
- **Shaded area**: Visual representation of balance growth

**How to read it**:
- Upward trend = You're accumulating wealth
- Downward trend = Your expenses exceed income
- Flat line = Breaking even

**Interactions**:
- Hover over points to see exact date and balance
- Zoom in/out using the toolbar
- Pan by clicking and dragging

#### Spending by Category Chart

**What it shows**: How your spending is distributed across categories

- **Donut chart**: Each slice represents a category
- **Percentage**: Proportion of total spending
- **Colors**: Automatically assigned to categories

**How to read it**:
- Larger slices = Categories where you spend most
- Use this to identify areas to reduce spending
- Compare months to track spending patterns

**Interactions**:
- Hover over slices to see category name and amount
- Click legend items to hide/show categories

### Investment Portfolio Analytics

#### Portfolio Value Evolution Chart

**What it shows**: How your portfolio value has grown over time

- **X-axis**: Date
- **Y-axis**: Portfolio value in euros
- **Line**: Total value of all assets
- **Shaded area**: Visual representation of growth

**How to read it**:
- Upward trend = Your investments are growing
- Volatility = Market fluctuations
- Compare to your cost basis (blue line in summary) to see overall gain/loss

**Interactions**:
- Hover to see exact date and value
- Zoom and pan to focus on specific periods

#### Asset Allocation Chart

**What it shows**: How your portfolio is distributed by asset type

- **Donut chart**: Each slice represents an asset type
- **Colors**:
  - Orange: Crypto
  - Blue: Stocks
  - Green: Bonds

**How to read it**:
- Shows diversification of your portfolio
- Well-diversified portfolios spread across multiple types
- Use this to identify concentration risk

**Interactions**:
- Hover to see asset type and percentage
- Click legend to hide/show types

### Exporting Data

Export your data to CSV for external analysis or backup:

#### Export Transactions

1. Click **"📊 Transactions CSV"** button
2. File is saved to `~/Downloads/transactions_YYYYMMDD_HHMMSS.csv`
3. Open in Excel, Google Sheets, or any spreadsheet software

**CSV Columns**:
- id, date, amount, category, type, description

#### Export Assets

1. Click **"💼 Assets CSV"** button
2. File is saved to `~/Downloads/assets_YYYYMMDD_HHMMSS.csv`

**CSV Columns**:
- id, ticker, quantity, price_buy, date_buy, current_price, asset_type

#### Export Orders

1. Click **"📋 Orders CSV"** button
2. File is saved to `~/Downloads/orders_YYYYMMDD_HHMMSS.csv`

**CSV Columns**:
- id, ticker, quantity, price, order_type, date, status

---

## Tips & Best Practices

### Data Entry Best Practices

1. **Be Consistent with Categories**: Use the same category names to get accurate analytics
2. **Enter Transactions Regularly**: Don't let them pile up - enter them daily or weekly
3. **Use Descriptions**: Add notes to help you remember what transactions were for
4. **Date Accuracy**: Use the actual transaction date, not the entry date

### Portfolio Management Tips

1. **Update Prices Regularly**: Refresh prices at least once a day for accurate portfolio value
2. **Track Cost Basis**: Always enter your actual purchase price for accurate gain/loss calculations
3. **Diversify**: Use the Asset Allocation chart to ensure you're not too concentrated in one type
4. **Long-term View**: Use the Portfolio Value chart to focus on long-term trends, not daily fluctuations

### Data Backup

Your data is stored locally in SQLite. To backup:

```bash
# Create backup
cp ~/Library/Application\ Support/Prism/prism.db ~/Documents/prism_backup_$(date +%Y%m%d).db

# Restore from backup
cp ~/Documents/prism_backup_YYYYMMDD.db ~/Library/Application\ Support/Prism/prism.db
```

**Recommended**: Back up your database weekly or after major data entry.

### Performance Tips

1. **Close unused tabs**: If you have many assets, closing Reports tab can improve performance
2. **Archive old data**: Consider exporting and removing very old transactions
3. **Limit price refreshes**: Don't refresh too frequently (5-minute cache helps)

---

## Keyboard Shortcuts

Master these shortcuts to speed up your workflow:

| Shortcut | Action |
|----------|--------|
| `Cmd+N` | New transaction |
| `Cmd+R` | Refresh prices (Investments tab) |
| `Cmd+E` | Export data (opens Reports tab) |
| `Cmd+T` | Toggle light/dark theme |
| `Cmd+Q` | Quit application |
| `Cmd+Tab` | Switch between tabs |

**macOS Note**: Replace `Cmd` with `Control` if running on Windows/Linux.

---

## Troubleshooting

### The app won't start

**Solution**:
1. Check Python version: `python3 --version` (must be 3.11+)
2. Verify virtual environment is activated: `source venv/bin/activate`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check for error messages in terminal

### Prices won't update

**Possible causes**:
- No internet connection
- API rate limit reached (wait 5-10 minutes)
- Invalid ticker symbol

**Solutions**:
1. Check your internet connection
2. Verify ticker symbols are correct
3. Try refreshing individual assets by editing and re-saving
4. Check API status:
   - CoinGecko: https://status.coingecko.com/
   - Yahoo Finance: Try accessing finance.yahoo.com

### Charts not displaying

**Possible causes**:
- No data entered yet
- Date range filter excluding all data
- PyQt6-WebEngine not installed

**Solutions**:
1. Add some transactions or assets first
2. Change date range filter to "All Time"
3. Reinstall: `pip install PyQt6-WebEngine`

### Database errors

**Possible causes**:
- Database file corrupted
- Insufficient disk space
- File permissions issue

**Solutions**:
1. Check disk space: `df -h`
2. Check file permissions: `ls -la ~/Library/Application\ Support/Prism/`
3. Restore from backup if available
4. Last resort: Delete database (⚠️ loses all data) and restart app

### App is slow

**Possible causes**:
- Too many transactions/assets
- Charts rendering on large datasets
- Background price updates running

**Solutions**:
1. Close Reports tab when not needed
2. Use date filters to limit data displayed
3. Wait for price updates to complete
4. Consider archiving old data

---

## FAQ

### Is my data stored in the cloud?

**No**. Prism stores all data locally on your computer in a SQLite database. Your financial data never leaves your machine (except when you explicitly export it).

### Do I need an API key?

**No**. Prism uses free APIs (CoinGecko and Yahoo Finance) that don't require API keys. These are subject to rate limits but sufficient for personal use.

### Can I use this on Windows or Linux?

**Mostly**. Prism is designed for macOS but the code should work on Windows/Linux with minor adjustments (paths, shortcuts). The .app bundle is macOS-specific.

### How often should I refresh prices?

**Recommendation**: Once or twice per day is sufficient for most users. The app caches prices for 5 minutes to avoid excessive API calls.

### Can I import transactions from my bank?

**Not yet**. CSV import is planned for a future version. Currently, you must enter transactions manually.

### Is my data encrypted?

**Not yet**. The current MVP stores data in plain text SQLite. Database encryption and password protection are planned for future versions.

### Can I track multiple currencies?

**Not yet**. Currently, all amounts are assumed to be in euros (€). Multi-currency support is planned for future versions.

### What happens if I delete the database?

All your data will be lost. Make sure to back up regularly! The app will create a new empty database on next launch.

### Can I sync across devices?

**Not yet**. Each installation has its own local database. Cloud sync is planned for future versions.

### How do I update the app?

Currently, you need to manually pull the latest code from Git:

```bash
cd prism
git pull origin main
pip install -r requirements.txt
python main.py
```

Auto-update functionality is planned for future versions.

### What's the maximum number of transactions/assets I can have?

SQLite can handle millions of records, but performance may degrade with very large datasets (10,000+ transactions). Use date filters and consider archiving old data.

### Can I customize categories?

**Yes**! The category field is free-text with auto-complete. Just type any category name you want. Common categories are pre-populated for convenience.

### How accurate are the price updates?

Prices come directly from CoinGecko (crypto) and Yahoo Finance (stocks), which are reliable sources. However:
- Prices may be delayed by a few minutes
- Some assets may not be available on these platforms
- Exchange rates affect accuracy for non-euro assets

### Can I track options or derivatives?

**Not currently**. Prism is designed for simple assets (crypto, stocks, bonds). Complex financial instruments may be added in future versions.

### What if I find a bug?

Please report bugs on GitHub Issues with:
- Description of the problem
- Steps to reproduce
- Error messages (if any)
- Your macOS version and Python version

---

## Getting Help

### Resources

- **README.md**: Project overview and installation
- **QUICKSTART.md**: Fast getting-started guide
- **ARCHITECTURE.md**: Technical documentation
- **DEVELOPMENT.md**: Developer guide

### Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share tips
- **Email**: support@prism-app.com (coming soon)

### Contributing

Prism is open-source! Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See DEVELOPMENT.md for coding guidelines.

---

## Changelog

### Version 0.9.0 (Current)
- ✅ Personal Finances tab with transaction management
- ✅ Investments tab with asset portfolio tracking
- ✅ Reports tab with interactive Plotly charts
- ✅ Real-time price updates via APIs
- ✅ CSV export functionality
- ✅ Light/dark theme support

### Upcoming Features
- 🔄 Order book management
- 🔄 CSV import for transactions
- 🔄 PDF report generation
- 🔄 Budget tracking and alerts
- 🔄 Recurring transactions
- 🔄 Data encryption
- 🔄 Multi-currency support

---

**Thank you for using Prism!** 🎨💰

We hope this guide helps you take control of your personal finances and investments. If you have suggestions for improving this guide, please let us know on GitHub.

*Last updated: December 2024*