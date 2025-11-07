"""Base configuration classes and utilities for the logging library."""

__all__ = [
    "OutputMode",
    "ServiceConfig",
    "HandlerBufferSettings",
    "ServiceHandler",
    "HandlerInstance",
    "Logger",
    "get_global_logger",
    "set_global_logger",
    "get_or_create_logger",
]

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional

from .models import CorrelationManager, LogEntry, LogLevel

# Type for valid output modes
OutputMode = Literal["cloud", "console", "file", "multi"]


@dataclass
class ServiceConfig(ABC):
    """abstract base class for service-specific configuration settings"""

    output_mode: OutputMode = "console"  # Default to file mode

    def __post_init__(self) -> None:
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the configuration"""
        raise NotImplementedError()


@dataclass
class HandlerBufferSettings(ABC):
    """abstract base configuration for logging configuration settings"""

    batch_size: int = 100
    flush_interval: int = 30  # seconds
    max_buffer_size: int = 1000


@dataclass
class ServiceHandler(ABC):
    """defines how a handler communicates with services to create logs"""

    buffer_settings: HandlerBufferSettings

    service_config: Optional[ServiceConfig] = (
        None  # has authentication and connection details to service1
    )

    buffer: List[LogEntry] = field(default_factory=list)

    # @classmethod
    # def from_config(cls, service_config: ServiceConfig):

    #     hc = cls(
    #         service_config = service_config

    #     )

    #     # if hasattr(config, 'to_platform_config') and callable(getattr(config, 'to_platform_config')):
    #     #     hc.platform_config = config.to_platform_config()
    #     return hc

    def validate_config(self) -> bool:
        if not self.service_config:
            raise ValueError("Service configuration is not set.")

        return self.service_config.validate_config()

    @abstractmethod
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to destination"""

    @abstractmethod
    async def flush(self) -> bool:
        """Flush any buffered entries"""

    async def close(self) -> None:
        """Clean up resources"""


@dataclass
class HandlerInstance:
    """Wraps a ServiceHandler with filtering logic (log level and method filtering)"""

    service_handler: ServiceHandler

    handler_name: Optional[str] = None  # friendly name for the handler

    log_level: LogLevel = LogLevel.INFO  # minimum log level to log.

    log_method: List[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH", "COMMENT"]
    )
    # filtered list of API requests to log, generally won't log GET requests

    def __post_init__(self) -> None:
        if not self.handler_name:
            self.handler_name = f"{self.service_handler.__class__.__name__}"
        self.validate_config()

    def validate_config(self) -> bool:
        """Validate the configuration"""
        if not self.service_handler:
            raise ValueError("must set a service handler")

        return self.service_handler.validate_config()

    async def write(self, entry: LogEntry) -> bool:
        """Write log entry to destination with filtering"""
        # Filter by log level - only filter DEBUG, always show INFO/WARNING/ERROR/CRITICAL
        if entry.level == LogLevel.DEBUG and not self.log_level.should_log(entry.level):
            return False

        # Filter by log method
        if entry.method and entry.method not in self.log_method:
            return False

        # Delegate to service handler
        await self.service_handler.write([entry])
        return True

    async def flush(self) -> bool:
        """Flush any buffered entries"""
        return await self.service_handler.flush()

    async def close(self) -> None:
        """Clean up resources"""
        await self.service_handler.close()


