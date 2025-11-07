"""
Decorators for automatic logging of function calls with dependency injection support
"""

import inspect
import time
from functools import wraps
from typing import Any, Callable, Optional

from .client.base import get_global_logger
from .client.extractors import (
    DefaultResultProcessor,
    EntityExtractor,
    HTTPDetailsExtractor,
    KwargsEntityExtractor,
    KwargsHTTPDetailsExtractor,
    KwargsMultiTenantExtractor,
    MultiTenantExtractor,
    ResultProcessor,
)
from .client.models import LogEntry, LogLevel


class LogDecoratorConfig:
    """Configuration for the log decorator with dependency injection."""

    def __init__(
        self,
        action_name: Optional[str] = None,
        level_name: Optional[str] = None,
        log_level: LogLevel = LogLevel.INFO,
        entity_extractor: Optional[EntityExtractor] = None,
        http_extractor: Optional[HTTPDetailsExtractor] = None,
        multitenant_extractor: Optional[MultiTenantExtractor] = None,
        result_processor: Optional[ResultProcessor] = None,
        include_params: bool = False,
        sensitive_params: Optional[list] = None,
        color: Optional[str] = None,
    ):
        """
        Args:
            action_name: Custom action name for logs (defaults to function name)
            level_name: Custom level name for logs (e.g., "get_data", "route_function")
            log_level: Minimum log level
            entity_extractor: Custom extractor for entity information
            http_extractor: Custom extractor for HTTP details
            multitenant_extractor: Custom extractor for multi-tenant info
            result_processor: Custom processor for function results
            include_params: Whether to include function parameters in logs
            sensitive_params: List of parameter names to sanitize
            color: Console color for log output (e.g., 'red', 'green', 'blue', 'yellow')
        """
        self.action_name = action_name
        self.level_name = level_name
        self.log_level = log_level
        self.color = color

        # Dependency injection with default implementations
        self.entity_extractor = entity_extractor or KwargsEntityExtractor()
        self.http_extractor = http_extractor or KwargsHTTPDetailsExtractor()
        self.multitenant_extractor = (
            multitenant_extractor or KwargsMultiTenantExtractor()
        )
        self.result_processor = result_processor or DefaultResultProcessor()

        self.include_params = include_params
        self.sensitive_params = sensitive_params or [
            "password",
            "token",
            "auth_token",
            "access_token",
            "secret",
            "api_key",
        ]


def log_call(
    func: Optional[Callable] = None,
    logger: Optional[Any] = None,
    logger_getter: Optional[Callable[[], Any]] = None,
    action_name: Optional[str] = None,
    level_name: Optional[str] = None,
    log_level: LogLevel = LogLevel.INFO,
    include_params: bool = False,
    sensitive_params: Optional[list] = None,
    config: Optional[LogDecoratorConfig] = None,
    color: Optional[str] = None,
) -> Any:
    """
    Decorator to automatically log function calls with full dependency injection support.

    This decorator follows SOLID principles:
    - Single Responsibility: Each component has one job
    - Open/Closed: Extend via custom extractors without modifying decorator
    - Liskov Substitution: Any extractor implementation works
    - Interface Segregation: Separate interfaces for different concerns
    - Dependency Inversion: Depends on abstractions, not implementations

    Args:
        logger: Direct logger instance (takes precedence)
        logger_getter: Callable that returns a logger instance
        action_name: Custom action name for logs (defaults to function name)
        log_level: Minimum log level (default: INFO)
        include_params: Whether to include function parameters in logs
        sensitive_params: List of parameter names to sanitize
        config: LogDecoratorConfig for custom extractors (optional)
        color: Console color for log output (e.g., 'red', 'green', 'blue', 'yellow')

    Examples:
        Basic usage:
        ```python
        @log_call(logger_getter=get_logger)
        async def my_function():
            pass
        ```

        With common options:
        ```python
        @log_call(
            logger_getter=get_logger,
            action_name="custom_action",
            log_level=LogLevel.DEBUG,
            include_params=True
        )
        async def my_function(param1, param2):
            pass
        ```

        With custom extractors:
        ```python
        @log_call(
            logger_getter=get_logger,
            config=LogDecoratorConfig(
                entity_extractor=MyCustomEntityExtractor(),
                result_processor=MyCustomResultProcessor()
            )
        )
        async def my_function():
            pass
        ```

        Combined usage:
        ```python
        @log_call(
            logger_getter=get_logger,
            action_name="process_order",
            log_level=LogLevel.INFO,
            include_params=True,
            config=LogDecoratorConfig(entity_extractor=OrderExtractor())
        )
        async def process_order(order_id, customer_id):
            pass
        ```
    """
    # Handle both @log_call and @log_call(...) usage
    if func is not None:
        # Called as @log_call (without arguments)
        return _create_log_call_decorator(
            func=func,
            logger=logger,
            logger_getter=logger_getter,
            action_name=action_name,
            level_name=level_name,
            log_level=log_level,
            include_params=include_params,
            sensitive_params=sensitive_params,
            config=config,
            color=color,
        )
    else:
        # Called as @log_call(...) (with arguments)
        def decorator(func: Callable) -> Any:
            return _create_log_call_decorator(
                func=func,
                logger=logger,
                logger_getter=logger_getter,
                action_name=action_name,
                level_name=level_name,
                log_level=log_level,
                include_params=include_params,
                sensitive_params=sensitive_params,
                config=config,
                color=color,
            )

        return decorator


