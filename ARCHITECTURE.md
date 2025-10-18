# Prism Architecture Documentation

This document provides a comprehensive overview of the Prism application architecture, design decisions, and implementation details.

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Architecture Layers](#architecture-layers)
5. [Database Design](#database-design)
6. [API Integration](#api-integration)
7. [UI Components](#ui-components)
8. [Data Flow](#data-flow)
9. [Design Patterns](#design-patterns)
10. [Testing Strategy](#testing-strategy)
11. [Future Enhancements](#future-enhancements)

## Overview

Prism is a desktop application for macOS built with Python and PyQt6. It follows a modular architecture with clear separation of concerns:

- **Presentation Layer**: PyQt6 UI components
- **Business Logic Layer**: Calculations, validations, and utilities
- **Data Access Layer**: Database operations via DatabaseManager
- **External Services Layer**: API integrations for real-time pricing

### Key Design Principles

1. **Modularity**: Each component is independent and reusable
2. **Separation of Concerns**: Clear boundaries between layers
3. **Single Responsibility**: Each module has one primary purpose
4. **Testability**: All components are unit-testable
5. **Local-First**: No cloud dependency, all data stored locally

## Technology Stack

### Core Technologies

- **Python 3.11+**: Main programming language
- **PyQt6**: GUI framework for native macOS UI
- **SQLite**: Embedded database for local data storage

### Key Libraries

#### UI & Visualization
- `PyQt6` (6.6.0+): Native GUI framework
- `PyQt6-WebEngine`: Web rendering for charts
- `plotly` (5.18.0+): Interactive data visualization
- `kaleido`: Static image export for Plotly

#### Data Processing
- `pandas` (2.1.0+): Data manipulation and analysis
- `numpy` (1.24.0+): Numerical operations

#### API & Networking
- `requests` (2.31.0+): Synchronous HTTP requests
- `aiohttp` (3.9.0+): Asynchronous HTTP requests
- `yfinance` (0.2.32+): Yahoo Finance API wrapper

#### Development & Testing
- `pytest` (7.4.0+): Testing framework
- `pytest-qt`: PyQt testing utilities
- `pytest-asyncio`: Async test support
- `black`: Code formatting
- `pylint`: Code linting

#### Packaging
- `pyinstaller` (6.3.0+): macOS .app bundle creation

## Project Structure

```
prism/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── QUICKSTART.md               # Quick start guide
├── ARCHITECTURE.md             # This file
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
├── run.sh                      # Convenience run script
├── add_sample_data.py          # Sample data generator
│
├── src/                        # Source code
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── schema.py          # Database schema & initialization
│   │   └── db_manager.py      # CRUD operations
│   │
│   ├── api/                    # External API integrations
│   │   ├── __init__.py
│   │   ├── crypto_api.py      # CoinGecko API wrapper
│   │   └── stock_api.py       # Yahoo Finance API wrapper
│   │
│   ├── ui/                     # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py     # Main application window
│   │   ├── themes.py          # Theme management
│   │   ├── personal_tab.py    # Personal finances tab (future)
│   │   ├── investments_tab.py # Investments tab (future)
│   │   ├── reports_tab.py     # Reports tab (future)
│   │   └── forms.py           # Input forms (future)
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── calculations.py    # Financial calculations
│   │   └── exports.py         # Data export utilities
│   │
│   └── models/                 # Data models (future)
│       └── __init__.py
│
└── tests/                      # Test suite
    ├── __init__.py
    ├── test_database.py        # Database tests
    ├── test_api.py            # API tests (future)
    └── test_calculations.py   # Calculation tests (future)
```

## Architecture Layers

### 1. Presentation Layer (UI)

**Location**: `src/ui/`

**Responsibilities**:
- Display data to the user
- Handle user input
- Manage application state
- Apply themes and styling

**Key Components**:
- `MainWindow`: Root application window with menu, toolbar, tabs
- `ThemeManager`: Manages light/dark themes and CSS stylesheets
- Tab widgets: Personal Finances, Investments, Reports

**Design Pattern**: Model-View-Controller (MVC)
- Views: PyQt6 widgets
- Controllers: Event handlers in MainWindow
- Model: DatabaseManager provides data

### 2. Business Logic Layer (Utils)

**Location**: `src/utils/`

**Responsibilities**:
- Financial calculations
- Data transformations
- Export formatting
- Business rules enforcement

**Key Modules**:

#### calculations.py
- `calculate_portfolio_value()`: Sum of all asset values
- `calculate_asset_performance()`: Gain/loss for single asset
- `calculate_balance_over_time()`: Balance evolution data
- `calculate_category_distribution()`: Expense breakdown
- `calculate_roi()`: Return on investment
- `calculate_diversification_score()`: Portfolio diversity metric

#### exports.py
- `export_orders_to_csv()`: Export order book
- `export_transactions_to_csv()`: Export transaction history
- `export_assets_to_csv()`: Export portfolio
- `export_portfolio_summary_to_csv()`: Summary report

### 3. Data Access Layer (Database)

**Location**: `src/database/`

**Responsibilities**:
- Database schema management
- CRUD operations
- Data validation
- Query optimization

**Key Components**:

#### schema.py
- `initialize_database()`: Create tables and indexes
- `get_database_path()`: Locate database file
- Schema versioning (for future migrations)

#### db_manager.py
- **DatabaseManager class**: Main interface to SQLite database
- Transaction operations: add, get, update, delete, search
- Asset operations: add, get, update, delete, price updates
- Order operations: add, get, update, close, delete
- Summary operations: balance, portfolio value, statistics

**Design Pattern**: Repository Pattern
- Encapsulates data access logic
- Provides clean API for data operations
- Hides SQL implementation details

### 4. External Services Layer (API)

**Location**: `src/api/`

**Responsibilities**:
- Fetch real-time price data
- Handle API rate limits
- Cache responses
- Error handling and fallbacks

**Key Components**:

#### crypto_api.py
- **CryptoAPI class**: CoinGecko API wrapper
- Methods: `get_price()`, `get_multiple_prices()`, async variants
- Features: Automatic caching (5 min), ticker mapping, error recovery

#### stock_api.py
- **StockAPI class**: Yahoo Finance API wrapper via yfinance
- Methods: `get_price()`, `get_multiple_prices()`, async variants
- Features: Multi-exchange support, caching, thread pool execution

**Design Pattern**: Adapter Pattern
- Adapts external APIs to internal interface
- Provides consistent API regardless of data source

## Database Design

### Schema Overview

```sql
-- Transactions: Personal finance tracking
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,              -- Positive = revenue, Negative = expense
    category TEXT NOT NULL,
    type TEXT NOT NULL,                -- 'personal' or 'investment'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assets: Investment holdings
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quantity REAL NOT NULL,
    price_buy REAL NOT NULL,
    date_buy TEXT NOT NULL,
    current_price REAL,                -- Updated via API
    asset_type TEXT NOT NULL,          -- 'crypto', 'stock', or 'bond'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date_buy)
);

-- Orders: Order book for trading
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    order_type TEXT NOT NULL,          -- 'buy' or 'sell'
    date TEXT NOT NULL,
    status TEXT NOT NULL,              -- 'open' or 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

- `idx_transactions_date`: Fast date-range queries
- `idx_transactions_category`: Category filtering
- `idx_transactions_type`: Type filtering
- `idx_assets_ticker`: Asset lookup by ticker
- `idx_assets_type`: Asset type filtering
- `idx_orders_ticker`: Order lookup by ticker
- `idx_orders_status`: Status filtering
- `idx_orders_date`: Date-range queries

### Triggers

- `update_transactions_timestamp`: Auto-update `updated_at` on changes
- `update_assets_timestamp`: Auto-update `updated_at` on changes
- `update_orders_timestamp`: Auto-update `updated_at` on changes

### Data Integrity

- **CHECK constraints**: Enforce valid enum values
- **UNIQUE constraints**: Prevent duplicate assets
- **NOT NULL constraints**: Required fields
- **Timestamps**: Audit trail for all records

## API Integration

### CoinGecko API (Cryptocurrency)

**Endpoint**: `https://api.coingecko.com/api/v3/simple/price`

**Features**:
- Free tier: ~50 calls/minute
- No API key required
- Returns prices in multiple currencies

**Implementation**:
```python
# Synchronous
price = crypto_api.get_price("BTC", currency="eur")

# Asynchronous
price = await crypto_api.get_price_async("BTC", currency="eur")

# Batch
prices = crypto_api.get_multiple_prices(["BTC", "ETH", "SOL"])
```

**Caching Strategy**:
- Cache duration: 5 minutes
- Per-ticker caching
- Fallback to cached price on API failure

### Yahoo Finance API (Stocks)

**Library**: `yfinance`

**Features**:
- No API key required
- Supports multiple exchanges
- Historical data available

**Implementation**:
```python
# Single stock
price = stock_api.get_price("AAPL")

# European stock
price = stock_api.get_price("LVMH.PA")

# Batch
prices = stock_api.get_multiple_prices(["AAPL", "MSFT", "GOOGL"])
```

**Exchange Suffixes**:
- `.PA`: Paris (Euronext Paris)
- `.DE`: Frankfurt (XETRA)
- `.L`: London (LSE)
- `.AS`: Amsterdam (Euronext Amsterdam)

### Error Handling

1. **Network Errors**: Use cached prices if available
2. **Rate Limits**: Implement exponential backoff (future)
3. **Invalid Tickers**: Return None, log warning
4. **Timeouts**: 10-second timeout, use cached data

## UI Components

### Theme System

**Design**: CSS-based theming with light/dark modes

**Implementation**:
- `ThemeManager`: Manages current theme state
- `Theme` enum: LIGHT or DARK
- CSS stylesheets: Complete styling for all widgets

**Color Palette**:

#### Light Theme
- Background: `#f5f5f7`
- Surface: `#ffffff`
- Primary: `#0071e3`
- Text: `#1d1d1f`
- Border: `#d2d2d7`

#### Dark Theme
- Background: `#1c1c1e`
- Surface: `#2c2c2e`
- Primary: `#0a84ff`
- Text: `#f5f5f7`
- Border: `#38383a`

### Main Window Structure

```
MainWindow
├── MenuBar
│   ├── File Menu (New, Export, Quit)
│   ├── View Menu (Theme, Refresh)
│   └── Help Menu (About)
├── ToolBar
│   ├── + Transaction Button
│   ├── + Asset Button
│   ├── Refresh Prices Button
│   └── Toggle Theme Button
├── TabWidget
│   ├── Personal Finances Tab
│   │   ├── Summary Cards (Balance, Transaction Count)
│   │   └── Content Area (Placeholder)
│   ├── Investments Tab
│   │   ├── Summary Cards (Portfolio Value, Asset Count)
│   │   └── Content Area (Placeholder)
│   └── Reports Tab
│       ├── Export Buttons (Orders, Transactions, Assets)
│       └── Content Area (Placeholder)
└── StatusBar
    └── Status Messages
```

## Data Flow

### Adding a Transaction

1. User clicks "+ Transaction" button
2. Form dialog opens (to be implemented)
3. User fills in: date, amount, category, description
4. Form validates input
5. `DatabaseManager.add_transaction()` called
6. Transaction inserted into SQLite
7. UI refreshes to show new transaction
8. Balance recalculated and displayed

### Refreshing Asset Prices

1. User clicks "Refresh Prices" button
2. `MainWindow._on_refresh_prices()` called
3. Fetch all assets from database
4. Separate assets by type (crypto vs. stock)
5. Batch API calls:
   - `CryptoAPI.get_multiple_prices()` for cryptos
   - `StockAPI.get_multiple_prices()` for stocks
6. Update `current_price` in database for each asset
7. Recalculate portfolio value
8. UI refreshes with new values
9. Status bar shows success message

### Exporting Data

1. User navigates to Reports tab
2. User clicks export button (e.g., "Export Orders")
3. Fetch data from database
4. Transform to CSV format
5. Generate filename with timestamp
6. Save to Downloads folder
7. Show success dialog with file path

## Design Patterns

### 1. Repository Pattern (DatabaseManager)
**Purpose**: Encapsulate data access logic
**Benefits**: 
- Centralized data operations
- Easy to test with mock databases
- Clean separation from business logic

### 2. Adapter Pattern (API Classes)
**Purpose**: Adapt external APIs to internal interface
**Benefits**:
- Consistent API regardless of source
- Easy to swap implementations
- Centralized error handling

### 3. Singleton Pattern (ThemeManager, DatabaseManager)
**Purpose**: Single instance of shared resources
**Benefits**:
- Consistent state across application
- Resource efficiency

### 4. Observer Pattern (PyQt Signals/Slots)
**Purpose**: Event-driven UI updates
**Benefits**:
- Loose coupling between components
- Reactive UI updates

### 5. Strategy Pattern (Calculation Functions)
**Purpose**: Interchangeable algorithms
**Benefits**:
- Flexible calculation methods
- Easy to extend with new metrics

## Testing Strategy

### Unit Tests

**Location**: `tests/`

**Coverage**:
- Database operations (CRUD)
- Calculations and business logic
- API wrappers (mocked)
- Export functions

**Tools**:
- `pytest`: Test framework
- `pytest-qt`: PyQt testing
- Temporary databases for isolation

**Example**:
```python
def test_add_transaction(test_db):
    transaction_id = test_db.add_transaction(
        date="2024-01-15",
        amount=-50.0,
        category="Food",
        transaction_type="personal"
    )
    assert transaction_id > 0
```

### Integration Tests (Future)

- End-to-end workflows
- UI interaction testing
- API integration testing

### Test Data

- `add_sample_data.py`: Generate realistic test data
- Temporary databases for each test
- Fixtures for common test scenarios

## Future Enhancements

### Phase 2: Enhanced UI
- Complete Personal Finances tab with transaction list
- Complete Investments tab with asset portfolio view
- Interactive Plotly charts
- Search and filtering
- Forms for data entry

### Phase 3: Advanced Features
- CSV import for bulk transactions
- PDF report generation with reportlab
- Budget tracking and alerts
- Recurring transactions
- Multi-currency support

### Phase 4: Security
- Database encryption with cryptography
- Password protection
- Secure storage of API keys
- Export encryption option

### Phase 5: Analytics
- Advanced charts (heatmaps, waterfall)
- Tax report generation
- Investment recommendations
- Performance benchmarking

### Phase 6: Sync & Backup
- iCloud sync (optional)
- Automatic backups
- Export/import of entire database
- Data migration tools

## Performance Considerations

### Current Optimizations

1. **Database Indexes**: Fast queries on frequently accessed columns
2. **API Caching**: 5-minute cache reduces API calls
3. **Batch Operations**: Multiple assets fetched in single API call
4. **Async API Calls**: Non-blocking price updates

### Future Optimizations

1. **Lazy Loading**: Load data on-demand for large datasets
2. **Virtual Scrolling**: Efficient rendering of large lists
3. **Background Workers**: Offload heavy operations
4. **Query Optimization**: Use prepared statements
5. **Memory Management**: Release resources proactively

## Security Considerations (Future)

### Data Protection
- Encrypt database at rest
- Secure API key storage (when needed)
- Password-protected exports

### Network Security
- HTTPS for all API calls
- Certificate validation
- Rate limiting implementation

### Privacy
- No telemetry or tracking
- No cloud storage (by design)
- Local-only data storage

## Deployment

### Development
```bash
python main.py
```

### Testing
```bash
pytest tests/
```

### Production (macOS .app)
```bash
pyinstaller --name=Prism --windowed --icon=assets/icon.icns main.py
```

### Distribution
- Code-sign the .app (requires Apple Developer account)
- Notarize for macOS Gatekeeper
- Create DMG installer

## Contributing Guidelines

1. Follow PEP 8 style guide
2. Use Black for code formatting
3. Write unit tests for new features
4. Update documentation
5. Use type hints
6. Add docstrings to all functions

## Conclusion

Prism's architecture is designed for:
- **Simplicity**: Easy to understand and maintain
- **Extensibility**: New features can be added modularly
- **Performance**: Fast and responsive UI
- **Reliability**: Comprehensive error handling
- **Testability**: All components can be unit-tested

The modular design allows for future enhancements without major refactoring, while the local-first approach ensures user data remains private and accessible offline.