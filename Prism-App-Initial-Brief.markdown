# Brief for Prism: Personal Finance & Investment App (Initial Iteration)

## Overview
**Prism** is a macOS desktop application for managing personal finances and investments (PEA, cryptos, financial placements) with a highly visual, intuitive interface inspired by Finary. It runs locally (no cloud), prioritizes speed, customizability, and real-time financial data via APIs. This first iteration is a Minimum Viable Product (MVP) to establish core functionality, a graphical UI, and a foundation for future features (e.g., encryption, advanced reports).

### Objectives
- Build a local macOS app with a modern, customizable UI.
- Enable tracking of personal expenses and investments (PEA, cryptos, placements).
- Provide real-time price updates for investments via public APIs.
- Support data export (order book in CSV).
- Display interactive graphs for financial insights.
- Ensure a lightweight, fast app with a local database.

### Target Platform
- macOS (bundle as a `.app` executable).
- Cross-platform compatibility to be considered later (not in this iteration).

## Technical Specifications
- **Language**: Python 3.11+ for rapid development and rich libraries.
- **GUI Framework**: PyQt6 for a native, customizable, and responsive interface.
- **Database**: SQLite for lightweight local storage.
- **Libraries**:
  - Data: `pandas` for transaction/investment manipulation.
  - Graphs: `plotly` for interactive, modern visualizations.
  - APIs: `requests` or `aiohttp` for async real-time price fetching (e.g., CoinGecko for cryptos, Yahoo Finance/Alpha Vantage for stocks).
  - Export: `csv` (native), `reportlab` for future PDF exports.
  - Packaging: `pyinstaller` to bundle into a macOS `.app`.
- **No security**: Skip encryption/passwords for now (to be added in future iterations).

## Functional Requirements

### 1. Database Schema (SQLite)
Create a local SQLite database (`prism.db`) with the following tables:
- **Transactions** (personal expenses/revenues):
  - `id`: Integer, primary key, auto-increment.
  - `date`: Date (YYYY-MM-DD).
  - `amount`: Float (positive for revenue, negative for expense).
  - `category`: Text (e.g., "Food", "Salary", "Transport").
  - `type`: Text ("personal" or "investment").
  - `description`: Text (optional, e.g., "Grocery store").
- **Assets** (investments: PEA, cryptos, placements):
  - `id`: Integer, primary key, auto-increment.
  - `ticker`: Text (e.g., "BTC", "AAPL", "BondX").
  - `quantity`: Float (e.g., 0.5 BTC, 10 shares).
  - `price_buy`: Float (purchase price per unit).
  - `date_buy`: Date.
  - `current_price`: Float (updated via API).
  - `asset_type`: Text ("crypto", "stock", "bond").
- **Orders** (order book for trading/investments):
  - `id`: Integer, primary key, auto-increment.
  - `ticker`: Text.
  - `quantity`: Float.
  - `price`: Float (order price).
  - `order_type`: Text ("buy" or "sell").
  - `date`: Date.
  - `status`: Text ("open", "closed").

### 2. User Interface (PyQt6)
Design a clean, modern UI with:
- **Main Window**: Tabbed layout with three tabs:
  - "Personal Finances": For expense/revenue tracking.
  - "Investments": For asset management and portfolio overview.
  - "Reports": For graphs and exports.
- **Features**:
  - **Dashboard**: Each tab has a dashboard with draggable widgets (e.g., graph widget, summary widget).
  - **Add Transaction/Asset**: "+" button opens a form (date, amount/ticker, category/asset_type, etc.).
  - **Customizability**: Support light/dark themes (toggle button) and resizable widgets.
  - **Search**: Search bar for transactions/assets by date, category, or ticker.
- **Style**: Use a clean, macOS-native look (e.g., rounded buttons, subtle animations). Inspiration: Finary’s sleek, minimal design.

### 3. Core Features
- **Add/Edit Transactions**: Form to input personal expenses/revenues (manual entry for MVP, CSV import later).
- **Add/Edit Assets**: Form to add investments (ticker, quantity, buy price, date). Auto-fetch current price via API on save.
- **Real-Time Price Updates**:
  - Button "Refresh Prices" in Investments tab.
  - Async API calls to:
    - CoinGecko: `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur` (free, no API key).
    - Yahoo Finance (via `yfinance` lib) for stocks (e.g., `AAPL`, `LVMH.PA` for PEA).
  - Update `current_price` in Assets table and recalculate portfolio value.
- **Order Book**:
  - Table view in Investments tab to list/add/edit orders (ticker, quantity, price, buy/sell).
  - Export to CSV (columns: ticker, quantity, price, order_type, date, status).
- **Graphs** (Plotly, embedded in PyQt):
  - Personal Finances tab:
    - Line chart: Balance evolution over time (sum of transactions).
    - Pie chart: Expense/revenue by category.
  - Investments tab:
    - Line chart: Portfolio value over time (based on `current_price` * `quantity`).
    - Pie chart: Portfolio allocation by asset_type (crypto, stock, bond).
- **Export**:
  - Button to export order book as CSV (`orders.csv`).
  - Future: PDF reports with embedded graphs (not in MVP).

### 4. Non-Functional Requirements
- **Performance**: App must be lightweight (<100MB memory) and responsive (<1s for UI updates).
- **Error Handling**: Graceful handling of API failures (e.g., fallback to last known price).
- **Testing**: Unit tests for:
  - Database CRUD operations.
  - API price fetching.
  - Portfolio calculations (total value, gains/losses).
- **Packaging**: Bundle as a macOS `.app` using `pyinstaller`.

## Development Plan
1. **Setup** (1-2 days):
   - Initialize Python project with virtualenv.
   - Install dependencies: `PyQt6`, `pandas`, `plotly`, `requests` (or `aiohttp`), `yfinance`.
   - Setup SQLite DB with schema above.
2. **UI Skeleton** (2-3 days):
   - Build main window with tabs, basic widgets, and theme toggle.
   - Implement forms for adding transactions/assets.
3. **Core Logic** (3-5 days):
   - CRUD for transactions, assets, orders (SQLite).
   - API integration for price updates (CoinGecko, Yahoo Finance).
   - Portfolio calculations (value, gains/losses).
4. **Graphs** (2-3 days):
   - Integrate Plotly for balance and allocation charts.
   - Embed in PyQt tabs.
5. **Export** (1 day):
   - CSV export for order book.
6. **Testing & Packaging** (2 days):
   - Write unit tests.
   - Bundle with `pyinstaller` into `.app`.

## Deliverables
- Source code in a Git repo (structure: `src/`, `tests/`, `requirements.txt`).
- Packaged `.app` for macOS.
- Basic README with setup/run instructions.
- Unit tests for core logic.

## Notes for Developer
- Prioritize modularity (separate modules for DB, UI, API, graphs).
- Use async for API calls to avoid UI freeze.
- Follow macOS UI guidelines (e.g., Human Interface Guidelines for button placement).
- Inspiration: Study Finary’s dashboard for layout ideas (but keep it simpler for MVP).
- Avoid external dependencies requiring API keys for now (use free APIs).

## Next Steps (Future Iterations)
- Add CSV import for transactions.
- Implement PDF reports with `reportlab`.
- Add encryption (`cryptography` lib) for data security.
- Support custom categories and budget alerts.
- Add more graphs (e.g., heatmap, waterfall).