def _create_log_call_decorator(
    func: Callable,
    logger: Optional[Any] = None,
    logger_getter: Optional[Callable[[], Any]] = None,
    action_name: Optional[str] = None,
    level_name: Optional[str] = None,
    log_level: LogLevel = LogLevel.INFO,
    include_params: bool = False,
    sensitive_params: Optional[list] = None,
    config: Optional[LogDecoratorConfig] = None,
    color: Optional[str] = None,
) -> Any:
    """Create the actual decorator with logger injection."""
    # Merge direct parameters with config
    if config is None:
        config = LogDecoratorConfig(
            action_name=action_name,
            level_name=level_name,
            log_level=log_level,
            include_params=include_params,
            sensitive_params=sensitive_params,
            color=color,
        )
    else:
        # Override config with direct parameters if provided
        if action_name is not None:
            config.action_name = action_name
        if level_name is not None:
            config.level_name = level_name
        if log_level != LogLevel.INFO:  # If not default
            config.log_level = log_level
        if include_params:
            config.include_params = include_params
        if sensitive_params is not None:
            config.sensitive_params = sensitive_params
        if color is not None:
            config.color = color

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the logger instance
        if logger is None:
            if logger_getter is not None:
                injected_logger = logger_getter()
            else:
                injected_logger = get_global_logger()
        else:
            injected_logger = logger

        # Temporarily inject logger into the function's module globals
        original_globals = func.__globals__.copy()
        func.__globals__["logger"] = injected_logger

        try:
            # Execute the function with logging
            return await _execute_with_logging(
                func, args, kwargs, config, logger, logger_getter, is_async=True
            )
        finally:
            # Restore original globals
            func.__globals__.clear()
            func.__globals__.update(original_globals)

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the logger instance
        if logger is None:
            if logger_getter is not None:
                injected_logger = logger_getter()
            else:
                injected_logger = get_global_logger()
        else:
            injected_logger = logger

        # Temporarily inject logger into the function's module globals
        original_globals = func.__globals__.copy()
        func.__globals__["logger"] = injected_logger

        try:
            # Execute the function with logging
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    return _execute_with_logging_sync(
                        func, args, kwargs, config, logger, logger_getter
                    )
                else:
                    return _execute_with_logging_sync(
                        func, args, kwargs, config, logger, logger_getter
                    )
            except RuntimeError:
                return _execute_with_logging_sync(
                    func, args, kwargs, config, logger, logger_getter
                )
        finally:
            # Restore original globals
            func.__globals__.clear()
            func.__globals__.update(original_globals)

    # Return the appropriate wrapper
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def _sanitize_params(kwargs: dict, sensitive_params: list) -> dict:
    """Sanitize sensitive parameters for logging."""
    safe_kwargs = {}
    for k, v in kwargs.items():
        if k in sensitive_params:
            safe_kwargs[k] = "***"
        elif k == "auth":
            safe_kwargs[k] = f"<{type(v).__name__}>"
        elif isinstance(v, (str, int, float, bool)):
            safe_kwargs[k] = str(v)
        elif v is None:
            safe_kwargs[k] = "None"
        else:
            safe_kwargs[k] = f"<{type(v).__name__}>"
    return safe_kwargs


