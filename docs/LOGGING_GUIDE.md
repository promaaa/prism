# Logging System Guide

## Overview

Prism includes a comprehensive logging system that tracks all operations, errors, and performance metrics throughout the application. This guide explains how to use the logging features both as a user and as a developer.

---

## User Guide

### Viewing Logs

#### Opening the Log Viewer

There are three ways to open the log viewer:

1. **Menu Bar**: `View` → `View Logs`
2. **Keyboard Shortcut**: `Cmd+L` (or `Ctrl+L`)
3. **Toolbar**: Click the "View Logs" button

#### Log Viewer Features

The log viewer provides:

- **Multiple Log Files**:
  - **Main Log**: All application events and operations
  - **Errors Only**: Only error and critical messages
  - **Performance**: Timing information for operations

- **Filtering**:
  - Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Search for specific text (case-insensitive)
  - Real-time updates with auto-refresh

- **Visual Features**:
  - Color-coded log levels for easy scanning
  - Syntax highlighting for better readability
  - Dark theme optimized for long viewing sessions
  - Search term highlighting in yellow

- **Actions**:
  - **Refresh Now**: Manually reload the current log file
  - **Auto-Refresh**: Toggle automatic updates every 2 seconds
  - **Clear Logs**: Delete all log files (requires confirmation)
  - **Export**: Save current log view to a text file

### Log File Locations

All logs are stored in: `~/.prism/logs/`

Individual log files:
- `prism.log` - Main application log (10 MB max, 5 backups)
- `prism_errors.log` - Errors only (5 MB max, 3 backups)
- `prism_performance.log` - Performance metrics (5 MB max, 2 backups)

### Understanding Log Messages

Each log entry contains:

```
2024-12-20 11:25:39 | INFO | prism.database | Initializing DatabaseManager...
└─ Timestamp ─────┘   └─ Level ─┘  └─ Module ─────┘  └─ Message ─────────────┘
```

#### Log Levels

- **DEBUG** (Cyan): Detailed diagnostic information
- **INFO** (Green): General informational messages
- **WARNING** (Orange): Warning messages, no immediate action needed
- **ERROR** (Red): Error messages, operation failed
- **CRITICAL** (Pink/Bold): Critical errors, application may be unstable

### Common Use Cases

#### Troubleshooting Price Fetch Issues

1. Open log viewer (`Cmd+L`)
2. Select "Main Log"
3. Set filter to "ERROR"
4. Search for ticker symbol (e.g., "BTC")
5. Check error messages for API issues

#### Checking Application Performance

1. Open log viewer
2. Select "Performance" log
3. Look for operations taking > 1 second
4. Check "Duration:" field in each entry

#### Finding Database Issues

1. Open log viewer
2. Set filter to "ERROR"
3. Search for "database"
4. Review error messages and stack traces

---

## Developer Guide

### Using the Logger

#### Basic Usage

```python
from utils.logger import get_logger

# Get a logger for your module
logger = get_logger("my_module")

# Log messages at different levels
logger.debug("Detailed diagnostic information")
logger.info("General informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with full traceback")
```

#### Convenience Functions

```python
from utils.logger import info, error, debug, warning, critical

# Quick logging without getting a logger instance
info("Application started")
error("Failed to connect to API")
debug(f"Processing {count} items")
```

### Decorators

#### Exception Logging

Automatically log exceptions with full context:

```python
from utils.logger import log_exception

@log_exception
def risky_operation():
    # If this raises an exception, it will be logged automatically
    result = do_something_dangerous()
    return result
```

#### Performance Tracking

Track execution time of functions:

```python
from utils.logger import log_performance

@log_performance("Database Query")
def fetch_all_transactions():
    # Execution time will be logged to performance log
    return db.get_all_transactions()
```

The performance log will show:
```
2024-12-20 11:30:15 | Database Query | Duration: 0.234s
```

#### Method Call Logging

Log all method calls with arguments:

```python
from utils.logger import log_method_call

class MyService:
    @log_method_call
    def process_data(self, data_id, force=False):
        # Method calls will be logged with arguments
        return self._do_processing(data_id, force)
```

### Context Managers

Use context managers for logging code blocks:

```python
from utils.logger import LogContext

def complex_operation():
    with LogContext("Processing large dataset"):
        # Start and completion will be logged automatically
        # Including duration and success/failure
        process_data()
        transform_results()
        save_to_database()
```

### Advanced Features

#### Custom Logger Names

```python
# Create loggers with custom names for better organization
api_logger = get_logger("api.custom_service")
ui_logger = get_logger("ui.custom_widget")
```

#### Changing Log Level

```python
from utils.logger import set_log_level

# Set global log level (affects console output)
set_log_level("DEBUG")  # Show all messages
set_log_level("WARNING")  # Only warnings and above
```

#### Clearing Logs

```python
from utils.logger import clear_logs

# Programmatically clear all log files
clear_logs()
```

#### Getting Log File Paths

```python
from utils.logger import get_log_files

log_files = get_log_files()
print(log_files["main"])        # Path to main log
print(log_files["errors"])      # Path to error log
print(log_files["performance"]) # Path to performance log
```

### Best Practices

