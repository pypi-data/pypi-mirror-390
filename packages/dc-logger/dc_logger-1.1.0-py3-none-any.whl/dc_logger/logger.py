"""
DC_Logger - Enhanced structured logging system

This is the main logger implementation that provides structured logging
with support for multiple handlers, correlation tracking, and cloud integrations.
"""

import asyncio
from asyncio import Task
from typing import Any, List, Optional

from .client.enums import LogLevel
from .client.exceptions import LogConfigError
from .client.models import LogEntry, correlation_manager
from .configs.base import LogConfig
from .configs.console import ConsoleLogConfig
from .handlers.base import LogHandler
from .handlers.cloud.aws import AWSCloudWatchHandler
from .handlers.cloud.azure import AzureLogAnalyticsHandler
from .handlers.cloud.datadog import DatadogHandler
from .handlers.cloud.gcp import GCPLoggingHandler
from .handlers.console import ConsoleHandler
from .handlers.file import FileHandler


class DCLogger:
    """Enhanced logger with structured logging and multiple handlers"""

    def __init__(self, config: LogConfig, app_name: str):
        self.config = config
        self.app_name = app_name
        self.handlers: List[LogHandler] = []
        self.buffer: List[LogEntry] = []
        self.correlation_manager = correlation_manager
        self.flush_task: Optional[Task[None]] = None

        # Validate configuration
        config.validate_config()

        # Initialize handlers based on config
        self._setup_handlers()

        # Try to start background flush task if event loop is available
        try:
            asyncio.get_running_loop()
            self._start_flush_task()
        except RuntimeError:
            # No event loop, task will be started when first log is called
            pass

    def _setup_handlers(self) -> None:
        """Setup handlers based on configuration"""
        # Get handler configurations from the config
        handler_configs = self.config.get_handler_configs()

        for handler_config in handler_configs:
            handler_type = handler_config["type"]
            config = handler_config["config"]
            cloud_config = handler_config.get("cloud_config")

            if handler_type == "console":
                self.handlers.append(ConsoleHandler(config))
            elif handler_type == "file":
                self.handlers.append(FileHandler(config))
            elif handler_type == "cloud":
                if cloud_config:
                    cloud_provider = cloud_config.get("cloud_provider")
                    if cloud_provider == "datadog":
                        self.handlers.append(DatadogHandler(config))
                    elif cloud_provider == "aws":
                        self.handlers.append(AWSCloudWatchHandler(config))
                    elif cloud_provider == "gcp":
                        self.handlers.append(GCPLoggingHandler(config))
                    elif cloud_provider == "azure":
                        self.handlers.append(AzureLogAnalyticsHandler(config))
                    else:
                        raise LogConfigError(
                            f"Unknown cloud provider: {cloud_provider}"
                        )
                else:
                    raise LogConfigError("Cloud handler missing cloud_config")
            else:
                raise LogConfigError(f"Unknown handler type: {handler_type}")

    def _start_flush_task(self) -> None:
        """Start the background flush task"""
        if self.flush_task is None:
            self.flush_task = asyncio.create_task(self._periodic_flush())

    async def log(self, level: LogLevel, message: str, **context: Any) -> bool:
        """Log a message with structured context"""

        # Check if we should log this level
        if not self.config.level.should_log(level):
            return True

        # Start flush task if not already started and event loop is available
        if self.flush_task is None:
            try:
                asyncio.get_running_loop()
                self._start_flush_task()
            except RuntimeError:
                pass

        # Create log entry
        entry = LogEntry.create(
            level=level,
            message=message,
            logger=context.get("logger", f"domolibrary.{self.app_name}"),
            user=context.get("user"),
            action=context.get("action"),
            entity=context.get("entity"),
            status=context.get("status", "info"),
            duration_ms=context.get("duration_ms"),
            trace_id=self.correlation_manager.trace_id_var.get(),
            request_id=self.correlation_manager.request_id_var.get(),
            session_id=self.correlation_manager.session_id_var.get(),
            correlation=self.correlation_manager.correlation_var.get(),
            multi_tenant=context.get("multi_tenant"),
            http_details=context.get("http_details"),
            extra=context.get("extra", {}),
            color=context.get("color"),
        )

        # Add to buffer
        self.buffer.append(entry)

        # Flush if buffer is full
        if len(self.buffer) >= self.config.batch_size:
            await self.flush()

        return True

    async def flush(self) -> bool:
        """Flush buffered entries to all handlers"""
        if not self.buffer:
            return True

        entries_to_flush = self.buffer.copy()
        self.buffer.clear()

        success = True
        for handler in self.handlers:
            if not await handler.write(entries_to_flush):
                success = False

        return success

    async def _periodic_flush(self) -> None:
        """Background task to periodically flush logs"""
        while True:
            await asyncio.sleep(self.config.flush_interval)
            await self.flush()

    # Convenience methods for different log levels
    async def debug(self, message: str, **context: Any) -> bool:
        return await self.log(LogLevel.DEBUG, message, **context)

    async def info(self, message: str, **context: Any) -> bool:
        return await self.log(LogLevel.INFO, message, **context)

    async def warning(self, message: str, **context: Any) -> bool:
        return await self.log(LogLevel.WARNING, message, **context)

    async def error(self, message: str, **context: Any) -> bool:
        return await self.log(LogLevel.ERROR, message, **context)

    async def critical(self, message: str, **context: Any) -> bool:
        return await self.log(LogLevel.CRITICAL, message, **context)

    def start_request(
        self, parent_trace_id: Optional[str] = None, auth: Any = None
    ) -> str:
        """Start a new request context"""
        return self.correlation_manager.start_request(parent_trace_id, auth)

    def end_request(self) -> None:
        """End current request context"""
        # Clear context variables (they'll be reset on next request)

    async def close(self) -> None:
        """Clean up resources"""
        # Cancel flush task
        if hasattr(self, "flush_task") and self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self.flush()

        # Close handlers
        for handler in self.handlers:
            await handler.close()


# Global logger instance
_global_logger: Optional[DCLogger] = None


def get_logger(app_name: str = "domolibrary") -> DCLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        config = ConsoleLogConfig(level=LogLevel.INFO, pretty_print=False)
        _global_logger = DCLogger(config, app_name)

    return _global_logger


def set_global_logger(logger: DCLogger) -> None:
    """Set the global logger instance"""
    global _global_logger
    _global_logger = logger