@dataclass
class Logger:
    """Enhanced logger with structured logging and automatic correlation tracking"""

    handlers: List[HandlerInstance] = field(default_factory=list)
    app_name: Optional[str] = "default_app"
    show_debugging: bool = False  # - True shows DEBUG, False filters it

    # Correlation manager (auto-initialized)
    correlation_manager: Optional[CorrelationManager] = field(
        default_factory=CorrelationManager
    )

    def __post_init__(self) -> None:
        """Initialize correlation manager and set handler log levels based on show_debugging"""
        if self.correlation_manager is None:
            self.correlation_manager = CorrelationManager()

        # Set handler log levels based on show_debugging
        debug_level = LogLevel.DEBUG if self.show_debugging else LogLevel.INFO
        for handler in self.handlers:
            handler.log_level = debug_level

    async def log(self, level: LogLevel, message: str, **context: Any) -> bool:
        """Core logging method - creates entry with auto-correlation and writes to handlers"""

        # Check if we should log this level - only filter DEBUG when show_debugging=False
        if level == LogLevel.DEBUG and not self.show_debugging:
            return True

        # Auto-generate or get existing correlation
        if self.correlation_manager and "correlation" not in context:
            correlation = self.correlation_manager.get_or_create_correlation()
            context["correlation"] = correlation

        # Create log entry
        entry_kwargs = {
            "level": level,
            "message": message,
            "app_name": self.app_name,
            "user": context.get("user"),
            "action": context.get("action"),
            "level_name": context.get("level_name"),
            "method": context.get("method", "COMMENT"),
            "entity": context.get("entity"),
            "status": context.get("status", "info"),
            "duration_ms": context.get("duration_ms"),
            "correlation": context.get("correlation"),
            "multi_tenant": context.get("multi_tenant"),
            "extra": context.get("extra", {}),
        }

        # Only include http_details if it's not None
        if context.get("http_details") is not None:
            entry_kwargs["http_details"] = context.get("http_details")

        entry = LogEntry.create(**entry_kwargs)

        # Write to all handlers (handlers manage their own buffering)
        for handler in self.handlers:
            await handler.write(entry)

        return True

    async def write(self, entry: LogEntry) -> None:
        """Direct write - for compatibility"""
        for handler in self.handlers:
            await handler.write(entry)

    # Convenience methods for different log levels
    async def debug(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log DEBUG level message with optional method and level_name"""
        context.update({"method": method, "level_name": level_name})
        return await self.log(LogLevel.DEBUG, message, **context)

    async def info(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log INFO level message with optional method and level_name"""
        context.update({"method": method, "level_name": level_name})
        return await self.log(LogLevel.INFO, message, **context)

    async def warning(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log WARNING level message with optional method and level_name"""
        context.update({"method": method, "level_name": level_name})
        return await self.log(LogLevel.WARNING, message, **context)

    async def error(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log ERROR level message with optional method and level_name"""
        context.update({"method": method, "level_name": level_name})
        return await self.log(LogLevel.ERROR, message, **context)

    async def critical(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log CRITICAL level message with optional method and level_name"""
        context.update({"method": method, "level_name": level_name})
        return await self.log(LogLevel.CRITICAL, message, **context)

    def create_entry(self, level: LogLevel, message: str, **kwargs: Any) -> LogEntry:
        """Create a LogEntry without logging it (for manual control)"""
        # Auto-generate or get existing correlation
        if self.correlation_manager and "correlation" not in kwargs:
            correlation = self.correlation_manager.get_or_create_correlation()
            kwargs["correlation"] = correlation

        entry = LogEntry.create(
            level=level, message=message, app_name=self.app_name or "default", **kwargs
        )
        return entry

    def start_new_trace(self) -> str:
        """Start a completely new trace to group a bundle of related logs.

        Use this to separate different operations:
        - Bundle 1: User login flow
        - Bundle 2: Data processing
        - Bundle 3: Report generation

        Returns the new trace_id.
        """
        if not self.correlation_manager:
            self.correlation_manager = CorrelationManager()
        return self.correlation_manager.start_new_trace()

    def start_request(
        self,
        parent_trace_id: Optional[str] = None,
        auth: Any = None,
        is_pagination_request: bool = False,
    ) -> str:
        """Start a new request context and return request ID"""
        if not self.correlation_manager:
            self.correlation_manager = CorrelationManager()
        return self.correlation_manager.start_request(
            parent_trace_id, auth, is_pagination_request
        )

    def end_request(self) -> None:
        """End the current request context (also clears trace)"""
        # Clear context variables for this request
        if self.correlation_manager:
            self.correlation_manager.trace_id_var.set(None)
            self.correlation_manager.request_id_var.set(None)
            self.correlation_manager.span_id_var.set(None)
            self.correlation_manager.correlation_var.set(None)

    async def close(self) -> None:
        """Clean up resources"""
        # Close all handlers
        for handler in self.handlers:
            await handler.close()

    # def get_cloud_config(self) -> Dict[str, Any]:
    #     return {"cloud_provider": "multi"}

    # def get_handler_configs(self) -> List[Dict[str, Any]]:
    #     return [
    #         {
    #             "type": handler.type,
    #             "config": handler.config,
    #             "cloud_config": (
    #                 handler.config.to_platform_config()
    #                 if handler.type == "cloud"
    #                 else None
    #             ),
    #         }
    #         for handler in self.handlers
    #     ]

    # @classmethod
    # def create(
    #     cls,
    #     handlers: List[Dict[str, Any]],
    #     level: LogLevel = LogLevel.INFO,
    #     batch_size: int = 100,
    #     flush_interval: int = 30,
    #     **kwargs
    # ) -> "MultiHandlerLogConfig":
    #     handler_configs = [
    #         HandlerConfig(type=h["type"], config=h["config"]) for h in handlers
    #     ]
    #     return cls(
    #         handlers=handler_configs,
    #         level=level,
    #         batch_size=batch_size,
    #         flush_interval=flush_interval,
    #         **kwargs
    #     )


# Global logger instance management
_global_logger: Optional[Logger] = None


def get_global_logger() -> Logger:
    """Get the global logger instance. Creates a default console logger if none exists."""
    global _global_logger

    if _global_logger is None:
        # Create a default console logger with text output
        from dc_logger.services.console.base import (
            ConsoleHandler,
            ConsoleServiceConfig,
        )

        # Create console config for text output
        console_config = ConsoleServiceConfig(output_mode="console", output_type="text")

        # Create console handler
        buffer_settings = HandlerBufferSettings()
        console_handler = ConsoleHandler(
            buffer_settings=buffer_settings, service_config=console_config
        )

        # Create handler instance
        handler_instance = HandlerInstance(
            service_handler=console_handler,
            handler_name="default_console",
            log_level=LogLevel.INFO,  # Will be updated by Logger.__post_init__
        )

        # Create logger with default console handler
        _global_logger = Logger(
            handlers=[handler_instance],
            app_name="default_app",
            show_debugging=False,  # Default: no debugging
        )

    return _global_logger


def set_global_logger(logger: Logger) -> None:
    """Set the global logger instance.

    Args:
        logger: The Logger instance to set as global
    """
    global _global_logger
    _global_logger = logger


def get_or_create_logger(
    handlers: Optional[List[HandlerInstance]] = None,
    app_name: str = "default_app",
    auto_set_global: bool = True,
) -> Logger:
    """Get existing global logger or create a new one.

    Args:
        handlers: List of HandlerInstance objects (only used if creating new logger)
        app_name: Application name (only used if creating new logger)
        auto_set_global: Whether to automatically set as global logger if creating new

    Returns:
        The global logger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = Logger(handlers=handlers or [], app_name=app_name)

    return _global_logger