1. **Use Appropriate Log Levels**:
   - `DEBUG`: Diagnostic info, variable values, flow control
   - `INFO`: Important events, milestones, successful operations
   - `WARNING`: Unexpected situations that don't prevent operation
   - `ERROR`: Operation failures, exceptions
   - `CRITICAL`: Severe errors that may cause application failure

2. **Include Context**:
   ```python
   # Good
   logger.info(f"Fetched price for {ticker}: {price} EUR")
   
   # Bad
   logger.info("Price fetched")
   ```

3. **Use Decorators for Consistent Logging**:
   ```python
   # All API calls should log exceptions and performance
   @log_exception
   @log_performance("API Call")
   def fetch_from_api(self, endpoint):
       return requests.get(endpoint)
   ```

4. **Don't Log Sensitive Data**:
   ```python
   # Never log passwords, API keys, or personal data
   logger.info(f"User logged in: {username}")  # OK
   logger.info(f"Password: {password}")        # NEVER!
   ```

5. **Use String Formatting**:
   ```python
   # Efficient - only formats if logged
   logger.debug("Processing item %s of %s", i, total)
   
   # Less efficient - always formats
   logger.debug(f"Processing item {i} of {total}")
   ```

---

## Troubleshooting

### Logs Not Appearing

- Check if `~/.prism/logs/` directory exists
- Verify file permissions
- Check if disk is full
- Try clearing logs and restarting

### Log Viewer Shows "Log file does not exist yet"

- This is normal on first run
- Perform some operations to generate logs
- Click "Refresh Now" to reload

### Performance Impact

- Logging is optimized for minimal impact
- File logging happens in a separate thread
- Log rotation prevents files from growing too large
- Typical overhead: < 1ms per log entry

### Disk Space

- Logs are automatically rotated
- Maximum total size: ~30 MB (all logs combined)
- Older log files are deleted automatically
- You can manually clear logs via the UI

---

## Configuration

### Log Directory

To change the log directory, edit `src/utils/logger.py`:

```python
# Default location
LOG_DIR = Path.home() / ".prism" / "logs"

# Custom location
LOG_DIR = Path("/custom/path/to/logs")
```

### Log Rotation

Adjust rotation settings in `logger.py`:

```python
file_handler = logging.handlers.RotatingFileHandler(
    MAIN_LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,               # 5 backup files
)
```

### Cache Duration

Change how long to cache logs in viewer:

```python
# In log_viewer_dialog.py
self._cache_duration = timedelta(minutes=5)  # Adjust as needed
```

---

## Examples

### Example: Logging Database Operations

```python
from utils.logger import get_logger, log_performance, log_exception

logger = get_logger("database")

@log_exception
@log_performance("add_transaction")
def add_transaction(self, date, amount, category):
    logger.debug(f"Adding transaction: {date}, {amount}, {category}")
    
    try:
        # Database operation
        cursor.execute("INSERT INTO ...")
        transaction_id = cursor.lastrowid
        
        logger.info(f"Transaction added: ID {transaction_id}")
        return transaction_id
        
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        raise
```

### Example: Logging API Calls

```python
from utils.logger import get_logger, LogContext

logger = get_logger("api.crypto")

def get_multiple_prices(self, tickers):
    with LogContext(f"Fetching {len(tickers)} crypto prices"):
        results = {}
        
        for ticker in tickers:
            try:
                price = self._fetch_single_price(ticker)
                results[ticker] = price
                logger.debug(f"Fetched {ticker}: {price}")
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                results[ticker] = None
        
        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"Successfully fetched {successful}/{len(tickers)} prices")
        
        return results
```

### Example: Logging UI Events

```python
from utils.logger import get_logger, log_exception

logger = get_logger("ui.main_window")

@log_exception
def _on_refresh_prices(self):
    logger.info("Refresh prices action triggered")
    
    try:
        self.investments_tab.refresh_prices()
        logger.info("Prices refreshed successfully")
        self.status_bar.showMessage("Prices updated", 3000)
    except Exception as e:
        logger.error(f"Failed to refresh prices: {e}")
        QMessageBox.critical(self, "Error", f"Failed to refresh prices:\n{str(e)}")
```

---

## FAQ

**Q: Do logs contain sensitive information?**
A: No. The logging system is designed to avoid logging passwords, API keys, or personal financial data.

**Q: Can I export logs for bug reports?**
A: Yes! Use the "Export" button in the log viewer to save logs to a file.

**Q: Will logs slow down my application?**
A: No. Logging is optimized for minimal performance impact (< 1ms per entry).

**Q: How much disk space do logs use?**
A: Maximum ~30 MB total. Logs are automatically rotated when they reach size limits.

**Q: Can I view logs from previous sessions?**
A: Yes! Rotated logs are kept with `.1`, `.2`, etc. suffixes. Use your system file viewer to open them.

**Q: How do I report a bug with logs?**
A: Open the log viewer, export the logs, and attach the exported file to your bug report.

---

## Summary

The Prism logging system provides:

✅ Comprehensive logging throughout the application
✅ Real-time log viewing with search and filtering
✅ Performance tracking for all major operations
✅ Automatic log rotation to manage disk space
✅ Color-coded, easy-to-read log format
✅ Developer-friendly decorators and utilities
✅ Production-ready error tracking

For more information, see:
- `src/utils/logger.py` - Main logging implementation
- `src/ui/log_viewer_dialog.py` - Log viewer UI
- `PROGRESS.md` - Development status and features