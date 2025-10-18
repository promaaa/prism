"""
Help dialog for Prism application.

Provides context-sensitive help and tutorials for each section of the app.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QListWidget,
    QSplitter,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from .tooltips import get_help_text, Tooltips


class HelpDialog(QDialog):
    """Context-sensitive help dialog."""

    def __init__(self, section: str = "welcome", parent=None):
        """
        Initialize help dialog.

        Args:
            section: Initial section to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Prism Help")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        self._init_ui()
        self._load_section(section)

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar with navigation
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self._populate_sidebar()
        self.sidebar.currentItemChanged.connect(self._on_section_changed)
        splitter.addWidget(self.sidebar)

        # Content area
        self.content = QTextBrowser()
        self.content.setOpenExternalLinks(True)
        splitter.addWidget(self.content)

        # Set splitter sizes (sidebar smaller than content)
        splitter.setSizes([250, 750])

        layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(15, 10, 15, 15)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Apply styling
        self._apply_styling()

    def _populate_sidebar(self):
        """Populate sidebar with help sections."""
        sections = [
            ("🏠 Welcome", "welcome"),
            ("💰 Personal Finances", "personal_finances"),
            ("📈 Investments", "investments"),
            ("📊 Reports", "reports"),
            ("📋 Order Book", "orders"),
            ("🔍 Log Viewer", "logs"),
            ("⚙️ Settings & Tips", "settings"),
            ("⌨️ Keyboard Shortcuts", "shortcuts"),
            ("❓ FAQ", "faq"),
        ]

        for title, section_id in sections:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, section_id)
            self.sidebar.addItem(item)

        # Select first item by default
        self.sidebar.setCurrentRow(0)

    def _apply_styling(self):
        """Apply custom styling to dialog."""
        self.sidebar.setStyleSheet(
            """
            QListWidget {
                background-color: #f5f5f5;
                border: none;
                font-size: 13px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
        """
        )

        self.content.setStyleSheet(
            """
            QTextBrowser {
                border: none;
                padding: 20px;
                font-size: 13px;
                line-height: 1.6;
            }
        """
        )

    def _on_section_changed(self, current, previous):
        """Handle section change."""
        if current:
            section_id = current.data(Qt.ItemDataRole.UserRole)
            self._load_section(section_id)

    def _load_section(self, section: str):
        """
        Load help content for a section.

        Args:
            section: Section identifier
        """
        content = self._get_section_content(section)
        self.content.setHtml(content)

        # Set sidebar selection
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == section:
                self.sidebar.setCurrentItem(item)
                break

    def _get_section_content(self, section: str) -> str:
        """
        Get HTML content for a section.

        Args:
            section: Section identifier

        Returns:
            HTML content string
        """
        # Base CSS for all sections
        css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                line-height: 1.7;
                color: #333;
            }
            h1 {
                color: #2196F3;
                border-bottom: 3px solid #2196F3;
                padding-bottom: 10px;
                margin-top: 0;
            }
            h2 {
                color: #1976D2;
                margin-top: 25px;
            }
            h3 {
                color: #0D47A1;
                margin-top: 20px;
            }
            code {
                background-color: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: "Monaco", "Courier New", monospace;
                font-size: 12px;
            }
            .tip {
                background-color: #E3F2FD;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            .warning {
                background-color: #FFF3E0;
                border-left: 4px solid #FF9800;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            .success {
                background-color: #E8F5E9;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            ul {
                line-height: 1.8;
            }
            ol {
                line-height: 1.8;
            }
            kbd {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 6px;
                font-family: monospace;
                font-size: 11px;
            }
        </style>
        """

        if section == "welcome":
            return (
                css
                + """
            <h1>Welcome to Prism! 🌟</h1>

            <p>Prism is your personal finance and investment management application, designed to help you track your money with ease and clarity.</p>

            <h2>What Can You Do?</h2>

            <div class="success">
                <h3>💰 Personal Finances</h3>
                <p>Track your income and expenses, categorize transactions, and see your balance at a glance.</p>
            </div>

            <div class="success">
                <h3>📈 Investments</h3>
                <p>Manage your portfolio of stocks and cryptocurrencies with real-time price updates from CoinGecko and Yahoo Finance.</p>
            </div>

            <div class="success">
                <h3>📊 Reports</h3>
                <p>Visualize your financial data with interactive charts and export to CSV for further analysis.</p>
            </div>

            <div class="success">
                <h3>📋 Order Book</h3>
                <p>Track your buy/sell orders and trading history in one organized place.</p>
            </div>

            <h2>Getting Started</h2>

            <ol>
                <li><b>Add Your First Transaction:</b> Click <code>+ Transaction</code> to record income or expenses</li>
                <li><b>Build Your Portfolio:</b> Click <code>+ Asset</code> to add investments (CAC 40 stocks or top cryptocurrencies)</li>
                <li><b>View Reports:</b> Navigate to the Reports tab to see charts and analytics</li>
                <li><b>Explore Features:</b> Hover over buttons for helpful tooltips!</li>
            </ol>

            <div class="tip">
                <b>💡 Pro Tip:</b> Start by adding a few transactions to see how the balance updates automatically. Then add some investments and click "Refresh Prices" to see live market data!
            </div>

            <h2>Key Features</h2>

            <ul>
                <li>✅ <b>Local Storage:</b> All data stored on your Mac (SQLite database)</li>
                <li>✅ <b>Real-Time Prices:</b> Live crypto & stock prices</li>
                <li>✅ <b>Smart Autocomplete:</b> 141 tickers (40 CAC 40 + 101 crypto)</li>
                <li>✅ <b>Interactive Charts:</b> Plotly-powered visualizations</li>
                <li>✅ <b>CSV Export:</b> Export data for Excel/Numbers</li>
                <li>✅ <b>Dark Mode:</b> Toggle theme with <kbd>Cmd+T</kbd></li>
                <li>✅ <b>Comprehensive Logging:</b> View logs with <kbd>Cmd+L</kbd></li>
            </ul>

            <h2>Navigation Tips</h2>

            <p>Use the sidebar on the left to explore different help topics, or use these keyboard shortcuts:</p>

            <ul>
                <li><kbd>Cmd+N</kbd> - New Transaction</li>
                <li><kbd>Cmd+R</kbd> - Refresh Prices</li>
                <li><kbd>Cmd+E</kbd> - Export Data</li>
                <li><kbd>Cmd+T</kbd> - Toggle Theme</li>
                <li><kbd>Cmd+L</kbd> - View Logs</li>
                <li><kbd>Cmd+Q</kbd> - Quit</li>
            </ul>

            <div class="tip">
                <b>Need More Help?</b> Select a topic from the sidebar to learn about specific features, or check the FAQ section for common questions.
            </div>
            """
            )

        elif section == "personal_finances":
            return css + get_help_text("personal_finances")

        elif section == "investments":
            return css + get_help_text("investments")

        elif section == "reports":
            return css + get_help_text("reports")

        elif section == "orders":
            return css + get_help_text("orders")

        elif section == "logs":
            return (
                css
                + """
            <h1>Log Viewer 🔍</h1>

            <p>The log viewer helps you monitor application activity and troubleshoot issues.</p>

            <h2>Opening the Log Viewer</h2>
            <ul>
                <li>Menu: <b>View → View Logs</b></li>
                <li>Keyboard: <kbd>Cmd+L</kbd></li>
                <li>Toolbar: Click <b>View Logs</b> button</li>
            </ul>

            <h2>Available Log Files</h2>

            <h3>Main Log</h3>
            <p>Contains all application events including:</p>
            <ul>
                <li>Database operations</li>
                <li>API calls and responses</li>
                <li>UI interactions</li>
                <li>Performance timing</li>
            </ul>

            <h3>Errors Only</h3>
            <p>Filtered view showing only ERROR and CRITICAL messages. Useful for troubleshooting problems.</p>

            <h3>Performance</h3>
            <p>Dedicated log for operation timing. Shows how long each operation takes.</p>

            <h2>Using Filters</h2>

            <h3>Log Level Filter</h3>
            <ul>
                <li><b>DEBUG</b> (Cyan) - Detailed diagnostic info</li>
                <li><b>INFO</b> (Green) - General events</li>
                <li><b>WARNING</b> (Orange) - Potential issues</li>
                <li><b>ERROR</b> (Red) - Operation failures</li>
                <li><b>CRITICAL</b> (Pink) - Severe problems</li>
            </ul>

            <h3>Search</h3>
            <p>Enter text to search logs. Search is case-insensitive and highlights matches in yellow.</p>

            <h2>Common Tasks</h2>

            <h3>Debugging Price Fetch Issues</h3>
            <ol>
                <li>Open log viewer (<kbd>Cmd+L</kbd>)</li>
                <li>Select "Main Log"</li>
                <li>Set filter to "ERROR"</li>
                <li>Search for the ticker (e.g., "BTC")</li>
                <li>Review error messages</li>
            </ol>

            <h3>Checking Performance</h3>
            <ol>
                <li>Select "Performance" log</li>
                <li>Look for operations with long duration</li>
                <li>Identify slow operations for optimization</li>
            </ol>

            <div class="tip">
                <b>💡 Pro Tip:</b> Enable "Auto-Refresh" to monitor logs in real-time while performing operations. Great for debugging!
            </div>

            <h2>Log File Locations</h2>
            <p>Logs are stored in: <code>~/.prism/logs/</code></p>
            <ul>
                <li><code>prism.log</code> - Main log (10 MB, 5 backups)</li>
                <li><code>prism_errors.log</code> - Errors (5 MB, 3 backups)</li>
                <li><code>prism_performance.log</code> - Performance (5 MB, 2 backups)</li>
            </ul>

            <div class="warning">
                <b>⚠️ Clearing Logs:</b> The "Clear Logs" button permanently deletes all log files. This cannot be undone. Use only if you need to free disk space or start fresh.
            </div>
            """
            )

        elif section == "settings":
            return (
                css
                + """
            <h1>Settings & Tips ⚙️</h1>

            <h2>Application Preferences</h2>

            <h3>Theme</h3>
            <p>Toggle between Light and Dark themes:</p>
            <ul>
                <li>Menu: <b>View → Toggle Theme</b></li>
                <li>Keyboard: <kbd>Cmd+T</kbd></li>
                <li>Toolbar: Click <b>Toggle Theme</b></li>
            </ul>
            <p>Theme preference is saved automatically.</p>

            <h3>Database Location</h3>
            <p>Your data is stored in:</p>
            <code>~/Library/Application Support/Prism/prism.db</code>

            <h3>Log Files</h3>
            <p>Application logs are stored in:</p>
            <code>~/.prism/logs/</code>

            <h2>Performance Tips</h2>

            <div class="tip">
                <h3>Price Refresh</h3>
                <p>Prices are cached for 5 minutes. If you refresh too frequently, cached prices are used to avoid API rate limits.</p>
            </div>

            <div class="tip">
                <h3>Large Portfolios</h3>
                <p>If you have many assets (50+), price refreshes may take longer. Be patient and watch the progress bar.</p>
            </div>

            <div class="tip">
                <h3>Chart Performance</h3>
                <p>Charts with thousands of data points may load slowly. Use date filters to focus on specific periods.</p>
            </div>

            <h2>Data Management</h2>

            <h3>Backup Your Data</h3>
            <p>Recommended backup methods:</p>
            <ol>
                <li><b>Database Backup:</b> Copy <code>prism.db</code> to external drive</li>
                <li><b>CSV Exports:</b> Export transactions and assets regularly</li>
                <li><b>Time Machine:</b> Ensure backups are enabled</li>
            </ol>

            <h3>Exporting Data</h3>
            <p>Export your data to CSV files for:</p>
            <ul>
                <li>Excel/Numbers analysis</li>
                <li>Tax preparation</li>
                <li>Sharing with accountant</li>
                <li>Backup purposes</li>
            </ul>

            <h2>Best Practices</h2>

            <div class="success">
                <h3>Consistent Categories</h3>
                <p>Use the same category names for similar transactions. This makes reports more meaningful.</p>
                <p><b>Good:</b> "Food", "Food", "Food"</p>
                <p><b>Bad:</b> "Food", "Groceries", "Eating"</p>
            </div>

            <div class="success">
                <h3>Regular Updates</h3>
                <p>Add transactions weekly or monthly to keep your balance accurate.</p>
            </div>

            <div class="success">
                <h3>Descriptive Notes</h3>
                <p>Add descriptions to remember important transaction details later.</p>
            </div>

            <h2>Troubleshooting</h2>

            <h3>Application Won't Start</h3>
            <ul>
                <li>Check if database file has correct permissions</li>
                <li>View logs: <code>~/.prism/logs/prism.log</code></li>
                <li>Try clearing logs and restarting</li>
            </ul>

            <h3>Prices Not Updating</h3>
            <ul>
                <li>Check internet connection</li>
                <li>Verify ticker symbols are correct</li>
                <li>View error log for API issues</li>
                <li>Try again in a few minutes (API rate limits)</li>
            </ul>

            <h3>Charts Not Displaying</h3>
            <ul>
                <li>Ensure you have transactions/assets in database</li>
                <li>Try selecting different date range</li>
                <li>Check if chart type requires specific data</li>
            </ul>
            """
            )

        elif section == "shortcuts":
            return (
                css
                + """
            <h1>Keyboard Shortcuts ⌨️</h1>

            <p>Speed up your workflow with these keyboard shortcuts.</p>

            <h2>Global Shortcuts</h2>

            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
                <tr style="background-color: #f5f5f5;">
                    <th>Action</th>
                    <th>Shortcut</th>
                </tr>
                <tr>
                    <td>New Transaction</td>
                    <td><kbd>Cmd+N</kbd></td>
                </tr>
                <tr>
                    <td>Refresh Prices</td>
                    <td><kbd>Cmd+R</kbd></td>
                </tr>
                <tr>
                    <td>Export Data</td>
                    <td><kbd>Cmd+E</kbd></td>
                </tr>
                <tr>
                    <td>Toggle Theme</td>
                    <td><kbd>Cmd+T</kbd></td>
                </tr>
                <tr>
                    <td>View Logs</td>
                    <td><kbd>Cmd+L</kbd></td>
                </tr>
                <tr>
                    <td>Quit Application</td>
                    <td><kbd>Cmd+Q</kbd></td>
                </tr>
            </table>

            <h2>Dialog Shortcuts</h2>

            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
                <tr style="background-color: #f5f5f5;">
                    <th>Action</th>
                    <th>Shortcut</th>
                </tr>
                <tr>
                    <td>Save/OK</td>
                    <td><kbd>Enter</kbd> or <kbd>Cmd+S</kbd></td>
                </tr>
                <tr>
                    <td>Cancel/Close</td>
                    <td><kbd>Esc</kbd></td>
                </tr>
            </table>

            <h2>Navigation</h2>

            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 15px 0;">
                <tr style="background-color: #f5f5f5;">
                    <th>Action</th>
                    <th>Shortcut</th>
                </tr>
                <tr>
                    <td>Switch Tabs</td>
                    <td><kbd>Cmd+1</kbd> through <kbd>Cmd+4</kbd></td>
                </tr>
                <tr>
                    <td>Navigate Tables</td>
                    <td><kbd>↑</kbd> <kbd>↓</kbd> Arrow keys</td>
                </tr>
                <tr>
                    <td>Navigate Autocomplete</td>
                    <td><kbd>↑</kbd> <kbd>↓</kbd> then <kbd>Enter</kbd></td>
                </tr>
            </table>

            <div class="tip">
                <b>💡 Pro Tip:</b> Hover over buttons and fields to see tooltips with additional shortcuts and help!
            </div>
            """
            )

        elif section == "faq":
            return (
                css
                + """
            <h1>Frequently Asked Questions ❓</h1>

            <h2>General</h2>

            <h3>Is my data secure?</h3>
            <p>Yes! All your data is stored locally on your Mac in a SQLite database. Nothing is sent to the cloud. The database is located at:</p>
            <code>~/Library/Application Support/Prism/prism.db</code>

            <h3>Can I use this on multiple devices?</h3>
            <p>Currently, Prism is a local application. To use on multiple Macs, you would need to manually copy the database file or use a cloud sync service like Dropbox for the database location.</p>

            <h3>How do I backup my data?</h3>
            <p>Three methods:</p>
            <ol>
                <li><b>Time Machine:</b> Standard macOS backups include Prism data</li>
                <li><b>Database Copy:</b> Manually copy <code>prism.db</code> file</li>
                <li><b>CSV Exports:</b> Export transactions and assets regularly</li>
            </ol>

            <h2>Pricing & APIs</h2>

            <h3>Do I need API keys?</h3>
            <p>No! Prism uses free public APIs:</p>
            <ul>
                <li><b>CoinGecko:</b> Cryptocurrency prices (no key required)</li>
                <li><b>Yahoo Finance:</b> Stock prices via yfinance library (no key required)</li>
            </ul>

            <h3>Why can't I find a specific cryptocurrency?</h3>
            <p>The autocomplete includes the top 100+ cryptocurrencies by market cap. If yours isn't listed, you can still manually enter the ticker symbol. Make sure it's a valid CoinGecko ticker.</p>

            <h3>Why are prices not updating?</h3>
            <p>Possible reasons:</p>
            <ul>
                <li>Cached prices (less than 5 minutes old)</li>
                <li>Internet connection issue</li>
                <li>Invalid ticker symbol</li>
                <li>API rate limit reached (wait a few minutes)</li>
                <li>API service temporarily down</li>
            </ul>
            <p>Check the error log (<kbd>Cmd+L</kbd>) for details.</p>

            <h3>How often are prices updated?</h3>
            <p>Prices are cached for 5 minutes to avoid excessive API calls. When you click "Refresh Prices", any price older than 5 minutes is fetched from the API.</p>

            <h2>Features</h2>

            <h3>Can I import transactions from my bank?</h3>
            <p>CSV import is planned for a future update. For now, you need to add transactions manually.</p>

            <h3>Can I track multiple currencies?</h3>
            <p>Currently, Prism uses EUR (€) as the base currency. Multi-currency support is planned for the future.</p>

            <h3>Can I generate tax reports?</h3>
            <p>Not yet. You can export your data to CSV and use it for tax preparation. Dedicated tax reports are planned for a future release.</p>

            <h3>Can I set budget limits?</h3>
            <p>Budget tracking is not available yet but is planned for a future update.</p>

            <h2>Troubleshooting</h2>

            <h3>The app is slow</h3>
            <p>Possible solutions:</p>
            <ul>
                <li>Close and restart the application</li>
                <li>Clear logs if they're very large (<kbd>Cmd+L</kbd> → Clear Logs)</li>
                <li>Reduce date range in Reports tab</li>
                <li>Check system resources (Activity Monitor)</li>
            </ul>

            <h3>I deleted something by accident</h3>
            <p>Unfortunately, deletions are permanent. There's no undo feature yet. This is why confirmation dialogs are shown for delete operations.</p>
            <p><b>Backup regularly!</b></p>

            <h3>Charts aren't showing</h3>
            <p>Charts require data:</p>
            <ul>
                <li><b>Balance/Category charts:</b> Need transactions</li>
                <li><b>Portfolio charts:</b> Need assets</li>
                <li>Try adjusting date range</li>
                <li>Ensure data exists for selected period</li>
            </ul>

            <h3>Where are the logs stored?</h3>
            <code>~/.prism/logs/</code>
            <p>Three files: main log, errors only, and performance log.</p>

            <h2>About Prism</h2>

            <h3>What does "Prism" mean?</h3>
            <p>A prism splits light into a spectrum of colors, helping you see things more clearly. Similarly, Prism helps you see your finances more clearly by breaking them down into categories, charts, and metrics.</p>

            <h3>Is this open source?</h3>
            <p>Check the LICENSE file in the application directory for licensing information.</p>

            <h3>How can I report bugs or request features?</h3>
            <p>Export your logs (<kbd>Cmd+L</kbd> → Export) and include them with your bug report. Feature requests are welcome!</p>

            <div class="success">
                <h3>Still have questions?</h3>
                <p>Check the sidebar for detailed help on each section, or hover over UI elements for tooltips!</p>
            </div>
            """
            )

        else:
            return (
                css
                + """
            <h1>Section Not Found</h1>
            <p>This help section is under construction. Please select another topic from the sidebar.</p>
            """
            )

    @staticmethod
    def show_help(section: str = "welcome", parent=None):
        """
        Show help dialog for a specific section.

        Args:
            section: Section identifier
            parent: Parent widget
        """
        dialog = HelpDialog(section, parent)
        dialog.exec()
