"""Factory functions for creating common logger configurations"""

from typing import Any, Optional

from ..client.enums import LogLevel
from .cloud import DatadogLogConfig
from .console import ConsoleLogConfig
from .multi_handler import HandlerConfig, MultiHandlerLogConfig


def create_console_config(
    level: LogLevel = LogLevel.INFO, pretty_print: bool = True, **kwargs: Any
) -> ConsoleLogConfig:
    """Create a simple console configuration"""
    return ConsoleLogConfig(level=level, pretty_print=pretty_print, **kwargs)


def create_file_config(
    file_path: str, level: LogLevel = LogLevel.INFO, **kwargs: Any
) -> ConsoleLogConfig:
    """Create a file configuration"""
    return ConsoleLogConfig(
        level=level,
        output_mode="file",
        destination=file_path,
        pretty_print=False,
        **kwargs,
    )


def create_console_file_config(
    file_path: str,
    level: LogLevel = LogLevel.INFO,
    pretty_print: bool = True,
    **kwargs: Any,
) -> MultiHandlerLogConfig:
    """Create a configuration that logs to both console and file"""
    console_config = ConsoleLogConfig(level=level, pretty_print=pretty_print, **kwargs)
    file_config = ConsoleLogConfig(
        level=level,
        output_mode="file",
        destination=file_path,
        pretty_print=False,
        **kwargs,
    )

    return MultiHandlerLogConfig(
        handlers=[
            HandlerConfig(type="console", config=console_config),
            HandlerConfig(type="file", config=file_config),
        ],
        level=level,
        **kwargs,
    )


def create_console_datadog_config(
    datadog_api_key: Optional[str] = None,
    datadog_app_key: Optional[str] = None,
    datadog_site: str = "datadoghq.com",
    datadog_service: str = "domolibrary",
    datadog_env: str = "production",
    level: LogLevel = LogLevel.INFO,
    pretty_print: bool = True,
    **kwargs: Any,
) -> MultiHandlerLogConfig:
    """Create a configuration that logs to both console and Datadog"""
    console_config = ConsoleLogConfig(level=level, pretty_print=pretty_print, **kwargs)
    datadog_config = DatadogLogConfig(
        api_key=datadog_api_key,
        app_key=datadog_app_key,
        site=datadog_site,
        service=datadog_service,
        env=datadog_env,
        level=level,
        **kwargs,
    )

    return MultiHandlerLogConfig(
        handlers=[
            HandlerConfig(type="console", config=console_config),
            HandlerConfig(
                type="cloud",
                config=datadog_config,
                platform_config=datadog_config.to_platform_config(),
            ),
        ],
        level=level,
        **kwargs,
    )


def create_console_file_datadog_config(
    file_path: str,
    datadog_api_key: Optional[str] = None,
    datadog_app_key: Optional[str] = None,
    datadog_site: str = "datadoghq.com",
    datadog_service: str = "domolibrary",
    datadog_env: str = "production",
    level: LogLevel = LogLevel.INFO,
    pretty_print: bool = True,
    **kwargs: Any,
) -> MultiHandlerLogConfig:
    """Create a configuration that logs to console, file, and Datadog"""
    console_config = ConsoleLogConfig(level=level, pretty_print=pretty_print, **kwargs)
    file_config = ConsoleLogConfig(
        level=level,
        output_mode="file",
        destination=file_path,
        pretty_print=False,
        **kwargs,
    )
    datadog_config = DatadogLogConfig(
        api_key=datadog_api_key,
        app_key=datadog_app_key,
        site=datadog_site,
        service=datadog_service,
        env=datadog_env,
        level=level,
        **kwargs,
    )

    return MultiHandlerLogConfig(
        handlers=[
            HandlerConfig(type="console", config=console_config),
            HandlerConfig(type="file", config=file_config),
            HandlerConfig(
                type="cloud",
                config=datadog_config,
                platform_config=datadog_config.to_platform_config(),
            ),
        ],
        level=level,
        **kwargs,
    )


def create_file_datadog_config(
    file_path: str,
    datadog_api_key: Optional[str] = None,
    datadog_app_key: Optional[str] = None,
    datadog_site: str = "datadoghq.com",
    datadog_service: str = "domolibrary",
    datadog_env: str = "production",
    level: LogLevel = LogLevel.INFO,
    **kwargs: Any,
) -> MultiHandlerLogConfig:
    """Create a configuration that logs to file and Datadog"""
    file_config = ConsoleLogConfig(
        level=level,
        output_mode="file",
        destination=file_path,
        pretty_print=False,
        **kwargs,
    )
    datadog_config = DatadogLogConfig(
        api_key=datadog_api_key,
        app_key=datadog_app_key,
        site=datadog_site,
        service=datadog_service,
        env=datadog_env,
        level=level,
        **kwargs,
    )

    return MultiHandlerLogConfig(
        handlers=[
            HandlerConfig(type="file", config=file_config),
            HandlerConfig(
                type="cloud",
                config=datadog_config,
                platform_config=datadog_config.to_platform_config(),
            ),
        ],
        level=level,
        **kwargs,
    )
