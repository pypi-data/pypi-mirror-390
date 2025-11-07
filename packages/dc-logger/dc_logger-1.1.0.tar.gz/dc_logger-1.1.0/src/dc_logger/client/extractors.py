"""Extractor interfaces and implementations for extracting context from function calls"""

__all__ = [
    "EntityExtractor",
    "HTTPDetailsExtractor",
    "MultiTenantExtractor",
    "ResultProcessor",
    "KwargsEntityExtractor",
    "KwargsHTTPDetailsExtractor",
    "KwargsMultiTenantExtractor",
    "DefaultResultProcessor",
]


from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple

from .models import HTTPDetails, LogEntity, MultiTenant


class EntityExtractor(ABC):
    """Abstract base class for extracting entity information from function arguments."""

    @abstractmethod
    def extract(self, func: Callable, args: tuple, kwargs: dict) -> Optional[LogEntity]:
        """Extract entity information from function call.

        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            LogEntity or None if no entity found
        """


class HTTPDetailsExtractor(ABC):
    """Abstract base class for extracting HTTP details from function arguments."""

    @abstractmethod
    def extract(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> Optional[HTTPDetails]:
        """Extract HTTP details from function call.

        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            HTTPDetails or None if no HTTP details found
        """


class MultiTenantExtractor(ABC):
    """Abstract base class for extracting multi-tenant information from function arguments."""

    @abstractmethod
    def extract(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> Optional[MultiTenant]:
        """Extract multi-tenant information from function call.

        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            MultiTenant or None if no multi-tenant info found
        """


class ResultProcessor(ABC):
    """Abstract base class for processing function results."""

    @abstractmethod
    def process(
        self, result: Any, http_details: Optional[HTTPDetails] = None
    ) -> Tuple[Dict[str, Any], Optional[HTTPDetails]]:
        """Process function result and optionally update HTTP details.

        Args:
            result: The function result
            http_details: Optional HTTP details to update

        Returns:
            Tuple of (result_context dict, updated http_details)
        """


class KwargsEntityExtractor(EntityExtractor):
    """Default entity extractor that looks for entity in kwargs."""

    def __init__(self, kwarg_name: str = "entity"):
        self.kwarg_name = kwarg_name

    def extract(self, func: Callable, args: tuple, kwargs: dict) -> Optional[LogEntity]:
        entity = kwargs.get(self.kwarg_name)
        return LogEntity.from_any(entity) if entity else None


class KwargsHTTPDetailsExtractor(HTTPDetailsExtractor):
    """Default HTTP details extractor that looks for common HTTP kwargs."""

    def extract(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> Optional[HTTPDetails]:
        # Check if http_details is directly provided
        if "http_details" in kwargs:
            hd = kwargs["http_details"]
            if isinstance(hd, HTTPDetails):
                return hd
            elif isinstance(hd, dict):
                return HTTPDetails(**hd)

        # Check kwargs first
        if any(k in kwargs for k in ["method", "url", "headers"]):
            return HTTPDetails(
                method=kwargs.get("method"),
                url=kwargs.get("url"),
                headers=kwargs.get("headers"),
                params=kwargs.get("params"),
                request_body=kwargs.get("body") or kwargs.get("request_body"),
            )

        # If not in kwargs, check function default parameters
        import inspect

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Check if any HTTP-related parameters have non-None values
        http_params = {}
        for param_name in [
            "method",
            "url",
            "headers",
            "params",
            "body",
            "request_body",
        ]:
            if param_name in bound_args.arguments:
                value = bound_args.arguments[param_name]
                if value is not None:
                    http_params[param_name] = value

        # If we found HTTP parameters, create HTTPDetails
        if http_params:
            return HTTPDetails(
                method=http_params.get("method"),
                url=http_params.get("url"),
                headers=http_params.get("headers"),
                params=http_params.get("params"),
                request_body=http_params.get("body") or http_params.get("request_body"),
            )

        return None


class KwargsMultiTenantExtractor(MultiTenantExtractor):
    """Default multi-tenant extractor that looks for multi_tenant in kwargs."""

    def extract(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> Optional[MultiTenant]:
        return MultiTenant.from_kwargs(kwargs)


class DefaultResultProcessor(ResultProcessor):
    """Default result processor with configurable result inclusion."""

    def __init__(self, include_result: bool = False, max_result_length: int = 100):
        self.include_result = include_result
        self.max_result_length = max_result_length

    def process(
        self, result: Any, http_details: Optional[HTTPDetails] = None
    ) -> Tuple[Dict[str, Any], Optional[HTTPDetails]]:
        result_context = {}

        # Update HTTP details if result has status/response attributes
        if http_details and hasattr(result, "status"):
            http_details.status_code = getattr(result, "status", None)

            if hasattr(result, "response"):
                response = result.response
                if isinstance(response, (str, bytes)):
                    http_details.response_size = len(response)
                    http_details.response_body = (
                        str(response)[:500]
                        if len(str(response)) > 500
                        else str(response)
                    )
                elif hasattr(response, "__len__"):
                    try:
                        http_details.response_size = len(response)
                    except Exception:
                        pass

        # Add result to context if requested
        if self.include_result and result is not None:
            if hasattr(result, "__len__") and len(result) > self.max_result_length:
                result_context["result"] = (
                    f"<{type(result).__name__} with {len(result)} items>"
                )
            elif isinstance(result, (str, int, float, bool)):
                result_context["result"] = str(result)
            elif result is None:
                result_context["result"] = "None"
            else:
                result_context["result"] = f"<{type(result).__name__}>"

        return result_context, http_details
