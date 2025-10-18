"""
Centralized logging system for Prism application.

This module provides a comprehensive logging infrastructure with:
- File-based logging with rotation
- Console logging for development
- Custom formatters for readability
- Log level management
- Performance tracking
- Error context capture
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import traceback
import functools
import time


# Log directory setup
LOG_DIR = Path.home() / ".prism" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log files
MAIN_LOG_FILE = LOG_DIR / "prism.log"
ERROR_LOG_FILE = LOG_DIR / "prism_errors.log"
PERFORMANCE_LOG_FILE = LOG_DIR / "prism_performance.log"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset_color = self.COLORS["RESET"]

        # Color the level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"

        return super().format(record)


class PrismLogger:
    """Main logger class for the Prism application."""

    _instance: Optional["PrismLogger"] = None
    _initialized: bool = False

    def __new__(cls):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger (only once)."""
        if self._initialized:
            return

        self._initialized = True
        self._setup_loggers()

    def _setup_loggers(self):
        """Set up all loggers with appropriate handlers and formatters."""

        # Main application logger
        self.logger = logging.getLogger("prism")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Clear any existing handlers
        self.logger.handlers.clear()

        # File handler for all logs (with rotation)
        file_handler = logging.handlers.RotatingFileHandler(
            MAIN_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # File handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Performance logger
        self.perf_logger = logging.getLogger("prism.performance")
        self.perf_logger.setLevel(logging.DEBUG)
        self.perf_logger.propagate = False

        perf_handler = logging.handlers.RotatingFileHandler(
            PERFORMANCE_LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=2,
            encoding="utf-8",
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_formatter = logging.Formatter(
            "%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        perf_handler.setFormatter(perf_formatter)
        self.perf_logger.addHandler(perf_handler)

        # Log initialization
        self.logger.info("=" * 80)
        self.logger.info("Prism Application Started")
        self.logger.info(f"Log directory: {LOG_DIR}")
        self.logger.info("=" * 80)

    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Optional name for the logger. If None, returns main logger.

        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"prism.{name}")
        return self.logger

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error message with exception info."""
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """Log critical message with exception info."""
        self.logger.critical(message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with full traceback."""
        self.logger.exception(message, **kwargs)

    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        Log performance metrics.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional context
        """
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        msg = f"{operation} | Duration: {duration:.3f}s"
        if context:
            msg += f" | {context}"
        self.perf_logger.info(msg)

    def set_level(self, level: str):
        """
        Set logging level.

        Args:
            level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        log_level = level_map.get(level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        self.logger.info(f"Log level set to {level.upper()}")

    def get_log_files(self) -> dict:
        """
        Get paths to all log files.

        Returns:
            Dictionary with log file types and paths
        """
        return {
            "main": MAIN_LOG_FILE,
            "errors": ERROR_LOG_FILE,
            "performance": PERFORMANCE_LOG_FILE,
        }

    def clear_logs(self):
        """Clear all log files (use with caution)."""
        try:
            for log_file in [MAIN_LOG_FILE, ERROR_LOG_FILE, PERFORMANCE_LOG_FILE]:
                if log_file.exists():
                    log_file.unlink()
            self._setup_loggers()
            self.logger.info("All log files cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear log files: {e}")


# Global logger instance
_logger_instance = PrismLogger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Optional name for the logger

    Returns:
        Logger instance
    """
    return _logger_instance.get_logger(name)


def log_exception(func):
    """
    Decorator to automatically log exceptions in functions.

    Usage:
        @log_exception
        def my_function():
            # function code
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise

    return wrapper


def log_performance(operation_name: str = None):
    """
    Decorator to automatically log function performance.

    Usage:
        @log_performance("Database Query")
        def my_function():
            # function code
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                _logger_instance.log_performance(op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                _logger_instance.log_performance(
                    op_name, duration, status="FAILED", error=str(e)
                )
                raise

        return wrapper

    return decorator


def log_method_call(func):
    """
    Decorator to log method calls with arguments.

    Usage:
        @log_method_call
        def my_method(self, arg1, arg2):
            # method code
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        # Get class name if method
        class_name = ""
        if args and hasattr(args[0], "__class__"):
            class_name = f"{args[0].__class__.__name__}."

        # Format arguments (skip 'self')
        args_repr = [repr(a) for a in args[1:]]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.debug(f"Calling {class_name}{func.__name__}({signature})")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{class_name}{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{class_name}{func.__name__} failed: {str(e)}")
            raise

    return wrapper


class LogContext:
    """Context manager for logging blocks of code."""

    def __init__(self, operation: str, logger_name: str = None):
        """
        Initialize log context.

        Args:
            operation: Name of the operation
            logger_name: Optional logger name
        """
        self.operation = operation
        self.logger = get_logger(logger_name)
        self.start_time = None

    def __enter__(self):
        """Enter context."""
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        duration = time.time() - self.start_time

        if exc_type is None:
            self.logger.debug(f"Completed: {self.operation} (took {duration:.3f}s)")
            _logger_instance.log_performance(self.operation, duration)
        else:
            self.logger.error(
                f"Failed: {self.operation} (took {duration:.3f}s) - {exc_val}"
            )
            _logger_instance.log_performance(
                self.operation, duration, status="FAILED", error=str(exc_val)
            )

        # Don't suppress exceptions
        return False


# Convenience functions
def debug(message: str, **kwargs):
    """Log debug message."""
    _logger_instance.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    _logger_instance.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    _logger_instance.warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message."""
    _logger_instance.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    _logger_instance.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """Log exception with traceback."""
    _logger_instance.exception(message, **kwargs)


def set_log_level(level: str):
    """Set global log level."""
    _logger_instance.set_level(level)


def get_log_files() -> dict:
    """Get paths to all log files."""
    return _logger_instance.get_log_files()


def clear_logs():
    """Clear all log files."""
    _logger_instance.clear_logs()
