"""
Performance monitoring module for Prism application.
Provides decorators, utilities, and collectors for tracking application performance.
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
import tracemalloc
from contextlib import contextmanager

from .logger import get_logger
from .config import get_config


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    memory_start_mb: Optional[float] = None
    memory_end_mb: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self):
        """Mark the operation as complete and calculate final metrics."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        # Memory usage
        process = psutil.Process()
        self.memory_end_mb = process.memory_info().rss / 1024 / 1024
        if self.memory_start_mb is not None:
            self.memory_delta_mb = self.memory_end_mb - self.memory_start_mb

        # CPU usage (over the duration)
        try:
            self.cpu_percent = process.cpu_percent(interval=None)
        except:
            pass

        # Thread and process info
        self.thread_id = threading.get_ident()
        self.process_id = process.pid


class PerformanceMonitor:
    """Central performance monitoring system."""

    def __init__(self):
        self.logger = get_logger("performance")
        self.config = get_config()
        self._metrics: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
        self._enabled = self.config.logging.enable_performance_logging
        self._slow_threshold_ms = self.config.logging.slow_query_threshold_ms

        # Memory tracing
        if self._enabled:
            tracemalloc.start()

    def is_enabled(self) -> bool:
        """Check if performance monitoring is enabled."""
        return self._enabled

    def enable(self):
        """Enable performance monitoring."""
        self._enabled = True
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    def disable(self):
        """Disable performance monitoring."""
        self._enabled = False
        if tracemalloc.is_tracing():
            tracemalloc.stop()

    def start_operation(self, operation: str, **metadata) -> PerformanceMetrics:
        """Start tracking a performance operation."""
        if not self._enabled:
            return PerformanceMetrics(operation=operation)

        metrics = PerformanceMetrics(
            operation=operation, start_time=time.time(), metadata=metadata
        )

        # Memory usage at start
        try:
            process = psutil.Process()
            metrics.memory_start_mb = process.memory_info().rss / 1024 / 1024
        except:
            pass

        return metrics

    def end_operation(self, metrics: PerformanceMetrics):
        """End tracking a performance operation."""
        if not self._enabled or not metrics.start_time:
            return

        metrics.complete()

        # Store metrics
        with self._lock:
            self._metrics.append(metrics)

        # Log if it's a slow operation
        if metrics.duration_ms and metrics.duration_ms > self._slow_threshold_ms:
            self.logger.warning(
                f"SLOW OPERATION: {metrics.operation} took {metrics.duration_ms:.2f}ms",
                extra={
                    "operation": metrics.operation,
                    "duration_ms": metrics.duration_ms,
                    "memory_delta_mb": metrics.memory_delta_mb,
                    "metadata": metrics.metadata,
                },
            )
        elif self.config.logging.level == "DEBUG":
            self.logger.debug(
                f"OPERATION: {metrics.operation} took {metrics.duration_ms:.2f}ms",
                extra={
                    "operation": metrics.operation,
                    "duration_ms": metrics.duration_ms,
                    "memory_delta_mb": metrics.memory_delta_mb,
                },
            )

    def get_recent_metrics(self, limit: int = 100) -> List[PerformanceMetrics]:
        """Get recent performance metrics."""
        with self._lock:
            return self._metrics[-limit:] if limit > 0 else self._metrics.copy()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        with self._lock:
            if not self._metrics:
                return {"total_operations": 0}

            operations = [m.operation for m in self._metrics]
            durations = [m.duration_ms for m in self._metrics if m.duration_ms]

            return {
                "total_operations": len(self._metrics),
                "unique_operations": len(set(operations)),
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "slow_operations": sum(
                    1
                    for m in self._metrics
                    if m.duration_ms and m.duration_ms > self._slow_threshold_ms
                ),
            }

    def clear_metrics(self):
        """Clear stored metrics."""
        with self._lock:
            self._metrics.clear()

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {}

    def get_system_info(self) -> Dict[str, Any]:
        """Get system performance information."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "active_threads": threading.active_count(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor


# Decorators for performance monitoring


def monitor_performance(operation: Optional[str] = None, **metadata):
    """
    Decorator to monitor function performance.

    Args:
        operation: Optional operation name (defaults to function name)
        **metadata: Additional metadata to store with metrics
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            if not monitor.is_enabled():
                return func(*args, **kwargs)

            op_name = operation or f"{func.__module__}.{func.__qualname__}"
            metrics = monitor.start_operation(op_name, **metadata)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.end_operation(metrics)

        return wrapper

    return decorator


