"""Handlers module - Log output handlers for various destinations"""

from .base import LogHandler
from .cloud import (
    AWSCloudWatchHandler,
    AzureLogAnalyticsHandler,
    CloudHandler,
    DatadogHandler,
    GCPLoggingHandler,
)
from .console import ConsoleHandler
from .file import FileHandler

__all__ = [
    # Base handler
    "LogHandler",
    # Local handlers
    "ConsoleHandler",
    "FileHandler",
    # Cloud handlers
    "CloudHandler",
    "DatadogHandler",
    "AWSCloudWatchHandler",
    "GCPLoggingHandler",
    "AzureLogAnalyticsHandler",
]
