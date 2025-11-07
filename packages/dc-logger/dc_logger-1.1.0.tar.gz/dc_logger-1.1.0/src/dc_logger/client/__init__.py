"""Client module - Core data models, exceptions, and utilities"""

from .enums import LogLevel
from .exceptions import (
    LogConfigError,
    LogFlushError,
    LoggingError,
    LogHandlerError,
    LogWriteError,
)
from .models import (
    Correlation,
    CorrelationManager,
    HTTPDetails,
    LogEntity,
    LogEntry,
    MultiTenant,
    correlation_manager,
)

# Note: The legacy `Entity` class still exists in `models.py` for backward compatibility and migration purposes.
# It is intentionally not exported here to discourage its use in new code. If you need to use it, import directly from `models.py`.
__all__ = [
    # Enums
    "LogLevel",
    # Exceptions
    "LoggingError",
    "LogHandlerError",
    "LogConfigError",
    "LogWriteError",
    "LogFlushError",
    # Models
    "LogEntity",
    "HTTPDetails",
    "Correlation",
    "MultiTenant",
    "LogEntry",
    # Correlation
    "CorrelationManager",
    "correlation_manager",
]