def monitor_async_performance(operation: Optional[str] = None, **metadata):
    """
    Decorator to monitor async function performance.

    Args:
        operation: Optional operation name (defaults to function name)
        **metadata: Additional metadata to store with metrics
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            if not monitor.is_enabled():
                return await func(*args, **kwargs)

            op_name = operation or f"{func.__module__}.{func.__qualname__}"
            metrics = monitor.start_operation(op_name, **metadata)

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                monitor.end_operation(metrics)

        return wrapper

    return decorator


@contextmanager
def performance_context(operation: str, **metadata):
    """
    Context manager for monitoring performance blocks.

    Args:
        operation: Operation name
        **metadata: Additional metadata to store with metrics
    """
    monitor = get_performance_monitor()
    metrics = monitor.start_operation(operation, **metadata)

    try:
        yield metrics
    finally:
        monitor.end_operation(metrics)


# Convenience functions


def log_performance_summary():
    """Log a summary of recent performance metrics."""
    monitor = get_performance_monitor()
    summary = monitor.get_metrics_summary()

    monitor.logger.info(
        "Performance Summary",
        extra={
            "total_operations": summary.get("total_operations", 0),
            "avg_duration_ms": summary.get("avg_duration_ms", 0),
            "max_duration_ms": summary.get("max_duration_ms", 0),
            "slow_operations": summary.get("slow_operations", 0),
        },
    )


def get_memory_snapshot() -> Dict[str, Any]:
    """Get a memory usage snapshot using tracemalloc."""
    monitor = get_performance_monitor()
    if not monitor.is_enabled() or not tracemalloc.is_tracing():
        return {}

    try:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")

        return {
            "total_blocks": len(top_stats),
            "top_10_allocations": [
                {
                    "size_mb": stat.size / 1024 / 1024,
                    "count": stat.count,
                    "file": stat.traceback[0].filename if stat.traceback else "unknown",
                    "line": stat.traceback[0].lineno if stat.traceback else 0,
                }
                for stat in top_stats[:10]
            ],
        }
    except Exception as e:
        monitor.logger.error(f"Failed to get memory snapshot: {e}")
        return {}


# Database-specific monitoring


def monitor_db_query(query_type: str = "query"):
    """Decorator for monitoring database queries."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return monitor_performance(
                f"db_{query_type}",
                query_type=query_type,
                table=getattr(
                    args[0] if args else None, "__class__.__name__", "unknown"
                ),
            )(func)(*args, **kwargs)

        return wrapper

    return decorator


# API-specific monitoring


def monitor_api_call(api_name: str, method: str = "GET"):
    """Decorator for monitoring API calls."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return monitor_performance(
                f"api_{api_name}", api_name=api_name, method=method
            )(func)(*args, **kwargs)

        return wrapper

    return decorator


# UI-specific monitoring


def monitor_ui_operation(operation: str):
    """Decorator for monitoring UI operations."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return monitor_performance(f"ui_{operation}", ui_operation=operation)(func)(
                *args, **kwargs
            )

        return wrapper

    return decorator


# Initialization


def init_performance_monitoring():
    """Initialize performance monitoring based on configuration."""
    config = get_config()
    monitor = get_performance_monitor()

    if config.logging.enable_performance_logging:
        monitor.enable()
        monitor.logger.info("Performance monitoring enabled")
    else:
        monitor.disable()


# Auto-initialize on import
init_performance_monitoring()