async def _execute_with_logging(
    func: Callable,
    args: tuple,
    kwargs: dict,
    config: LogDecoratorConfig,
    logger: Optional[Any],
    logger_getter: Optional[Callable],
    is_async: bool = True,
) -> Any:
    """Execute function with logging (async version)."""
    start_time = time.time()

    # Get logger instance with proper priority:
    # 1. Direct logger parameter (decorator argument)
    # 2. logger_getter callable
    # 3. Global logger fallback
    if logger is None:
        if logger_getter is not None:
            logger = logger_getter()
        else:
            logger = get_global_logger()

    # Extract context using injected extractors
    entity = config.entity_extractor.extract(func, args, kwargs)
    http_details = config.http_extractor.extract(func, args, kwargs)
    multi_tenant = config.multitenant_extractor.extract(func, args, kwargs)

    # Only include HTTP details if they're actually HTTP-related (not COMMENT)
    if http_details and http_details.method == "COMMENT":
        http_details = None

    # Get caller information
    current_frame = inspect.currentframe()
    if current_frame and current_frame.f_back and current_frame.f_back.f_back:
        caller_frame = current_frame.f_back.f_back
        caller_info = {
            "file": caller_frame.f_code.co_filename,
            "line": caller_frame.f_lineno,
            "function": caller_frame.f_code.co_name,
        }
    else:
        caller_info = {
            "file": "unknown",
            "line": 0,
            "function": "unknown",
        }

    # Build context
    log_context = {
        "action": config.action_name or func.__qualname__,
        "entity": entity,
        "multi_tenant": multi_tenant,
    }

    # Only include http_details if it's not None (i.e., not COMMENT method)
    if http_details is not None:
        log_context["http_details"] = http_details

    extra = {
        "function": func.__qualname__,
        "module": func.__module__,
        "caller": caller_info,
    }

    # Sanitize params if requested
    if config.include_params:
        safe_kwargs = _sanitize_params(kwargs, config.sensitive_params)
        extra["parameters"] = safe_kwargs

    result_context = {}
    try:
        # Execute function
        if is_async:
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        duration_ms = int((time.time() - start_time) * 1000)

        # Process result using injected processor
        result_context, updated_http = config.result_processor.process(
            result, http_details
        )
        if updated_http:
            log_context["http_details"] = updated_http

        # Determine status
        status_code = updated_http.status_code if updated_http else None
        is_error = status_code and status_code >= 400

        # Log success or HTTP error
        if logger:
            level = LogLevel.ERROR if is_error else config.log_level
            message = f"{log_context['action']} {'failed with HTTP error' if is_error else 'completed'}"

            # Use logger.log() to get automatic correlation generation
            if is_async and hasattr(logger, "log"):
                merged_extra = extra.copy()
                if "extra" in result_context:
                    merged_extra.update(result_context["extra"])
                    # Remove extra from result_context to avoid duplicate keyword argument
                    result_context_without_extra = {
                        k: v for k, v in result_context.items() if k != "extra"
                    }
                else:
                    result_context_without_extra = result_context

                # Merge log_context and result_context, with result_context taking precedence
                merged_context = log_context.copy()
                merged_context.update(result_context_without_extra)

                await logger.log(
                    level=level,
                    message=message,
                    duration_ms=duration_ms,
                    status="error" if is_error else "success",
                    level_name=config.level_name,
                    color=config.color,
                    **merged_context,
                    extra=merged_extra,
                )
            elif hasattr(logger, "write"):
                # Fallback: manually generate correlation if logger has correlation_manager
                if (
                    hasattr(logger, "correlation_manager")
                    and logger.correlation_manager
                ):
                    correlation = logger.correlation_manager.get_or_create_correlation()
                    log_context["correlation"] = correlation

                entry = LogEntry.create(
                    level=level,
                    message=message,
                    app_name=getattr(logger, "app_name", "default_app"),
                    duration_ms=duration_ms,
                    status="error" if is_error else "success",
                    level_name=config.level_name,
                    color=config.color,
                    **log_context,
                    **result_context,
                    extra=extra,
                )
                await logger.write(entry)

        return result

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        # Extract error details
        if hasattr(e, "status") and http_details:
            http_details.status_code = getattr(e, "status", None)
            log_context["http_details"] = http_details

        error_extra = {
            **extra,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }

        # Log error
        if logger:
            message = f"{log_context['action']} failed: {str(e)}"

            # Use logger.log() to get automatic correlation generation
            if is_async and hasattr(logger, "log"):
                merged_extra = error_extra.copy()
                if "extra" in result_context:
                    merged_extra.update(result_context["extra"])
                    result_context_without_extra = {
                        k: v for k, v in result_context.items() if k != "extra"
                    }
                else:
                    result_context_without_extra = result_context

                if result_context:
                    merged_context_error = log_context.copy()
                    merged_context_error.update(result_context_without_extra)
                else:
                    merged_context_error = log_context

                await logger.log(
                    level=LogLevel.ERROR,
                    message=message,
                    duration_ms=duration_ms,
                    status="error",
                    color=config.color,
                    **merged_context_error,
                    extra=error_extra,
                )
            elif hasattr(logger, "write"):
                # Fallback: manually generate correlation if logger has correlation_manager
                if (
                    hasattr(logger, "correlation_manager")
                    and logger.correlation_manager
                ):
                    correlation = logger.correlation_manager.get_or_create_correlation()
                    log_context["correlation"] = correlation

                entry = LogEntry.create(
                    level=LogLevel.ERROR,
                    message=message,
                    app_name=getattr(logger, "app_name", "default_app"),
                    duration_ms=duration_ms,
                    status="error",
                    color=config.color,
                    **log_context,
                    extra=error_extra,
                )
                await logger.write(entry)

        raise


