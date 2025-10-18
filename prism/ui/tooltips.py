"""
Centralized tooltips and help text for Prism application.

This module provides consistent, helpful tooltips and help text
throughout the application for better user experience.
"""

from typing import Dict


class Tooltips:
    """Centralized tooltip and help text manager."""

    # ==================== MAIN WINDOW ====================

    MAIN_WINDOW = {
        "new_transaction": "Add a new personal finance transaction (Cmd+N)",
        "new_asset": "Add a new investment asset to your portfolio",
        "refresh_prices": "Update current prices for all assets (Cmd+R)",
        "export_data": "Export your data to CSV files (Cmd+E)",
        "toggle_theme": "Switch between light and dark themes (Cmd+T)",
        "view_logs": "View application logs and performance data (Cmd+L)",
        "quit": "Close the application (Cmd+Q)",
    }

    # ==================== PERSONAL FINANCES TAB ====================

    PERSONAL_TAB = {
        "balance_card": "Your current balance: total income minus total expenses",
        "income_card": "Sum of all income transactions (positive amounts)",
        "expenses_card": "Sum of all expense transactions (negative amounts)",
        "count_card": "Total number of transactions in your database",
        "add_button": "Add a new transaction to track income or expenses",
        "refresh_button": "Reload transaction data from the database",
        "transaction_table": "Click on a row to see details. Use Edit/Delete buttons to manage transactions.",
        "edit_button": "Modify the selected transaction's details",
        "delete_button": "Permanently remove this transaction (requires confirmation)",
    }

    TRANSACTION_FORM = {
        "date": "Select the date when this transaction occurred",
        "amount": "Enter amount in euros. Use positive numbers for income, negative for expenses.\nExample: 2500 for salary, -45.50 for groceries",
        "category": "Choose or type a category to organize your transactions.\nExamples: Salary, Food, Rent, Entertainment, Healthcare",
        "type_personal": "Personal transactions (daily expenses, income)",
        "type_investment": "Investment-related transactions (dividends, capital gains)",
        "description": "Optional notes about this transaction.\nExample: 'Monthly salary from Acme Corp' or 'Weekly groceries at Carrefour'",
    }

    # ==================== INVESTMENTS TAB ====================

    INVESTMENTS_TAB = {
        "portfolio_value_card": "Current total value of all your investments based on latest prices",
        "invested_card": "Total amount you've invested (sum of all purchase costs)",
        "gain_loss_card": "Your profit or loss: (Current Value - Total Invested).\nGreen = profit, Red = loss",
        "assets_count_card": "Number of different assets in your portfolio",
        "add_button": "Add a new investment asset (stock, crypto, or bond)",
        "refresh_prices_button": "Fetch latest prices from CoinGecko and Yahoo Finance for all your assets",
        "asset_table": "Your investment portfolio. Click rows to see details. Prices update when you click Refresh.",
        "edit_button": "Modify asset quantity or purchase details",
        "delete_button": "Remove this asset from your portfolio (requires confirmation)",
    }

    ASSET_FORM = {
        "asset_type_crypto": "Cryptocurrency (Bitcoin, Ethereum, etc.)",
        "asset_type_stock": "Stock shares (CAC 40, US stocks, etc.)",
        "asset_type_bond": "Bonds or fixed-income securities",
        "ticker": "Start typing to see suggestions.\nCrypto: BTC, ETH, SOL, TAO\nStocks: MC.PA (LVMH), AIR.PA (Airbus)\nSearch by company name or category!",
        "quantity": "How many units you own.\nExamples: 0.5 BTC, 10 shares, 1000 bonds",
        "buy_price": "Price per unit when you purchased (in euros).\nExample: 35000 for 1 BTC bought at €35,000",
        "purchase_date": "When did you purchase this asset?",
        "fetch_price": "Click to get the current market price for verification.\nHelps ensure you entered the correct ticker symbol.",
    }

    # ==================== ORDER BOOK TAB ====================

    ORDERS_TAB = {
        "total_orders_card": "Total number of orders in your order book",
        "open_orders_card": "Orders that are still active and not yet executed",
        "closed_orders_card": "Completed or cancelled orders",
        "total_value_card": "Combined value of all orders (quantity × price)",
        "add_button": "Create a new buy or sell order",
        "refresh_button": "Reload orders from the database",
        "filter_all": "Show all orders regardless of status",
        "filter_open": "Show only open (active) orders",
        "filter_closed": "Show only closed (completed) orders",
        "close_all_open": "Mark all open orders as closed (batch operation)",
        "delete_all_closed": "Remove all closed orders from database (requires confirmation)",
        "order_table": "Your order history. Green = buy orders, Red = sell orders.\nOrange status = open, Green status = closed",
        "edit_button": "Modify order details (ticker, quantity, price, status)",
        "toggle_status_button": "Switch order between open and closed status",
        "delete_button": "Permanently remove this order (requires confirmation)",
    }

    ORDER_FORM = {
        "ticker": "Asset ticker symbol.\nExamples: BTC, ETH, MC.PA, AIR.PA",
        "order_type_buy": "Buy order - purchasing an asset",
        "order_type_sell": "Sell order - selling an asset",
        "quantity": "Number of units to buy or sell.\nExample: 0.1 BTC, 50 shares",
        "price": "Target price per unit in euros.\nExample: 30000 for buying BTC at €30,000",
        "order_date": "When was this order placed?",
        "status_open": "Order is active and not yet executed",
        "status_closed": "Order has been completed or cancelled",
    }

    # ==================== REPORTS TAB ====================

    REPORTS_TAB = {
        "date_range": "Filter all reports and charts by time period",
        "date_all_time": "Show all data since you started using Prism",
        "date_7_days": "Last 7 days",
        "date_30_days": "Last 30 days (1 month)",
        "date_90_days": "Last 90 days (3 months)",
        "date_6_months": "Last 6 months",
        "date_year": "Last 12 months (1 year)",
        "date_custom": "Choose your own start and end dates",
        "export_transactions": "Download all transactions as CSV file",
        "export_assets": "Download investment portfolio as CSV file",
        "export_orders": "Download order book as CSV file",
        "balance_chart": "Interactive chart showing how your balance evolved over time.\nHover for details, zoom, pan, and download as image.",
        "category_chart": "Pie chart showing spending distribution by category.\nClick legend items to show/hide categories.",
        "portfolio_chart": "Track your investment portfolio value over time.\nSee how your investments are performing!",
        "allocation_chart": "Visual breakdown of your portfolio by asset type.\nShows crypto vs stocks vs bonds distribution.",
    }

    # ==================== LOG VIEWER ====================

    LOG_VIEWER = {
        "log_file_selector": "Choose which log file to view:\n• Main Log: All events\n• Errors Only: Problems only\n• Performance: Timing data",
        "level_filter": "Filter by log level:\n• ALL: Show everything\n• DEBUG: Detailed diagnostics\n• INFO: Important events\n• WARNING: Potential issues\n• ERROR: Failures\n• CRITICAL: Severe problems",
        "search_box": "Search for specific text in logs.\nExample: search for a ticker, error message, or operation name",
        "auto_refresh": "Automatically reload logs every 2 seconds.\nUseful for monitoring real-time activity.",
        "refresh_now": "Manually reload the current log file",
        "clear_logs": "Delete all log files.\n⚠️ This action cannot be undone! Use for troubleshooting or to free disk space.",
        "export_logs": "Save current log view to a text file.\nUseful for bug reports or sharing with support.",
    }

    # ==================== COMMON UI ELEMENTS ====================

    COMMON = {
        "ok_button": "Save changes and close this dialog",
        "cancel_button": "Discard changes and close this dialog (Esc)",
        "save_button": "Save changes to database",
        "delete_button": "Remove this item permanently (requires confirmation)",
        "close_button": "Close this window",
        "help_button": "Show help and documentation",
        "search_field": "Type to search and filter results",
        "date_picker": "Click the calendar icon to choose a date",
        "dropdown": "Click to see available options",
    }

    # ==================== VALIDATION MESSAGES ====================

    VALIDATION = {
        "required_field": "This field is required",
        "invalid_number": "Please enter a valid number",
        "positive_number": "Value must be greater than zero",
        "invalid_date": "Please select a valid date",
        "invalid_ticker": "Please enter a valid ticker symbol",
        "empty_selection": "Please select an option",
    }

    # ==================== SUCCESS MESSAGES ====================

    SUCCESS = {
        "transaction_added": "Transaction added successfully! ✅",
        "transaction_updated": "Transaction updated successfully! ✅",
        "transaction_deleted": "Transaction deleted successfully! ✅",
        "asset_added": "Asset added to portfolio! ✅",
        "asset_updated": "Asset updated successfully! ✅",
        "asset_deleted": "Asset removed from portfolio! ✅",
        "order_added": "Order created successfully! ✅",
        "order_updated": "Order updated successfully! ✅",
        "order_deleted": "Order deleted successfully! ✅",
        "prices_refreshed": "Prices updated successfully! ✅",
        "data_exported": "Data exported successfully! ✅",
        "logs_cleared": "Logs cleared successfully! ✅",
    }

    # ==================== ERROR MESSAGES ====================

    ERRORS = {
        "database_error": "Database error occurred. Please check logs for details.",
        "api_error": "Failed to fetch data from API. Please check your internet connection.",
        "validation_error": "Please fix the highlighted fields and try again.",
        "file_error": "Failed to read or write file. Check permissions and disk space.",
        "price_fetch_failed": "Could not fetch current price. The ticker might be invalid or API is unavailable.",
        "export_failed": "Export failed. Please check file path and permissions.",
    }

    # ==================== INFO MESSAGES ====================

    INFO = {
        "no_data": "No data to display yet. Add some transactions or assets to get started!",
        "loading": "Loading data, please wait...",
        "fetching_prices": "Fetching latest prices from market data providers...",
        "calculating": "Calculating portfolio metrics...",
        "empty_chart": "Not enough data to generate this chart. Add more transactions or assets!",
        "cache_used": "Using cached price data (less than 5 minutes old)",
    }

    # ==================== KEYBOARD SHORTCUTS ====================

    SHORTCUTS = {
        "new": "Cmd+N - New Transaction",
        "refresh": "Cmd+R - Refresh Prices",
        "export": "Cmd+E - Export Data",
        "theme": "Cmd+T - Toggle Theme",
        "logs": "Cmd+L - View Logs",
        "quit": "Cmd+Q - Quit Application",
        "save": "Cmd+S - Save",
        "close": "Esc - Close Dialog",
    }


