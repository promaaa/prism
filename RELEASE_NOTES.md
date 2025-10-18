# Prism Release Notes

## Version 1.0.0-rc1 (Release Candidate 1)
**Release Date:** December 2024
**Status:** MVP Complete - Ready for Testing

---

## 🎉 Highlights

This is the first release candidate of Prism, featuring a complete MVP implementation of a personal finance and investment management application for macOS. All core features are implemented and functional!

### What's New in 1.0.0-rc1

- ✅ **4 Complete Functional Tabs**: Personal Finances, Investments, Order Book, and Reports
- ✅ **Full CRUD Operations**: Add, edit, delete, and view all data types
- ✅ **Interactive Visualizations**: Beautiful Plotly charts for financial insights
- ✅ **Real-Time Data**: Automatic price updates via CoinGecko and Yahoo Finance APIs
- ✅ **Application Icon System**: Customizable app icon (prism2.png) with dock/taskbar display
- ✅ **Comprehensive Documentation**: User guides, developer docs, and quick start guides

---

## 📋 Features

### Personal Finances Tab
- Transaction management (add, edit, delete)
- Summary cards showing balance, income, expenses, and transaction count
- Searchable transaction table with color-coded amounts
- Category auto-complete for consistent tracking
- Date picker for easy date selection
- Real-time balance calculations

### Investments Tab
- Asset portfolio management (crypto, stocks, bonds)
- Real-time price updates from CoinGecko and Yahoo Finance
- Portfolio summary cards (value, cost, gain/loss, count)
- Detailed asset table with performance metrics
- Background price refresh with progress tracking
- Gain/loss calculations (both € and %)
- Support for international exchanges (e.g., LVMH.PA for Paris)

### Order Book Tab (NEW!)
- Complete order tracking system
- Buy/sell order management
- Order status management (open/closed)
- Filter by status (all, open, closed)
- Quick actions for bulk operations
- Color-coded order types and status
- Total order value calculations

### Reports & Analytics Tab
- Interactive Plotly charts:
  - Balance evolution over time (line chart)
  - Spending by category (donut chart)
  - Portfolio value evolution (line chart)
  - Asset allocation by type (donut chart)
- Date range filters (7/30/90 days, 6 months, year, custom)
- CSV export for transactions, assets, and orders
- Responsive chart resizing
- Empty state handling

### Application Icon System (NEW!)
- Support for custom application icon (prism2.png)
- Fallback to icon.png if primary icon not found
- Icon displayed in window, dock, and application switcher
- Setup script (setup_icon.sh) for easy icon installation
- Comprehensive icon documentation

### Core Infrastructure
- SQLite database with 3 tables (transactions, assets, orders)
- Efficient database operations with connection management
- API integrations (CoinGecko, Yahoo Finance) with caching
- Theme system (light/dark modes)
- Keyboard shortcuts (Cmd+N, Cmd+R, Cmd+E, Cmd+T, Cmd+Q)
- Status bar notifications
- Signal-based architecture for reactive updates

---

## 🔧 Technical Details

### System Requirements
- macOS 10.15+ (Catalina or later)
- Python 3.11 or higher
- 100MB available memory
- Internet connection (for price updates)

### Dependencies
- PyQt6 >= 6.6.0 (GUI framework)
- PyQt6-WebEngine >= 6.6.0 (for charts)
- plotly >= 5.18.0 (interactive charts)
- pandas >= 2.1.0 (data manipulation)
- requests >= 2.31.0 (API calls)
- yfinance >= 0.2.32 (stock prices)
- aiohttp >= 3.9.0 (async API calls)

### Database Schema
- **transactions**: id, date, amount, category, type, description
- **assets**: id, ticker, quantity, price_buy, date_buy, current_price, asset_type
- **orders**: id, ticker, quantity, price, order_type, date, status

### API Integrations
- **CoinGecko API**: Free crypto prices, no API key required, 5-minute caching
- **Yahoo Finance**: Free stock prices via yfinance library, 5-minute caching

---

## 📊 Statistics

- **Lines of Code**: ~8,200+
- **Python Files**: 23
- **UI Components**: 4 major tabs
- **Interactive Charts**: 4 (Plotly)
- **Database Tables**: 3
- **Test Coverage**: ~70%

---

## 🐛 Known Issues

- CSV import functionality not yet implemented (planned for v1.1)
- Some edge cases in error handling need improvement
- Integration tests for UI components pending
- Performance with very large datasets (10,000+ transactions) not optimized

---

## 🔜 What's Coming Next (v1.1)

- CSV import for bulk data entry
- Enhanced error handling and logging
- UI tooltips and help text
- Integration tests
- Performance optimizations
- macOS .app bundle for distribution

---

## 📚 Documentation

This release includes comprehensive documentation:

- **README.md**: Project overview and installation
- **QUICKSTART.md**: Get started in 5 minutes
- **USER_GUIDE.md**: Complete user manual with examples
- **DEVELOPMENT.md**: Developer guide with coding standards
- **ARCHITECTURE.md**: Technical architecture documentation
- **PROGRESS.md**: Development progress tracking
- **assets/README.md**: Icon specifications and guidelines

---

## 🚀 Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/prism.git
   cd prism
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set up application icon:
   ```bash
   ./setup_icon.sh
   ```

5. Run the application:
   ```bash
   python main.py
   ```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please see DEVELOPMENT.md for coding guidelines and standards.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📝 Changelog

### Version 1.0.0-rc1 (Current)

#### Added
- Personal Finances tab with complete transaction management
- Investments tab with portfolio tracking and price updates
- Order Book tab with buy/sell order tracking
- Reports tab with 4 interactive Plotly charts
- Application icon system with prism2.png support
- Date range filters for reports
- CSV export for all data types
- Theme system (light/dark)
- Background price refresh with progress bar
- Summary cards in all tabs
- Color-coded data visualization
- Filter by status in Order Book
- Quick actions for bulk operations
- Comprehensive documentation (7 guides)
- Icon setup script
- Keyboard shortcuts

#### Technical
- SQLite database with 3 tables
- CoinGecko API integration
- Yahoo Finance API integration
- 5-minute API response caching
- Signal-based reactive architecture
- Thread-safe database operations
- Background threading for price updates
- Responsive UI layouts
- Form validation across all dialogs

---

## ⚠️ Important Notes

- This is a Release Candidate - please test thoroughly before using for production data
- Always backup your database file: `~/Library/Application Support/Prism/prism.db`
- Price updates require internet connection
- Some APIs have rate limits - avoid excessive price refreshes
- Data is stored locally only - no cloud backup (yet)

---

## 🙏 Acknowledgments

- **PyQt6**: Excellent GUI framework
- **Plotly**: Beautiful interactive charts
- **CoinGecko**: Free cryptocurrency price API
- **Yahoo Finance**: Free stock price data
- **Inspired by**: Finary, Mint, Personal Capital

---

## 📧 Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share tips
- **Email**: support@prism-app.com (coming soon)

---

## 📄 License

MIT License - See LICENSE file for details

---

**Thank you for testing Prism 1.0.0-rc1!** 🎨💰

We appreciate your feedback and bug reports. Together, we'll make Prism the best personal finance app for macOS!

*Released: December 2024*
*Next Release: v1.1.0 (Q1 2025)*