def _execute_with_logging_sync(
    func: Callable,
    args: tuple,
    kwargs: dict,
    config: LogDecoratorConfig,
    logger: Optional[Any],
    logger_getter: Optional[Callable],
) -> Any:
    """Execute function with logging (sync version)."""
    start_time = time.time()

    # Get logger instance with proper priority:
    # 1. Direct logger parameter (decorator argument)
    # 2. logger_getter callable
    # 3. Global logger fallback
    if logger is None:
        if logger_getter is not None:
            logger = logger_getter()
        else:
            logger = get_global_logger()

    try:
        result = func(*args, **kwargs)
        duration_ms = int((time.time() - start_time) * 1000)

        if logger:
            import asyncio

            entity = config.entity_extractor.extract(func, args, kwargs)
            http_details = config.http_extractor.extract(func, args, kwargs)
            multi_tenant = config.multitenant_extractor.extract(func, args, kwargs)

            # Only include HTTP details if they're actually HTTP-related (not COMMENT)
            if http_details and http_details.method == "COMMENT":
                http_details = None

            # Manually generate correlation if logger has correlation_manager
            correlation = None
            if hasattr(logger, "correlation_manager") and logger.correlation_manager:
                # Try to get correlation using the method that exists
                if hasattr(logger.correlation_manager, "get_or_create_correlation"):
                    correlation = logger.correlation_manager.get_or_create_correlation()
                else:
                    # Fallback for older correlation manager - create a simple correlation
                    context = logger.correlation_manager.get_current_context()
                    # Filter to only include fields that Correlation accepts
                    correlation = {
                        "trace_id": context.get("trace_id"),
                        "span_id": context.get("span_id"),
                        "parent_span_id": context.get("parent_span_id"),
                    }

            entry = LogEntry.create(
                level=config.log_level,
                message=f"{config.action_name or func.__qualname__} completed",
                app_name=getattr(logger, "app_name", "default_app"),
                action=config.action_name or func.__qualname__,
                entity=entity,
                multi_tenant=multi_tenant,
                duration_ms=duration_ms,
                status="success",
                correlation=correlation,
                color=config.color,
            )

            # Only add http_details if it's not None (i.e., not COMMENT method)
            if http_details is not None:
                entry.http_details = http_details

            # Run async write in sync context
            if hasattr(logger, "write"):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If event loop is running, schedule the write
                        asyncio.create_task(logger.write(entry))
                    else:
                        # No running loop, use run_until_complete
                        loop.run_until_complete(logger.write(entry))
                except RuntimeError:
                    # No event loop, create one
                    asyncio.run(logger.write(entry))

        return result

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        # Logger is already resolved above, just use it
        if logger:
            import asyncio

            entity = config.entity_extractor.extract(func, args, kwargs)
            http_details = config.http_extractor.extract(func, args, kwargs)
            multi_tenant = config.multitenant_extractor.extract(func, args, kwargs)

            # Only include HTTP details if they're actually HTTP-related (not COMMENT)
            if http_details and http_details.method == "COMMENT":
                http_details = None

            # Manually generate correlation if logger has correlation_manager
            correlation = None
            if hasattr(logger, "correlation_manager") and logger.correlation_manager:
                # Try to get correlation using the method that exists
                if hasattr(logger.correlation_manager, "get_or_create_correlation"):
                    correlation = logger.correlation_manager.get_or_create_correlation()
                else:
                    # Fallback for older correlation manager - create a simple correlation
                    context = logger.correlation_manager.get_current_context()
                    # Filter to only include fields that Correlation accepts
                    correlation = {
                        "trace_id": context.get("trace_id"),
                        "span_id": context.get("span_id"),
                        "parent_span_id": context.get("parent_span_id"),
                    }

            entry = LogEntry.create(
                level=LogLevel.ERROR,
                message=f"{config.action_name or func.__qualname__} failed: {str(e)}",
                app_name=getattr(logger, "app_name", "default_app"),
                action=config.action_name or func.__qualname__,
                entity=entity,
                multi_tenant=multi_tenant,
                http_details=http_details,
                duration_ms=duration_ms,
                status="error",
                correlation=correlation,
                color=config.color,
                extra={"error_type": type(e).__name__, "error_message": str(e)},
            )

            # Run async write in sync context
            if hasattr(logger, "write"):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If event loop is running, schedule the write
                        asyncio.create_task(logger.write(entry))
                    else:
                        # No running loop, use run_until_complete
                        loop.run_until_complete(logger.write(entry))
                except RuntimeError:
                    # No event loop, create one
                    asyncio.run(logger.write(entry))

        raise


# Legacy alias for backward compatibility
log_function_call = log_call
