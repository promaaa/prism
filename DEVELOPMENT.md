# Prism Development Guide

This guide is for developers who want to contribute to Prism or understand its internals.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Database Development](#database-development)
7. [API Development](#api-development)
8. [UI Development](#ui-development)
9. [Debugging](#debugging)
10. [Building & Packaging](#building--packaging)
11. [Common Tasks](#common-tasks)
12. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- macOS 10.15+ (Catalina or later)
- Python 3.11 or higher
- Git
- Xcode Command Line Tools (for some dependencies)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/prism.git
cd prism

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import PyQt6; print('PyQt6 installed successfully')"
```

### First Run

```bash
# Run the application
python main.py

# Add sample data (optional)
python add_sample_data.py

# Run tests
pytest tests/
```

## Development Environment

### Recommended IDE

**VS Code** with extensions:
- Python
- Pylance
- Black Formatter
- PyQt6 Snippets

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.rulers": [88],
        "editor.tabSize": 4
    }
}
```

### Alternative: PyCharm

1. Open project directory
2. Configure Python interpreter to use `venv`
3. Enable pytest as test runner
4. Configure Black as external tool

## Project Structure

```
prism/
├── main.py                 # Entry point - keep minimal
├── src/                    # All source code here
│   ├── database/           # Database layer
│   │   ├── schema.py      # Schema only, no business logic
│   │   └── db_manager.py  # CRUD operations
│   ├── api/                # External API wrappers
│   ├── ui/                 # PyQt6 UI components
│   ├── utils/              # Pure functions, no state
│   └── models/             # Data classes (future)
└── tests/                  # Mirror src/ structure
```

### Module Responsibilities

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `database/` | Data persistence | SQLite only |
| `api/` | External services | requests, aiohttp |
| `ui/` | User interface | PyQt6, database, api |
| `utils/` | Business logic | pandas, numpy |
| `models/` | Data structures | None (future) |

## Coding Standards

### Style Guide

Follow **PEP 8** with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized by stdlib → third-party → local

### Code Formatting

```bash
# Format all code
black src/ tests/

# Check specific file
black --check src/database/db_manager.py

# Format with line length
black --line-length 88 src/
```

### Linting

```bash
# Lint all code
pylint src/

# Lint specific module
pylint src/database/

# Disable specific warnings
pylint --disable=C0103,R0913 src/
```

### Type Hints

**Always use type hints** for function signatures:

```python
from typing import List, Dict, Optional, Any

def calculate_balance(
    transactions: List[Dict[str, Any]],
    start_date: Optional[str] = None
) -> float:
    """Calculate balance with type hints."""
    pass
```

### Docstrings

Use **Google-style docstrings**:

```python
def add_transaction(
    self,
    date: str,
    amount: float,
    category: str
) -> int:
    """
    Add a new transaction to the database.

    Args:
        date: Transaction date in YYYY-MM-DD format
        amount: Transaction amount (positive for revenue)
        category: Transaction category

    Returns:
        int: ID of the newly created transaction

    Raises:
        ValueError: If date format is invalid
    """
    pass
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_database.py

# Specific test
pytest tests/test_database.py::TestTransactions::test_add_transaction

# With coverage
pytest --cov=src tests/

# Verbose output
pytest -v tests/

# Stop on first failure
pytest -x tests/
```

### Writing Tests

**Test file structure:**

```python
import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager

@pytest.fixture
def test_db():
    """Create temporary test database."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = Path(temp_file.name)
    temp_file.close()
    
    # Initialize
    from database.schema import initialize_database
    initialize_database(db_path)
    
    db = DatabaseManager(db_path)
    yield db
    
    # Cleanup
    db_path.unlink()

def test_feature(test_db):
    """Test description."""
    # Arrange
    data = {"key": "value"}
    
    # Act
    result = test_db.method(data)
    
    # Assert
    assert result is not None
```

### Test Coverage Goals

- **Database**: 100% coverage
- **Utilities**: 90%+ coverage
- **API**: 80%+ coverage (mock external calls)
- **UI**: Manual testing (Qt components hard to unit test)

## Database Development

### Adding a New Table

1. **Update schema.py:**

```python
def initialize_database(db_path: Optional[Path] = None) -> None:
    # ... existing code ...
    
    # Add new table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_new_table_field
        ON new_table(field)
    """)
```

2. **Add CRUD methods to db_manager.py:**

```python
def add_new_item(self, field: str) -> int:
    """Add item to new table."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO new_table (field) VALUES (?)",
        (field,)
    )
    
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return item_id
```

3. **Write tests in test_database.py:**

```python
def test_add_new_item(test_db):
    """Test adding new item."""
    item_id = test_db.add_new_item("value")
    assert item_id > 0
```

### Migration Strategy (Future)

When schema changes are needed:

1. Create migration file: `migrations/001_add_new_table.sql`
2. Track schema version in database
3. Apply migrations on startup
4. Test rollback procedures

## API Development

### Adding a New API

1. **Create new file:** `src/api/new_api.py`

```python
"""
New API integration for Prism.
"""

import requests
from typing import Optional, Dict, Any

class NewAPI:
    """Wrapper for New API service."""
    
    BASE_URL = "https://api.example.com/v1"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cache: Dict[str, Any] = {}
    
    def get_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from API."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/data",
                params={"symbol": symbol},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None
```

2. **Update `src/api/__init__.py`:**

```python
from .new_api import NewAPI

__all__ = ["CryptoAPI", "StockAPI", "NewAPI"]
```

3. **Add caching** for performance
4. **Add error handling** with retries
5. **Write integration tests** (can use mocks)

### API Best Practices

- Cache responses (5-15 minutes typical)
- Handle rate limits gracefully
- Provide sync and async variants
- Return None on errors, log details
- Use type hints for all methods

## UI Development

### Adding a New Tab

1. **Create tab file:** `src/ui/new_tab.py`

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class NewTab(QWidget):
    """New tab widget."""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        title = QLabel("New Feature")
        title.setProperty("class", "title")
        layout.addWidget(title)
```

2. **Add to main_window.py:**

```python
from ui.new_tab import NewTab

# In _create_central_widget():
self.new_tab = NewTab(self.db)
self.tab_widget.addTab(self.new_tab, "New Feature")
```

### Theme Integration

All widgets automatically inherit theme. For custom styling:

```python
# Use theme colors
color = self.theme_manager.get_color("primary")
widget.setStyleSheet(f"background-color: {color};")

# Or use CSS classes
label.setProperty("class", "title")  # Large bold text
label.setProperty("class", "caption")  # Small gray text
```

### UI Best Practices

- Keep UI logic separate from business logic
- Use signals/slots for event handling
- Test UI manually (automated UI tests are complex)
- Follow macOS Human Interface Guidelines
- Use theme colors, not hardcoded values

## Debugging

### Python Debugger (pdb)

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use Python 3.7+ breakpoint()
breakpoint()
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Database Debugging

```bash
# Open database in SQLite CLI
sqlite3 ~/Library/Application\ Support/Prism/prism.db

# Useful queries
.tables                          # List tables
.schema transactions             # Show table structure
SELECT * FROM transactions;      # View data
.quit                           # Exit
```

### Qt Debugging

```python
# Enable Qt logging
import os
os.environ['QT_LOGGING_RULES'] = 'qt.*=true'

# Or in code
from PyQt6.QtCore import qDebug
qDebug("Debug message")
```

## Building & Packaging

### Development Build

```bash
# Just run directly
python main.py
```

### Production Build (.app)

```bash
# Basic build
pyinstaller --name=Prism \
            --windowed \
            --icon=assets/icon.icns \
            main.py

# Advanced build with data files
pyinstaller --name=Prism \
            --windowed \
            --icon=assets/icon.icns \
            --add-data="src:src" \
            --clean \
            main.py
```

### Code Signing (macOS)

```bash
# Sign the .app
codesign --deep --force --verify --verbose \
         --sign "Developer ID Application: Your Name" \
         dist/Prism.app

# Verify signature
codesign --verify --verbose dist/Prism.app
```

### Notarization (macOS)

```bash
# Create ZIP
ditto -c -k --keepParent dist/Prism.app Prism.zip

# Submit for notarization
xcrun notarytool submit Prism.zip \
      --apple-id your@email.com \
      --team-id TEAMID \
      --wait

# Staple ticket
xcrun stapler staple dist/Prism.app
```

## Common Tasks

### Adding a New Calculation

1. Add function to `src/utils/calculations.py`:

```python
def calculate_new_metric(data: List[Dict]) -> float:
    """
    Calculate new financial metric.
    
    Args:
        data: List of financial records
    
    Returns:
        float: Calculated metric
    """
    # Implementation
    return result
```

2. Add test to `tests/test_calculations.py`
3. Update `__init__.py` to export function
4. Use in UI or reports

### Adding a New Export Format

1. Add function to `src/utils/exports.py`:

```python
def export_to_format(data: List[Dict], path: Path) -> bool:
    """Export data to new format."""
    try:
        # Implementation
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False
```

2. Add button in Reports tab
3. Connect to export function
4. Test with sample data

### Adding a New Ticker

For cryptocurrencies (CoinGecko):

```python
# In crypto_api.py
TICKER_TO_ID = {
    # ... existing ...
    "NEW": "new-coin-id",  # Get ID from coingecko.com
}
```

For stocks (Yahoo Finance):
```python
# Just use the ticker directly
# TICKER.EXCHANGE format
# Examples: AAPL (US), LVMH.PA (Paris), BMW.DE (Frankfurt)
```

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate venv
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Locked Error

```python
# Ensure connections are closed
conn = self._get_connection()
try:
    # ... operations ...
finally:
    conn.close()
```

### PyQt Import Errors

```bash
# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-WebEngine
pip install PyQt6 PyQt6-WebEngine
```

### API Connection Issues

```python
# Check connection
import requests
try:
    r = requests.get("https://api.coingecko.com/api/v3/ping")
    print(r.json())
except Exception as e:
    print(f"Connection failed: {e}")
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code improvements
- `docs/description` - Documentation

### Commit Messages

```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat: Add portfolio diversification score

Calculate HHI-based diversification score for portfolios.
Returns value from 0-100 where 100 is perfectly diversified.

Closes #42
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
```

## Performance Tips

### Database Optimization

```python
# Use transactions for bulk operations
conn = self._get_connection()
cursor = conn.cursor()
try:
    for item in items:
        cursor.execute("INSERT INTO ...", item)
    conn.commit()
finally:
    conn.close()

# Use indexes for frequent queries
# Already created in schema.py
```

### API Optimization

```python
# Batch requests instead of individual
# Good
prices = api.get_multiple_prices(["BTC", "ETH", "SOL"])

# Bad
btc = api.get_price("BTC")
eth = api.get_price("ETH")
sol = api.get_price("SOL")
```

### UI Optimization

```python
# Use signals to prevent blocking
from PyQt6.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(dict)
    
    def run(self):
        result = expensive_operation()
        self.finished.emit(result)
```

## Resources

### Documentation
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLite Docs](https://www.sqlite.org/docs.html)
- [Python Style Guide](https://pep8.org/)

### Tools
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [Postman](https://www.postman.com/) - API testing
- [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html)

### Community
- GitHub Issues - Bug reports
- GitHub Discussions - Feature requests
- Pull Requests - Code contributions

---

**Happy Coding! 🚀**

For questions, open an issue or start a discussion.