def get_tooltip(category: str, key: str) -> str:
    """
    Get a tooltip text by category and key.

    Args:
        category: Category name (e.g., "PERSONAL_TAB", "ASSET_FORM")
        key: Specific tooltip key

    Returns:
        Tooltip text or empty string if not found
    """
    tooltips_dict = getattr(Tooltips, category, {})
    return tooltips_dict.get(key, "")


def apply_tooltip(widget, category: str, key: str):
    """
    Apply a tooltip to a widget.

    Args:
        widget: PyQt6 widget
        category: Tooltip category
        key: Tooltip key
    """
    tooltip = get_tooltip(category, key)
    if tooltip:
        widget.setToolTip(tooltip)


def get_help_text(section: str) -> str:
    """
    Get comprehensive help text for a section.

    Args:
        section: Section name

    Returns:
        Help text
    """
    help_texts = {
        "personal_finances": """
<h3>Personal Finances Tab</h3>
<p>Track your income and expenses to understand your financial health.</p>

<h4>How to Add a Transaction:</h4>
<ol>
<li>Click the <b>"+ Transaction"</b> button</li>
<li>Enter the date, amount, and category</li>
<li>Use positive numbers for income, negative for expenses</li>
<li>Add an optional description</li>
<li>Click <b>OK</b> to save</li>
</ol>

<h4>Understanding Your Balance:</h4>
<ul>
<li><b>Balance:</b> Total Income - Total Expenses</li>
<li><b>Income:</b> All positive transactions</li>
<li><b>Expenses:</b> All negative transactions</li>
</ul>

<h4>Tips:</h4>
<ul>
<li>Use consistent categories for better reports</li>
<li>Add descriptions to remember transaction details</li>
<li>Review your spending regularly</li>
</ul>
        """,
        "investments": """
<h3>Investments Tab</h3>
<p>Manage your investment portfolio with real-time price tracking.</p>

<h4>How to Add an Asset:</h4>
<ol>
<li>Click the <b>"+ Asset"</b> button</li>
<li>Type ticker symbol or company name (autocomplete helps!)</li>
<li>Enter quantity and purchase price</li>
<li>Select purchase date</li>
<li>Click <b>"Fetch Current Price"</b> to verify ticker</li>
<li>Click <b>OK</b> to save</li>
</ol>

<h4>Refreshing Prices:</h4>
<p>Click <b>"Refresh Prices"</b> to update all asset prices from:</p>
<ul>
<li><b>CoinGecko</b> for cryptocurrencies</li>
<li><b>Yahoo Finance</b> for stocks</li>
</ul>

<h4>Understanding Metrics:</h4>
<ul>
<li><b>Portfolio Value:</b> Current total worth of all assets</li>
<li><b>Total Invested:</b> How much money you put in</li>
<li><b>Gain/Loss:</b> Your profit or loss (green = winning!)</li>
<li><b>Gain %:</b> Percentage return on investment</li>
</ul>
        """,
        "reports": """
<h3>Reports Tab</h3>
<p>Visualize your financial data with interactive charts.</p>

<h4>Available Charts:</h4>
<ul>
<li><b>Balance Evolution:</b> Track balance over time</li>
<li><b>Spending by Category:</b> See where money goes</li>
<li><b>Portfolio Value:</b> Investment growth tracking</li>
<li><b>Asset Allocation:</b> Portfolio diversification</li>
</ul>

<h4>Using Date Filters:</h4>
<p>Select a time period to focus your analysis:</p>
<ul>
<li>Quick options: Last 7/30/90 days, 6 months, 1 year</li>
<li>Custom: Choose exact date range</li>
<li>All charts update automatically</li>
</ul>

<h4>Exporting Data:</h4>
<p>Click export buttons to save data as CSV files for:</p>
<ul>
<li>Excel analysis</li>
<li>Backup purposes</li>
<li>Tax preparation</li>
<li>Sharing with accountant</li>
</ul>
        """,
        "orders": """
<h3>Order Book Tab</h3>
<p>Track your trading orders and execution history.</p>

<h4>How to Add an Order:</h4>
<ol>
<li>Click the <b>"+ Order"</b> button</li>
<li>Enter ticker symbol (BTC, ETH, MC.PA, etc.)</li>
<li>Choose Buy or Sell</li>
<li>Enter quantity and target price</li>
<li>Set status (Open or Closed)</li>
<li>Click <b>OK</b> to save</li>
</ol>

<h4>Order Status:</h4>
<ul>
<li><b>Open:</b> Active order, not yet executed</li>
<li><b>Closed:</b> Completed or cancelled</li>
</ul>

<h4>Filtering Orders:</h4>
<p>Use filter buttons to view:</p>
<ul>
<li>All orders</li>
<li>Only open orders</li>
<li>Only closed orders</li>
</ul>

<h4>Batch Operations:</h4>
<ul>
<li><b>Close All Open:</b> Mark all open orders as closed</li>
<li><b>Delete All Closed:</b> Clean up completed orders</li>
</ul>
        """,
    }
    return help_texts.get(section, "")


# Placeholder/example text for forms
EXAMPLES = {
    "transaction_amount": "e.g., 2500 or -45.50",
    "transaction_category": "e.g., Salary, Food, Rent",
    "transaction_description": "e.g., Monthly salary from Acme Corp",
    "asset_ticker": "Start typing: BTC, ETH, MC.PA, AIR.PA...",
    "asset_quantity": "e.g., 0.5 BTC or 10 shares",
    "asset_buy_price": "e.g., 35000",
    "order_ticker": "e.g., BTC, ETH, SOL, MC.PA",
    "order_quantity": "e.g., 0.1 or 50",
    "order_price": "e.g., 30000",
}
