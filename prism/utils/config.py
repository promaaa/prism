"""
Configuration module for Prism application.
Centralizes all application settings, performance parameters, and configurable options.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database-related configuration."""

    # Connection settings
    connection_timeout: float = 30.0
    max_connections: int = 5

    # Query optimization
    default_page_size: int = 50
    max_page_size: int = 1000

    # Performance settings
    enable_query_logging: bool = False
    enable_performance_monitoring: bool = True


@dataclass
class APIConfig:
    """API-related configuration."""

    # Timeout settings
    request_timeout: float = 30.0
    async_request_timeout: float = 15.0

    # Retry settings
    max_retries: int = 3
    retry_backoff_factor: float = 0.5

    # Rate limiting
    requests_per_minute: int = 50

    # Batch processing
    max_batch_size: int = 100
    concurrent_requests: int = 5

    # Cache settings
    cache_timeout: int = 300  # 5 minutes
    max_cache_size: int = 1000


@dataclass
class UIConfig:
    """UI-related configuration."""

    # Pagination settings
    personal_transactions_page_size: int = 100
    investments_page_size: int = 50
    orders_page_size: int = 50

    # Available page sizes
    page_size_options: list = field(default_factory=lambda: [25, 50, 100, 200, 500])

    # Chart settings
    chart_cache_timeout: int = 300  # 5 minutes
    max_chart_cache_size: int = 50

    # Loading indicators
    show_loading_animations: bool = True
    loading_animation_duration: int = 200  # milliseconds


@dataclass
class PerformanceConfig:
    """Performance-related configuration."""

    # Thread pool settings
    max_workers: int = 4
    thread_pool_timeout: float = 30.0

    # Memory management
    max_memory_cache_mb: int = 100
    cleanup_interval_seconds: int = 300

    # Async processing
    enable_async_processing: bool = True
    max_concurrent_operations: int = 3


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_console_logging: bool = True
    enable_file_logging: bool = True

    # Performance logging
    enable_performance_logging: bool = False
    slow_query_threshold_ms: int = 100


@dataclass
class ApplicationConfig:
    """Main application configuration."""

    # Application info
    name: str = "Prism"
    version: str = "1.2.0"
    organization: str = "Prism"

    # Paths
    data_dir: Optional[Path] = None
    log_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None

    # Feature flags
    enable_beta_features: bool = False
    enable_debug_mode: bool = False

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """Configuration manager with environment variable and file support."""

    def __init__(self):
        self._config = ApplicationConfig()
        self._load_from_environment()
        self._setup_paths()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Database settings
        self._config.database.connection_timeout = float(
            os.getenv("PRISM_DB_TIMEOUT", self._config.database.connection_timeout)
        )
        self._config.database.max_connections = int(
            os.getenv("PRISM_DB_MAX_CONNECTIONS", self._config.database.max_connections)
        )

        # API settings
        self._config.api.request_timeout = float(
            os.getenv("PRISM_API_TIMEOUT", self._config.api.request_timeout)
        )
        self._config.api.max_retries = int(
            os.getenv("PRISM_API_MAX_RETRIES", self._config.api.max_retries)
        )
        self._config.api.concurrent_requests = int(
            os.getenv(
                "PRISM_API_CONCURRENT_REQUESTS", self._config.api.concurrent_requests
            )
        )

        # UI settings
        self._config.ui.personal_transactions_page_size = int(
            os.getenv(
                "PRISM_UI_TRANSACTIONS_PAGE_SIZE",
                self._config.ui.personal_transactions_page_size,
            )
        )
        self._config.ui.investments_page_size = int(
            os.getenv(
                "PRISM_UI_INVESTMENTS_PAGE_SIZE", self._config.ui.investments_page_size
            )
        )

        # Performance settings
        self._config.performance.max_workers = int(
            os.getenv("PRISM_MAX_WORKERS", self._config.performance.max_workers)
        )
        self._config.performance.enable_async_processing = (
            os.getenv("PRISM_ENABLE_ASYNC", "true").lower() == "true"
        )

        # Logging settings
        self._config.logging.level = os.getenv(
            "PRISM_LOG_LEVEL", self._config.logging.level
        ).upper()
        self._config.logging.enable_performance_logging = (
            os.getenv("PRISM_PERFORMANCE_LOGGING", "false").lower() == "true"
        )

        # Debug mode
        self._config.enable_debug_mode = (
            os.getenv("PRISM_DEBUG", "false").lower() == "true"
        )

    def _setup_paths(self):
        """Set up application paths."""
        # Use XDG Base Directory specification if available
        data_home = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        cache_home = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

        # Application-specific directories
        app_data_dir = Path(data_home) / self._config.name.lower()
        app_cache_dir = Path(cache_home) / self._config.name.lower()
        app_config_dir = Path(config_home) / self._config.name.lower()

        # Create directories if they don't exist
        app_data_dir.mkdir(parents=True, exist_ok=True)
        app_cache_dir.mkdir(parents=True, exist_ok=True)
        app_config_dir.mkdir(parents=True, exist_ok=True)

        self._config.data_dir = app_data_dir
        self._config.cache_dir = app_cache_dir
        self._config.log_dir = app_data_dir / "logs"
        self._config.log_dir.mkdir(exist_ok=True)

    @property
    def config(self) -> ApplicationConfig:
        """Get the current configuration."""
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated key."""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = getattr(value, k)
            return value
        except AttributeError:
            return default

    def set(self, key: str, value: Any):
        """Set a configuration value by dot-separated key."""
        keys = key.split(".")
        obj = self._config

        # Navigate to the parent object
        for k in keys[:-1]:
            obj = getattr(obj, k)

        # Set the final attribute
        setattr(obj, keys[-1], value)

    def reload(self):
        """Reload configuration from environment and files."""
        self._load_from_environment()
        self._setup_paths()


# Global configuration instance
config_manager = ConfigManager()
config = config_manager.config


def get_config() -> ApplicationConfig:
    """Get the global configuration instance."""
    return config


def get_setting(key: str, default: Any = None) -> Any:
    """Get a configuration setting by key."""
    return config_manager.get(key, default)


def set_setting(key: str, value: Any):
    """Set a configuration setting by key."""
    config_manager.set(key, value)


# Convenience functions for common settings
def get_db_page_size() -> int:
    """Get default database page size."""
    return config.database.default_page_size


def get_api_timeout() -> float:
    """Get API request timeout."""
    return config.api.request_timeout


def get_ui_page_size(tab_name: str) -> int:
    """Get UI page size for a specific tab."""
    if tab_name == "personal":
        return config.ui.personal_transactions_page_size
    elif tab_name == "investments":
        return config.ui.investments_page_size
    elif tab_name == "orders":
        return config.ui.orders_page_size
    else:
        return config.database.default_page_size


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return config.enable_debug_mode


def is_async_enabled() -> bool:
    """Check if async processing is enabled."""
    return config.performance.enable_async_processing
