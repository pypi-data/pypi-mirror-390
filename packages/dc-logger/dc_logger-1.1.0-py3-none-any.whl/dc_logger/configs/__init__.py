"""Configuration module - Logger configurations for various platforms"""

from .base import LogConfig
from .cloud import (
    AWSCloudWatchLogConfig,
    AzureLogAnalyticsConfig,
    DatadogLogConfig,
    GCPLoggingConfig,
    LogCloudConfig,
)
from .console import ConsoleLogConfig
from .factory import (
    create_console_config,
    create_console_datadog_config,
    create_console_file_config,
    create_console_file_datadog_config,
    create_file_config,
    create_file_datadog_config,
)
from .multi_handler import HandlerConfig, MultiHandlerLogConfig

__all__ = [
    # Base config
    "LogConfig",
    "ConsoleLogConfig",
    # Cloud configs
    "LogCloudConfig",
    "DatadogLogConfig",
    "AWSCloudWatchLogConfig",
    "GCPLoggingConfig",
    "AzureLogAnalyticsConfig",
    # Multi-handler config
    "MultiHandlerLogConfig",
    "HandlerConfig",
    # Factory functions
    "create_console_config",
    "create_file_config",
    "create_console_file_config",
    "create_console_datadog_config",
    "create_console_file_datadog_config",
    "create_file_datadog_config",
]
